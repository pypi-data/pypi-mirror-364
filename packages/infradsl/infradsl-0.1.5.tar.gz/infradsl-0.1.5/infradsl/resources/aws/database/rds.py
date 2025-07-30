from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ....core.nexus.base_resource import BaseResource, ResourceSpec


class DBEngine(Enum):
    """Database engine types"""
    MYSQL = "mysql"
    POSTGRES = "postgres"
    MARIADB = "mariadb"
    ORACLE_EE = "oracle-ee"
    ORACLE_SE2 = "oracle-se2"
    SQLSERVER_EE = "sqlserver-ee"
    SQLSERVER_SE = "sqlserver-se"
    SQLSERVER_EX = "sqlserver-ex"
    SQLSERVER_WEB = "sqlserver-web"
    AURORA_MYSQL = "aurora-mysql"
    AURORA_POSTGRESQL = "aurora-postgresql"


class DBInstanceClass(Enum):
    """Database instance classes"""
    # Burstable Performance
    T3_MICRO = "db.t3.micro"
    T3_SMALL = "db.t3.small"
    T3_MEDIUM = "db.t3.medium"
    T3_LARGE = "db.t3.large"
    T3_XLARGE = "db.t3.xlarge"
    T3_2XLARGE = "db.t3.2xlarge"
    
    # General Purpose
    M5_LARGE = "db.m5.large"
    M5_XLARGE = "db.m5.xlarge"
    M5_2XLARGE = "db.m5.2xlarge"
    M5_4XLARGE = "db.m5.4xlarge"
    M5_8XLARGE = "db.m5.8xlarge"
    M5_12XLARGE = "db.m5.12xlarge"
    M5_16XLARGE = "db.m5.16xlarge"
    M5_24XLARGE = "db.m5.24xlarge"
    
    # Memory Optimized
    R5_LARGE = "db.r5.large"
    R5_XLARGE = "db.r5.xlarge"
    R5_2XLARGE = "db.r5.2xlarge"
    R5_4XLARGE = "db.r5.4xlarge"
    R5_8XLARGE = "db.r5.8xlarge"
    R5_12XLARGE = "db.r5.12xlarge"
    R5_16XLARGE = "db.r5.16xlarge"
    R5_24XLARGE = "db.r5.24xlarge"


class StorageType(Enum):
    """Storage types for RDS"""
    GP2 = "gp2"
    GP3 = "gp3"
    IO1 = "io1"
    MAGNETIC = "standard"


@dataclass
class BackupConfig:
    """Backup configuration"""
    backup_retention_period: int = 7
    backup_window: str = "03:00-04:00"
    copy_tags_to_snapshot: bool = True
    delete_automated_backups: bool = True
    deletion_protection: bool = False
    final_snapshot_identifier: Optional[str] = None
    skip_final_snapshot: bool = False


@dataclass
class MaintenanceConfig:
    """Maintenance configuration"""
    maintenance_window: str = "sun:04:00-sun:05:00"
    auto_minor_version_upgrade: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    monitoring_interval: int = 0
    monitoring_role_arn: Optional[str] = None
    performance_insights_enabled: bool = False
    performance_insights_retention_period: int = 7
    enabled_cloudwatch_logs_exports: List[str] = field(default_factory=list)


@dataclass
class AWSRDSSpec(ResourceSpec):
    """Specification for AWS RDS Instance"""
    
    # Basic configuration
    engine: DBEngine = DBEngine.MYSQL
    engine_version: Optional[str] = None
    instance_class: DBInstanceClass = DBInstanceClass.T3_MICRO
    
    # Database configuration
    database_name: Optional[str] = None
    username: str = "admin"
    password: Optional[str] = None
    port: Optional[int] = None
    
    # Storage configuration
    allocated_storage: int = 20
    max_allocated_storage: Optional[int] = None
    storage_type: StorageType = StorageType.GP3
    storage_encrypted: bool = True
    kms_key_id: Optional[str] = None
    iops: Optional[int] = None
    storage_throughput: Optional[int] = None
    
    # Network configuration
    db_subnet_group_name: Optional[str] = None
    vpc_security_group_ids: List[str] = field(default_factory=list)
    availability_zone: Optional[str] = None
    multi_az: bool = False
    publicly_accessible: bool = False
    
    # Backup and maintenance
    backup_config: BackupConfig = field(default_factory=BackupConfig)
    maintenance_config: MaintenanceConfig = field(default_factory=MaintenanceConfig)
    
    # Monitoring
    monitoring_config: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Advanced features
    parameter_group_name: Optional[str] = None
    option_group_name: Optional[str] = None
    character_set_name: Optional[str] = None
    timezone: Optional[str] = None
    
    # Read replicas
    read_replicas: List[str] = field(default_factory=list)
    replicate_source_db: Optional[str] = None
    
    # Tags
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class AWSRDS(BaseResource):
    """
    AWS RDS Database Instance with all engines and comprehensive features with Rails-like conventions.
    
    Examples:
        # MySQL database
        mysql_db = (AWSRDS("prod-mysql")
                    .mysql("8.0")
                    .instance_class("db.r5.xlarge")
                    .database("myapp")
                    .username("admin")
                    .generated_password()
                    .storage(100, "gp3")
                    .multi_az()
                    .subnet_group("prod-db-subnet-group")
                    .security_groups(["sg-database"])
                    .backup(retention_days=30)
                    .monitoring()
                    .encryption()
                    .production())
        
        # PostgreSQL with read replica
        postgres_db = (AWSRDS("prod-postgres")
                       .postgresql("14.6")
                       .instance_class("db.r5.2xlarge")
                       .database("myapp")
                       .username("postgres")
                       .generated_password()
                       .storage(500, "gp3")
                       .multi_az()
                       .subnet_group("prod-db-subnet-group")
                       .security_groups(["sg-database"])
                       .backup(retention_days=30)
                       .monitoring()
                       .performance_insights()
                       .encryption()
                       .read_replica("prod-postgres-replica", "us-west-2")
                       .production())
                       
        # SQL Server Enterprise
        sqlserver_db = (AWSRDS("prod-sqlserver")
                       .sqlserver_ee("15.00")
                       .instance_class("db.m5.4xlarge")
                       .database("MyAppDB")
                       .username("sa")
                       .generated_password()
                       .storage(1000, "io1", iops=5000)
                       .multi_az()
                       .subnet_group("prod-db-subnet-group")
                       .security_groups(["sg-database"])
                       .backup(retention_days=35)
                       .monitoring()
                       .encryption()
                       .timezone("UTC")
                       .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: AWSRDSSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "AWSRDS"
        
    def _create_spec(self) -> AWSRDSSpec:
        return AWSRDSSpec()
        
    def _validate_spec(self) -> None:
        """Validate AWS RDS specification"""
        if not self.spec.username:
            raise ValueError("Database username is required")
            
        if self.spec.storage_type == StorageType.IO1 and not self.spec.iops:
            raise ValueError("IOPS must be specified for io1 storage")
            
        if self.spec.max_allocated_storage and self.spec.max_allocated_storage < self.spec.allocated_storage:
            raise ValueError("max_allocated_storage must be greater than allocated_storage")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "identifier": self.metadata.name,
            "engine": self.spec.engine.value,
            "instance_class": self.spec.instance_class.value,
            "username": self.spec.username,
            "allocated_storage": self.spec.allocated_storage,
            "storage_type": self.spec.storage_type.value,
            "storage_encrypted": self.spec.storage_encrypted,
            "multi_az": self.spec.multi_az,
            "publicly_accessible": self.spec.publicly_accessible,
            "vpc_security_group_ids": self.spec.vpc_security_group_ids,
            "tags": {**self.spec.tags, **self.metadata.to_tags()},
        }
        
        # Optional configurations
        if self.spec.engine_version:
            config["engine_version"] = self.spec.engine_version
        if self.spec.database_name:
            config["database_name"] = self.spec.database_name
        if self.spec.password:
            config["password"] = self.spec.password
        if self.spec.port:
            config["port"] = self.spec.port
        if self.spec.max_allocated_storage:
            config["max_allocated_storage"] = self.spec.max_allocated_storage
        if self.spec.kms_key_id:
            config["kms_key_id"] = self.spec.kms_key_id
        if self.spec.iops:
            config["iops"] = self.spec.iops
        if self.spec.storage_throughput:
            config["storage_throughput"] = self.spec.storage_throughput
        if self.spec.db_subnet_group_name:
            config["db_subnet_group_name"] = self.spec.db_subnet_group_name
        if self.spec.availability_zone:
            config["availability_zone"] = self.spec.availability_zone
        if self.spec.parameter_group_name:
            config["parameter_group_name"] = self.spec.parameter_group_name
        if self.spec.option_group_name:
            config["option_group_name"] = self.spec.option_group_name
        if self.spec.character_set_name:
            config["character_set_name"] = self.spec.character_set_name
        if self.spec.timezone:
            config["timezone"] = self.spec.timezone
        if self.spec.replicate_source_db:
            config["replicate_source_db"] = self.spec.replicate_source_db
            
        # Backup configuration
        backup = self.spec.backup_config
        config.update({
            "backup_retention_period": backup.backup_retention_period,
            "backup_window": backup.backup_window,
            "copy_tags_to_snapshot": backup.copy_tags_to_snapshot,
            "delete_automated_backups": backup.delete_automated_backups,
            "deletion_protection": backup.deletion_protection,
            "skip_final_snapshot": backup.skip_final_snapshot
        })
        
        if backup.final_snapshot_identifier:
            config["final_snapshot_identifier"] = backup.final_snapshot_identifier
            
        # Maintenance configuration
        maintenance = self.spec.maintenance_config
        config.update({
            "maintenance_window": maintenance.maintenance_window,
            "auto_minor_version_upgrade": maintenance.auto_minor_version_upgrade
        })
        
        # Monitoring configuration
        monitoring = self.spec.monitoring_config
        config.update({
            "monitoring_interval": monitoring.monitoring_interval,
            "performance_insights_enabled": monitoring.performance_insights_enabled,
            "performance_insights_retention_period": monitoring.performance_insights_retention_period,
            "enabled_cloudwatch_logs_exports": monitoring.enabled_cloudwatch_logs_exports
        })
        
        if monitoring.monitoring_role_arn:
            config["monitoring_role_arn"] = monitoring.monitoring_role_arn

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "aws":
            config.update(self._to_aws_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _to_aws_config(self) -> Dict[str, Any]:
        """Convert to AWS RDS configuration"""
        return {
            "resource_type": "aws_db_instance"
        }
        
    # Fluent interface methods
    
    # Database engines
    
    def mysql(self, version: str = None) -> Self:
        """Use MySQL engine (chainable)"""
        self.spec.engine = DBEngine.MYSQL
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 3306
        return self
        
    def postgresql(self, version: str = None) -> Self:
        """Use PostgreSQL engine (chainable)"""
        self.spec.engine = DBEngine.POSTGRES
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 5432
        return self
        
    def mariadb(self, version: str = None) -> Self:
        """Use MariaDB engine (chainable)"""
        self.spec.engine = DBEngine.MARIADB
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 3306
        return self
        
    def oracle_ee(self, version: str = None) -> Self:
        """Use Oracle Enterprise Edition (chainable)"""
        self.spec.engine = DBEngine.ORACLE_EE
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 1521
        return self
        
    def oracle_se2(self, version: str = None) -> Self:
        """Use Oracle Standard Edition 2 (chainable)"""
        self.spec.engine = DBEngine.ORACLE_SE2
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 1521
        return self
        
    def sqlserver_ee(self, version: str = None) -> Self:
        """Use SQL Server Enterprise Edition (chainable)"""
        self.spec.engine = DBEngine.SQLSERVER_EE
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 1433
        return self
        
    def sqlserver_se(self, version: str = None) -> Self:
        """Use SQL Server Standard Edition (chainable)"""
        self.spec.engine = DBEngine.SQLSERVER_SE
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 1433
        return self
        
    def sqlserver_ex(self, version: str = None) -> Self:
        """Use SQL Server Express Edition (chainable)"""
        self.spec.engine = DBEngine.SQLSERVER_EX
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 1433
        return self
        
    def sqlserver_web(self, version: str = None) -> Self:
        """Use SQL Server Web Edition (chainable)"""
        self.spec.engine = DBEngine.SQLSERVER_WEB
        self.spec.engine_version = version
        if not self.spec.port:
            self.spec.port = 1433
        return self
        
    # Instance configuration
    
    def instance_class(self, instance_class: Union[str, DBInstanceClass]) -> Self:
        """Set instance class (chainable)"""
        if isinstance(instance_class, str):
            # Try to find matching enum, otherwise use custom class
            try:
                self.spec.instance_class = DBInstanceClass(instance_class)
            except ValueError:
                self.spec.instance_class = instance_class
        else:
            self.spec.instance_class = instance_class
        return self
        
    def burstable(self, size: str = "micro") -> Self:
        """Use burstable performance instance (chainable)"""
        type_map = {
            "micro": DBInstanceClass.T3_MICRO,
            "small": DBInstanceClass.T3_SMALL,
            "medium": DBInstanceClass.T3_MEDIUM,
            "large": DBInstanceClass.T3_LARGE,
            "xlarge": DBInstanceClass.T3_XLARGE,
            "2xlarge": DBInstanceClass.T3_2XLARGE
        }
        self.spec.instance_class = type_map.get(size, DBInstanceClass.T3_MICRO)
        return self
        
    def general_purpose(self, size: str = "large") -> Self:
        """Use general purpose instance (chainable)"""
        if isinstance(size, str) and not size.startswith("db.m5."):
            size = f"db.m5.{size}"
        return self.instance_class(size)
        
    def memory_optimized(self, size: str = "large") -> Self:
        """Use memory optimized instance (chainable)"""
        if isinstance(size, str) and not size.startswith("db.r5."):
            size = f"db.r5.{size}"
        return self.instance_class(size)
        
    # Database configuration
    
    def database(self, name: str) -> Self:
        """Set database name (chainable)"""
        self.spec.database_name = name
        return self
        
    def username(self, username: str) -> Self:
        """Set master username (chainable)"""
        self.spec.username = username
        return self
        
    def password(self, password: str) -> Self:
        """Set master password (chainable)"""
        self.spec.password = password
        return self
        
    def generated_password(self) -> Self:
        """Use AWS-generated password (chainable)"""
        self.spec.password = None  # AWS will generate
        return self
        
    def port(self, port: int) -> Self:
        """Set database port (chainable)"""
        self.spec.port = port
        return self
        
    # Storage configuration
    
    def storage(self, size: int, storage_type: str = "gp3", iops: int = None, 
               throughput: int = None) -> Self:
        """Configure storage (chainable)"""
        self.spec.allocated_storage = size
        self.spec.storage_type = StorageType(storage_type)
        self.spec.iops = iops
        self.spec.storage_throughput = throughput
        return self
        
    def storage_autoscaling(self, max_size: int) -> Self:
        """Enable storage autoscaling (chainable)"""
        self.spec.max_allocated_storage = max_size
        return self
        
    def high_performance_storage(self, size: int, iops: int) -> Self:
        """Configure high-performance storage (chainable)"""
        return self.storage(size, "io1", iops)
        
    # Network configuration
    
    def subnet_group(self, group_name: str) -> Self:
        """Set DB subnet group (chainable)"""
        self.spec.db_subnet_group_name = group_name
        return self
        
    def security_groups(self, sg_ids: List[str]) -> Self:
        """Set VPC security groups (chainable)"""
        self.spec.vpc_security_group_ids = sg_ids.copy()
        return self
        
    def security_group(self, sg_id: str) -> Self:
        """Add VPC security group (chainable)"""
        if sg_id not in self.spec.vpc_security_group_ids:
            self.spec.vpc_security_group_ids.append(sg_id)
        return self
        
    def availability_zone(self, az: str) -> Self:
        """Set availability zone (chainable)"""
        self.spec.availability_zone = az
        return self
        
    def multi_az(self, enabled: bool = True) -> Self:
        """Enable Multi-AZ deployment (chainable)"""
        self.spec.multi_az = enabled
        return self
        
    def publicly_accessible(self, enabled: bool = True) -> Self:
        """Enable public accessibility (chainable)"""
        self.spec.publicly_accessible = enabled
        return self
        
    # Security
    
    def encryption(self, enabled: bool = True, kms_key: str = None) -> Self:
        """Enable storage encryption (chainable)"""
        self.spec.storage_encrypted = enabled
        self.spec.kms_key_id = kms_key
        return self
        
    def deletion_protection(self, enabled: bool = True) -> Self:
        """Enable deletion protection (chainable)"""
        self.spec.backup_config.deletion_protection = enabled
        return self
        
    # Backup configuration
    
    def backup(self, retention_days: int = 7, window: str = "03:00-04:00") -> Self:
        """Configure automated backups (chainable)"""
        self.spec.backup_config.backup_retention_period = retention_days
        self.spec.backup_config.backup_window = window
        return self
        
    def no_backup(self) -> Self:
        """Disable automated backups (chainable)"""
        self.spec.backup_config.backup_retention_period = 0
        return self
        
    def final_snapshot(self, identifier: str = None) -> Self:
        """Enable final snapshot on deletion (chainable)"""
        self.spec.backup_config.skip_final_snapshot = False
        self.spec.backup_config.final_snapshot_identifier = identifier or f"{self.name}-final-snapshot"
        return self
        
    def skip_final_snapshot(self) -> Self:
        """Skip final snapshot on deletion (chainable)"""
        self.spec.backup_config.skip_final_snapshot = True
        return self
        
    # Maintenance
    
    def maintenance_window(self, window: str) -> Self:
        """Set maintenance window (chainable)"""
        self.spec.maintenance_config.maintenance_window = window
        return self
        
    def auto_minor_version_upgrade(self, enabled: bool = True) -> Self:
        """Enable automatic minor version upgrades (chainable)"""
        self.spec.maintenance_config.auto_minor_version_upgrade = enabled
        return self
        
    # Monitoring
    
    def monitoring(self, enabled: bool = True, interval: int = 60, role_arn: str = None) -> Self:
        """Enable enhanced monitoring (chainable)"""
        self.spec.monitoring_config.monitoring_interval = interval if enabled else 0
        self.spec.monitoring_config.monitoring_role_arn = role_arn
        return self
        
    def performance_insights(self, enabled: bool = True, retention_period: int = 7) -> Self:
        """Enable Performance Insights (chainable)"""
        self.spec.monitoring_config.performance_insights_enabled = enabled
        self.spec.monitoring_config.performance_insights_retention_period = retention_period
        return self
        
    def log_exports(self, logs: List[str]) -> Self:
        """Enable CloudWatch log exports (chainable)"""
        self.spec.monitoring_config.enabled_cloudwatch_logs_exports = logs.copy()
        return self
        
    # Advanced configuration
    
    def parameter_group(self, group_name: str) -> Self:
        """Set parameter group (chainable)"""
        self.spec.parameter_group_name = group_name
        return self
        
    def option_group(self, group_name: str) -> Self:
        """Set option group (chainable)"""
        self.spec.option_group_name = group_name
        return self
        
    def character_set(self, charset: str) -> Self:
        """Set character set (Oracle only) (chainable)"""
        self.spec.character_set_name = charset
        return self
        
    def timezone(self, tz: str) -> Self:
        """Set timezone (SQL Server only) (chainable)"""
        self.spec.timezone = tz
        return self
        
    # Read replicas
    
    def read_replica(self, identifier: str, region: str = None) -> "AWSRDS":
        """Create read replica (LEGO principle)"""
        replica = AWSRDS(identifier)
        replica.spec.replicate_source_db = self.name
        
        # Copy configuration from source
        replica.spec.engine = self.spec.engine
        replica.spec.engine_version = self.spec.engine_version
        replica.spec.instance_class = self.spec.instance_class
        replica.spec.storage_encrypted = self.spec.storage_encrypted
        replica.spec.kms_key_id = self.spec.kms_key_id
        replica.spec.monitoring_config = self.spec.monitoring_config
        
        self.spec.read_replicas.append(identifier)
        return replica
        
    # Tags
    
    def tag(self, key: str, value: str) -> Self:
        """Add a tag (chainable)"""
        self.spec.tags[key] = value
        return self
        
    def tags(self, tags_dict: Dict[str, str] = None, **tags) -> Self:
        """Set multiple tags (chainable)"""
        if tags_dict:
            self.spec.tags.update(tags_dict)
        if tags:
            self.spec.tags.update(tags)
        return self
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .multi_az()
                .deletion_protection()
                .backup(retention_days=30)
                .monitoring()
                .performance_insights()
                .encryption()
                .auto_minor_version_upgrade(False)  # Control updates manually
                .final_snapshot()
                .tag("Environment", "production")
                .tag("Backup", "required")
                .tag("Monitoring", "enabled"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .backup(retention_days=7)
                .monitoring()
                .encryption()
                .skip_final_snapshot()
                .tag("Environment", "staging")
                .tag("Backup", "optional"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .burstable("small")
                .no_backup()
                .skip_final_snapshot()
                .tag("Environment", "development")
                .tag("AutoShutdown", "enabled"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the RDS instance via provider"""
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
        """Update the RDS instance via provider"""
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
        """Destroy the RDS instance via provider"""
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
    
    def get_engine(self) -> str:
        """Get database engine"""
        return self.spec.engine.value
        
    def get_instance_class(self) -> str:
        """Get instance class"""
        return self.spec.instance_class.value if isinstance(self.spec.instance_class, DBInstanceClass) else str(self.spec.instance_class)
        
    def is_encrypted(self) -> bool:
        """Check if storage is encrypted"""
        return self.spec.storage_encrypted
        
    def is_multi_az(self) -> bool:
        """Check if Multi-AZ is enabled"""
        return self.spec.multi_az
        
    def get_backup_retention(self) -> int:
        """Get backup retention period"""
        return self.spec.backup_config.backup_retention_period
        
    def has_read_replicas(self) -> bool:
        """Check if database has read replicas"""
        return len(self.spec.read_replicas) > 0
        
    def get_read_replicas(self) -> List[str]:
        """Get read replica identifiers"""
        return self.spec.read_replicas.copy()