"""
GCP Provider Services
"""

from .compute import ComputeService
from .dns import DNSService

__all__ = ["ComputeService", "DNSService"]