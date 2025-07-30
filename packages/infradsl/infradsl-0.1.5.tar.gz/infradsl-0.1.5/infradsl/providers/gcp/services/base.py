"""
Base GCP Service Class
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..provider import GCPComputeProvider

from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class BaseGCPService:
    """Base class for GCP service implementations"""
    
    def __init__(self, provider: "GCPComputeProvider"):
        self.provider = provider
        self.config = provider.config
        self._project_id = provider._project_id
        self._compute_client = provider._compute_client
        
    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for resource - override in subclasses"""
        return {"hourly": 0.0, "monthly": 0.0}
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration - override in subclasses"""
        return []
    
    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview resource creation - override in subclasses"""
        return {}
    
    def preview_update(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Preview resource update - override in subclasses"""
        return {"changes": list(updates.keys())}
    
    def get_delete_warnings(self) -> List[str]:
        """Get warnings for resource deletion - override in subclasses"""
        return []