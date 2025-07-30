from typing import List, Any
from ...core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext


class DatabaseTemplate(BaseTemplate):
    """
    Database Template
    
    A comprehensive template for deploying managed database instances with:
    - Multiple database engines (PostgreSQL, MySQL, etc.)
    - High availability and Multi-AZ deployment
    - Automated backups and point-in-time recovery
    - Read replicas for scaling
    - Security groups and encryption
    - Performance monitoring
    """
    
    def _create_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="Database",
            version="1.0.0",
            description="Managed database with high availability and backups",
            author="InfraDSL Team", 
            category="database",
            tags=["database", "rds", "managed", "backup", "ha"],
            providers=["aws", "gcp", "azure"],
            parameters_schema={
                "type": "object",
                "properties": {
                    "engine": {
                        "type": "string",
                        "default": "postgresql",
                        "description": "Database engine (postgresql, mysql, mariadb)"
                    },
                    "version": {
                        "type": "string", 
                        "default": "latest",
                        "description": "Database version"
                    },
                    "instance_class": {
                        "type": "string",
                        "default": "small",
                        "description": "Database instance size"
                    },
                    "allocated_storage": {
                        "type": "integer",
                        "default": 100,
                        "description": "Initial storage in GB"
                    },
                    "max_storage": {
                        "type": "integer",
                        "default": 1000,
                        "description": "Maximum storage for autoscaling"
                    },
                    "multi_az": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable Multi-AZ deployment"
                    },
                    "backup_retention": {
                        "type": "integer", 
                        "default": 7,
                        "description": "Backup retention in days"
                    },
                    "enable_encryption": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable storage encryption"
                    },
                    "monitoring": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable enhanced monitoring"
                    },
                    "performance_insights": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable Performance Insights"
                    },
                    "read_replicas": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of read replicas"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "endpoint": {"type": "string", "description": "Database endpoint"},
                    "port": {"type": "integer", "description": "Database port"},
                    "database_name": {"type": "string", "description": "Database name"},
                    "master_username": {"type": "string", "description": "Master username"}
                }
            },
            examples=[
                {
                    "name": "PostgreSQL Database",
                    "description": "High-availability PostgreSQL database",
                    "code": '''db = Template.Database("app-db").with_parameters(
    engine="postgresql",
    instance_class="medium",
    allocated_storage=200,
    multi_az=True,
    read_replicas=1
).production()'''
                }
            ]
        )
        
    def build(self, context: TemplateContext) -> List[Any]:
        """Build the database infrastructure"""
        provider_type = self._detect_provider(context)
        
        if provider_type == "aws":
            return self._build_aws_database(context)
        else:
            raise NotImplementedError(f"Database template not implemented for {provider_type}")
            
    def _detect_provider(self, context: TemplateContext) -> str:
        """Detect target provider"""
        return context.provider_configs.get("type", "aws")
        
    def _build_aws_database(self, context: TemplateContext) -> List[Any]:
        """Build AWS RDS database"""
        from ...resources.aws.database.rds import AWSRDS
        from ...resources.aws.security.security_group import AWSSecurityGroup
        
        resources = []
        
        # Parameters
        engine = context.parameters.get("engine", "postgresql")
        version = context.parameters.get("version", "latest")
        instance_class = context.parameters.get("instance_class", "small")
        allocated_storage = context.parameters.get("allocated_storage", 100)
        max_storage = context.parameters.get("max_storage", 1000)
        multi_az = context.parameters.get("multi_az", True)
        backup_retention = context.parameters.get("backup_retention", 7)
        enable_encryption = context.parameters.get("enable_encryption", True)
        monitoring = context.parameters.get("monitoring", True)
        performance_insights = context.parameters.get("performance_insights", True)
        read_replicas = context.parameters.get("read_replicas", 0)
        
        # Create database security group
        db_sg = (AWSSecurityGroup(f"{context.name}-db-sg")
                 .vpc("vpc-default")
                 .description("Security group for database")
                 .allow_postgresql(from_cidr="10.0.0.0/8")
                 .allow_mysql(from_cidr="10.0.0.0/8")
                 .tag("Component", "Database"))
        
        resources.append(db_sg)
        
        # Create RDS instance
        db = AWSRDS(context.name)
        
        # Configure engine
        if engine == "postgresql":
            db = db.postgresql(version if version != "latest" else "14.6")
        elif engine == "mysql":
            db = db.mysql(version if version != "latest" else "8.0")
        elif engine == "mariadb":
            db = db.mariadb(version if version != "latest" else "10.6")
            
        # Configure instance
        instance_class_map = {
            "micro": "db.t3.micro",
            "small": "db.t3.small",
            "medium": "db.r5.large",
            "large": "db.r5.xlarge",
            "xlarge": "db.r5.2xlarge"
        }
        db = db.instance_class(instance_class_map.get(instance_class, instance_class))
        
        # Configure database
        db = (db.database(f"{context.name.replace('-', '_')}_db")
              .username("admin")  
              .generated_password()
              .storage(allocated_storage, "gp3")
              .storage_autoscaling(max_storage)
              .security_groups([db_sg.name])
              .backup(retention_days=backup_retention))
              
        # Configure high availability
        if multi_az:
            db = db.multi_az()
            
        # Configure encryption
        if enable_encryption:
            db = db.encryption()
            
        # Configure monitoring
        if monitoring:
            db = db.monitoring()
            
        if performance_insights:
            db = db.performance_insights()
            
        # Apply environment configuration
        if context.environment == "production":
            db = db.production()
        elif context.environment == "staging":
            db = db.staging()
        else:
            db = db.development()
            
        resources.append(db)
        
        # Create read replicas
        for i in range(read_replicas):
            replica = db.read_replica(f"{context.name}-replica-{i+1}")
            resources.append(replica)
            
        # Set outputs
        self.set_output("endpoint", f"${{{db.name}.endpoint}}")
        self.set_output("port", f"${{{db.name}.port}}")
        self.set_output("database_name", f"{context.name.replace('-', '_')}_db")
        self.set_output("master_username", "admin")
        
        return resources