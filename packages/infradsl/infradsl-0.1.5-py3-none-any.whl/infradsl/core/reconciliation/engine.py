"""
Self-Healing Engine for InfraDSL

This module implements the core self-healing engine that monitors infrastructure
drift and automatically applies reconciliation policies to maintain desired state.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from enum import Enum

from .policies import (
    ReconciliationPolicy,
    DriftEvent,
    DriftSeverity,
    ReconciliationTrigger,
    ReconciliationResult,
    create_default_policies,
)
from ..interfaces.provider import ProviderInterface
from ..nexus.base_resource import ResourceMetadata
from ..discovery.integration import get_discovery_integration
from ..cache import get_cache_manager


logger = logging.getLogger(__name__)


class EngineStatus(Enum):
    """Status of the self-healing engine"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class EngineConfig:
    """Configuration for the self-healing engine"""

    # Monitoring settings
    check_interval_seconds: int = 300  # 5 minutes
    drift_detection_enabled: bool = True
    health_check_enabled: bool = True

    # Reconciliation settings
    auto_remediation_enabled: bool = True
    max_concurrent_reconciliations: int = 5
    reconciliation_timeout_seconds: int = 300

    # Filtering
    monitored_projects: Optional[Set[str]] = None
    monitored_environments: Optional[Set[str]] = None
    monitored_resource_types: Optional[Set[str]] = None

    # Notifications
    notification_enabled: bool = True
    notification_rate_limit_minutes: int = 30

    # Persistence
    persist_events: bool = True
    event_retention_days: int = 30


class SelfHealingEngine:
    """
    Self-healing engine that monitors infrastructure and applies reconciliation policies
    """

    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.status = EngineStatus.STOPPED
        self.policies: List[ReconciliationPolicy] = []
        self.providers: Dict[str, ProviderInterface] = {}
        self.notifiers: List[Callable] = []

        # Runtime state
        self._monitoring_task: Optional[asyncio.Task] = None
        self._reconciliation_semaphore = asyncio.Semaphore(
            self.config.max_concurrent_reconciliations
        )
        self._last_notification_time: Dict[str, datetime] = {}

        # Statistics
        self.stats = {
            "checks_performed": 0,
            "drift_events_detected": 0,
            "reconciliations_attempted": 0,
            "reconciliations_successful": 0,
            "notifications_sent": 0,
            "last_check_time": None,
            "uptime_start": None,
        }

        # Event storage
        self.recent_events: List[DriftEvent] = []
        self.recent_results: List[ReconciliationResult] = []

        # Initialize discovery integration
        self.discovery_integration = get_discovery_integration()
        self.cache_manager = get_cache_manager()

    def add_policy(self, policy: ReconciliationPolicy) -> None:
        """Add a reconciliation policy"""
        self.policies.append(policy)
        logger.info(f"Added reconciliation policy: {policy.name}")

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a reconciliation policy by name"""
        original_count = len(self.policies)
        self.policies = [p for p in self.policies if p.name != policy_name]
        removed = len(self.policies) < original_count

        if removed:
            logger.info(f"Removed reconciliation policy: {policy_name}")

        return removed

    def register_provider(self, name: str, provider: ProviderInterface) -> None:
        """Register a provider for monitoring"""
        self.providers[name] = provider
        logger.info(f"Registered provider for self-healing: {name}")

    def add_notifier(self, notifier: Callable) -> None:
        """Add a notification callback"""
        self.notifiers.append(notifier)
        logger.info("Added notification callback")

    async def start(self) -> None:
        """Start the self-healing engine"""
        if self.status != EngineStatus.STOPPED:
            logger.warning(f"Engine already {self.status.value}")
            return

        self.status = EngineStatus.STARTING
        logger.info("Starting self-healing engine")

        # Load default policies if none configured
        if not self.policies:
            self.policies = create_default_policies()
            logger.info(f"Loaded {len(self.policies)} default reconciliation policies")

        # Initialize discovery integration
        self.discovery_integration.initialize()

        # Start monitoring
        self.status = EngineStatus.RUNNING
        self.stats["uptime_start"] = datetime.now(timezone.utc)

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Self-healing engine started successfully")

    async def stop(self) -> None:
        """Stop the self-healing engine"""
        if self.status == EngineStatus.STOPPED:
            return

        self.status = EngineStatus.STOPPING
        logger.info("Stopping self-healing engine")

        # Cancel monitoring task
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        self.status = EngineStatus.STOPPED
        logger.info("Self-healing engine stopped")

    async def pause(self) -> None:
        """Pause the self-healing engine"""
        if self.status == EngineStatus.RUNNING:
            self.status = EngineStatus.PAUSED
            logger.info("Self-healing engine paused")

    async def resume(self) -> None:
        """Resume the self-healing engine"""
        if self.status == EngineStatus.PAUSED:
            self.status = EngineStatus.RUNNING
            logger.info("Self-healing engine resumed")

    async def force_check(
        self,
        project: Optional[str] = None,
        environment: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[DriftEvent]:
        """Force an immediate drift check"""
        logger.info("Starting forced drift check")

        # Discover resources
        resources = await self._discover_resources(project, environment, resource_type)

        # Check for drift
        drift_events = []
        for resource in resources:
            events = await self._check_resource_drift(resource)
            drift_events.extend(events)

        logger.info(f"Force check completed: {len(drift_events)} drift events detected")
        return drift_events

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self.status == EngineStatus.RUNNING:
            try:
                # Check if paused
                if self.status == EngineStatus.PAUSED:
                    await asyncio.sleep(10)
                    continue

                # Perform monitoring check
                await self._perform_monitoring_check()

                # Update stats
                self.stats["checks_performed"] += 1
                self.stats["last_check_time"] = datetime.now(timezone.utc)

                # Wait for next check
                await asyncio.sleep(self.config.check_interval_seconds)

            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                self.status = EngineStatus.ERROR
                await asyncio.sleep(60)  # Wait before retrying

    async def _perform_monitoring_check(self) -> None:
        """Perform a single monitoring check"""
        logger.debug("Performing monitoring check")

        try:
            # Discover resources
            resources = await self._discover_resources()

            # Check each resource for drift
            drift_events = []
            for resource in resources:
                events = await self._check_resource_drift(resource)
                drift_events.extend(events)

            # Update statistics
            self.stats["drift_events_detected"] += len(drift_events)

            # Process drift events
            if drift_events:
                await self._process_drift_events(drift_events)

            # Clean up old events
            self._cleanup_old_events()

        except Exception as e:
            logger.error(f"Error during monitoring check: {e}")
            raise

    async def _discover_resources(
        self,
        project: Optional[str] = None,
        environment: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Discover resources for monitoring"""

        # Use discovery integration for efficient resource discovery
        if project and environment:
            return await self.discovery_integration.discover_for_monitoring(
                project=project,
                environment=environment,
                max_age_minutes=self.config.check_interval_seconds // 60,
            )
        elif resource_type:
            return await self.discovery_integration.discover_specific_resources(
                resource_types=[resource_type], project=project, environment=environment
            )
        else:
            # Comprehensive discovery
            return await self.discovery_integration.discover_comprehensive()

    async def _check_resource_drift(self, resource: Dict[str, Any]) -> List[DriftEvent]:
        """Check a single resource for drift"""
        drift_events = []

        try:
            # Get current state from provider
            provider_name = resource.get("provider")
            if provider_name not in self.providers:
                logger.debug(f"No provider registered for {provider_name}")
                return drift_events

            provider = self.providers[provider_name]
            resource_id = resource.get("cloud_id")
            resource_type = resource.get("type")

            # Validate required parameters
            if not resource_id or not resource_type:
                logger.debug(
                    f"Missing resource_id or resource_type for {resource.get('name', 'unknown')}"
                )
                return drift_events

            # Get current state
            current_state = provider.get_resource(str(resource_id), str(resource_type))
            if not current_state:
                # Resource not found - might be deleted
                drift_events.append(
                    self._create_drift_event(
                        resource=resource,
                        drift_type="resource_deleted",
                        severity=DriftSeverity.HIGH,
                        current_state={},
                        desired_state=resource.get("configuration", {}),
                        diff={"status": {"old": "active", "new": "deleted"}},
                    )
                )
                return drift_events

            # Compare states
            desired_state = resource.get("configuration", {})
            diff = self._calculate_drift(desired_state, current_state)

            if diff:
                # Determine drift severity
                severity = self._assess_drift_severity(diff, str(resource_type))

                drift_events.append(
                    self._create_drift_event(
                        resource=resource,
                        drift_type="configuration_drift",
                        severity=severity,
                        current_state=current_state,
                        desired_state=desired_state,
                        diff=diff,
                    )
                )

            # Health check
            if self.config.health_check_enabled:
                health_events = await self._check_resource_health(resource, provider)
                drift_events.extend(health_events)

        except Exception as e:
            logger.error(
                f"Error checking drift for {resource.get('name', 'unknown')}: {e}"
            )

            # Create error event
            drift_events.append(
                self._create_drift_event(
                    resource=resource,
                    drift_type="health_check_failed",
                    severity=DriftSeverity.MEDIUM,
                    current_state={"error": str(e)},
                    desired_state={"healthy": True},
                    diff={"health_status": {"old": "unknown", "new": "error"}},
                )
            )

        return drift_events

    def _calculate_drift(
        self, desired: Dict[str, Any], current: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate drift between desired and current state"""
        diff = {}

        # Check for changes in desired fields
        for key, desired_value in desired.items():
            current_value = current.get(key)

            if current_value != desired_value:
                diff[key] = {
                    "desired": desired_value,
                    "current": current_value,
                    "old": current_value,
                    "new": desired_value,
                }

        return diff

    def _assess_drift_severity(
        self, diff: Dict[str, Any], resource_type: str
    ) -> DriftSeverity:
        """Assess the severity of detected drift"""

        # Critical fields that indicate high severity
        critical_fields = {
            "security_groups",
            "firewall_rules",
            "network_access",
            "encryption",
            "backup_enabled",
            "monitoring_enabled",
        }

        # High severity fields
        high_severity_fields = {
            "size",
            "machine_type",
            "instance_type",
            "disk_size",
            "region",
            "zone",
            "image",
            "version",
        }

        # Medium severity fields
        medium_severity_fields = {"tags", "labels", "description", "name"}

        # Check for critical drift
        if any(field in diff for field in critical_fields):
            return DriftSeverity.CRITICAL

        # Check for high severity drift
        if any(field in diff for field in high_severity_fields):
            return DriftSeverity.HIGH

        # Check for medium severity drift
        if any(field in diff for field in medium_severity_fields):
            return DriftSeverity.MEDIUM

        # Default to low severity
        return DriftSeverity.LOW

    async def _check_resource_health(
        self, resource: Dict[str, Any], provider: ProviderInterface
    ) -> List[DriftEvent]:
        """Check resource health"""
        health_events = []

        try:
            # Basic health check - verify provider connectivity
            is_healthy = provider.health_check()

            if not is_healthy:
                health_events.append(
                    self._create_drift_event(
                        resource=resource,
                        drift_type="health_check_failed",
                        severity=DriftSeverity.MEDIUM,
                        current_state={"healthy": False},
                        desired_state={"healthy": True},
                        diff={"health_status": {"old": "healthy", "new": "unhealthy"}},
                    )
                )

        except Exception as e:
            logger.error(
                f"Health check failed for {resource.get('name', 'unknown')}: {e}"
            )

        return health_events

    def _create_drift_event(
        self,
        resource: Dict[str, Any],
        drift_type: str,
        severity: DriftSeverity,
        current_state: Dict[str, Any],
        desired_state: Dict[str, Any],
        diff: Dict[str, Any],
    ) -> DriftEvent:
        """Create a drift event"""

        # Extract metadata
        metadata = ResourceMetadata(
            id=resource.get("id", ""),
            name=resource.get("name", ""),
            project=resource.get("project", ""),
            environment=resource.get("environment", ""),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return DriftEvent(
            resource_id=resource.get("cloud_id", ""),
            resource_type=resource.get("type", ""),
            resource_name=resource.get("name", ""),
            provider=resource.get("provider", ""),
            project=resource.get("project", ""),
            environment=resource.get("environment", ""),
            drift_type=drift_type,
            severity=severity,
            trigger=ReconciliationTrigger.DRIFT_DETECTED,
            detected_at=datetime.now(timezone.utc),
            desired_state=desired_state,
            current_state=current_state,
            diff=diff,
            metadata=metadata,
            tags=resource.get("tags", {}),
            previous_events=[],
            failure_count=0,
        )

    async def _process_drift_events(self, drift_events: List[DriftEvent]) -> None:
        """Process detected drift events"""
        for event in drift_events:
            # Store event
            self.recent_events.append(event)

            # Apply reconciliation policies
            if self.config.auto_remediation_enabled:
                await self._apply_reconciliation_policies(event)

    async def _apply_reconciliation_policies(self, event: DriftEvent) -> None:
        """Apply reconciliation policies to a drift event"""
        async with self._reconciliation_semaphore:
            try:
                # Find applicable policies
                applicable_policies = [
                    policy for policy in self.policies if policy.can_trigger(event)
                ]

                if not applicable_policies:
                    logger.debug(f"No policies applicable for {event.resource_name}")
                    return

                # Apply first applicable policy
                policy = applicable_policies[0]
                logger.info(f"Applying policy {policy.name} to {event.resource_name}")

                # Get provider
                provider = self.providers.get(event.provider)
                if not provider:
                    logger.error(f"No provider available for {event.provider}")
                    return

                # Create notifier
                notifier = self._create_notifier(event)

                # Execute policy
                result = await asyncio.wait_for(
                    policy.execute(event, provider, notifier),
                    timeout=self.config.reconciliation_timeout_seconds,
                )

                # Store result
                self.recent_results.append(result)

                # Update statistics
                self.stats["reconciliations_attempted"] += 1
                if result.success:
                    self.stats["reconciliations_successful"] += 1

                logger.info(f"Reconciliation completed: {result.message}")

            except asyncio.TimeoutError:
                logger.error(f"Reconciliation timeout for {event.resource_name}")
            except Exception as e:
                logger.error(f"Error applying reconciliation policies: {e}")

    def _create_notifier(self, event: DriftEvent) -> Optional[Callable]:
        """Create a notifier function for the event"""
        if not self.config.notification_enabled or not self.notifiers:
            return None

        # Rate limiting
        rate_limit_key = f"{event.resource_id}:{event.drift_type}"
        last_notification = self._last_notification_time.get(rate_limit_key)

        if last_notification and datetime.now(
            timezone.utc
        ) - last_notification < timedelta(
            minutes=self.config.notification_rate_limit_minutes
        ):
            return None

        async def notifier(message: str) -> None:
            # Send to all registered notifiers
            for notify_func in self.notifiers:
                try:
                    await notify_func(message)
                    self.stats["notifications_sent"] += 1
                except Exception as e:
                    logger.error(f"Notification failed: {e}")

            # Update rate limiting
            self._last_notification_time[rate_limit_key] = datetime.now(timezone.utc)

        return notifier

    def _cleanup_old_events(self) -> None:
        """Clean up old events and results"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(
            days=self.config.event_retention_days
        )

        # Clean up events
        self.recent_events = [
            event for event in self.recent_events if event.detected_at > cutoff_time
        ]

        # Clean up results
        self.recent_results = [
            result for result in self.recent_results if result.timestamp > cutoff_time
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        uptime = None
        if self.stats["uptime_start"]:
            uptime = (
                datetime.now(timezone.utc) - self.stats["uptime_start"]
            ).total_seconds()

        return {
            "status": self.status.value,
            "uptime_seconds": uptime,
            "stats": self.stats.copy(),
            "policies": [
                {
                    "name": policy.name,
                    "description": policy.description,
                    "enabled": policy.enabled,
                    "trigger_count": policy.trigger_count,
                    "last_triggered": (
                        policy.last_triggered.isoformat()
                        if policy.last_triggered
                        else None
                    ),
                }
                for policy in self.policies
            ],
            "providers": list(self.providers.keys()),
            "recent_events": len(self.recent_events),
            "recent_results": len(self.recent_results),
        }

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent drift events"""
        events = sorted(self.recent_events, key=lambda e: e.detected_at, reverse=True)
        return [
            {
                "resource_name": event.resource_name,
                "resource_type": event.resource_type,
                "provider": event.provider,
                "project": event.project,
                "environment": event.environment,
                "drift_type": event.drift_type,
                "severity": event.severity.value,
                "detected_at": event.detected_at.isoformat(),
                "diff": event.diff,
            }
            for event in events[:limit]
        ]

    def get_recent_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent reconciliation results"""
        results = sorted(self.recent_results, key=lambda r: r.timestamp, reverse=True)
        return [
            {
                "action": result.action.value,
                "success": result.success,
                "message": result.message,
                "timestamp": result.timestamp.isoformat(),
                "duration": result.duration,
                "details": result.details,
            }
            for result in results[:limit]
        ]


# Global self-healing engine instance
_self_healing_engine = None


def get_self_healing_engine() -> SelfHealingEngine:
    """Get the global self-healing engine instance"""
    global _self_healing_engine
    if _self_healing_engine is None:
        _self_healing_engine = SelfHealingEngine()
    return _self_healing_engine
