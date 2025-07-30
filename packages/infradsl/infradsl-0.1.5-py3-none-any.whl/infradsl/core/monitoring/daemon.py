"""
Drift Monitoring Daemon - Continuous infrastructure drift monitoring

This module implements the DriftMonitoringDaemon class that provides
continuous monitoring of infrastructure drift with configurable intervals
and intelligent caching.
"""

import asyncio
import logging
import signal
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
import uuid
import json

from infradsl.core.nexus import NexusEngine
from infradsl.core.nexus.base_resource import BaseResource, ResourceState
from infradsl.core.cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class DaemonState(Enum):
    """Daemon state enumeration"""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"


class MonitoringPolicy:
    """Policy for monitoring specific resources or resource types"""

    def __init__(
        self,
        name: str,
        resource_filter: Optional[Dict[str, Any]] = None,
        check_interval: int = 300,  # 5 minutes
        priority: str = "medium",
        auto_remediate: bool = False,
        notification_channels: Optional[List[str]] = None,
    ):
        self.name = name
        self.resource_filter = resource_filter or {}
        self.check_interval = check_interval
        self.priority = priority
        self.auto_remediate = auto_remediate
        self.notification_channels = notification_channels or []
        self.last_check: Optional[datetime] = None
        self.check_count = 0
        self.drift_count = 0


class DriftResult:
    """Result of a drift check operation"""

    def __init__(
        self,
        resource_id: str,
        resource_name: str,
        resource_type: str,
        drift_detected: bool,
        drift_details: Optional[Dict[str, Any]] = None,
        check_timestamp: Optional[datetime] = None,
        policy_name: Optional[str] = None,
    ):
        self.resource_id = resource_id
        self.resource_name = resource_name
        self.resource_type = resource_type
        self.drift_detected = drift_detected
        self.drift_details = drift_details or {}
        self.check_timestamp = check_timestamp or datetime.now(timezone.utc)
        self.policy_name = policy_name


class DriftMonitoringDaemon:
    """
    Continuous drift monitoring daemon with configurable intervals
    and intelligent caching.
    """

    def __init__(
        self,
        nexus_engine: Optional[NexusEngine] = None,
        cache_manager: Optional[CacheManager] = None,
        default_interval: int = 300,  # 5 minutes
        max_concurrent_checks: int = 10,
        enable_intelligent_caching: bool = True,
        cache_ttl: int = 3600,  # 1 hour
    ):
        """
        Initialize the drift monitoring daemon

        Args:
            nexus_engine: NexusEngine instance for resource operations
            cache_manager: Cache manager for intelligent caching
            default_interval: Default monitoring interval in seconds
            max_concurrent_checks: Maximum concurrent drift checks
            enable_intelligent_caching: Enable intelligent caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.nexus_engine = nexus_engine or NexusEngine()
        self.cache_manager = cache_manager
        self.default_interval = default_interval
        self.max_concurrent_checks = max_concurrent_checks
        self.enable_intelligent_caching = enable_intelligent_caching
        self.cache_ttl = cache_ttl

        # Daemon state
        self.state = DaemonState.STOPPED
        self.start_time: Optional[datetime] = None
        self.last_full_check: Optional[datetime] = None

        # Monitoring configuration
        self.policies: Dict[str, MonitoringPolicy] = {}
        self.resource_schedules: Dict[str, datetime] = {}
        self.drift_history: List[DriftResult] = []

        # Event handlers
        self.drift_detected_handlers: List[Callable[[DriftResult], None]] = []
        self.check_completed_handlers: List[Callable[[List[DriftResult]], None]] = []
        self.daemon_state_handlers: List[Callable[[DaemonState], None]] = []

        # Async control
        self._main_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._pause_event = asyncio.Event()
        self._check_semaphore = asyncio.Semaphore(max_concurrent_checks)

        # Statistics
        self.stats = {
            "total_checks": 0,
            "drift_detected": 0,
            "last_check_duration": 0,
            "average_check_duration": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Setup signal handlers
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        try:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
        except ValueError:
            # Signals not available (e.g., in some test environments)
            pass

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self.stop())

    def add_policy(self, policy: MonitoringPolicy):
        """Add a monitoring policy"""
        self.policies[policy.name] = policy
        logger.info(f"Added monitoring policy: {policy.name}")

    def remove_policy(self, policy_name: str):
        """Remove a monitoring policy"""
        if policy_name in self.policies:
            del self.policies[policy_name]
            logger.info(f"Removed monitoring policy: {policy_name}")

    def add_drift_detected_handler(self, handler: Callable[[DriftResult], None]):
        """Add a drift detected event handler"""
        self.drift_detected_handlers.append(handler)

    def add_check_completed_handler(self, handler: Callable[[List[DriftResult]], None]):
        """Add a check completed event handler"""
        self.check_completed_handlers.append(handler)

    def add_daemon_state_handler(self, handler: Callable[[DaemonState], None]):
        """Add a daemon state change handler"""
        self.daemon_state_handlers.append(handler)

    def _set_state(self, new_state: DaemonState):
        """Set daemon state and notify handlers"""
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            logger.info(f"Daemon state changed: {old_state.value} -> {new_state.value}")

            # Notify handlers
            for handler in self.daemon_state_handlers:
                try:
                    handler(new_state)
                except Exception as e:
                    logger.error(f"Error in daemon state handler: {e}")

    async def start(self):
        """Start the monitoring daemon"""
        if self.state != DaemonState.STOPPED:
            logger.warning("Daemon is already running or starting")
            return

        self._set_state(DaemonState.STARTING)

        # Clear shutdown event
        self._shutdown_event.clear()
        self._pause_event.clear()

        # Set start time
        self.start_time = datetime.now(timezone.utc)

        # Start the main monitoring loop
        self._main_task = asyncio.create_task(self._monitoring_loop())

        self._set_state(DaemonState.RUNNING)
        logger.info("Drift monitoring daemon started successfully")

    async def stop(self, timeout: int = 30):
        """Stop the monitoring daemon"""
        if self.state == DaemonState.STOPPED:
            logger.info("Daemon is already stopped")
            return

        self._set_state(DaemonState.STOPPING)

        # Signal shutdown
        self._shutdown_event.set()

        # Wait for the main task to complete
        if self._main_task:
            try:
                await asyncio.wait_for(self._main_task, timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning("Daemon shutdown timed out, forcing termination")
                self._main_task.cancel()
                try:
                    await self._main_task
                except asyncio.CancelledError:
                    pass

        self._set_state(DaemonState.STOPPED)
        logger.info("Drift monitoring daemon stopped")

    async def pause(self):
        """Pause the monitoring daemon"""
        if self.state != DaemonState.RUNNING:
            logger.warning("Daemon is not running, cannot pause")
            return

        self._set_state(DaemonState.PAUSED)
        self._pause_event.set()
        logger.info("Drift monitoring daemon paused")

    async def resume(self):
        """Resume the monitoring daemon"""
        if self.state != DaemonState.PAUSED:
            logger.warning("Daemon is not paused, cannot resume")
            return

        self._set_state(DaemonState.RUNNING)
        self._pause_event.clear()
        logger.info("Drift monitoring daemon resumed")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop")

        try:
            while not self._shutdown_event.is_set():
                # Check if paused
                if self._pause_event.is_set():
                    await asyncio.sleep(1)
                    continue

                # Perform monitoring cycle
                await self._perform_monitoring_cycle()

                # Wait for the next cycle
                await asyncio.sleep(1)  # Small sleep to prevent busy waiting

        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            raise
        finally:
            logger.info("Monitoring loop ended")

    async def _perform_monitoring_cycle(self):
        """Perform one monitoring cycle"""
        current_time = datetime.now(timezone.utc)

        # Collect resources that need checking
        resources_to_check = []

        # Check if we need a full check (no policies defined)
        if not self.policies:
            if (
                not self.last_full_check
                or current_time - self.last_full_check
                >= timedelta(seconds=self.default_interval)
            ):
                resources_to_check.extend(self.nexus_engine._registry.list_all())
                self.last_full_check = current_time
        else:
            # Check resources based on policies
            for policy_name, policy in self.policies.items():
                if (
                    not policy.last_check
                    or current_time - policy.last_check
                    >= timedelta(seconds=policy.check_interval)
                ):
                    # Get resources matching policy filter
                    matching_resources = self._get_resources_for_policy(policy)
                    resources_to_check.extend(matching_resources)

                    # Update policy last check time
                    policy.last_check = current_time

        # Perform drift checks
        if resources_to_check:
            start_time = time.time()

            # Remove duplicates
            unique_resources = {r.metadata.id: r for r in resources_to_check}

            # Perform concurrent checks
            drift_results = await self._check_resources_for_drift(
                list(unique_resources.values())
            )

            # Update statistics
            check_duration = time.time() - start_time
            self.stats["total_checks"] += len(unique_resources)
            self.stats["last_check_duration"] = check_duration
            self.stats["average_check_duration"] = (
                self.stats["average_check_duration"]
                * (self.stats["total_checks"] - len(unique_resources))
                + check_duration
            ) / self.stats["total_checks"]

            # Process results
            await self._process_drift_results(drift_results)

    def _get_resources_for_policy(self, policy: MonitoringPolicy) -> List[BaseResource]:
        """Get resources matching a policy filter"""
        all_resources = self.nexus_engine._registry.list_all()
        matching_resources = []

        for resource in all_resources:
            if self._resource_matches_filter(resource, policy.resource_filter):
                matching_resources.append(resource)

        return matching_resources

    def _resource_matches_filter(
        self, resource: BaseResource, filter_dict: Dict[str, Any]
    ) -> bool:
        """Check if a resource matches a filter"""
        if not filter_dict:
            return True

        # Check a resource type
        if "type" in filter_dict:
            if resource.__class__.__name__ != filter_dict["type"]:
                return False

        # Check provider
        if "provider" in filter_dict:
            if getattr(resource, "provider", None) != filter_dict["provider"]:
                return False

        # Check a project
        if "project" in filter_dict:
            if resource.metadata.project != filter_dict["project"]:
                return False

        # Check environment
        if "environment" in filter_dict:
            if resource.metadata.environment != filter_dict["environment"]:
                return False

        # Check labels
        if "labels" in filter_dict:
            resource_labels = resource.metadata.labels or {}
            for key, value in filter_dict["labels"].items():
                if resource_labels.get(key) != value:
                    return False

        return True

    async def _check_resources_for_drift(
        self, resources: List[BaseResource]
    ) -> List[DriftResult]:
        """Check multiple resources for drift concurrently"""
        drift_results = []

        # Create semaphore-limited tasks
        tasks = []
        for resource in resources:
            task = asyncio.create_task(self._check_single_resource_drift(resource))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Error checking drift for resource {resources[i].name}: {result}"
                )
                # Create error result
                drift_results.append(
                    DriftResult(
                        resource_id=resources[i].metadata.id,
                        resource_name=resources[i].name,
                        resource_type=resources[i].__class__.__name__,
                        drift_detected=False,
                        drift_details={"error": str(result)},
                    )
                )
            else:
                drift_results.append(result)

        return drift_results

    async def _check_single_resource_drift(self, resource: BaseResource) -> DriftResult:
        """Check a single resource for drift"""
        async with self._check_semaphore:
            # Check cache first
            if self.enable_intelligent_caching and self.cache_manager:
                cache_key = f"drift_check:{resource.metadata.id}"
                cached_result = self.cache_manager.get(cache_key)

                if cached_result:
                    self.stats["cache_hits"] += 1
                    return DriftResult(
                        resource_id=resource.metadata.id,
                        resource_name=resource.name,
                        resource_type=resource.__class__.__name__,
                        drift_detected=cached_result.get("drift_detected", False),
                        drift_details=cached_result.get("drift_details", {}),
                        check_timestamp=datetime.fromisoformat(
                            cached_result.get(
                                "timestamp", datetime.now(timezone.utc).isoformat()
                            )
                        ),
                    )
                else:
                    self.stats["cache_misses"] += 1

            # Perform actual drift check
            try:
                if hasattr(resource, "check_drift"):
                    drift_detected = await resource.check_drift()
                else:
                    # Default drift check based on resource state
                    drift_detected = resource.state == ResourceState.DRIFTED

                # Get drift details if available
                drift_details = {}
                if hasattr(resource, "get_drift_details"):
                    drift_details = await resource.get_drift_details()

                result = DriftResult(
                    resource_id=resource.metadata.id,
                    resource_name=resource.name,
                    resource_type=resource.__class__.__name__,
                    drift_detected=drift_detected,
                    drift_details=drift_details,
                )

                # Cache the result
                if self.enable_intelligent_caching and self.cache_manager:
                    try:
                        cache_data = {
                            "drift_detected": drift_detected,
                            "drift_details": drift_details,
                            "timestamp": result.check_timestamp.isoformat(),
                        }
                        self.cache_manager.set(
                            cache_key, cache_data, ttl=self.cache_ttl
                        )
                    except Exception as e:
                        logger.warning(
                            f"Cache set error for {resource.metadata.id}: {e}"
                        )

                return result

            except Exception as e:
                logger.error(f"Error checking drift for resource {resource.name}: {e}")
                return DriftResult(
                    resource_id=resource.metadata.id,
                    resource_name=resource.name,
                    resource_type=resource.__class__.__name__,
                    drift_detected=False,
                    drift_details={"error": str(e)},
                )

    async def _process_drift_results(self, drift_results: List[DriftResult]):
        """Process drift check results"""
        # Update statistics
        drift_count = sum(1 for r in drift_results if r.drift_detected)
        self.stats["drift_detected"] += drift_count

        # Add to history
        self.drift_history.extend(drift_results)

        # Keep only recent history (last 1000 entries)
        if len(self.drift_history) > 1000:
            self.drift_history = self.drift_history[-1000:]

        # Notify handlers
        for result in drift_results:
            if result.drift_detected:
                for handler in self.drift_detected_handlers:
                    try:
                        handler(result)
                    except Exception as e:
                        logger.error(f"Error in drift detected handler: {e}")

        # Notify check completed handlers
        for handler in self.check_completed_handlers:
            try:
                handler(drift_results)
            except Exception as e:
                logger.error(f"Error in check completed handler: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status"""
        uptime = None
        if self.start_time:
            uptime = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        return {
            "state": self.state.value,
            "uptime": uptime,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_full_check": (
                self.last_full_check.isoformat() if self.last_full_check else None
            ),
            "policies": {
                name: {
                    "check_interval": policy.check_interval,
                    "last_check": (
                        policy.last_check.isoformat() if policy.last_check else None
                    ),
                    "check_count": policy.check_count,
                    "drift_count": policy.drift_count,
                    "auto_remediate": policy.auto_remediate,
                }
                for name, policy in self.policies.items()
            },
            "statistics": self.stats.copy(),
            "drift_history_count": len(self.drift_history),
        }

    def get_drift_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent drift history"""
        recent_history = (
            self.drift_history[-limit:] if limit > 0 else self.drift_history
        )

        return [
            {
                "resource_id": result.resource_id,
                "resource_name": result.resource_name,
                "resource_type": result.resource_type,
                "drift_detected": result.drift_detected,
                "drift_details": result.drift_details,
                "check_timestamp": result.check_timestamp.isoformat(),
                "policy_name": result.policy_name,
            }
            for result in recent_history
        ]

    async def force_check(self, resource_id: Optional[str] = None) -> List[DriftResult]:
        """Force an immediate drift check"""
        if resource_id:
            # Check specific resource
            resource = self.nexus_engine._registry.get(resource_id)
            if not resource:
                raise ValueError(f"Resource {resource_id} not found")

            result = await self._check_single_resource_drift(resource)
            await self._process_drift_results([result])
            return [result]
        else:
            # Check all resources
            resources = self.nexus_engine._registry.list_all()
            results = await self._check_resources_for_drift(resources)
            await self._process_drift_results(results)
            return results

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.stop()
