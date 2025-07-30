from typing import Optional, Dict, Any, Self, List, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class ReleaseChannel(Enum):
    """GKE release channels"""
    RAPID = "RAPID"
    REGULAR = "REGULAR"
    STABLE = "STABLE"
    UNSPECIFIED = "UNSPECIFIED"


class NodePoolMode(Enum):
    """Node pool operating modes"""
    SYSTEM = "SYSTEM"
    USER = "USER"


class DiskType(Enum):
    """Disk types for nodes"""
    PD_STANDARD = "pd-standard"
    PD_SSD = "pd-ssd"
    PD_BALANCED = "pd-balanced"


class ImageType(Enum):
    """Node image types"""
    COS_CONTAINERD = "COS_CONTAINERD"      # Container-Optimized OS with containerd
    COS = "COS"                            # Container-Optimized OS  
    UBUNTU_CONTAINERD = "UBUNTU_CONTAINERD" # Ubuntu with containerd
    UBUNTU = "UBUNTU"                      # Ubuntu
    WINDOWS_SAC = "WINDOWS_SAC"            # Windows Server SAC
    WINDOWS_LTSC = "WINDOWS_LTSC"          # Windows Server LTSC


@dataclass
class NodePoolSpec:
    """Node pool specification"""
    name: str
    node_count: int = 3
    min_node_count: int = 1
    max_node_count: int = 10
    machine_type: str = "e2-medium"
    disk_size_gb: int = 100
    disk_type: DiskType = DiskType.PD_STANDARD
    image_type: ImageType = ImageType.COS_CONTAINERD
    preemptible: bool = False
    spot: bool = False
    mode: NodePoolMode = NodePoolMode.USER
    
    # Security
    service_account: Optional[str] = None
    oauth_scopes: List[str] = field(default_factory=lambda: [
        "https://www.googleapis.com/auth/cloud-platform"
    ])
    
    # Taints and labels
    node_labels: Dict[str, str] = field(default_factory=dict)
    node_taints: List[Dict[str, str]] = field(default_factory=list)
    
    # Zones
    zones: List[str] = field(default_factory=list)


@dataclass
class WorkloadIdentitySpec:
    """Workload Identity configuration"""
    enabled: bool = False
    workload_pool: Optional[str] = None


@dataclass
class NetworkPolicySpec:
    """Network policy configuration"""
    enabled: bool = False
    provider: str = "CALICO"  # CALICO or PROVIDER_UNSPECIFIED


@dataclass
class AddonsSpec:
    """Cluster add-ons configuration"""
    http_load_balancing: bool = True
    horizontal_pod_autoscaling: bool = True
    network_policy_config: bool = False
    istio_config: bool = False
    cloud_run_config: bool = False
    dns_cache_config: bool = False
    config_connector_config: bool = False
    gce_persistent_disk_csi_driver_config: bool = True


@dataclass
class GKESpec(ResourceSpec):
    """Specification for a GKE cluster resource"""
    
    # Core configuration
    location: str = "us-central1"
    zones: List[str] = field(default_factory=list)
    regional: bool = True  # Regional vs zonal cluster
    
    # Kubernetes version
    kubernetes_version: Optional[str] = None
    release_channel: ReleaseChannel = ReleaseChannel.REGULAR
    
    # Node pools
    node_pools: List[NodePoolSpec] = field(default_factory=list)
    remove_default_node_pool: bool = True
    
    # Network configuration
    network: str = "default"
    subnetwork: Optional[str] = None
    enable_private_nodes: bool = False
    enable_private_endpoint: bool = False
    master_ipv4_cidr_block: Optional[str] = None
    
    # IP allocation (for VPC-native clusters)
    ip_allocation_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Security
    enable_legacy_abac: bool = False
    enable_network_policy: bool = True
    network_policy: NetworkPolicySpec = field(default_factory=NetworkPolicySpec)
    
    # Master authorized networks
    master_authorized_networks: List[Dict[str, str]] = field(default_factory=list)
    
    # Workload Identity
    workload_identity: WorkloadIdentitySpec = field(default_factory=WorkloadIdentitySpec)
    
    # Add-ons
    addons: AddonsSpec = field(default_factory=AddonsSpec)
    
    # Maintenance policy
    maintenance_window: Optional[Dict[str, Any]] = None
    
    # Logging and monitoring
    logging_service: str = "logging.googleapis.com/kubernetes"
    monitoring_service: str = "monitoring.googleapis.com/kubernetes"
    enable_cloud_logging: bool = True
    enable_cloud_monitoring: bool = True
    
    # Labels
    resource_labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class GKECluster(BaseResource):
    """
    GCP GKE (Google Kubernetes Engine) cluster with Rails-like conventions.
    
    Examples:
        # Simple development cluster
        dev_cluster = (GKECluster("dev-cluster")
                      .region("us-central1")
                      .development())
        
        # Production cluster with multiple node pools
        prod_cluster = (GKECluster("prod-cluster")
                       .region("us-central1")
                       .production()
                       .add_node_pool("system", machine_type="e2-standard-4", min_nodes=2, max_nodes=5)
                       .add_node_pool("workload", machine_type="n1-standard-2", min_nodes=1, max_nodes=20)
                       .workload_identity()
                       .private_cluster())
        
        # Auto-scaling cluster
        auto_cluster = (GKECluster("auto-cluster")
                       .region("us-west1")
                       .add_node_pool("auto", machine_type="e2-medium", min_nodes=0, max_nodes=50)
                       .enable_autoscaling()
                       .spot_instances())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: GKESpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "GKECluster"
        
        # Set smart defaults based on name patterns
        if any(keyword in name.lower() for keyword in ["prod", "production"]):
            self.spec.regional = True
            self.spec.enable_network_policy = True
            self.spec.workload_identity.enabled = True
            self.spec.release_channel = ReleaseChannel.STABLE
        elif "dev" in name.lower() or "test" in name.lower():
            self.spec.regional = False  # Cheaper zonal cluster
            self.spec.zones = ["us-central1-a"]  # Single zone for dev
            
        # Add default system node pool if none specified
        if not self.spec.node_pools:
            system_pool = NodePoolSpec(
                name="system-pool",
                node_count=3,
                machine_type="e2-medium",
                mode=NodePoolMode.SYSTEM
            )
            self.spec.node_pools.append(system_pool)
            
    def _create_spec(self) -> GKESpec:
        return GKESpec()
        
    def _validate_spec(self) -> None:
        """Validate cluster specification"""
        if not self.spec.node_pools:
            raise ValueError("At least one node pool is required")
            
        if self.spec.enable_private_nodes and not self.spec.master_ipv4_cidr_block:
            self.spec.master_ipv4_cidr_block = "172.16.0.0/28"  # Default private master range
            
        if not self.spec.regional and not self.spec.zones:
            raise ValueError("Zonal cluster requires explicit zone configuration")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "location": self.spec.location,
            "initial_node_count": 1 if self.spec.remove_default_node_pool else self.spec.node_pools[0].node_count,
            "remove_default_node_pool": self.spec.remove_default_node_pool,
            "resource_labels": {**self.spec.resource_labels, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP GKE configuration"""
        config = {
            "resource_type": "container_cluster"
        }
        
        # Location configuration
        if self.spec.regional:
            config["location"] = self.spec.location
        else:
            # Zonal cluster - use first zone
            zone = self.spec.zones[0] if self.spec.zones else f"{self.spec.location}-a"
            config["location"] = zone
            
        # Kubernetes version and release channel
        if self.spec.kubernetes_version:
            config["min_master_version"] = self.spec.kubernetes_version
            
        if self.spec.release_channel != ReleaseChannel.UNSPECIFIED:
            config["release_channel"] = {
                "channel": self.spec.release_channel.value
            }
            
        # Network configuration
        config["network"] = self.spec.network
        if self.spec.subnetwork:
            config["subnetwork"] = self.spec.subnetwork
            
        # IP allocation for VPC-native clusters
        if self.spec.ip_allocation_policy:
            config["ip_allocation_policy"] = self.spec.ip_allocation_policy
        else:
            # Default VPC-native configuration
            config["ip_allocation_policy"] = {
                "cluster_ipv4_cidr_block": "",  # Let GKE choose
                "services_ipv4_cidr_block": ""  # Let GKE choose
            }
            
        # Private cluster configuration
        if self.spec.enable_private_nodes:
            config["private_cluster_config"] = {
                "enable_private_nodes": True,
                "enable_private_endpoint": self.spec.enable_private_endpoint,
                "master_ipv4_cidr_block": self.spec.master_ipv4_cidr_block
            }
            
        # Master authorized networks
        if self.spec.master_authorized_networks:
            config["master_authorized_networks_config"] = {
                "cidr_blocks": self.spec.master_authorized_networks
            }
            
        # Network policy
        if self.spec.enable_network_policy:
            config["network_policy"] = {
                "enabled": True,
                "provider": self.spec.network_policy.provider
            }
            
        # Workload Identity
        if self.spec.workload_identity.enabled:
            config["workload_identity_config"] = {
                "workload_pool": self.spec.workload_identity.workload_pool or f"PROJECT_ID.svc.id.goog"
            }
            
        # Add-ons configuration
        addons_config = {}
        if not self.spec.addons.http_load_balancing:
            addons_config["http_load_balancing"] = {"disabled": True}
        if not self.spec.addons.horizontal_pod_autoscaling:
            addons_config["horizontal_pod_autoscaling"] = {"disabled": True}
        if self.spec.addons.network_policy_config:
            addons_config["network_policy_config"] = {"disabled": False}
        if self.spec.addons.istio_config:
            addons_config["istio_config"] = {"disabled": False}
        if self.spec.addons.cloud_run_config:
            addons_config["cloud_run_config"] = {"disabled": False}
        if self.spec.addons.dns_cache_config:
            addons_config["dns_cache_config"] = {"enabled": True}
        if self.spec.addons.config_connector_config:
            addons_config["config_connector_config"] = {"enabled": True}
        if self.spec.addons.gce_persistent_disk_csi_driver_config:
            addons_config["gce_persistent_disk_csi_driver_config"] = {"enabled": True}
            
        if addons_config:
            config["addons_config"] = addons_config
            
        # Logging and monitoring
        config["logging_service"] = self.spec.logging_service
        config["monitoring_service"] = self.spec.monitoring_service
        
        # Maintenance policy
        if self.spec.maintenance_window:
            config["maintenance_policy"] = self.spec.maintenance_window
            
        # Node pools
        if self.spec.node_pools:
            config["node_pool"] = []
            for pool in self.spec.node_pools:
                pool_config = self._build_node_pool_config(pool)
                config["node_pool"].append(pool_config)

        return config
        
    def _build_node_pool_config(self, pool: NodePoolSpec) -> Dict[str, Any]:
        """Build node pool configuration"""
        pool_config = {
            "name": pool.name,
            "initial_node_count": pool.node_count,
            "node_config": {
                "machine_type": pool.machine_type,
                "disk_size_gb": pool.disk_size_gb,
                "disk_type": pool.disk_type.value,
                "image_type": pool.image_type.value,
                "preemptible": pool.preemptible,
                "spot": pool.spot,
                "oauth_scopes": pool.oauth_scopes,
                "labels": pool.node_labels,
                "tags": [f"{self.name}-node"]
            }
        }
        
        # Service account
        if pool.service_account:
            pool_config["node_config"]["service_account"] = pool.service_account
        
        # Node taints
        if pool.node_taints:
            pool_config["node_config"]["taint"] = pool.node_taints
            
        # Autoscaling
        if pool.min_node_count != pool.max_node_count:
            pool_config["autoscaling"] = {
                "min_node_count": pool.min_node_count,
                "max_node_count": pool.max_node_count
            }
            
        # Node pool management
        pool_config["management"] = {
            "auto_repair": True,
            "auto_upgrade": True
        }
        
        # Node locations (zones)
        if pool.zones:
            pool_config["node_locations"] = pool.zones
            
        return pool_config
        
    # Fluent interface methods
    
    # Location methods
    
    def region(self, region_name: str) -> Self:
        """Set cluster region (chainable)"""
        self.spec.location = region_name
        self.spec.regional = True
        return self
        
    def zone(self, zone_name: str) -> Self:
        """Set single zone for zonal cluster (chainable)"""
        self.spec.location = zone_name
        self.spec.zones = [zone_name]
        self.spec.regional = False
        return self
        
    def zones(self, zone_list: List[str]) -> Self:
        """Set multiple zones (chainable)"""
        self.spec.zones = zone_list
        return self
        
    def regional_cluster(self) -> Self:
        """Configure as regional cluster (chainable)"""
        self.spec.regional = True
        return self
        
    def zonal_cluster(self, zone: str) -> Self:
        """Configure as zonal cluster (chainable)"""
        self.spec.regional = False
        self.spec.zones = [zone]
        return self
        
    # Kubernetes version
    
    def kubernetes_version(self, version: str) -> Self:
        """Set Kubernetes version (chainable)"""
        self.spec.kubernetes_version = version
        return self
        
    def release_channel(self, channel: str) -> Self:
        """Set release channel (chainable)"""
        self.spec.release_channel = ReleaseChannel(channel.upper())
        return self
        
    def stable_channel(self) -> Self:
        """Use stable release channel (chainable)"""
        self.spec.release_channel = ReleaseChannel.STABLE
        return self
        
    def regular_channel(self) -> Self:
        """Use regular release channel (chainable)"""
        self.spec.release_channel = ReleaseChannel.REGULAR
        return self
        
    def rapid_channel(self) -> Self:
        """Use rapid release channel (chainable)"""
        self.spec.release_channel = ReleaseChannel.RAPID
        return self
        
    # Node pool management
    
    def add_node_pool(self, name: str, machine_type: str = "e2-medium", 
                     node_count: int = 3, min_nodes: int = 1, max_nodes: int = 10,
                     preemptible: bool = False, spot: bool = False) -> Self:
        """Add node pool (chainable)"""
        pool = NodePoolSpec(
            name=name,
            machine_type=machine_type,
            node_count=node_count,
            min_node_count=min_nodes,
            max_node_count=max_nodes,
            preemptible=preemptible,
            spot=spot
        )
        self.spec.node_pools.append(pool)
        return self
        
    def system_node_pool(self, machine_type: str = "e2-standard-4", node_count: int = 3) -> Self:
        """Add system node pool for cluster services (chainable)"""
        pool = NodePoolSpec(
            name="system-pool",
            machine_type=machine_type,
            node_count=node_count,
            mode=NodePoolMode.SYSTEM,
            node_labels={"pool-type": "system"}
        )
        # Replace default system pool if exists
        self.spec.node_pools = [p for p in self.spec.node_pools if p.mode != NodePoolMode.SYSTEM]
        self.spec.node_pools.append(pool)
        return self
        
    def workload_node_pool(self, name: str = "workload-pool", machine_type: str = "n1-standard-2",
                          min_nodes: int = 1, max_nodes: int = 10) -> Self:
        """Add workload node pool for applications (chainable)"""
        pool = NodePoolSpec(
            name=name,
            machine_type=machine_type,
            node_count=min_nodes,
            min_node_count=min_nodes,
            max_node_count=max_nodes,
            mode=NodePoolMode.USER,
            node_labels={"pool-type": "workload"}
        )
        self.spec.node_pools.append(pool)
        return self
        
    def spot_instances(self, enabled: bool = True) -> Self:
        """Enable spot instances for cost savings (chainable)"""
        for pool in self.spec.node_pools:
            pool.spot = enabled
        return self
        
    def preemptible_instances(self, enabled: bool = True) -> Self:
        """Enable preemptible instances for cost savings (chainable)"""
        for pool in self.spec.node_pools:
            pool.preemptible = enabled
        return self
        
    # Network configuration
    
    def network(self, network_name: str, subnet: str = None) -> Self:
        """Set network configuration (chainable)"""
        self.spec.network = network_name
        if subnet:
            self.spec.subnetwork = subnet
        return self
        
    def private_cluster(self, enable_private_endpoint: bool = False) -> Self:
        """Configure as private cluster (chainable)"""
        self.spec.enable_private_nodes = True
        self.spec.enable_private_endpoint = enable_private_endpoint
        return self
        
    def public_cluster(self) -> Self:
        """Configure as public cluster (chainable)"""
        self.spec.enable_private_nodes = False
        self.spec.enable_private_endpoint = False
        return self
        
    def master_cidr(self, cidr_block: str) -> Self:
        """Set master CIDR block for private cluster (chainable)"""
        self.spec.master_ipv4_cidr_block = cidr_block
        return self
        
    def authorized_network(self, cidr: str, name: str = "default") -> Self:
        """Add authorized network for master access (chainable)"""
        auth_net = {"cidr_block": cidr, "display_name": name}
        if auth_net not in self.spec.master_authorized_networks:
            self.spec.master_authorized_networks.append(auth_net)
        return self
        
    # Security features
    
    def workload_identity(self, workload_pool: str = None) -> Self:
        """Enable Workload Identity (chainable)"""
        self.spec.workload_identity.enabled = True
        if workload_pool:
            self.spec.workload_identity.workload_pool = workload_pool
        return self
        
    def network_policy(self, enabled: bool = True, provider: str = "CALICO") -> Self:
        """Configure network policy (chainable)"""
        self.spec.enable_network_policy = enabled
        self.spec.network_policy.enabled = enabled
        self.spec.network_policy.provider = provider
        return self
        
    # Add-ons and features
    
    def disable_legacy_abac(self) -> Self:
        """Disable legacy ABAC (chainable)"""
        self.spec.enable_legacy_abac = False
        return self
        
    def enable_autoscaling(self) -> Self:
        """Enable cluster autoscaling (chainable)"""
        self.spec.addons.horizontal_pod_autoscaling = True
        return self
        
    def enable_istio(self) -> Self:
        """Enable Istio service mesh (chainable)"""
        self.spec.addons.istio_config = True
        return self
        
    def enable_cloud_run(self) -> Self:
        """Enable Cloud Run on GKE (chainable)"""
        self.spec.addons.cloud_run_config = True
        return self
        
    def enable_dns_cache(self) -> Self:
        """Enable NodeLocal DNS cache (chainable)"""
        self.spec.addons.dns_cache_config = True
        return self
        
    def enable_config_connector(self) -> Self:
        """Enable Config Connector (chainable)"""
        self.spec.addons.config_connector_config = True
        return self
        
    # Maintenance
    
    def maintenance_window(self, start_time: str, duration: str = "4h") -> Self:
        """Set maintenance window (chainable)"""
        self.spec.maintenance_window = {
            "daily_maintenance_window": {
                "start_time": start_time,
                "duration": duration
            }
        }
        return self
        
    # Labels
    
    def label(self, key: str, value: str) -> Self:
        """Add a label (chainable)"""
        self.spec.resource_labels[key] = value
        return self
        
    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set multiple labels (chainable)"""
        if labels_dict:
            self.spec.resource_labels.update(labels_dict)
        if labels:
            self.spec.resource_labels.update(labels)
        return self
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .regional_cluster()
                .stable_channel()
                .workload_identity()
                .network_policy()
                .system_node_pool("e2-standard-4", 3)
                .workload_node_pool("prod-workload", "n1-standard-2", min_nodes=3, max_nodes=20)
                .maintenance_window("03:00")
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .regional_cluster()
                .regular_channel()
                .workload_identity()
                .system_node_pool("e2-standard-2", 2)
                .workload_node_pool("staging-workload", "e2-medium", min_nodes=1, max_nodes=10)
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .regular_channel()
                .system_node_pool("e2-medium", 1)
                .workload_node_pool("dev-workload", "e2-small", min_nodes=0, max_nodes=5)
                .preemptible_instances()
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the cluster via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the cluster via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the cluster via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )
        
    # Convenience methods
    
    def get_endpoint(self) -> Optional[str]:
        """Get cluster endpoint"""
        return self.status.provider_data.get("endpoint")
        
    def get_master_version(self) -> Optional[str]:
        """Get master Kubernetes version"""
        return self.status.provider_data.get("master_version")
        
    def get_kubeconfig(self) -> Optional[str]:
        """Get kubeconfig for cluster access"""
        # This would typically be generated by the provider
        return self.status.provider_data.get("kubeconfig")