"""
Universal state detection service for cross-provider resource management.

This service provides a provider-agnostic way to detect the current state
of resources across different cloud providers.
"""

from typing import Any, Dict, List, Optional
import logging
from ..interfaces.provider import ProviderInterface
from ..interfaces.resource_mapping import (
    StandardResourceType,
    get_resource_mapping,
    normalize_resource_data,
)
from ..nexus.base_resource import ResourceState

logger = logging.getLogger(__name__)


class UniversalStateDetector:
    """Detects resource state across different cloud providers"""

    def __init__(self, provider: ProviderInterface):
        self.provider = provider
        self.provider_type = provider.config.type.value

    def get_current_state(self, resource: Any) -> Optional[Dict[str, Any]]:
        """
        Get current state of resource from provider in normalized format.

        Args:
            resource: InfraDSL resource instance

        Returns:
            Normalized resource data or None if not found
        """
        try:
            # Determine standard resource type from InfraDSL resource
            standard_type = self._get_standard_resource_type(resource)
            if not standard_type:
                logger.warning(f"Unknown resource type for {resource.name}")
                return None

            # Get provider-specific mapping
            mapping = get_resource_mapping(self.provider_type, standard_type)
            if not mapping:
                logger.warning(
                    f"No mapping for {standard_type} on {self.provider_type}"
                )
                return None

            # Check if provider has cached state lookup capability
            if hasattr(self.provider, 'get_resource_state'):
                # Try cached lookup first (for cached providers)
                cached_state = self.provider.get_resource_state(resource.metadata)
                if cached_state:
                    # Convert cached state to expected format
                    cloud_id = cached_state.get('id')
                    if cloud_id and hasattr(resource, "status"):
                        resource.status.cloud_id = str(cloud_id)
                        resource.status.state = ResourceState.ACTIVE
                    return cached_state
            
            # Fallback to provider-specific list operation
            raw_resources = self.provider.list_resources(mapping.list_operation)

            for raw_resource in raw_resources:
                if raw_resource.get(mapping.name_field) == resource.name:
                    # Link the resource to cloud ID for updates
                    cloud_id = raw_resource.get(mapping.id_field)
                    if cloud_id and hasattr(resource, "status"):
                        resource.status.cloud_id = str(cloud_id)

                        # Set resource state based on provider status
                        status = raw_resource.get(mapping.status_field, "").lower()
                        if mapping.active_statuses and any(
                            active in status for active in mapping.active_statuses
                        ):
                            resource.status.state = ResourceState.ACTIVE
                        else:
                            resource.status.state = ResourceState.PENDING

                    # Extract and preserve resource identity from tags
                    self._extract_resource_identity(resource, raw_resource, mapping)

                    # Return normalized resource data
                    return normalize_resource_data(
                        self.provider_type, standard_type, raw_resource
                    )

            return None

        except Exception as e:
            logger.debug(f"Error checking current state for {resource.name}: {e}")
            return None

    def _get_standard_resource_type(
        self, resource: Any
    ) -> Optional[StandardResourceType]:
        """Map InfraDSL resource to standard resource type"""
        # Try multiple ways to get the resource type
        resource_type_name = getattr(resource, "_resource_type", "").lower()
        
        # If not found, check metadata annotations
        if not resource_type_name and hasattr(resource, "metadata") and hasattr(resource.metadata, "annotations"):
            resource_type_name = resource.metadata.annotations.get("resource_type", "").lower()
        
        # If still not found, use class name as fallback
        if not resource_type_name:
            resource_type_name = resource.__class__.__name__.lower()

        type_mapping = {
            # Core Compute Resources
            "virtualmachine": StandardResourceType.VIRTUAL_MACHINE,
            "vm": StandardResourceType.VIRTUAL_MACHINE,
            "instance": StandardResourceType.VIRTUAL_MACHINE,
            "staticip": StandardResourceType.STATIC_IP,
            "static_ip": StandardResourceType.STATIC_IP,
            "instancegroup": StandardResourceType.INSTANCE_GROUP,
            "instance_group": StandardResourceType.INSTANCE_GROUP,
            "webserver": StandardResourceType.WEB_SERVER,
            "web_server": StandardResourceType.WEB_SERVER,
            
            # Container & Orchestration Resources
            "cloudrun": StandardResourceType.CLOUD_RUN,
            "cloud_run": StandardResourceType.CLOUD_RUN,
            "kubernetescluster": StandardResourceType.KUBERNETES_CLUSTER,
            "kubernetes_cluster": StandardResourceType.KUBERNETES_CLUSTER,
            "gke": StandardResourceType.KUBERNETES_CLUSTER,
            "gkecluster": StandardResourceType.KUBERNETES_CLUSTER,
            "gke_cluster": StandardResourceType.KUBERNETES_CLUSTER,
            "containerservice": StandardResourceType.CONTAINER_SERVICE,
            "container_service": StandardResourceType.CONTAINER_SERVICE,
            
            # Database Resources
            "database": StandardResourceType.DATABASE,
            "db": StandardResourceType.DATABASE,
            "cloudsql": StandardResourceType.CLOUD_SQL,
            "cloud_sql": StandardResourceType.CLOUD_SQL,
            "rds": StandardResourceType.DATABASE,
            "awsrds": StandardResourceType.DATABASE,
            
            # Storage Resources
            "storage": StandardResourceType.STORAGE,
            "storagebucket": StandardResourceType.STORAGE_BUCKET,
            "storage_bucket": StandardResourceType.STORAGE_BUCKET,
            "cloudstorage": StandardResourceType.CLOUD_STORAGE,
            "cloud_storage": StandardResourceType.CLOUD_STORAGE,
            "gcloudstorage": StandardResourceType.CLOUD_STORAGE,
            "gcs": StandardResourceType.CLOUD_STORAGE,
            "s3": StandardResourceType.S3,
            "bucket": StandardResourceType.STORAGE_BUCKET,
            
            # Network Resources
            "network": StandardResourceType.NETWORK,
            "vpc": StandardResourceType.VPC,
            "vpcnetwork": StandardResourceType.VPC,
            "vpc_network": StandardResourceType.VPC,
            "vpcpeering": StandardResourceType.VPC_PEERING,
            "vpc_peering": StandardResourceType.VPC_PEERING,
            "sharedvpc": StandardResourceType.SHARED_VPC,
            "shared_vpc": StandardResourceType.SHARED_VPC,
            "natgateway": StandardResourceType.NAT_GATEWAY,
            "nat_gateway": StandardResourceType.NAT_GATEWAY,
            "cloudnat": StandardResourceType.CLOUD_NAT,
            "cloud_nat": StandardResourceType.CLOUD_NAT,
            
            # Security Resources
            "securitygroup": StandardResourceType.SECURITY_GROUP,
            "security_group": StandardResourceType.SECURITY_GROUP,
            "firewall": StandardResourceType.FIREWALL,
            "vpcfirewall": StandardResourceType.VPC_FIREWALL,
            "vpc_firewall": StandardResourceType.VPC_FIREWALL,
            "secret": StandardResourceType.SECRET,
            "secretmanager": StandardResourceType.SECRET_MANAGER,
            "secret_manager": StandardResourceType.SECRET_MANAGER,
            "certificate": StandardResourceType.CERTIFICATE,
            "certificatemanager": StandardResourceType.CERTIFICATE_MANAGER,
            "certificate_manager": StandardResourceType.CERTIFICATE_MANAGER,
            
            # DNS & CDN Resources
            "dns": StandardResourceType.DNS_RECORD,
            "dnsrecord": StandardResourceType.DNS_RECORD,
            "dns_record": StandardResourceType.DNS_RECORD,
            "clouddns": StandardResourceType.CLOUD_DNS,
            "cloud_dns": StandardResourceType.CLOUD_DNS,
            "cdn": StandardResourceType.CDN,
            "cloudfront": StandardResourceType.CLOUDFRONT,
            "route53": StandardResourceType.ROUTE53,
            "domainregistration": StandardResourceType.DOMAIN_REGISTRATION,
            "domain_registration": StandardResourceType.DOMAIN_REGISTRATION,
            
            # Load Balancer Resources
            "loadbalancer": StandardResourceType.LOAD_BALANCER,
            "load_balancer": StandardResourceType.LOAD_BALANCER,
            "lb": StandardResourceType.LOAD_BALANCER,
            
            # Firebase Resources
            "firebase": StandardResourceType.FIREBASE_SERVICE,
            "firebaseservice": StandardResourceType.FIREBASE_SERVICE,
            "firebase_service": StandardResourceType.FIREBASE_SERVICE,
            "firebaseauth": StandardResourceType.FIREBASE_AUTH,
            "firebase_auth": StandardResourceType.FIREBASE_AUTH,
            "firebasehosting": StandardResourceType.FIREBASE_HOSTING,
            "firebase_hosting": StandardResourceType.FIREBASE_HOSTING,
            
            # AWS Resource Types
            "awss3": StandardResourceType.S3,
            "awscloudfront": StandardResourceType.CLOUDFRONT,
            "awsroute53": StandardResourceType.ROUTE53,
            "awsec2": StandardResourceType.VIRTUAL_MACHINE,
            "awsdomainregistration": StandardResourceType.DOMAIN_REGISTRATION,
            "awscertificatemanager": StandardResourceType.CERTIFICATE_MANAGER,
            "awsvpc": StandardResourceType.VPC,
            "awssecuritygroup": StandardResourceType.SECURITY_GROUP,
            "awsnatgateway": StandardResourceType.NAT_GATEWAY,
            "awsvpcpeering": StandardResourceType.VPC_PEERING,
            "awsloadbalancer": StandardResourceType.LOAD_BALANCER,
            "awslambda": StandardResourceType.CONTAINER_SERVICE,
            "awseks": StandardResourceType.KUBERNETES_CLUSTER,
            "awsecs": StandardResourceType.CONTAINER_SERVICE,
            
            # Azure Resource Types
            "azurevm": StandardResourceType.AZURE_VM,
            "azure_vm": StandardResourceType.AZURE_VM,
            "azurestorage": StandardResourceType.AZURE_STORAGE,
            "azure_storage": StandardResourceType.AZURE_STORAGE,
            "azuresql": StandardResourceType.AZURE_SQL,
            "azure_sql": StandardResourceType.AZURE_SQL,
            "azurevnet": StandardResourceType.AZURE_VNET,
            "azure_vnet": StandardResourceType.AZURE_VNET,
        }

        return type_mapping.get(resource_type_name)

    def _extract_resource_identity(
        self, resource: Any, raw_resource: Dict[str, Any], mapping
    ) -> None:
        """Extract resource identity information from cloud resource tags/labels"""
        tags_data = raw_resource.get(mapping.tags_field, [])

        # Handle different tag formats (DO uses list, GCP uses dict)
        if isinstance(tags_data, list):
            # DigitalOcean format: ["infradsl.id:uuid", "project:name"]
            for tag in tags_data:
                if isinstance(tag, str) and tag.startswith("infradsl.id:"):
                    existing_id = tag.split(":", 1)[1]
                    if hasattr(resource, "metadata"):
                        resource.metadata.id = existing_id
                    break
        elif isinstance(tags_data, dict):
            # GCP format: {"infradsl.id": "uuid", "project": "name"}
            infradsl_id = tags_data.get("infradsl.id") or tags_data.get("infradsl_id")
            if infradsl_id and hasattr(resource, "metadata"):
                resource.metadata.id = infradsl_id


def create_state_detector(provider: ProviderInterface) -> UniversalStateDetector:
    """Factory function to create a state detector for any provider"""
    return UniversalStateDetector(provider)
