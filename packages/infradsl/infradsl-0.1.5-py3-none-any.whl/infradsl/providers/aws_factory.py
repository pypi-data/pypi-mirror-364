"""
AWS Provider - Simple factory for AWS resources
"""

from typing import Any, Dict, Optional

from ..resources.compute.virtual_machine import VirtualMachine
from ..resources.aws.compute.ec2 import AWSEC2
from ..resources.aws.network.vpc import AWSVPC
from ..resources.aws.network.nat_gateway import AWSNATGateway
from ..resources.aws.network.vpc_peering import AWSVPCPeering
from ..resources.aws.database.rds import AWSRDS
from ..resources.aws.storage.s3 import AWSS3
from ..resources.aws.security.security_group import AWSSecurityGroup
from ..resources.aws.compute.load_balancer import AWSLoadBalancer
from ..resources.network.cloudfront import CloudFront
from ..resources.network.route53 import Route53
from ..resources.network.domain_registration import DomainRegistration
from ..resources.network.certificate_manager import CertificateManager
from ..core.nexus import get_registry
from ..core.interfaces.provider import ProviderType, ProviderConfig


class AWS:
    """
    AWS provider factory for creating resources.

    Usage:
        vm = AWS.EC2("my-vm").ubuntu().create()
    """

    _default_config: Optional[ProviderConfig] = None

    @classmethod
    def configure(
        cls,
        region: str = "us-east-1",
        credentials: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """Configure AWS provider defaults"""
        cls._default_config = ProviderConfig(
            type=ProviderType.AWS,
            region=region,
            credentials=credentials,
            options=kwargs,
        )

    @classmethod
    def _get_provider(cls):
        """Get AWS provider instance"""
        if not cls._default_config:
            # Use default configuration
            cls._default_config = ProviderConfig(
                type=ProviderType.AWS, region="us-east-1"
            )

        registry = get_registry()
        return registry.create_provider(ProviderType.AWS, cls._default_config)

    @classmethod
    def EC2(cls, name: str) -> AWSEC2:
        """Create an EC2 instance with full AWS-specific features"""
        ec2 = AWSEC2(name)
        provider = cls._get_provider()
        ec2._provider = provider
        return ec2

    @classmethod
    def Instance(cls, name: str) -> AWSEC2:
        """Alias for EC2"""
        return cls.EC2(name)

    @classmethod
    def VM(cls, name: str) -> AWSEC2:
        """Alias for EC2"""
        return cls.EC2(name)

    @classmethod
    def VPC(cls, name: str) -> AWSVPC:
        """Create a VPC with full AWS-specific features"""
        vpc = AWSVPC(name)
        provider = cls._get_provider()
        vpc._provider = provider
        return vpc

    @classmethod
    def Network(cls, name: str) -> AWSVPC:
        """Alias for VPC"""
        return cls.VPC(name)

    @classmethod
    def RDS(cls, name: str) -> AWSRDS:
        """Create an RDS database with full AWS-specific features"""
        rds = AWSRDS(name)
        provider = cls._get_provider()
        rds._provider = provider
        return rds

    @classmethod
    def Database(cls, name: str) -> AWSRDS:
        """Alias for RDS"""
        return cls.RDS(name)

    @classmethod
    def DB(cls, name: str) -> AWSRDS:
        """Alias for RDS"""
        return cls.RDS(name)

    @classmethod
    def CloudFront(cls, name: str) -> CloudFront:
        """Create a CloudFront CDN distribution"""
        cloudfront = CloudFront(name)
        provider = cls._get_provider()
        cloudfront._provider = provider  # type: ignore
        return cloudfront

    @classmethod
    def CDN(cls, name: str) -> CloudFront:  # type: ignore
        """Alias for CloudFront"""
        return cls.CloudFront(name)

    @classmethod
    def S3(cls, name: str) -> AWSS3:
        """Create an S3 bucket with full AWS-specific features"""
        s3 = AWSS3(name)
        provider = cls._get_provider()
        s3._provider = provider
        return s3

    @classmethod
    def Bucket(cls, name: str) -> AWSS3:
        """Alias for S3"""
        return cls.S3(name)

    @classmethod
    def Route53(cls, name: str) -> Route53:
        """Create Route53 DNS records"""
        route53 = Route53(name)
        provider = cls._get_provider()
        route53._provider = provider  # type: ignore
        return route53

    @classmethod
    def DNS(cls, name: str) -> Route53:  # type: ignore
        """Alias for Route53"""
        return cls.Route53(name)

    @classmethod
    def DomainRegistration(cls, name: str) -> DomainRegistration:
        """Create Route53 domain registration"""
        domain_registration = DomainRegistration(name)
        provider = cls._get_provider()
        domain_registration._provider = provider  # type: ignore
        return domain_registration

    @classmethod
    def Domain(cls, name: str) -> DomainRegistration:  # type: ignore
        """Alias for DomainRegistration"""
        return cls.DomainRegistration(name)

    @classmethod
    def CertificateManager(cls, name: str) -> CertificateManager:
        """Create Certificate Manager SSL certificate"""
        certificate_manager = CertificateManager(name)
        provider = cls._get_provider()
        certificate_manager._provider = provider  # type: ignore
        return certificate_manager

    @classmethod
    def Certificate(cls, name: str) -> CertificateManager:  # type: ignore
        """Alias for CertificateManager"""
        return cls.CertificateManager(name)

    @classmethod
    def SSL(cls, name: str) -> CertificateManager:  # type: ignore
        """Alias for CertificateManager"""
        return cls.CertificateManager(name)

    @classmethod
    def SecurityGroup(cls, name: str) -> AWSSecurityGroup:
        """Create a Security Group with full AWS-specific features"""
        sg = AWSSecurityGroup(name)
        provider = cls._get_provider()
        sg._provider = provider
        return sg

    @classmethod
    def SG(cls, name: str) -> AWSSecurityGroup:
        """Alias for SecurityGroup"""
        return cls.SecurityGroup(name)

    @classmethod
    def LoadBalancer(cls, name: str) -> AWSLoadBalancer:
        """Create a Load Balancer (ALB/NLB) with full AWS-specific features"""
        lb = AWSLoadBalancer(name)
        provider = cls._get_provider()
        lb._provider = provider
        return lb

    @classmethod
    def LB(cls, name: str) -> AWSLoadBalancer:
        """Alias for LoadBalancer"""
        return cls.LoadBalancer(name)

    @classmethod
    def ALB(cls, name: str) -> AWSLoadBalancer:
        """Create an Application Load Balancer"""
        return cls.LoadBalancer(name).application()

    @classmethod
    def NLB(cls, name: str) -> AWSLoadBalancer:
        """Create a Network Load Balancer"""
        return cls.LoadBalancer(name).network()

    @classmethod
    def NATGateway(cls, name: str) -> AWSNATGateway:
        """Create a NAT Gateway with full AWS-specific features"""
        nat = AWSNATGateway(name)
        provider = cls._get_provider()
        nat._provider = provider
        return nat

    @classmethod
    def NAT(cls, name: str) -> AWSNATGateway:
        """Alias for NATGateway"""
        return cls.NATGateway(name)

    @classmethod
    def VPCPeering(cls, name: str) -> AWSVPCPeering:
        """Create a VPC Peering Connection with full AWS-specific features"""
        peering = AWSVPCPeering(name)
        provider = cls._get_provider()
        peering._provider = provider
        return peering

    @classmethod
    def Peering(cls, name: str) -> AWSVPCPeering:
        """Alias for VPCPeering"""
        return cls.VPCPeering(name)
