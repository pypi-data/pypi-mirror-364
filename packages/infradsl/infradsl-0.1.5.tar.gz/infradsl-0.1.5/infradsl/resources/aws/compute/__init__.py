"""
AWS Compute resources for InfraDSL
"""

from .ec2 import AWSEC2
from .load_balancer import AWSLoadBalancer

__all__ = [
    "AWSEC2",
    "AWSLoadBalancer",
]