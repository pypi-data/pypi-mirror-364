"""
Auto-Remediation Safety Checks - Safety check implementations and management
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from .models import SafetyCheck, SafetyLevel
from infradsl.core.nexus.base_resource import BaseResource, ResourceState

logger = logging.getLogger(__name__)


class SafetyCheckManager:
    """Manager for safety checks"""
    
    def __init__(self):
        self.safety_checks: Dict[str, SafetyCheck] = {}
        self._setup_default_safety_checks()
    
    def add_safety_check(self, safety_check: SafetyCheck):
        """Add a safety check"""
        self.safety_checks[safety_check.name] = safety_check
        logger.info(f"Added safety check: {safety_check.name}")
    
    def get_safety_checks(self) -> Dict[str, SafetyCheck]:
        """Get all safety checks"""
        return self.safety_checks
    
    def _setup_default_safety_checks(self):
        """Setup default safety checks"""

        # Production environment check
        def check_production_environment(
            resource: BaseResource, context: Dict[str, Any]
        ) -> bool:
            """Check if resource is in production environment"""
            return resource.metadata.environment != "production"

        self.add_safety_check(
            SafetyCheck(
                name="production_environment",
                description="Ensure production resources require manual approval",
                check_function=check_production_environment,
                severity=SafetyLevel.CRITICAL,
            )
        )

        # Critical resource check
        def check_critical_resource(
            resource: BaseResource, context: Dict[str, Any]
        ) -> bool:
            """Check if resource is marked as critical"""
            labels = resource.metadata.labels or {}
            return labels.get("tier") != "critical"

        self.add_safety_check(
            SafetyCheck(
                name="critical_resource",
                description="Ensure critical resources require manual approval",
                check_function=check_critical_resource,
                severity=SafetyLevel.HIGH,
            )
        )

        # Business hours check
        def check_business_hours(
            resource: BaseResource, context: Dict[str, Any]
        ) -> bool:
            """Check if current time is within business hours"""
            now = datetime.now(timezone.utc)
            # Business hours: 9 AM to 5 PM UTC, Monday to Friday
            weekday = now.weekday()  # 0-6, Monday is 0
            hour = now.hour

            return weekday < 5 and 9 <= hour < 17  # Monday-Friday, 9 AM to 5 PM

        self.add_safety_check(
            SafetyCheck(
                name="business_hours",
                description="Ensure changes are made during business hours",
                check_function=check_business_hours,
                severity=SafetyLevel.MEDIUM,
            )
        )

        # Resource state check
        def check_resource_state(
            resource: BaseResource, context: Dict[str, Any]
        ) -> bool:
            """Check if resource is in a stable state"""
            return resource.status.state in [
                ResourceState.ACTIVE,
                ResourceState.DRIFTED,
            ]

        self.add_safety_check(
            SafetyCheck(
                name="resource_state",
                description="Ensure resource is in a stable state",
                check_function=check_resource_state,
                severity=SafetyLevel.HIGH,
            )
        )