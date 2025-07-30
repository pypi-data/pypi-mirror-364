"""
Cache Manager - handles updating cache with resource changes
"""

import logging
from datetime import datetime
from typing import Any, Dict
import uuid

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cache updates for resource changes"""

    def update_cache_after_create(self, resource: Any) -> None:
        """Update cache with newly created resource"""
        try:
            # Get the current state from the provider to cache the actual resource
            current_state = self._get_current_state(resource)
            if current_state:
                self._add_to_cache_with_resource(resource, current_state)
        except Exception as e:
            logger.debug(f"Failed to update cache after creating {resource.name}: {e}")

    def update_cache_after_update(self, resource: Any) -> None:
        """Update cache with updated resource"""
        try:
            # Get the current state from the provider to cache the updated resource
            current_state = self._get_current_state(resource)
            if current_state:
                self._add_to_cache(resource.name, current_state)
        except Exception as e:
            logger.debug(f"Failed to update cache after updating {resource.name}: {e}")

    def remove_from_cache(self, resource: Any) -> None:
        """Remove resource from cache"""
        try:
            from ....core.state.engine import StateEngine

            # Initialize state engine with file storage for caching
            cache_engine = StateEngine(storage_backend="file")

            # Remove from cache
            cache_engine.storage.delete(resource.name)

        except Exception as e:
            logger.debug(f"Failed to remove {resource.name} from cache: {e}")

    def _get_current_state(self, resource: Any) -> Dict[str, Any] | None:
        """Get current state of resource from provider"""
        try:
            if hasattr(resource, "_provider") and resource._provider:
                from ....core.services.state_detection import create_state_detector
                state_detector = create_state_detector(resource._provider)
                return state_detector.get_current_state(resource)
            return None
        except Exception as e:
            logger.debug(f"Error checking current state for {resource.name}: {e}")
            return None

    def _add_to_cache(self, resource_name: str, resource_state: Dict[str, Any]) -> None:
        """Add or update resource in cache"""
        try:
            from ....core.state.engine import StateEngine

            # Initialize state engine with file storage for caching
            cache_engine = StateEngine(storage_backend="file")

            # Normalize resource state to match state discovery format
            normalized_state = self._normalize_for_cache(resource_state)

            # Add timestamp for cache validation
            normalized_state["discovered_at"] = datetime.now().isoformat()

            # Store in cache
            cache_engine.storage.set(resource_name, normalized_state)

        except Exception as e:
            logger.debug(f"Failed to add {resource_name} to cache: {e}")

    def _add_to_cache_with_resource(self, resource: Any, resource_state: Dict[str, Any]) -> None:
        """Add or update resource in cache with resource context"""
        try:
            from ....core.cache.simple_postgres_cache import get_simple_cache

            # Use PostgreSQL cache instead of file-based cache
            cache = get_simple_cache()

            # Get provider and resource information
            provider = self._detect_provider_from_resource(resource, resource_state)
            resource_type = self._get_resource_type(resource, resource_state)
            resource_id = resource_state.get("id", str(resource.metadata.id))
            resource_name = resource.name
            
            # Extract additional context
            project = getattr(resource.metadata, "project", "")
            environment = getattr(resource.metadata, "environment", "")
            region = resource_state.get("region", "")
            
            # Normalize the resource state using pattern-based normalization
            normalized_state = self._normalize_for_cache_with_resource(resource, resource_state)
            
            # Merge normalized state with original state to preserve all fields
            final_state = {**resource_state, **normalized_state}

            # Cache the resource state in PostgreSQL
            cache.cache_resource_state(
                provider=provider,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=resource_name,
                state_data=final_state,
                project=project,
                environment=environment,
                region=region,
                ttl_seconds=3600  # 1 hour TTL
            )
            
            logger.debug(f"Added {resource_name} ({resource_type}) to PostgreSQL cache with pattern-based normalization")

        except Exception as e:
            logger.debug(f"Failed to add {resource.name} to PostgreSQL cache: {e}")

    def _normalize_for_cache_with_resource(self, resource: Any, resource_state: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize resource state with resource type awareness"""
        try:
            # Detect resource type from resource
            resource_type = self._get_resource_type(resource, resource_state)
            
            # Create a normalized state that matches the state discovery format
            normalized = {
                "name": resource_state.get("name", resource.name),
                "id": resource_state.get("id", str(uuid.uuid4())),
                "type": resource_type,
                "provider": self._detect_provider_from_state(resource_state),
                "state": self._normalize_state(resource_state.get("status", "active")),
                "project": resource_state.get("project", getattr(resource.metadata, "project", "default")),
                "environment": resource_state.get("environment", getattr(resource.metadata, "environment", "unknown")),
                "cloud_id": resource_state.get("id"),
                "region": resource_state.get("region"),
                "zone": resource_state.get("zone"),
                "created_at": resource_state.get("created_at"),
                "tags": resource_state.get("tags", []),
                "metadata": {},
            }
            
            # Add resource-type specific fields
            self._add_resource_specific_fields(normalized, resource, resource_state, resource_type)
            
            return normalized
        except Exception as e:
            logger.debug(f"Error normalizing resource state: {e}")
            return {}

    def _normalize_for_cache(self, resource_state: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize resource state to match state discovery format"""
        try:
            # Create a normalized state that matches the state discovery format
            normalized = {
                "name": resource_state.get("name"),
                "id": resource_state.get("id", str(uuid.uuid4())),
                "type": "VirtualMachine",  # Default type
                "provider": self._detect_provider_from_state(resource_state),
                "state": self._normalize_state(resource_state.get("status", "active")),
                "project": resource_state.get("project", "default"),
                "environment": resource_state.get("environment", "unknown"),
                "cloud_id": resource_state.get("id"),
                "region": resource_state.get("region"),
                "zone": resource_state.get("zone"),
                "machine_type": resource_state.get("machine_type"),
                "size": resource_state.get("size"),
                "image": resource_state.get("image"),
                "ip_address": resource_state.get("ip_address"),
                "private_ip_address": resource_state.get("private_ip_address"),
                "created_at": resource_state.get("created_at"),
                "tags": resource_state.get("tags", []),
                "metadata": {},
                "configuration": {
                    "machine_type": resource_state.get("machine_type"),
                    "size": resource_state.get("size"),
                    "image": resource_state.get("image"),
                    "backups": resource_state.get("backups", False),
                    "monitoring": resource_state.get("monitoring", True),
                    "ipv6": resource_state.get("ipv6", False),
                },
            }

            # Extract metadata from tags
            if isinstance(normalized["tags"], list):
                for tag in normalized["tags"]:
                    if tag.startswith("infradsl.") and ":" in tag:
                        key, value = tag.split(":", 1)
                        normalized["metadata"][key] = value
                        if key == "infradsl.project":
                            normalized["project"] = value
                        elif key == "infradsl.environment":
                            normalized["environment"] = value
                        elif key == "infradsl.id":
                            normalized["id"] = value

            return normalized

        except Exception as e:
            # If normalization fails, return original state with minimal additions
            logger.debug(f"Failed to normalize state for cache: {e}")
            return resource_state

    def _detect_provider_from_state(self, resource_state: Dict[str, Any]) -> str:
        """Detect provider from resource state"""
        # Check for provider-specific fields
        if "machine_type" in resource_state and "zone" in resource_state:
            return "gcp"
        elif "size" in resource_state and resource_state.get("size", "").startswith("s-"):
            return "digitalocean"
        elif "instance_type" in resource_state:
            return "aws"
        else:
            return "unknown"
    
    def _detect_provider_from_resource(self, resource: Any, resource_state: Dict[str, Any]) -> str:
        """Detect provider from resource and state"""
        # Try to get provider from resource first
        if hasattr(resource, "_provider") and resource._provider:
            provider_str = str(resource._provider.__class__.__name__).lower()
            if "gcp" in provider_str or "google" in provider_str:
                return "gcp"
            elif "aws" in provider_str:
                return "aws"
            elif "digitalocean" in provider_str:
                return "digitalocean"
        
        # Fallback to state-based detection
        return self._detect_provider_from_state(resource_state)

    def _normalize_state(self, cloud_status: str) -> str:
        """Normalize cloud status to standard values"""
        status_lower = cloud_status.lower()

        if status_lower in ["running", "active", "available"]:
            return "active"
        elif status_lower in ["stopped", "terminated", "destroyed"]:
            return "inactive"
        elif status_lower in ["provisioning", "staging", "pending", "creating"]:
            return "pending"
        elif status_lower in ["error", "failed", "crashed"]:
            return "error"
        else:
            return "unknown"

    def _get_resource_type(self, resource: Any, resource_state: Dict[str, Any]) -> str:
        """Get the resource type from resource or state"""
        # Try multiple ways to get the resource type
        
        # 1. Check resource annotations
        if hasattr(resource, "metadata") and hasattr(resource.metadata, "annotations"):
            resource_type = resource.metadata.annotations.get("resource_type", "")
            if resource_type:
                return resource_type
        
        # 2. Check resource class name
        class_name = resource.__class__.__name__
        if class_name:
            return class_name
            
        # 3. Check resource _resource_type attribute
        resource_type = getattr(resource, "_resource_type", "")
        if resource_type:
            return resource_type
            
        # 4. Fallback to state-based detection
        if "DomainName" in resource_state and "Id" in resource_state:
            return "CloudFront"
        elif "Bucket" in resource_state or "bucket" in resource_state:
            return "S3"
        elif "HostedZoneId" in resource_state:
            return "Route53"
        elif "machine_type" in resource_state:
            return "VirtualMachine"
        elif "url" in resource_state and "latest_revision" in resource_state:
            return "CloudRun"
            
        return "Unknown"

    def _add_resource_specific_fields(self, normalized: Dict[str, Any], resource: Any, 
                                    resource_state: Dict[str, Any], resource_type: str) -> None:
        """Add resource-type specific fields using universal patterns"""
        try:
            # Use pattern-based normalization instead of hardcoded types
            self._normalize_by_resource_pattern(normalized, resource_state, resource_type)
                
        except Exception as e:
            logger.debug(f"Error adding resource-specific fields: {e}")

    def _normalize_by_resource_pattern(self, normalized: Dict[str, Any], resource_state: Dict[str, Any], resource_type: str) -> None:
        """Universal normalization based on resource type patterns"""
        resource_type_lower = resource_type.lower()
        
        # Compute/Virtual Machine resources pattern
        if any(pattern in resource_type_lower for pattern in ["vm", "instance", "compute", "machine"]):
            self._normalize_compute_resource(normalized, resource_state)
            
        # Storage/Bucket resources pattern
        elif any(pattern in resource_type_lower for pattern in ["storage", "bucket", "s3", "gcs"]):
            self._normalize_storage_resource(normalized, resource_state)
            
        # Database/SQL resources pattern
        elif any(pattern in resource_type_lower for pattern in ["database", "sql", "db", "rds"]):
            self._normalize_database_resource(normalized, resource_state)
            
        # Network/VPC resources pattern
        elif any(pattern in resource_type_lower for pattern in ["network", "vpc", "firewall", "nat", "peering"]):
            self._normalize_network_resource(normalized, resource_state)
            
        # DNS/Domain resources pattern
        elif any(pattern in resource_type_lower for pattern in ["dns", "domain", "route53", "clouddns"]):
            self._normalize_dns_resource(normalized, resource_state)
            
        # CDN/Distribution resources pattern
        elif any(pattern in resource_type_lower for pattern in ["cdn", "cloudfront", "distribution"]):
            self._normalize_cdn_resource(normalized, resource_state)
            
        # Container/Orchestration resources pattern
        elif any(pattern in resource_type_lower for pattern in ["container", "kubernetes", "gke", "eks", "cloudrun", "run"]):
            self._normalize_container_resource(normalized, resource_state)
            
        # Security/Secret resources pattern
        elif any(pattern in resource_type_lower for pattern in ["secret", "certificate", "key", "security"]):
            self._normalize_security_resource(normalized, resource_state)
            
        # Firebase resources pattern
        elif any(pattern in resource_type_lower for pattern in ["firebase", "auth", "hosting"]):
            self._normalize_firebase_resource(normalized, resource_state)
            
        # Load Balancer resources pattern
        elif any(pattern in resource_type_lower for pattern in ["load", "balancer", "lb"]):
            self._normalize_loadbalancer_resource(normalized, resource_state)
            
        # Azure resources pattern
        elif any(pattern in resource_type_lower for pattern in ["azure", "azurevm", "azuresql", "azurestorage"]):
            self._normalize_azure_resource(normalized, resource_state)
            
        # Fallback: extract common fields
        else:
            self._normalize_generic_resource(normalized, resource_state)

    def _normalize_compute_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize compute/virtual machine resources"""
        normalized.update({
            "machine_type": resource_state.get("machine_type") or resource_state.get("instance_type"),
            "size": resource_state.get("size"),
            "image": resource_state.get("image") or resource_state.get("image_id"),
            "ip_address": resource_state.get("ip_address") or resource_state.get("public_ip"),
            "private_ip_address": resource_state.get("private_ip_address") or resource_state.get("private_ip"),
            "availability_zone": resource_state.get("zone") or resource_state.get("availability_zone"),
            "subnet_id": resource_state.get("subnet_id"),
            "security_groups": resource_state.get("security_groups", []),
            "key_pair": resource_state.get("key_name") or resource_state.get("key_pair"),
        })

    def _normalize_storage_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize storage/bucket resources"""
        normalized.update({
            "bucket_name": resource_state.get("Name") or resource_state.get("bucket") or resource_state.get("name"),
            "location": resource_state.get("LocationConstraint") or resource_state.get("location") or resource_state.get("region"),
            "storage_class": resource_state.get("storage_class") or resource_state.get("StorageClass"),
            "versioning": resource_state.get("versioning", False),
            "encryption": resource_state.get("encryption", {}),
            "website_config": resource_state.get("website", {}),
            "cors_config": resource_state.get("cors", []),
            "lifecycle_rules": resource_state.get("lifecycle", []),
        })

    def _normalize_database_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize database/SQL resources"""
        normalized.update({
            "db_instance_class": resource_state.get("tier") or resource_state.get("DBInstanceClass"),
            "engine": resource_state.get("engine") or resource_state.get("Engine"),
            "engine_version": resource_state.get("engine_version") or resource_state.get("EngineVersion"),
            "allocated_storage": resource_state.get("disk_size") or resource_state.get("AllocatedStorage"),
            "storage_type": resource_state.get("disk_type") or resource_state.get("StorageType"),
            "backup_retention": resource_state.get("backup_retention_period"),
            "multi_az": resource_state.get("high_availability") or resource_state.get("MultiAZ"),
            "publicly_accessible": resource_state.get("publicly_accessible", False),
            "vpc_security_groups": resource_state.get("vpc_security_groups", []),
        })

    def _normalize_network_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize network/VPC resources"""
        normalized.update({
            "cidr_block": resource_state.get("cidr") or resource_state.get("CidrBlock"),
            "vpc_id": resource_state.get("vpc_id") or resource_state.get("VpcId"),
            "subnet_id": resource_state.get("subnet_id") or resource_state.get("SubnetId"),
            "route_table_id": resource_state.get("route_table_id"),
            "internet_gateway_id": resource_state.get("internet_gateway_id"),
            "nat_gateway_id": resource_state.get("nat_gateway_id"),
            "network_acl_id": resource_state.get("network_acl_id"),
            "peering_connection_id": resource_state.get("peering_connection_id"),
            "firewall_rules": resource_state.get("allowed", []) or resource_state.get("rules", []),
        })

    def _normalize_dns_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize DNS/domain resources"""
        normalized.update({
            "zone_id": resource_state.get("zone_id") or resource_state.get("HostedZoneId"),
            "dns_name": resource_state.get("dns_name") or resource_state.get("dnsName"),
            "zone_name": resource_state.get("Name") or resource_state.get("name"),
            "name_servers": resource_state.get("name_servers") or resource_state.get("nameServers", []),
            "record_count": resource_state.get("ResourceRecordSetCount"),
            "dnssec_enabled": resource_state.get("dnssec_enabled", False),
            "visibility": resource_state.get("visibility") or resource_state.get("Config.PrivateZone"),
        })

    def _normalize_cdn_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize CDN/distribution resources"""
        normalized.update({
            "distribution_id": resource_state.get("Id") or resource_state.get("distribution_id"),
            "domain_name": resource_state.get("DomainName") or resource_state.get("domain_name"),
            "origin_domain": resource_state.get("origin_domain"),
            "status": resource_state.get("Status") or resource_state.get("status"),
            "comment": resource_state.get("Comment") or resource_state.get("comment"),
            "enabled": resource_state.get("Enabled", True),
            "price_class": resource_state.get("PriceClass") or resource_state.get("price_class"),
            "aliases": resource_state.get("Aliases", []) or resource_state.get("aliases", []),
        })

    def _normalize_container_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize container/orchestration resources"""
        normalized.update({
            "cluster_name": resource_state.get("cluster_name") or resource_state.get("name"),
            "service_url": resource_state.get("url") or resource_state.get("service_url"),
            "latest_revision": resource_state.get("latest_revision"),
            "image": resource_state.get("image") or resource_state.get("container_image"),
            "service_status": resource_state.get("status") or resource_state.get("State"),
            "node_count": resource_state.get("currentNodeCount") or resource_state.get("node_count"),
            "kubernetes_version": resource_state.get("currentMasterVersion") or resource_state.get("version"),
            "endpoint": resource_state.get("endpoint") or resource_state.get("masterAuth.clusterCaCertificate"),
            "node_pools": resource_state.get("nodePools", []),
        })

    def _normalize_security_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize security/secret resources"""
        normalized.update({
            "secret_name": resource_state.get("name") or resource_state.get("Name"),
            "secret_arn": resource_state.get("ARN") or resource_state.get("arn"),
            "version_id": resource_state.get("version") or resource_state.get("VersionId"),
            "certificate_arn": resource_state.get("CertificateArn"),
            "domain_name": resource_state.get("DomainName") or resource_state.get("domain"),
            "certificate_status": resource_state.get("Status") or resource_state.get("status"),
            "expiration_date": resource_state.get("NotAfter") or resource_state.get("expiration"),
            "subject_alternative_names": resource_state.get("SubjectAlternativeNames", []),
            "replication": resource_state.get("replication", {}),
        })

    def _normalize_firebase_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize Firebase resources"""
        normalized.update({
            "project_id": resource_state.get("project_id") or resource_state.get("projectId"),
            "site_name": resource_state.get("site_name") or resource_state.get("name"),
            "default_url": resource_state.get("default_url") or resource_state.get("defaultUrl"),
            "custom_domain": resource_state.get("custom_domain"),
            "auth_config": resource_state.get("auth_config", {}),
            "hosting_config": resource_state.get("hosting_config", {}),
            "enabled_providers": resource_state.get("enabled_providers", []),
        })

    def _normalize_loadbalancer_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize load balancer resources"""
        normalized.update({
            "load_balancer_arn": resource_state.get("LoadBalancerArn") or resource_state.get("arn"),
            "load_balancer_name": resource_state.get("LoadBalancerName") or resource_state.get("name"),
            "dns_name": resource_state.get("DNSName") or resource_state.get("dns_name"),
            "scheme": resource_state.get("Scheme") or resource_state.get("scheme"),
            "load_balancer_type": resource_state.get("Type") or resource_state.get("type"),
            "availability_zones": resource_state.get("AvailabilityZones", []),
            "security_groups": resource_state.get("SecurityGroups", []),
            "target_groups": resource_state.get("target_groups", []),
        })

    def _normalize_azure_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Normalize Azure resources"""
        normalized.update({
            "resource_group": resource_state.get("resourceGroup") or resource_state.get("resource_group"),
            "location": resource_state.get("location") or resource_state.get("region"),
            "provisioning_state": resource_state.get("provisioningState"),
            "vm_size": resource_state.get("hardwareProfile.vmSize") or resource_state.get("size"),
            "os_type": resource_state.get("storageProfile.osDisk.osType"),
            "subscription_id": resource_state.get("subscription_id"),
            "tenant_id": resource_state.get("tenant_id"),
            "managed_identity": resource_state.get("identity", {}),
        })

    def _normalize_generic_resource(self, normalized: Dict[str, Any], resource_state: Dict[str, Any]) -> None:
        """Fallback normalization for unknown resource types"""
        # Extract common fields that most resources have
        common_fields = {
            "resource_id": resource_state.get("id") or resource_state.get("Id") or resource_state.get("resourceId"),
            "resource_name": resource_state.get("name") or resource_state.get("Name") or resource_state.get("resourceName"),
            "resource_type": resource_state.get("type") or resource_state.get("Type") or resource_state.get("resourceType"),
            "location": resource_state.get("location") or resource_state.get("region") or resource_state.get("zone"),
            "arn": resource_state.get("arn") or resource_state.get("ARN"),
            "created_time": resource_state.get("created_at") or resource_state.get("CreationTime") or resource_state.get("creationTimestamp"),
            "modified_time": resource_state.get("updated_at") or resource_state.get("LastModifiedTime") or resource_state.get("lastModifiedTime"),
            "description": resource_state.get("description") or resource_state.get("Description"),
        }
        
        # Only add non-null values
        for key, value in common_fields.items():
            if value is not None:
                normalized[key] = value