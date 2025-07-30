from typing import Optional, Dict, Any, Self, List, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class DatabaseEngine(Enum):
    """GCP Cloud SQL database engines"""
    MYSQL = "MYSQL"
    POSTGRESQL = "POSTGRES"
    SQL_SERVER = "SQLSERVER"


class DatabaseTier(Enum):
    """GCP Cloud SQL database tiers"""
    # Shared-core instances
    DB_F1_MICRO = "db-f1-micro"        # 0.6 GB RAM
    DB_G1_SMALL = "db-g1-small"        # 1.7 GB RAM
    
    # Standard instances
    DB_N1_STANDARD_1 = "db-n1-standard-1"   # 1 vCPU, 3.75 GB RAM
    DB_N1_STANDARD_2 = "db-n1-standard-2"   # 2 vCPU, 7.5 GB RAM
    DB_N1_STANDARD_4 = "db-n1-standard-4"   # 4 vCPU, 15 GB RAM
    DB_N1_STANDARD_8 = "db-n1-standard-8"   # 8 vCPU, 30 GB RAM
    DB_N1_STANDARD_16 = "db-n1-standard-16" # 16 vCPU, 60 GB RAM
    DB_N1_STANDARD_32 = "db-n1-standard-32" # 32 vCPU, 120 GB RAM
    DB_N1_STANDARD_64 = "db-n1-standard-64" # 64 vCPU, 240 GB RAM
    
    # High-memory instances
    DB_N1_HIGHMEM_2 = "db-n1-highmem-2"     # 2 vCPU, 13 GB RAM
    DB_N1_HIGHMEM_4 = "db-n1-highmem-4"     # 4 vCPU, 26 GB RAM
    DB_N1_HIGHMEM_8 = "db-n1-highmem-8"     # 8 vCPU, 52 GB RAM
    DB_N1_HIGHMEM_16 = "db-n1-highmem-16"   # 16 vCPU, 104 GB RAM
    DB_N1_HIGHMEM_32 = "db-n1-highmem-32"   # 32 vCPU, 208 GB RAM
    DB_N1_HIGHMEM_64 = "db-n1-highmem-64"   # 64 vCPU, 416 GB RAM


class AvailabilityType(Enum):
    """Database availability types"""
    ZONAL = "ZONAL"          # Single zone
    REGIONAL = "REGIONAL"    # High availability across zones


class StorageType(Enum):
    """Storage types"""
    SSD = "PD_SSD"
    HDD = "PD_HDD"


@dataclass
class BackupConfiguration:
    """Backup configuration"""
    enabled: bool = True
    start_time: str = "02:00"           # HH:MM format
    point_in_time_recovery: bool = True
    transaction_log_retention_days: int = 7
    retention_days: int = 30


@dataclass
class ReplicaConfiguration:
    """Read replica configuration"""
    tier: Optional[DatabaseTier] = None
    availability_type: AvailabilityType = AvailabilityType.ZONAL
    region: Optional[str] = None
    zone: Optional[str] = None
    disk_size: Optional[int] = None
    disk_type: StorageType = StorageType.SSD


@dataclass
class CloudSQLSpec(ResourceSpec):
    """Specification for a GCP Cloud SQL instance"""
    
    # Core configuration
    database_engine: DatabaseEngine = DatabaseEngine.POSTGRESQL
    database_version: str = "POSTGRES_14"
    tier: DatabaseTier = DatabaseTier.DB_N1_STANDARD_1
    
    # Location
    region: str = "us-central1"
    zone: Optional[str] = None
    availability_type: AvailabilityType = AvailabilityType.ZONAL
    
    # Storage
    disk_type: StorageType = StorageType.SSD
    disk_size: int = 20  # GB
    disk_autoresize: bool = True
    disk_autoresize_limit: int = 0  # 0 means no limit
    
    # Database settings
    database_name: str = "defaultdb"
    root_password: Optional[str] = None
    
    # Network
    private_network: Optional[str] = None
    authorized_networks: List[Dict[str, str]] = field(default_factory=list)
    require_ssl: bool = False
    
    # Backup
    backup_config: BackupConfiguration = field(default_factory=BackupConfiguration)
    
    # High availability
    replica_configuration: Optional[ReplicaConfiguration] = None
    
    # Maintenance
    maintenance_window_day: int = 7  # Sunday = 1, Saturday = 7
    maintenance_window_hour: int = 4
    maintenance_window_update_track: str = "stable"  # stable, canary
    
    # Flags (database engine specific settings)
    database_flags: Dict[str, Any] = field(default_factory=dict)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Deletion protection
    deletion_protection: bool = False
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class CloudSQL(BaseResource):
    """
    GCP Cloud SQL managed database with Rails-like conventions.
    
    Examples:
        # Simple PostgreSQL database
        db = (CloudSQL("my-app-db")
              .postgresql("14")
              .tier("db-n1-standard-2")
              .region("us-central1"))
        
        # Production database with high availability
        prod_db = (CloudSQL("prod-db")
                  .postgresql("14") 
                  .tier("db-n1-standard-4")
                  .region("us-central1")
                  .high_availability()
                  .backup_enabled()
                  .deletion_protection())
                  
        # Database with read replica
        main_db = (CloudSQL("main-db")
                  .mysql("8.0")
                  .tier("db-n1-standard-2")
                  .region("us-central1"))
        
        read_replica = main_db.read_replica("read-db", region="us-west1")
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: CloudSQLSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "CloudSQL"
        
        # Set smart defaults based on name patterns
        if any(keyword in name.lower() for keyword in ["prod", "production"]):
            self.spec.availability_type = AvailabilityType.REGIONAL
            self.spec.deletion_protection = True
            self.spec.tier = DatabaseTier.DB_N1_STANDARD_2
        elif "test" in name.lower() or "dev" in name.lower():
            self.spec.tier = DatabaseTier.DB_F1_MICRO
            self.spec.disk_size = 10
            
    def _create_spec(self) -> CloudSQLSpec:
        return CloudSQLSpec()
        
    def _validate_spec(self) -> None:
        """Validate database specification"""
        if self.spec.disk_size < 10:
            raise ValueError("Disk size must be at least 10 GB")
            
        if not self.spec.database_name:
            raise ValueError("Database name is required")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "database_version": self.spec.database_version,
            "tier": self.spec.tier.value,
            "region": self.spec.region,
            "settings": self._build_settings(),
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
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

    def _build_settings(self) -> Dict[str, Any]:
        """Build settings configuration"""
        settings = {
            "availability_type": self.spec.availability_type.value,
            "disk_type": self.spec.disk_type.value,
            "disk_size": self.spec.disk_size,
            "disk_autoresize": self.spec.disk_autoresize,
            "user_labels": self.spec.labels,
        }
        
        # Disk autoresize limit
        if self.spec.disk_autoresize_limit > 0:
            settings["disk_autoresize_limit"] = self.spec.disk_autoresize_limit
        
        # Zone (for zonal instances)
        if self.spec.zone:
            settings["location_preference"] = {"zone": self.spec.zone}
            
        # Backup configuration
        if self.spec.backup_config.enabled:
            settings["backup_configuration"] = {
                "enabled": True,
                "start_time": self.spec.backup_config.start_time,
                "point_in_time_recovery_enabled": self.spec.backup_config.point_in_time_recovery,
                "backup_retention_settings": {
                    "retained_backups": self.spec.backup_config.retention_days
                }
            }
            
            # Transaction log retention (PostgreSQL/MySQL)
            if self.spec.database_engine in [DatabaseEngine.POSTGRESQL, DatabaseEngine.MYSQL]:
                settings["backup_configuration"]["transaction_log_retention_days"] = \
                    self.spec.backup_config.transaction_log_retention_days
        
        # IP configuration
        ip_config = {}
        if self.spec.private_network:
            ip_config["private_network"] = self.spec.private_network
            ip_config["ipv4_enabled"] = False  # Private IP only
        else:
            ip_config["ipv4_enabled"] = True
            
        if self.spec.authorized_networks:
            ip_config["authorized_networks"] = self.spec.authorized_networks
            
        if self.spec.require_ssl:
            ip_config["require_ssl"] = True
            
        if ip_config:
            settings["ip_configuration"] = ip_config
            
        # Maintenance window
        settings["maintenance_window"] = {
            "day": self.spec.maintenance_window_day,
            "hour": self.spec.maintenance_window_hour,
            "update_track": self.spec.maintenance_window_update_track
        }
        
        # Database flags
        if self.spec.database_flags:
            settings["database_flags"] = [
                {"name": key, "value": str(value)}
                for key, value in self.spec.database_flags.items()
            ]
            
        return settings

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Cloud SQL configuration"""
        config = {
            "resource_type": "sql_database_instance"
        }
        
        # Deletion protection
        if self.spec.deletion_protection:
            config["deletion_protection"] = True
            
        # Root password
        if self.spec.root_password:
            config["root_password"] = self.spec.root_password

        return config
        
    # Fluent interface methods
    
    # Database engines
    
    def postgresql(self, version: str = "14") -> Self:
        """Use PostgreSQL engine (chainable)"""
        self.spec.database_engine = DatabaseEngine.POSTGRESQL
        self.spec.database_version = f"POSTGRES_{version}"
        return self
        
    def mysql(self, version: str = "8.0") -> Self:
        """Use MySQL engine (chainable)"""
        self.spec.database_engine = DatabaseEngine.MYSQL
        self.spec.database_version = f"MYSQL_{version.replace('.', '_')}"
        return self
        
    def sql_server(self, version: str = "2019") -> Self:
        """Use SQL Server engine (chainable)"""
        self.spec.database_engine = DatabaseEngine.SQL_SERVER
        if version == "2019":
            self.spec.database_version = "SQLSERVER_2019_STANDARD"
        elif version == "2017":
            self.spec.database_version = "SQLSERVER_2017_STANDARD"
        else:
            self.spec.database_version = f"SQLSERVER_{version}_STANDARD"
        return self
        
    # Instance sizing
    
    def tier(self, machine_type: str) -> Self:
        """Set database tier/machine type (chainable)"""
        if isinstance(machine_type, str):
            # Handle string tier names
            try:
                self.spec.tier = DatabaseTier(machine_type)
            except ValueError:
                # If not a standard tier, set as custom
                self.spec.provider_config["custom_tier"] = machine_type
        else:
            self.spec.tier = machine_type
        return self
        
    # Convenience tier methods
    
    def micro(self) -> Self:
        """Use shared micro instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_F1_MICRO
        return self
        
    def small(self) -> Self:
        """Use small shared instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_G1_SMALL
        return self
        
    def standard_1(self) -> Self:
        """Use standard 1 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_STANDARD_1
        return self
        
    def standard_2(self) -> Self:
        """Use standard 2 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_STANDARD_2
        return self
        
    def standard_4(self) -> Self:
        """Use standard 4 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_STANDARD_4
        return self
        
    def standard_8(self) -> Self:
        """Use standard 8 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_STANDARD_8
        return self
        
    def standard_16(self) -> Self:
        """Use standard 16 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_STANDARD_16
        return self
        
    def standard_32(self) -> Self:
        """Use standard 32 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_STANDARD_32
        return self
        
    def highmem_2(self) -> Self:
        """Use high-memory 2 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_HIGHMEM_2
        return self
        
    def highmem_4(self) -> Self:
        """Use high-memory 4 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_HIGHMEM_4
        return self
        
    def highmem_8(self) -> Self:
        """Use high-memory 8 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_HIGHMEM_8
        return self
        
    def highmem_16(self) -> Self:
        """Use high-memory 16 vCPU instance (chainable)"""
        self.spec.tier = DatabaseTier.DB_N1_HIGHMEM_16
        return self
        
    # Location methods
    
    def region(self, region_name: str) -> Self:
        """Set region (chainable)"""
        self.spec.region = region_name
        return self
        
    def zone(self, zone_name: str) -> Self:
        """Set specific zone for zonal instances (chainable)"""
        self.spec.zone = zone_name
        return self
        
    def high_availability(self) -> Self:
        """Enable high availability across zones (chainable)"""
        self.spec.availability_type = AvailabilityType.REGIONAL
        return self
        
    def zonal(self) -> Self:
        """Use single zone deployment (chainable)"""
        self.spec.availability_type = AvailabilityType.ZONAL
        return self
        
    # Storage methods
    
    def disk_size(self, size_gb: int) -> Self:
        """Set disk size in GB (chainable)"""
        self.spec.disk_size = size_gb
        return self
        
    def ssd_storage(self) -> Self:
        """Use SSD storage (chainable)"""
        self.spec.disk_type = StorageType.SSD
        return self
        
    def hdd_storage(self) -> Self:
        """Use HDD storage (chainable)"""
        self.spec.disk_type = StorageType.HDD
        return self
        
    def auto_resize(self, enabled: bool = True, limit: int = 0) -> Self:
        """Enable disk auto-resize (chainable)"""
        self.spec.disk_autoresize = enabled
        self.spec.disk_autoresize_limit = limit
        return self
        
    # Database settings
    
    def database_name(self, name: str) -> Self:
        """Set database name (chainable)"""
        self.spec.database_name = name
        return self
        
    def root_password(self, password: str) -> Self:
        """Set root password (chainable)"""
        self.spec.root_password = password
        return self
        
    # Network configuration
    
    def private_ip(self, network: str = None) -> Self:
        """Enable private IP (chainable)"""
        self.spec.private_network = network or "default"
        return self
        
    def public_ip(self) -> Self:
        """Enable public IP (chainable)"""
        self.spec.private_network = None
        return self
        
    def authorized_network(self, cidr: str, name: str = "default") -> Self:
        """Add authorized network (chainable)"""
        auth_net = {"value": cidr, "name": name}
        if auth_net not in self.spec.authorized_networks:
            self.spec.authorized_networks.append(auth_net)
        return self
        
    def ssl_required(self, required: bool = True) -> Self:
        """Require SSL connections (chainable)"""
        self.spec.require_ssl = required
        return self
        
    # Backup configuration
    
    def backup_enabled(self, start_time: str = "02:00") -> Self:
        """Enable automated backups (chainable)"""
        self.spec.backup_config.enabled = True
        self.spec.backup_config.start_time = start_time
        return self
        
    def backup_disabled(self) -> Self:
        """Disable automated backups (chainable)"""
        self.spec.backup_config.enabled = False
        return self
        
    def point_in_time_recovery(self, enabled: bool = True) -> Self:
        """Enable point-in-time recovery (chainable)"""
        self.spec.backup_config.point_in_time_recovery = enabled
        return self
        
    def backup_retention(self, days: int) -> Self:
        """Set backup retention in days (chainable)"""
        self.spec.backup_config.retention_days = days
        return self
        
    # Database flags
    
    def database_flag(self, name: str, value: Any) -> Self:
        """Set database flag (chainable)"""
        self.spec.database_flags[name] = value
        return self
        
    def database_flags(self, flags: Dict[str, Any]) -> Self:
        """Set multiple database flags (chainable)"""
        self.spec.database_flags.update(flags)
        return self
        
    # Maintenance
    
    def maintenance_window(self, day: int, hour: int, track: str = "stable") -> Self:
        """Set maintenance window (chainable)"""
        if not (1 <= day <= 7):
            raise ValueError("Day must be between 1 (Sunday) and 7 (Saturday)")
        if not (0 <= hour <= 23):
            raise ValueError("Hour must be between 0 and 23")
        
        self.spec.maintenance_window_day = day
        self.spec.maintenance_window_hour = hour
        self.spec.maintenance_window_update_track = track
        return self
        
    # Labels
    
    def label(self, key: str, value: str) -> Self:
        """Add a label (chainable)"""
        self.spec.labels[key] = value
        return self
        
    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set multiple labels (chainable)"""
        if labels_dict:
            self.spec.labels.update(labels_dict)
        if labels:
            self.spec.labels.update(labels)
        return self
        
    # Protection
    
    def deletion_protection(self, enabled: bool = True) -> Self:
        """Enable deletion protection (chainable)"""
        self.spec.deletion_protection = enabled
        return self
        
    # Read replicas (LEGO principle)
    
    def read_replica(self, name: str, region: str = None, tier: str = None) -> "CloudSQL":
        """Create read replica of this database (LEGO principle)"""
        replica = CloudSQL(name)
        
        # Inherit configuration from master
        replica.spec.database_engine = self.spec.database_engine
        replica.spec.database_version = self.spec.database_version
        replica.spec.database_name = self.spec.database_name
        
        # Set replica-specific configuration
        replica.spec.replica_configuration = ReplicaConfiguration()
        replica.spec.replica_configuration.tier = DatabaseTier(tier) if tier else self.spec.tier
        replica.spec.replica_configuration.region = region or self.spec.region
        
        # Labels
        replica.spec.labels = self.spec.labels.copy()
        replica.spec.labels["replica_of"] = self.name
        
        # Mark as replica in provider config
        replica.spec.provider_config["master_instance_name"] = self.name
        replica.spec.provider_config["replica_configuration"] = {
            "master_instance_name": self.name
        }
        
        return replica
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .high_availability()
                .backup_enabled()
                .point_in_time_recovery()
                .backup_retention(30)
                .deletion_protection()
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .backup_enabled()
                .backup_retention(7)
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .micro()
                .backup_disabled()
                .label("environment", "development"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the database via provider"""
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
        """Update the database via provider"""
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
        """Destroy the database via provider"""
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
    
    def get_connection_string(self) -> Optional[str]:
        """Get database connection string"""
        if not self.status.provider_data:
            return None
            
        host = self.status.provider_data.get("ip_address")
        port = self.status.provider_data.get("port", 5432 if self.spec.database_engine == DatabaseEngine.POSTGRESQL else 3306)
        database = self.spec.database_name
        
        if self.spec.database_engine == DatabaseEngine.POSTGRESQL:
            ssl_param = "?sslmode=require" if self.spec.require_ssl else ""
            return f"postgresql://username:password@{host}:{port}/{database}{ssl_param}"
        elif self.spec.database_engine == DatabaseEngine.MYSQL:
            ssl_param = "?ssl-mode=REQUIRED" if self.spec.require_ssl else ""
            return f"mysql://username:password@{host}:{port}/{database}{ssl_param}"
        elif self.spec.database_engine == DatabaseEngine.SQL_SERVER:
            return f"sqlserver://username:password@{host}:{port};database={database}"
            
        return None
        
    def get_ip_address(self) -> Optional[str]:
        """Get database IP address"""
        return self.status.provider_data.get("ip_address")