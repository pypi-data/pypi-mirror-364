"""
DigitalOcean Managed Database
"""

from typing import Optional, List, Dict, Any, Self
from dataclasses import dataclass, field
from enum import Enum

from ...core.nexus.base_resource import BaseResource, ResourceSpec
from ...core.interfaces.provider import ProviderType


class DatabaseEngine(Enum):
    """Supported database engines"""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    REDIS = "redis"
    MONGODB = "mongodb"


class DatabaseSize(Enum):
    """Standardized database sizes"""

    BASIC = "basic"  # 1 CPU, 1GB RAM, 10GB disk
    STANDARD = "standard"  # 1 CPU, 2GB RAM, 25GB disk
    PERFORMANCE = "performance"  # 2 CPU, 4GB RAM, 50GB disk
    PROFESSIONAL = "professional"  # 4 CPU, 8GB RAM, 115GB disk
    CUSTOM = "custom"  # Custom specifications


@dataclass
class ManagedDatabaseSpec(ResourceSpec):
    """Specification for a managed database resource"""

    # Core configuration
    engine: DatabaseEngine = DatabaseEngine.POSTGRESQL
    version: str = "14"
    size: DatabaseSize = DatabaseSize.STANDARD

    # Custom sizing (when size is CUSTOM)
    cpu_cores: Optional[int] = None
    memory_gb: Optional[int] = None
    disk_size_gb: Optional[int] = None

    # Database configuration
    database_name: str = "defaultdb"
    database_user: Optional[str] = None

    # High availability
    num_nodes: int = 1
    standby_nodes: int = 0

    # Security
    allowed_ips: List[str] = field(default_factory=list)
    require_ssl: bool = True

    # Backup configuration
    backup_hour: int = 2  # UTC hour for automated backups
    backup_minute: int = 0  # Minute within the hour

    # Maintenance
    maintenance_day: str = "sunday"  # Day of week for maintenance
    maintenance_hour: int = 4  # UTC hour for maintenance

    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class ManagedDatabase(BaseResource):
    """
    Universal managed database resource that works across providers.

    Examples:
        # Simple PostgreSQL database
        db = ManagedDatabase("my-db").postgresql().create()

        # Custom configuration
        db = (ManagedDatabase("app-db")
              .postgresql("14")
              .size(DatabaseSize.PERFORMANCE)
              .database_name("myapp")
              .high_availability(3)
              .allow_ip("10.0.0.0/8")
              .create())
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.spec: ManagedDatabaseSpec = self._create_spec()

    def _create_spec(self) -> ManagedDatabaseSpec:
        return ManagedDatabaseSpec()

    def _validate_spec(self) -> None:
        """Validate database specification"""
        if self.spec.size == DatabaseSize.CUSTOM:
            if not all(
                [self.spec.cpu_cores, self.spec.memory_gb, self.spec.disk_size_gb]
            ):
                raise ValueError(
                    "Custom database size requires cpu_cores, memory_gb, and disk_size_gb"
                )

        if self.spec.num_nodes < 1:
            raise ValueError("Number of nodes must be at least 1")

        if not self.spec.database_name:
            raise ValueError("Database name is required")

        # Validate maintenance day
        valid_days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        if self.spec.maintenance_day.lower() not in valid_days:
            raise ValueError(f"Invalid maintenance day. Must be one of: {valid_days}")

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        # Handle case where provider is still a string (not resolved)
        if isinstance(self._provider, str):
            provider_type_str = self._provider.lower()
        else:
            # Get provider type from provider object
            provider_type = self._provider.config.type
            provider_type_str = (
                provider_type.value
                if hasattr(provider_type, "value")
                else str(provider_type)
            )

        # Base configuration
        config = {
            "name": self.metadata.name,
            "engine": self.spec.engine.value,
            "version": self.spec.version,
            "size": self.spec.size.value,
            "database_name": self.spec.database_name,
            "database_user": self.spec.database_user,
            "num_nodes": self.spec.num_nodes,
            "standby_nodes": self.spec.standby_nodes,
            "allowed_ips": self.spec.allowed_ips,
            "require_ssl": self.spec.require_ssl,
            "backup_hour": self.spec.backup_hour,
            "backup_minute": self.spec.backup_minute,
            "maintenance_day": self.spec.maintenance_day,
            "maintenance_hour": self.spec.maintenance_hour,
            "tags": self.metadata.to_tags(),
        }

        # Add custom sizing if specified
        if self.spec.size == DatabaseSize.CUSTOM:
            config.update(
                {
                    "cpu_cores": self.spec.cpu_cores,
                    "memory_gb": self.spec.memory_gb,
                    "disk_size_gb": self.spec.disk_size_gb,
                }
            )

        # Provider-specific mappings
        if provider_type_str.lower() in ["digital_ocean", "digitalocean"]:
            config.update(self._to_digitalocean_config())
        # Future: AWS RDS, GCP Cloud SQL support

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_digitalocean_config(self) -> Dict[str, Any]:
        """Convert to DigitalOcean Managed Database configuration"""
        # Map database sizes to DO slugs
        size_mapping = {
            DatabaseSize.BASIC: "db-s-1vcpu-1gb",
            DatabaseSize.STANDARD: "db-s-1vcpu-2gb",
            DatabaseSize.PERFORMANCE: "db-s-2vcpu-4gb",
            DatabaseSize.PROFESSIONAL: "db-s-4vcpu-8gb",
        }

        # Map engines to DO engine names
        engine_mapping = {
            DatabaseEngine.POSTGRESQL: "pg",
            DatabaseEngine.MYSQL: "mysql",
            DatabaseEngine.REDIS: "redis",
            DatabaseEngine.MONGODB: "mongodb",
        }

        config = {
            "resource_type": "managed_database",
            "engine": engine_mapping.get(self.spec.engine, "pg"),
            "size": size_mapping.get(self.spec.size, "db-s-1vcpu-2gb"),
            "region": getattr(self.spec, "region", "nyc1"),
        }

        # DigitalOcean specific fields
        if self.spec.engine in [DatabaseEngine.POSTGRESQL, DatabaseEngine.MYSQL]:
            # SQL databases support multiple nodes for HA
            if self.spec.num_nodes > 1:
                config["num_nodes"] = self.spec.num_nodes

        # Redis and MongoDB use different sizing approach
        if self.spec.engine == DatabaseEngine.REDIS:
            config["size"] = "db-s-1vcpu-1gb"  # Redis has different sizing

        return config

    # Fluent interface methods

    def postgresql(self, version: str = "14") -> Self:
        """Set PostgreSQL engine"""
        self.spec.engine = DatabaseEngine.POSTGRESQL
        self.spec.version = version
        return self

    def mysql(self, version: str = "8") -> Self:
        """Set MySQL engine"""
        self.spec.engine = DatabaseEngine.MYSQL
        self.spec.version = version
        return self

    def redis(self, version: str = "7") -> Self:
        """Set Redis engine"""
        self.spec.engine = DatabaseEngine.REDIS
        self.spec.version = version
        return self

    def mongodb(self, version: str = "5.0") -> Self:
        """Set MongoDB engine"""
        self.spec.engine = DatabaseEngine.MONGODB
        self.spec.version = version
        return self

    def size(self, database_size: DatabaseSize) -> Self:
        """Set database size"""
        self.spec.size = database_size
        return self

    def custom_size(self, cpu_cores: int, memory_gb: int, disk_size_gb: int) -> Self:
        """Set custom database size"""
        self.spec.size = DatabaseSize.CUSTOM
        self.spec.cpu_cores = cpu_cores
        self.spec.memory_gb = memory_gb
        self.spec.disk_size_gb = disk_size_gb
        return self

    def database_name(self, name: str) -> Self:
        """Set database name"""
        self.spec.database_name = name
        return self

    def database_user(self, username: str) -> Self:
        """Set database username"""
        self.spec.database_user = username
        return self

    def high_availability(self, num_nodes: int, standby_nodes: int = 0) -> Self:
        """Configure high availability with multiple nodes"""
        self.spec.num_nodes = num_nodes
        self.spec.standby_nodes = standby_nodes
        return self

    def allow_ip(self, ip_cidr: str) -> Self:
        """Add allowed IP address or CIDR range"""
        if ip_cidr not in self.spec.allowed_ips:
            self.spec.allowed_ips.append(ip_cidr)
        return self

    def allow_ips(self, ip_cidrs: List[str]) -> Self:
        """Set allowed IP addresses or CIDR ranges"""
        self.spec.allowed_ips = ip_cidrs
        return self

    def ssl_required(self, required: bool = True) -> Self:
        """Require SSL connections"""
        self.spec.require_ssl = required
        return self

    def backup_schedule(self, hour: int, minute: int = 0) -> Self:
        """Set automated backup schedule (UTC)"""
        if not (0 <= hour <= 23):
            raise ValueError("Hour must be between 0 and 23")
        if not (0 <= minute <= 59):
            raise ValueError("Minute must be between 0 and 59")

        self.spec.backup_hour = hour
        self.spec.backup_minute = minute
        return self

    def maintenance_window(self, day: str, hour: int) -> Self:
        """Set maintenance window"""
        valid_days = [
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ]
        if day.lower() not in valid_days:
            raise ValueError(f"Invalid day. Must be one of: {valid_days}")
        if not (0 <= hour <= 23):
            raise ValueError("Hour must be between 0 and 23")

        self.spec.maintenance_day = day.lower()
        self.spec.maintenance_hour = hour
        return self

    def provider_override(self, **kwargs) -> Self:
        """Override provider-specific settings"""
        self.spec.provider_config.update(kwargs)
        return self

    # Provider-specific implementations

    def _provider_create(self) -> Dict[str, Any]:
        """Create the database via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        # Type cast to help type checker
        from typing import cast
        from ...core.interfaces.provider import ProviderInterface

        provider = cast(ProviderInterface, self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the database via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        if not self.status.cloud_id:
            raise ValueError(
                "Resource has no cloud ID - cannot update a resource that hasn't been created"
            )

        # Type cast to help type checker
        from typing import cast
        from ...core.interfaces.provider import ProviderInterface

        provider = cast(ProviderInterface, self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the database via provider"""
        if not self._provider:
            raise ValueError("No provider attached")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use a provider factory or ensure proper provider setup."
            )

        if not self.status.cloud_id:
            raise ValueError(
                "Resource has no cloud ID - cannot destroy a resource that hasn't been created"
            )

        # Type cast to help type checker
        from typing import cast
        from ...core.interfaces.provider import ProviderInterface

        provider = cast(ProviderInterface, self._provider)

        config = self._to_provider_config()
        resource_type = config.pop("resource_type")

        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )

    # Convenience methods

    def get_connection_uri(self) -> Optional[str]:
        """Get database connection URI"""
        provider_data = self.status.provider_data
        if not provider_data:
            return None

        host = provider_data.get("host")
        port = provider_data.get("port")
        database = provider_data.get("database")
        username = provider_data.get("username")
        password = provider_data.get("password")

        if not all([host, port, database, username]):
            return None

        # Build connection URI based on engine
        if self.spec.engine == DatabaseEngine.POSTGRESQL:
            ssl_param = "?sslmode=require" if self.spec.require_ssl else ""
            return f"postgresql://{username}:{password}@{host}:{port}/{database}{ssl_param}"
        elif self.spec.engine == DatabaseEngine.MYSQL:
            ssl_param = "?ssl-mode=REQUIRED" if self.spec.require_ssl else ""
            return f"mysql://{username}:{password}@{host}:{port}/{database}{ssl_param}"
        elif self.spec.engine == DatabaseEngine.REDIS:
            ssl_scheme = "rediss" if self.spec.require_ssl else "redis"
            return f"{ssl_scheme}://{username}:{password}@{host}:{port}"
        elif self.spec.engine == DatabaseEngine.MONGODB:
            ssl_param = "?ssl=true" if self.spec.require_ssl else ""
            return (
                f"mongodb://{username}:{password}@{host}:{port}/{database}{ssl_param}"
            )

        return None

    def get_host(self) -> Optional[str]:
        """Get database host"""
        return self.status.provider_data.get("host")

    def get_port(self) -> Optional[int]:
        """Get database port"""
        return self.status.provider_data.get("port")

    def get_credentials(self) -> Dict[str, str]:
        """Get database credentials"""
        provider_data = self.status.provider_data
        return {
            "username": provider_data.get("username", ""),
            "password": provider_data.get("password", ""),
            "database": provider_data.get("database", ""),
        }

    @property
    def _resource_type(self) -> str:
        """Get resource type name for state detection"""
        return "ManagedDatabase"
