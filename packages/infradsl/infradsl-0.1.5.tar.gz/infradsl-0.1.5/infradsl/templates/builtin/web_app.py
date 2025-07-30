from typing import List, Any
from ...core.templates.base import BaseTemplate, TemplateMetadata, TemplateContext


class WebAppTemplate(BaseTemplate):
    """
    Web Application Template
    
    A comprehensive template for deploying scalable web applications with:
    - Load balancer for high availability
    - Multiple application servers
    - SSL/TLS certificate management
    - Auto-scaling configuration
    - Health checks and monitoring
    
    This template extends the GenericVM template and adds web-specific components.
    """
    
    def _create_metadata(self) -> TemplateMetadata:
        return TemplateMetadata(
            name="WebApp",
            version="1.0.0", 
            description="Scalable web application with load balancer and SSL",
            author="InfraDSL Team",
            category="web",
            tags=["web", "scalable", "load-balancer", "ssl", "app"],
            requires=["GenericVM"],
            providers=["aws", "gcp", "azure"],
            parameters_schema={
                "type": "object",
                "properties": {
                    "instance_count": {
                        "type": "integer",
                        "default": 2,
                        "description": "Number of application instances"
                    },
                    "instance_type": {
                        "type": "string",
                        "default": "medium", 
                        "description": "Instance size for app servers"
                    },
                    "ssl_certificate": {
                        "type": "string",
                        "description": "SSL certificate ARN or path"
                    },
                    "domain_name": {
                        "type": "string",
                        "description": "Custom domain name"
                    },
                    "app_port": {
                        "type": "integer",
                        "default": 8080,
                        "description": "Application port"
                    },
                    "health_check_path": {
                        "type": "string",
                        "default": "/health",
                        "description": "Health check endpoint"
                    },
                    "auto_scaling": {
                        "type": "boolean", 
                        "default": True,
                        "description": "Enable auto-scaling"
                    },
                    "min_instances": {
                        "type": "integer",
                        "default": 1,
                        "description": "Minimum instances for auto-scaling"
                    },
                    "max_instances": {
                        "type": "integer", 
                        "default": 10,
                        "description": "Maximum instances for auto-scaling"
                    }
                },
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "load_balancer_dns": {"type": "string"},
                    "application_url": {"type": "string"},
                    "ssl_certificate_arn": {"type": "string"}
                }
            },
            examples=[
                {
                    "name": "Simple Web App",
                    "description": "Basic web application with load balancer",
                    "code": '''app = Template.WebApp("my-app").with_parameters(
    instance_count=3,
    domain_name="myapp.com"
).production()'''
                }
            ]
        )
        
    def build(self, context: TemplateContext) -> List[Any]:
        """Build the web application infrastructure"""
        resources = []
        
        # Get parameters
        instance_count = context.parameters.get("instance_count", 2)
        instance_type = context.parameters.get("instance_type", "medium")
        ssl_certificate = context.parameters.get("ssl_certificate")
        domain_name = context.parameters.get("domain_name")
        app_port = context.parameters.get("app_port", 8080)
        health_check_path = context.parameters.get("health_check_path", "/health")
        
        provider_type = self._detect_provider(context)
        
        if provider_type == "aws":
            return self._build_aws_webapp(context, resources)
        else:
            raise NotImplementedError(f"WebApp template not implemented for {provider_type}")
            
    def _detect_provider(self, context: TemplateContext) -> str:
        """Detect target provider"""
        return context.provider_configs.get("type", "aws")
        
    def _build_aws_webapp(self, context: TemplateContext, resources: List[Any]) -> List[Any]:
        """Build AWS web application"""
        from ...resources.aws.compute.ec2 import AWSEC2
        from ...resources.aws.compute.load_balancer import AWSLoadBalancer
        from ...resources.aws.security.security_group import AWSSecurityGroup
        
        # Parameters
        instance_count = context.parameters.get("instance_count", 2) 
        instance_type = context.parameters.get("instance_type", "medium")
        app_port = context.parameters.get("app_port", 8080)
        health_check_path = context.parameters.get("health_check_path", "/health")
        ssl_certificate = context.parameters.get("ssl_certificate")
        
        # Create security groups
        alb_sg = (AWSSecurityGroup(f"{context.name}-alb-sg")
                  .vpc("vpc-default")  # Would be parameterized
                  .description("Security group for load balancer")
                  .allow_http_from_anywhere()
                  .allow_https_from_anywhere()
                  .tag("Component", "LoadBalancer"))
                  
        app_sg = (AWSSecurityGroup(f"{context.name}-app-sg")
                  .vpc("vpc-default")
                  .description("Security group for application servers")
                  .allow_port(app_port, from_sg=alb_sg.name)
                  .allow_ssh_from("10.0.0.0/8")
                  .tag("Component", "Application"))
        
        resources.extend([alb_sg, app_sg])
        
        # Create application load balancer
        alb = (AWSLoadBalancer(f"{context.name}-alb")
               .application()
               .internet_facing()
               .subnets(["subnet-public-1a", "subnet-public-1b"])
               .security_groups([alb_sg.name])
               .target_group("web-servers", 80, "HTTP")
               .health_check(health_check_path, port=app_port)
               .http_listener(80, "web-servers"))
               
        if ssl_certificate:
            alb = alb.https_listener(443, ssl_certificate, "web-servers")
            
        resources.append(alb)
        
        # Create application instances
        for i in range(instance_count):
            vm = (AWSEC2(f"{context.name}-app-{i+1}")
                  .ubuntu("22.04")
                  .general_purpose(instance_type)
                  .security_groups([app_sg.name])
                  .startup_script(f"""#!/bin/bash
apt-get update
apt-get install -y nginx
# Configure nginx to proxy to app on port {app_port}
systemctl start nginx
systemctl enable nginx
""")
                  .tag("Component", "Application")
                  .tag("AppName", context.name))
                  
            if context.environment == "production":
                vm = vm.production()
            elif context.environment == "staging":
                vm = vm.staging()
            else:
                vm = vm.development()
                
            resources.append(vm)
            
        # Set outputs
        self.set_output("load_balancer_dns", f"${{{alb.name}.dns_name}}")
        
        if context.parameters.get("domain_name"):
            self.set_output("application_url", f"https://{context.parameters['domain_name']}")
        else:
            self.set_output("application_url", f"http://${{{alb.name}.dns_name}}")
            
        if ssl_certificate:
            self.set_output("ssl_certificate_arn", ssl_certificate)
            
        return resources