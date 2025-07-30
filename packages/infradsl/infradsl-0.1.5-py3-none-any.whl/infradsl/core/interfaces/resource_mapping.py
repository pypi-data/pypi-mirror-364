"""
Universal resource mapping for cross-provider compatibility.

This module provides a standard way to map InfraDSL resource types to 
provider-specific resource types and operations.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass


class StandardResourceType(Enum):
    """Standard InfraDSL resource types that work across all providers"""

    # Core Compute Resources
    VIRTUAL_MACHINE = "virtual_machine"
    STATIC_IP = "static_ip"
    INSTANCE_GROUP = "instance_group"
    WEB_SERVER = "web_server"
    
    # Container & Orchestration Resources
    CLOUD_RUN = "cloud_run"
    KUBERNETES_CLUSTER = "kubernetes_cluster"
    CONTAINER_SERVICE = "container_service"
    
    # Database Resources
    DATABASE = "database"
    CLOUD_SQL = "cloud_sql"
    
    # Storage Resources
    STORAGE = "storage"
    STORAGE_BUCKET = "storage_bucket"
    CLOUD_STORAGE = "cloud_storage"
    S3 = "s3"
    
    # Network Resources
    NETWORK = "network"
    VPC = "vpc"
    VPC_PEERING = "vpc_peering"
    SHARED_VPC = "shared_vpc"
    NAT_GATEWAY = "nat_gateway"
    CLOUD_NAT = "cloud_nat"
    
    # Security Resources
    SECURITY_GROUP = "security_group"
    FIREWALL = "firewall"
    VPC_FIREWALL = "vpc_firewall"
    SECRET = "secret"
    SECRET_MANAGER = "secret_manager"
    CERTIFICATE = "certificate"
    CERTIFICATE_MANAGER = "certificate_manager"
    
    # DNS & CDN Resources
    DNS_RECORD = "dns_record"
    CLOUD_DNS = "cloud_dns"
    CDN = "cdn"
    CLOUDFRONT = "cloudfront"
    ROUTE53 = "route53"
    DOMAIN_REGISTRATION = "domain_registration"
    
    # Load Balancer Resources
    LOAD_BALANCER = "load_balancer"
    
    # Firebase Resources
    FIREBASE_SERVICE = "firebase_service"
    FIREBASE_AUTH = "firebase_auth"
    FIREBASE_HOSTING = "firebase_hosting"
    
    # Azure Resources
    AZURE_VM = "azure_vm"
    AZURE_STORAGE = "azure_storage"
    AZURE_SQL = "azure_sql"
    AZURE_VNET = "azure_vnet"


@dataclass
class ResourceTypeMapping:
    """Maps standard resource types to provider-specific types"""

    standard_type: StandardResourceType
    provider_type: str
    list_operation: str
    get_operation: Optional[str] = None

    # Field mappings for normalization
    id_field: str = "id"
    name_field: str = "name"
    status_field: str = "status"
    tags_field: str = "tags"

    # Status value mappings
    active_statuses: Optional[List[str]] = None
    pending_statuses: Optional[List[str]] = None

    def __post_init__(self):
        if self.active_statuses is None:
            self.active_statuses = ["active", "running", "available"]
        if self.pending_statuses is None:
            self.pending_statuses = ["pending", "creating", "starting"]


class ProviderResourceMappings:
    """Registry of resource mappings for each provider"""

    # DigitalOcean mappings
    DIGITALOCEAN = {
        StandardResourceType.VIRTUAL_MACHINE: ResourceTypeMapping(
            standard_type=StandardResourceType.VIRTUAL_MACHINE,
            provider_type="droplet",
            list_operation="droplet",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="tags",
            active_statuses=["active"],
            pending_statuses=["new", "starting", "pending"],
        ),
        StandardResourceType.DATABASE: ResourceTypeMapping(
            standard_type=StandardResourceType.DATABASE,
            provider_type="database",
            list_operation="database",
            active_statuses=["online"],
            pending_statuses=["creating", "migrating"],
        ),
        StandardResourceType.LOAD_BALANCER: ResourceTypeMapping(
            standard_type=StandardResourceType.LOAD_BALANCER,
            provider_type="load_balancer",
            list_operation="load_balancer",
            active_statuses=["active"],
            pending_statuses=["new", "creating"],
        ),
    }

    # GCP mappings
    GCP = {
        StandardResourceType.VIRTUAL_MACHINE: ResourceTypeMapping(
            standard_type=StandardResourceType.VIRTUAL_MACHINE,
            provider_type="instance",
            list_operation="instance",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",  # GCP uses "labels" instead of "tags"
            active_statuses=["RUNNING"],
            pending_statuses=["PENDING", "STAGING", "STARTING"],
        ),
        StandardResourceType.DATABASE: ResourceTypeMapping(
            standard_type=StandardResourceType.DATABASE,
            provider_type="sql_instance",
            list_operation="sql_instance",
            status_field="state",
            tags_field="settings.userLabels",
            active_statuses=["RUNNABLE"],
            pending_statuses=["PENDING_CREATE", "CREATING", "STARTING"],
        ),
        StandardResourceType.CLOUD_SQL: ResourceTypeMapping(
            standard_type=StandardResourceType.CLOUD_SQL,
            provider_type="sql_instance",
            list_operation="sql_instance",
            status_field="state",
            tags_field="settings.userLabels",
            active_statuses=["RUNNABLE"],
            pending_statuses=["PENDING_CREATE", "CREATING", "STARTING"],
        ),
        StandardResourceType.DNS_RECORD: ResourceTypeMapping(
            standard_type=StandardResourceType.DNS_RECORD,
            provider_type="dns_managed_zone",
            list_operation="dns_managed_zone",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.CLOUD_DNS: ResourceTypeMapping(
            standard_type=StandardResourceType.CLOUD_DNS,
            provider_type="dns_managed_zone",
            list_operation="dns_managed_zone",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.CLOUD_RUN: ResourceTypeMapping(
            standard_type=StandardResourceType.CLOUD_RUN,
            provider_type="cloud_run_service",
            list_operation="cloud_run_service",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["deployed"],
            pending_statuses=["creating", "updating"],
        ),
        StandardResourceType.STORAGE_BUCKET: ResourceTypeMapping(
            standard_type=StandardResourceType.STORAGE_BUCKET,
            provider_type="storage_bucket",
            list_operation="storage_bucket",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.CLOUD_STORAGE: ResourceTypeMapping(
            standard_type=StandardResourceType.CLOUD_STORAGE,
            provider_type="storage_bucket",
            list_operation="storage_bucket",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.STATIC_IP: ResourceTypeMapping(
            standard_type=StandardResourceType.STATIC_IP,
            provider_type="compute_address",
            list_operation="compute_address",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["RESERVED", "IN_USE"],
            pending_statuses=["RESERVING"],
        ),
        StandardResourceType.INSTANCE_GROUP: ResourceTypeMapping(
            standard_type=StandardResourceType.INSTANCE_GROUP,
            provider_type="instance_group_manager",
            list_operation="instance_group_manager",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["RUNNING"],
            pending_statuses=["CREATING", "UPDATING"],
        ),
        StandardResourceType.VPC: ResourceTypeMapping(
            standard_type=StandardResourceType.VPC,
            provider_type="compute_network",
            list_operation="compute_network",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.VPC_FIREWALL: ResourceTypeMapping(
            standard_type=StandardResourceType.VPC_FIREWALL,
            provider_type="compute_firewall",
            list_operation="compute_firewall",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.CLOUD_NAT: ResourceTypeMapping(
            standard_type=StandardResourceType.CLOUD_NAT,
            provider_type="compute_router_nat",
            list_operation="compute_router_nat",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["RUNNING"],
            pending_statuses=["CREATING"],
        ),
        StandardResourceType.VPC_PEERING: ResourceTypeMapping(
            standard_type=StandardResourceType.VPC_PEERING,
            provider_type="compute_network_peering",
            list_operation="compute_network_peering",
            id_field="name",
            name_field="name",
            status_field="state",
            tags_field="labels",
            active_statuses=["ACTIVE"],
            pending_statuses=["CREATING"],
        ),
        StandardResourceType.KUBERNETES_CLUSTER: ResourceTypeMapping(
            standard_type=StandardResourceType.KUBERNETES_CLUSTER,
            provider_type="container_cluster",
            list_operation="container_cluster",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="resourceLabels",
            active_statuses=["RUNNING"],
            pending_statuses=["PROVISIONING", "RECONCILING"],
        ),
        StandardResourceType.SECRET_MANAGER: ResourceTypeMapping(
            standard_type=StandardResourceType.SECRET_MANAGER,
            provider_type="secret_manager_secret",
            list_operation="secret_manager_secret",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.CERTIFICATE_MANAGER: ResourceTypeMapping(
            standard_type=StandardResourceType.CERTIFICATE_MANAGER,
            provider_type="compute_ssl_certificate",
            list_operation="compute_ssl_certificate",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.FIREBASE_AUTH: ResourceTypeMapping(
            standard_type=StandardResourceType.FIREBASE_AUTH,
            provider_type="firebase_auth",
            list_operation="firebase_auth",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.FIREBASE_HOSTING: ResourceTypeMapping(
            standard_type=StandardResourceType.FIREBASE_HOSTING,
            provider_type="firebase_hosting",
            list_operation="firebase_hosting",
            id_field="name",
            name_field="name",
            status_field="status",
            tags_field="labels",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
    }

    # AWS mappings
    AWS = {
        StandardResourceType.VIRTUAL_MACHINE: ResourceTypeMapping(
            standard_type=StandardResourceType.VIRTUAL_MACHINE,
            provider_type="instance",
            list_operation="ec2_instance",
            status_field="State.Name",
            tags_field="Tags",
            active_statuses=["running"],
            pending_statuses=["pending", "starting"],
        ),
        StandardResourceType.DATABASE: ResourceTypeMapping(
            standard_type=StandardResourceType.DATABASE,
            provider_type="rds_instance",
            list_operation="rds_instance",
            id_field="DBInstanceIdentifier",
            name_field="DBInstanceIdentifier",
            status_field="DBInstanceStatus",
            tags_field="Tags",
            active_statuses=["available"],
            pending_statuses=["creating", "backing-up", "modifying"],
        ),
        StandardResourceType.CLOUDFRONT: ResourceTypeMapping(
            standard_type=StandardResourceType.CLOUDFRONT,
            provider_type="cloudfront",
            list_operation="cloudfront_distribution",
            id_field="Id",
            name_field="Comment",  # CloudFront uses Comment as identifier
            status_field="Status",
            tags_field="Tags",
            active_statuses=["Deployed"],
            pending_statuses=["InProgress"],
        ),
        StandardResourceType.S3: ResourceTypeMapping(
            standard_type=StandardResourceType.S3,
            provider_type="s3",
            list_operation="s3_bucket",
            id_field="Name",
            name_field="Name",
            status_field="Status",
            tags_field="Tags",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.STORAGE_BUCKET: ResourceTypeMapping(
            standard_type=StandardResourceType.STORAGE_BUCKET,
            provider_type="s3",
            list_operation="s3_bucket",
            id_field="Name",
            name_field="Name",
            status_field="Status",
            tags_field="Tags",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.ROUTE53: ResourceTypeMapping(
            standard_type=StandardResourceType.ROUTE53,
            provider_type="route53",
            list_operation="route53_zone",
            id_field="Id",
            name_field="Name",
            status_field="Status",
            tags_field="Tags",
            active_statuses=["active"],
            pending_statuses=["pending"],
        ),
        StandardResourceType.DOMAIN_REGISTRATION: ResourceTypeMapping(
            standard_type=StandardResourceType.DOMAIN_REGISTRATION,
            provider_type="domain_registration",
            list_operation="domain_registration",
            id_field="DomainName",
            name_field="DomainName",
            status_field="Status",
            tags_field="Tags",
            active_statuses=["SUCCESSFUL"],
            pending_statuses=["PENDING", "IN_PROGRESS"],
        ),
        StandardResourceType.CERTIFICATE_MANAGER: ResourceTypeMapping(
            standard_type=StandardResourceType.CERTIFICATE_MANAGER,
            provider_type="certificate_manager",
            list_operation="certificate_manager",
            id_field="CertificateArn",
            name_field="DomainName",
            status_field="Status",
            tags_field="Tags",
            active_statuses=["ISSUED"],
            pending_statuses=["PENDING_VALIDATION", "VALIDATION_TIMED_OUT"],
        ),
        StandardResourceType.VPC: ResourceTypeMapping(
            standard_type=StandardResourceType.VPC,
            provider_type="vpc",
            list_operation="vpc",
            id_field="VpcId",
            name_field="VpcId",
            status_field="State",
            tags_field="Tags",
            active_statuses=["available"],
            pending_statuses=["pending"],
        ),
        StandardResourceType.SECURITY_GROUP: ResourceTypeMapping(
            standard_type=StandardResourceType.SECURITY_GROUP,
            provider_type="security_group",
            list_operation="security_group",
            id_field="GroupId",
            name_field="GroupName",
            status_field="State",
            tags_field="Tags",
            active_statuses=["active"],
            pending_statuses=["creating"],
        ),
        StandardResourceType.NAT_GATEWAY: ResourceTypeMapping(
            standard_type=StandardResourceType.NAT_GATEWAY,
            provider_type="nat_gateway",
            list_operation="nat_gateway",
            id_field="NatGatewayId",
            name_field="NatGatewayId",
            status_field="State",
            tags_field="Tags",
            active_statuses=["available"],
            pending_statuses=["pending", "creating"],
        ),
        StandardResourceType.VPC_PEERING: ResourceTypeMapping(
            standard_type=StandardResourceType.VPC_PEERING,
            provider_type="vpc_peering_connection",
            list_operation="vpc_peering_connection",
            id_field="VpcPeeringConnectionId",
            name_field="VpcPeeringConnectionId",
            status_field="Status.Code",
            tags_field="Tags",
            active_statuses=["active"],
            pending_statuses=["pending-acceptance", "provisioning"],
        ),
        StandardResourceType.LOAD_BALANCER: ResourceTypeMapping(
            standard_type=StandardResourceType.LOAD_BALANCER,
            provider_type="load_balancer",
            list_operation="load_balancer",
            id_field="LoadBalancerArn",
            name_field="LoadBalancerName",
            status_field="State.Code",
            tags_field="Tags",
            active_statuses=["active"],
            pending_statuses=["provisioning"],
        ),
    }

    # Azure mappings
    AZURE = {
        StandardResourceType.AZURE_VM: ResourceTypeMapping(
            standard_type=StandardResourceType.AZURE_VM,
            provider_type="virtual_machine",
            list_operation="virtual_machine",
            id_field="id",
            name_field="name",
            status_field="provisioningState",
            tags_field="tags",
            active_statuses=["Succeeded"],
            pending_statuses=["Creating", "Updating"],
        ),
        StandardResourceType.AZURE_STORAGE: ResourceTypeMapping(
            standard_type=StandardResourceType.AZURE_STORAGE,
            provider_type="storage_account",
            list_operation="storage_account",
            id_field="id",
            name_field="name",
            status_field="provisioningState",
            tags_field="tags",
            active_statuses=["Succeeded"],
            pending_statuses=["Creating"],
        ),
        StandardResourceType.AZURE_SQL: ResourceTypeMapping(
            standard_type=StandardResourceType.AZURE_SQL,
            provider_type="sql_database",
            list_operation="sql_database",
            id_field="id",
            name_field="name",
            status_field="status",
            tags_field="tags",
            active_statuses=["Online"],
            pending_statuses=["Creating", "Copying"],
        ),
        StandardResourceType.AZURE_VNET: ResourceTypeMapping(
            standard_type=StandardResourceType.AZURE_VNET,
            provider_type="virtual_network",
            list_operation="virtual_network",
            id_field="id",
            name_field="name",
            status_field="provisioningState",
            tags_field="tags",
            active_statuses=["Succeeded"],
            pending_statuses=["Creating", "Updating"],
        ),
    }


def get_provider_mapping(
    provider_type: str,
) -> Dict[StandardResourceType, ResourceTypeMapping]:
    """Get resource mappings for a specific provider"""
    mappings = {
        "digitalocean": ProviderResourceMappings.DIGITALOCEAN,
        "gcp": ProviderResourceMappings.GCP,
        "aws": ProviderResourceMappings.AWS,
        "azure": ProviderResourceMappings.AZURE,
    }

    return mappings.get(provider_type.lower(), {})


def get_resource_mapping(
    provider_type: str, standard_type: StandardResourceType
) -> Optional[ResourceTypeMapping]:
    """Get specific resource mapping for provider and resource type"""
    provider_mappings = get_provider_mapping(provider_type)
    return provider_mappings.get(standard_type)


def normalize_resource_data(
    provider_type: str, standard_type: StandardResourceType, raw_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Normalize provider-specific resource data to standard format"""
    mapping = get_resource_mapping(provider_type, standard_type)
    if not mapping:
        return raw_data

    # Extract standard fields using provider-specific field names
    # For tags, check if raw_data already has a 'tags' field (from provider processing)
    # Otherwise fall back to the mapped field
    tags_value = raw_data.get("tags")
    if tags_value is None:
        tags_value = _get_nested_value(raw_data, mapping.tags_field, [])
    
    normalized = {
        "id": _get_nested_value(raw_data, mapping.id_field),
        "name": _get_nested_value(raw_data, mapping.name_field),
        "status": _get_nested_value(raw_data, mapping.status_field),
        "tags": tags_value,
        "provider_type": mapping.provider_type,
        "standard_type": standard_type.value,
    }

    # Add provider-specific fields that are commonly used in fingerprinting
    if provider_type.lower() == "digitalocean":
        normalized.update(
            {
                "region": raw_data.get("region"),
                "size": raw_data.get("size"),
                "image": raw_data.get("image"),
                "backups": raw_data.get("backups", False),
                "ipv6": raw_data.get("ipv6", True),
                "monitoring": raw_data.get("monitoring", True),
                "user_data": raw_data.get("user_data"),
                "ip_address": raw_data.get("ip_address"),
                "private_ip_address": raw_data.get("private_ip_address"),
                "created_at": raw_data.get("created_at"),
                "additional_disks": raw_data.get("additional_disks", []),
            }
        )
    elif provider_type.lower() == "gcp":
        normalized.update(
            {
                "region": raw_data.get("region"),
                "zone": raw_data.get("zone"),
                "size": raw_data.get("size"),
                "machine_type": raw_data.get("machine_type"),
                "image": raw_data.get("image"),
                "backups": raw_data.get("backups", False),
                "ipv6": raw_data.get("ipv6", False),
                "monitoring": raw_data.get("monitoring", True),
                "ip_address": raw_data.get("ip_address"),
                "private_ip_address": raw_data.get("private_ip_address"),
                "created_at": raw_data.get("created_at"),
                "labels": raw_data.get("labels", {}),
            }
        )

    # Normalize status to standard values
    status = normalized.get("status", "").lower()
    if mapping.active_statuses and any(
        active_status.lower() in status for active_status in mapping.active_statuses
    ):
        normalized["standard_status"] = "active"
    elif mapping.pending_statuses and any(
        pending_status.lower() in status for pending_status in mapping.pending_statuses
    ):
        normalized["standard_status"] = "pending"
    else:
        normalized["standard_status"] = "unknown"

    return normalized


def _get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested dictionary value using dot notation (e.g., 'settings.userLabels')"""
    keys = path.split(".")
    current = data

    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current
