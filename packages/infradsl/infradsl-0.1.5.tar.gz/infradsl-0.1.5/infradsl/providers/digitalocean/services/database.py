"""
DigitalOcean Managed Database Service
"""

import requests
from typing import Dict, Any, Optional, List
from ....core.exceptions import ProviderException
from ....core.interfaces.provider import ResourceMetadata
from .tag import TagService


class DatabaseService:
    """Handles managed database operations for DigitalOcean"""

    def __init__(self, client, credentials: Optional[Dict[str, Any]] = None):
        self._client = client
        self._credentials = credentials
        self.tag_service = TagService(credentials)
        self._base_url = "https://api.digitalocean.com/v2"

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make a request to the DigitalOcean API"""
        if not self._credentials:
            raise ProviderException("No credentials configured")

        headers = {
            "Authorization": f"Bearer {self._credentials.get('token')}",
            "Content-Type": "application/json",
        }

        url = f"{self._base_url}/{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ProviderException(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.RequestException as e:
            raise ProviderException(f"API request failed: {str(e)}")

    def create_database(
        self, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Create a DigitalOcean Managed Database"""
        try:
            # Extract database configuration
            db_config = {
                "name": config["name"],
                "engine": config["engine"],
                "version": config["version"],
                "size": config.get("size", "db-s-1vcpu-2gb"),
                "region": config.get("region", "nyc1"),
                "num_nodes": config.get("num_nodes", 1),
            }

            # Add database-specific configuration for SQL databases
            if config["engine"] in ["pg", "mysql"]:
                if config.get("database_name"):
                    # DigitalOcean uses 'database' field for the database name
                    db_config["database"] = config["database_name"]
                if config.get("database_user"):
                    # DigitalOcean uses 'user' field for the database user
                    db_config["user"] = config["database_user"]
            
            # Add SSL configuration
            if config.get("require_ssl", True):
                db_config["ssl"] = True

            # Convert tags
            tags_dict = config.get("tags", {})
            tag_list = self.tag_service.convert_tags_to_digitalocean(tags_dict)
            if tag_list:
                db_config["tags"] = tag_list

            # Create database cluster via API
            response = self._make_request("POST", "databases", db_config)
            database_data = response.get("database", {})

            # Wait for database to be ready
            database_id = database_data.get("id")
            database_data = self._wait_for_database(database_id)

            # Configure allowed IPs (firewall rules) - this must be done after creation
            if config.get("allowed_ips"):
                self._update_firewall_rules(database_id, config["allowed_ips"])
            else:
                # If no allowed IPs specified, default to secure configuration
                # Block all access initially - user must explicitly allow IPs
                self._update_firewall_rules(database_id, [])

            # Get connection details
            connection_info = self._get_connection_info(database_data)

            return {
                "cloud_id": database_data.get("id"),
                "name": database_data.get("name"),
                "status": database_data.get("status"),
                "provider_type": "digitalocean",
                "region": database_data.get("region"),
                "engine": database_data.get("engine"),
                "version": database_data.get("version"),
                "size": database_data.get("size"),
                "host": connection_info["host"],
                "port": connection_info["port"],
                "database": connection_info["database"],
                "username": connection_info["username"],
                "password": connection_info["password"],
                "uri": connection_info["uri"],
                "tags": self.tag_service.convert_tags_from_digitalocean(
                    database_data.get("tags", [])
                ),
            }

        except Exception as e:
            raise ProviderException(f"Failed to create database: {str(e)}")

    def get_database(self, database_id: str) -> Optional[Dict[str, Any]]:
        """Get database details"""
        try:
            # Get database cluster via API
            response = self._make_request("GET", f"databases/{database_id}")
            database_data = response.get("database", {})

            if not database_data:
                return None

            # Get connection details
            connection_info = self._get_connection_info(database_data)

            return {
                "cloud_id": database_data.get("id"),
                "name": database_data.get("name"),
                "status": database_data.get("status"),
                "provider_type": "digitalocean",
                "region": database_data.get("region"),
                "engine": database_data.get("engine"),
                "version": database_data.get("version"),
                "size": database_data.get("size"),
                "host": connection_info["host"],
                "port": connection_info["port"],
                "database": connection_info["database"],
                "username": connection_info["username"],
                "password": connection_info["password"],
                "uri": connection_info["uri"],
                "tags": self.tag_service.convert_tags_from_digitalocean(
                    database_data.get("tags", [])
                ),
                "created_at": database_data.get("created_at"),
                "maintenance_window": database_data.get("maintenance_window", {}),
            }

        except Exception as e:
            raise ProviderException(f"Failed to get database: {str(e)}")

    def update_database(
        self, database_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update database configuration"""
        try:
            # Get current database
            current_db = self.get_database(database_id)
            if not current_db:
                raise ProviderException(f"Database {database_id} not found")

            # Update allowed configuration
            # Note: DigitalOcean has limited update capabilities for databases
            updated = False

            # Update size if changed
            if "size" in updates and updates["size"] != current_db.get("size"):
                resize_data = {"size": updates["size"]}
                self._make_request(
                    "PUT", f"databases/{database_id}/resize", resize_data
                )
                updated = True

            # Update firewall rules if changed
            if "allowed_ips" in updates:
                self._update_firewall_rules(database_id, updates["allowed_ips"])
                updated = True

            # Update tags if changed
            if "tags" in updates:
                tag_list = self.tag_service.convert_tags_to_digitalocean(
                    updates["tags"]
                )
                tag_data = {"tags": tag_list}
                self._make_request("PUT", f"databases/{database_id}/tags", tag_data)
                updated = True

            # Update maintenance window if changed
            if "maintenance_day" in updates or "maintenance_hour" in updates:
                current_maintenance = current_db.get("maintenance_window", {})
                maintenance_window = {
                    "day": updates.get(
                        "maintenance_day", current_maintenance.get("day")
                    ),
                    "hour": updates.get(
                        "maintenance_hour", current_maintenance.get("hour")
                    ),
                }
                self._make_request(
                    "PUT", f"databases/{database_id}/maintenance", maintenance_window
                )
                updated = True

            if updated:
                # Wait for updates to complete
                self._wait_for_database(database_id)

            result = self.get_database(database_id)
            if result is None:
                raise ProviderException(
                    f"Database {database_id} not found after update"
                )
            return result

        except Exception as e:
            raise ProviderException(f"Failed to update database: {str(e)}")

    def delete_database(self, database_id: str) -> None:
        """Delete a database cluster"""
        try:
            # Delete database via API
            self._make_request("DELETE", f"databases/{database_id}")

        except Exception as e:
            raise ProviderException(f"Failed to delete database: {str(e)}")

    def list_databases(
        self, tags: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """List all databases, optionally filtered by tags"""
        try:
            # Get all database clusters via API
            response = self._make_request("GET", "databases")
            databases = response.get("databases", [])

            result = []
            for db_data in databases:
                # Convert database tags to dict
                db_tags_list = self.tag_service.convert_tags_from_digitalocean(
                    db_data.get("tags", [])
                )

                # Convert tag list to dict for filtering
                db_tags = {}
                for tag in db_tags_list:
                    if ":" in tag:
                        key, value = tag.split(":", 1)
                        db_tags[key] = value

                # Filter by tags if specified
                if tags:
                    if not all(db_tags.get(k) == v for k, v in tags.items()):
                        continue

                # Get connection details
                connection_info = self._get_connection_info(db_data)

                result.append(
                    {
                        "cloud_id": db_data.get("id"),
                        "name": db_data.get("name"),
                        "status": db_data.get("status"),
                        "provider_type": "digitalocean",
                        "region": db_data.get("region"),
                        "engine": db_data.get("engine"),
                        "version": db_data.get("version"),
                        "size": db_data.get("size"),
                        "host": connection_info["host"],
                        "port": connection_info["port"],
                        "database": connection_info["database"],
                        "username": connection_info["username"],
                        "uri": connection_info["uri"],
                        "tags": db_tags,
                    }
                )

            return result

        except Exception as e:
            raise ProviderException(f"Failed to list databases: {str(e)}")

    def _wait_for_database(self, database_id: str) -> Dict[str, Any]:
        """Wait for database to be ready"""
        import time

        max_attempts = 30  # 15 minutes max
        attempt = 0

        while attempt < max_attempts:
            response = self._make_request("GET", f"databases/{database_id}")
            database_data = response.get("database", {})

            if database_data.get("status") == "online":
                return database_data

            time.sleep(30)  # Check every 30 seconds
            attempt += 1

        raise ProviderException(f"Database {database_id} did not become ready in time")

    def _update_firewall_rules(self, database_id: str, allowed_ips: List[str]) -> None:
        """Update database firewall rules"""
        try:
            # Convert IPs to firewall rules format
            rules = []
            for ip in allowed_ips:
                rules.append({"type": "ip_addr", "value": ip})

            # Update firewall rules via API
            self._make_request(
                "PUT", f"databases/{database_id}/firewall", {"rules": rules}
            )

        except Exception as e:
            raise ProviderException(f"Failed to update firewall rules: {str(e)}")

    def _get_connection_info(self, database_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract connection information from database data"""
        try:
            # Get primary connection info
            connection = database_data.get("connection", {})

            # Build connection URI based on engine
            uri = connection.get("uri", "")

            return {
                "host": connection.get("host", ""),
                "port": connection.get("port", 0),
                "database": connection.get("database", ""),
                "username": connection.get("user", ""),
                "password": connection.get("password", ""),
                "uri": uri,
                "ssl_required": connection.get("ssl", True),
            }

        except Exception as e:
            raise ProviderException(f"Failed to get connection info: {str(e)}")

    def plan_create_database(
        self, config: Dict[str, Any], metadata: ResourceMetadata
    ) -> Dict[str, Any]:
        """Preview the creation of a DigitalOcean managed database"""
        # Validate configuration first
        errors = self._validate_database_config(config)
        if errors:
            return {
                "resource_type": "managed_database",
                "action": "create",
                "status": "error",
                "errors": errors,
                "config": config,
            }

        # Estimate cost
        cost = self._estimate_database_cost(config)

        # Build the preview plan
        return {
            "resource_type": "managed_database",
            "action": "create",
            "status": "ready",
            "config": config,
            "metadata": metadata.to_dict(),
            "estimated_cost": cost,
            "changes": {
                "create": {
                    "name": config["name"],
                    "engine": config["engine"],
                    "version": config["version"],
                    "size": config.get("size", "db-s-1vcpu-2gb"),
                    "region": config.get("region", "nyc1"),
                    "num_nodes": config.get("num_nodes", 1),
                    "database_name": config.get("database_name"),
                    "database_user": config.get("database_user"),
                    "require_ssl": config.get("require_ssl", True),
                    "allowed_ips": config.get("allowed_ips", []),
                    "tags": config.get("tags", {}),
                }
            },
        }

    def plan_update_database(
        self, database_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Preview the update of a DigitalOcean managed database"""
        # Get current database state
        current_database = self.get_database(database_id)
        if not current_database:
            return {
                "resource_type": "managed_database",
                "resource_id": database_id,
                "action": "update",
                "status": "error",
                "message": f"Database {database_id} not found",
            }

        # Analyze what changes would be made
        changes = {}
        if "size" in updates and updates["size"] != current_database.get("size"):
            changes["size"] = {
                "old": current_database.get("size"),
                "new": updates["size"],
            }

        if "allowed_ips" in updates:
            current_ips = current_database.get("allowed_ips", [])
            new_ips = updates["allowed_ips"]
            if current_ips != new_ips:
                changes["allowed_ips"] = {
                    "old": current_ips,
                    "new": new_ips,
                }

        if "tags" in updates:
            current_tags = current_database.get("tags", {})
            new_tags = updates["tags"]
            if current_tags != new_tags:
                changes["tags"] = {
                    "old": current_tags,
                    "new": new_tags,
                }

        # Note: DigitalOcean doesn't support changing engine, version, or region after creation
        unsupported_changes = []
        for field in ["engine", "version", "region", "name"]:
            if field in updates:
                unsupported_changes.append(
                    f"Cannot change {field} after database creation"
                )

        return {
            "resource_type": "managed_database",
            "resource_id": database_id,
            "action": "update",
            "status": "ready" if not unsupported_changes else "warning",
            "changes": changes,
            "warnings": unsupported_changes,
            "current_state": current_database,
            "updates": updates,
        }

    def plan_delete_database(self, database_id: str) -> Dict[str, Any]:
        """Preview the deletion of a DigitalOcean managed database"""
        # Get current database state
        current_database = self.get_database(database_id)
        if not current_database:
            return {
                "resource_type": "managed_database",
                "resource_id": database_id,
                "action": "delete",
                "status": "error",
                "message": f"Database {database_id} not found",
            }

        # Check for potential impact
        warnings = []
        if current_database.get("status") == "online":
            warnings.append("Database is currently online and serving traffic")

        return {
            "resource_type": "managed_database",
            "resource_id": database_id,
            "action": "delete",
            "status": "ready",
            "current_state": current_database,
            "warnings": warnings,
            "impact": {
                "data_loss": "All data in the database will be permanently lost",
                "connection_loss": "All connections to the database will be terminated",
                "backups": "Existing backups will be retained for 7 days",
            },
        }

    def discover_databases(
        self, query: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """Discover DigitalOcean managed databases with enhanced metadata"""
        # For now, this is similar to list_databases but could be enhanced with:
        # - Unmanaged resource detection
        # - Cost analysis
        # - Security scanning
        # - Compliance checking
        tags = query.filters.get("tags") if query and hasattr(query, "filters") else None
        databases = self.list_databases(tags)

        # Enhance each database with discovery metadata
        enhanced_databases = []
        for database in databases:
            enhanced_database = database.copy()
            enhanced_database["discovery_metadata"] = {
                "discovered_at": self._get_current_timestamp(),
                "managed_by_infradsl": self._is_managed_by_infradsl(database),
                "cost_analysis": self._analyze_database_cost(database),
            }
            enhanced_databases.append(enhanced_database)

        return enhanced_databases

    def _validate_database_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate database configuration"""
        errors = []

        if "name" not in config:
            errors.append("Database name is required")

        if "engine" not in config:
            errors.append("Database engine is required")
        elif config["engine"] not in ["pg", "mysql", "redis", "mongodb"]:
            errors.append(f"Invalid database engine: {config['engine']}")

        if "version" not in config:
            errors.append("Database version is required")

        if "region" in config:
            # This would need to check against actual regions
            pass

        if "size" in config:
            # This would need to check against actual sizes
            pass

        return errors

    def _estimate_database_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for a managed database"""
        # DigitalOcean database pricing (approximate)
        size_costs = {
            "db-s-1vcpu-1gb": {"hourly": 0.022, "monthly": 15.0},  # Basic
            "db-s-1vcpu-2gb": {"hourly": 0.037, "monthly": 25.0},  # Standard
            "db-s-2vcpu-4gb": {"hourly": 0.084, "monthly": 60.0},  # Performance
            "db-s-4vcpu-8gb": {"hourly": 0.169, "monthly": 120.0},  # Professional
            "db-s-6vcpu-16gb": {"hourly": 0.337, "monthly": 240.0},  # Premium
            "db-s-8vcpu-32gb": {"hourly": 0.675, "monthly": 480.0},  # High Performance
        }

        size = config.get("size", "db-s-1vcpu-2gb")
        costs = size_costs.get(size, {"hourly": 0.037, "monthly": 25.0})

        # Additional nodes increase cost
        num_nodes = config.get("num_nodes", 1)
        standby_nodes = config.get("standby_nodes", 0)
        total_nodes = num_nodes + standby_nodes

        return {
            "hourly": costs["hourly"] * total_nodes,
            "monthly": costs["monthly"] * total_nodes,
        }

    def _get_current_timestamp(self) -> str:
        """Get current timestamp for discovery metadata"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

    def _is_managed_by_infradsl(self, database: Dict[str, Any]) -> bool:
        """Check if database is managed by InfraDSL"""
        tags = database.get("tags", {})
        return "infradsl.managed" in tags or "infradsl:managed" in tags

    def _analyze_database_cost(self, database: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost for a database"""
        size = database.get("size", "db-s-1vcpu-2gb")
        config = {"size": size}
        return self._estimate_database_cost(config)
