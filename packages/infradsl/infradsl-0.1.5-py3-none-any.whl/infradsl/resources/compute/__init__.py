"""
Compute resources
"""

from .cloud_run import CloudRun
from .instance_group import InstanceGroup, InstanceTemplate
from .load_balancer import LoadBalancer
from .static_ip import StaticIP
from .virtual_machine import VirtualMachine, InstanceSize, ImageType
from .web_server import WebServer

__all__ = [
    "CloudRun",
    "VirtualMachine",
    "InstanceSize",
    "ImageType",
    "WebServer",
    "StaticIP",
    "InstanceGroup",
    "InstanceTemplate", 
    "LoadBalancer"
]
