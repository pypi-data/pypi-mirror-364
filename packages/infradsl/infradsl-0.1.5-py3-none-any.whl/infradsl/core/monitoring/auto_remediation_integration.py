"""
Auto-Remediation Integration - Connects drift monitoring with auto-remediation

This module integrates the drift monitoring daemon with the auto-remediation
engine to provide seamless automated infrastructure healing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone

from .daemon import DriftMonitoringDaemon, DriftResult, MonitoringPolicy
from .auto_remediation import AutoRemediationEngine, SafetyLevel, RemediationRequest
from .notifications import NotificationManager
from infradsl.core.nexus import NexusEngine

logger = logging.getLogger(__name__)


class AutoRemediationIntegration:
    """
    Integration between drift monitoring and auto-remediation systems
    """
    
    def __init__(
        self,
        drift_daemon: Optional[DriftMonitoringDaemon] = None,
        remediation_engine: Optional[AutoRemediationEngine] = None,
        notification_manager: Optional[NotificationManager] = None,
        nexus_engine: Optional[NexusEngine] = None,
        auto_remediation_enabled: bool = True,
        auto_approval_enabled: bool = False,
    ):
        """
        Initialize the integration
        
        Args:
            drift_daemon: Drift monitoring daemon
            remediation_engine: Auto-remediation engine
            notification_manager: Notification manager
            nexus_engine: Nexus engine
            auto_remediation_enabled: Enable automatic remediation
            auto_approval_enabled: Enable automatic approval for low-risk actions
        """
        self.nexus_engine = nexus_engine or NexusEngine()
        self.notification_manager = notification_manager or NotificationManager()
        
        self.drift_daemon = drift_daemon or DriftMonitoringDaemon(
            nexus_engine=self.nexus_engine,
            enable_intelligent_caching=False  # Disable caching for demo
        )
        
        self.remediation_engine = remediation_engine or AutoRemediationEngine(
            nexus_engine=self.nexus_engine,
            notification_manager=self.notification_manager,
            enable_auto_approval=auto_approval_enabled,
        )
        
        self.auto_remediation_enabled = auto_remediation_enabled
        self.auto_approval_enabled = auto_approval_enabled
        
        # Statistics
        self.stats = {
            "drift_events_processed": 0,
            "remediation_requests_created": 0,
            "auto_approved_requests": 0,
            "manual_requests": 0,
            "integration_errors": 0,
        }
        
        # Setup integration handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup integration event handlers"""
        # Connect drift detection to auto-remediation
        self.drift_daemon.add_drift_detected_handler(self._handle_drift_detected)
        
        # Connect check completion to summary processing
        self.drift_daemon.add_check_completed_handler(self._handle_check_completed)
    
    async def _handle_drift_detected(self, drift_result: DriftResult):
        """Handle drift detected event"""
        try:
            logger.info(f"Processing drift detected: {drift_result.resource_name}")
            
            # Update statistics
            self.stats["drift_events_processed"] += 1
            
            # Check if auto-remediation is enabled
            if not self.auto_remediation_enabled:
                logger.info(f"Auto-remediation disabled for {drift_result.resource_name}")
                return
            
            # Check if resource should be auto-remediated
            if not self._should_auto_remediate(drift_result):
                logger.info(f"Auto-remediation skipped for {drift_result.resource_name}")
                return
            
            # Create remediation request
            request = await self.remediation_engine.request_remediation(
                drift_result=drift_result,
                requested_by="drift-monitoring-daemon",
                force_manual_approval=not self.auto_approval_enabled
            )
            
            # Update statistics
            self.stats["remediation_requests_created"] += 1
            
            logger.info(f"Remediation requested: {request.id} for {drift_result.resource_name}")
            
        except Exception as e:
            logger.error(f"Error handling drift detected: {e}")
            self.stats["integration_errors"] += 1
    
    async def _handle_check_completed(self, drift_results: List[DriftResult]):
        """Handle check completed event"""
        try:
            # Count drift events
            drift_count = sum(1 for r in drift_results if r.drift_detected)
            
            if drift_count > 0:
                logger.info(f"Check completed: {drift_count} drift events detected")
                
                # Process batch remediation if needed
                await self._process_batch_remediation(drift_results)
            
        except Exception as e:
            logger.error(f"Error handling check completed: {e}")
            self.stats["integration_errors"] += 1
    
    def _should_auto_remediate(self, drift_result: DriftResult) -> bool:
        """Check if a drift result should be auto-remediated"""
        
        # Check for error conditions that shouldn't be auto-remediated
        if "error" in drift_result.drift_details:
            logger.info(f"Skipping auto-remediation for error: {drift_result.resource_name}")
            return False
        
        # Check for critical resources
        if "critical" in str(drift_result.drift_details).lower():
            logger.info(f"Skipping auto-remediation for critical resource: {drift_result.resource_name}")
            return False
        
        # Check for production environment
        if hasattr(drift_result, 'environment') and getattr(drift_result, 'environment') == 'production':
            logger.info(f"Skipping auto-remediation for production resource: {drift_result.resource_name}")
            return False
        
        # Check for specific policy settings
        policy_name = getattr(drift_result, 'policy_name', None)
        if policy_name:
            # Find the policy
            policy = self.drift_daemon.policies.get(policy_name)
            if policy and not policy.auto_remediate:
                logger.info(f"Auto-remediation disabled by policy {policy_name}")
                return False
        
        return True
    
    async def _process_batch_remediation(self, drift_results: List[DriftResult]):
        """Process batch remediation for multiple drift results"""
        try:
            # Filter for drift events that should be remediated
            remediable_drifts = [
                r for r in drift_results 
                if r.drift_detected and self._should_auto_remediate(r)
            ]
            
            if not remediable_drifts:
                return
            
            # Group by safety level
            by_safety_level = {}
            for drift in remediable_drifts:
                safety_level = self._assess_safety_level(drift)
                if safety_level not in by_safety_level:
                    by_safety_level[safety_level] = []
                by_safety_level[safety_level].append(drift)
            
            # Process each safety level
            for safety_level, drifts in by_safety_level.items():
                if len(drifts) > 1:
                    logger.info(f"Processing {len(drifts)} {safety_level.value} drift events")
                    
                    # Create batch remediation request
                    await self._create_batch_remediation_request(drifts, safety_level)
                    
        except Exception as e:
            logger.error(f"Error processing batch remediation: {e}")
    
    async def _create_batch_remediation_request(self, drifts: List[DriftResult], safety_level: SafetyLevel):
        """Create a batch remediation request"""
        # For now, process each drift individually
        # In the future, this could be enhanced to handle batches
        for drift in drifts:
            try:
                await self.remediation_engine.request_remediation(
                    drift_result=drift,
                    requested_by="batch-remediation-system",
                    force_manual_approval=safety_level != SafetyLevel.LOW
                )
            except Exception as e:
                logger.error(f"Error creating batch remediation request: {e}")
    
    def _assess_safety_level(self, drift_result: DriftResult) -> SafetyLevel:
        """Assess safety level for a drift result"""
        # Use the remediation engine's assessment
        return self.remediation_engine._assess_safety_level(drift_result)
    
    async def start(self):
        """Start the integration"""
        logger.info("Starting auto-remediation integration...")
        
        # Start drift daemon
        await self.drift_daemon.start()
        
        logger.info("Auto-remediation integration started")
    
    async def stop(self):
        """Stop the integration"""
        logger.info("Stopping auto-remediation integration...")
        
        # Stop drift daemon
        await self.drift_daemon.stop()
        
        logger.info("Auto-remediation integration stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "auto_remediation_enabled": self.auto_remediation_enabled,
            "auto_approval_enabled": self.auto_approval_enabled,
            "drift_daemon_status": self.drift_daemon.get_status(),
            "remediation_engine_stats": self.remediation_engine.get_statistics(),
            "integration_stats": self.stats.copy(),
        }
    
    def enable_auto_remediation(self):
        """Enable auto-remediation"""
        self.auto_remediation_enabled = True
        logger.info("Auto-remediation enabled")
    
    def disable_auto_remediation(self):
        """Disable auto-remediation"""
        self.auto_remediation_enabled = False
        logger.info("Auto-remediation disabled")
    
    def enable_auto_approval(self):
        """Enable auto-approval"""
        self.auto_approval_enabled = True
        self.remediation_engine.enable_auto_approval = True
        logger.info("Auto-approval enabled")
    
    def disable_auto_approval(self):
        """Disable auto-approval"""
        self.auto_approval_enabled = False
        self.remediation_engine.enable_auto_approval = False
        logger.info("Auto-approval disabled")
    
    def add_monitoring_policy(self, policy: MonitoringPolicy):
        """Add monitoring policy to the daemon"""
        self.drift_daemon.add_policy(policy)
        logger.info(f"Added monitoring policy: {policy.name}")
    
    def remove_monitoring_policy(self, policy_name: str):
        """Remove monitoring policy from the daemon"""
        self.drift_daemon.remove_policy(policy_name)
        logger.info(f"Removed monitoring policy: {policy_name}")
    
    async def approve_request(self, request_id: str, approved_by: str) -> bool:
        """Approve a remediation request"""
        return await self.remediation_engine.approve_remediation(request_id, approved_by)
    
    async def reject_request(self, request_id: str, rejected_by: str, reason: str) -> bool:
        """Reject a remediation request"""
        return await self.remediation_engine.reject_remediation(request_id, rejected_by, reason)
    
    async def rollback_request(self, request_id: str, rolled_back_by: str, reason: str) -> bool:
        """Rollback a remediation request"""
        return await self.remediation_engine.rollback_remediation(request_id, rolled_back_by, reason)
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get pending remediation requests"""
        return self.remediation_engine.list_pending_requests()
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific request"""
        return self.remediation_engine.get_request_status(request_id)
    
    async def force_check(self, resource_id: Optional[str] = None) -> List[DriftResult]:
        """Force an immediate drift check"""
        return await self.drift_daemon.force_check(resource_id)


# Global integration instance
_auto_remediation_integration = None


def get_auto_remediation_integration() -> AutoRemediationIntegration:
    """Get the global auto-remediation integration instance"""
    global _auto_remediation_integration
    if _auto_remediation_integration is None:
        _auto_remediation_integration = AutoRemediationIntegration()
    return _auto_remediation_integration


async def setup_auto_remediation_integration(
    enable_auto_remediation: bool = True,
    enable_auto_approval: bool = False,
    monitoring_policies: Optional[List[MonitoringPolicy]] = None,
    notification_config: Optional[Dict[str, Any]] = None,
) -> AutoRemediationIntegration:
    """
    Setup auto-remediation integration
    
    Args:
        enable_auto_remediation: Enable automatic remediation
        enable_auto_approval: Enable automatic approval for low-risk actions
        monitoring_policies: Custom monitoring policies
        notification_config: Notification configuration
    
    Returns:
        Configured AutoRemediationIntegration instance
    """
    integration = AutoRemediationIntegration(
        auto_remediation_enabled=enable_auto_remediation,
        auto_approval_enabled=enable_auto_approval,
    )
    
    # Configure notifications if provided
    if notification_config:
        if "slack_webhook" in notification_config:
            integration.notification_manager.configure_slack(
                notification_config["slack_webhook"]
            )
        
        if "email_config" in notification_config:
            integration.notification_manager.configure_email(
                **notification_config["email_config"]
            )
        
        if "webhook_url" in notification_config:
            integration.notification_manager.configure_webhook(
                notification_config["webhook_url"]
            )
    
    # Add monitoring policies if provided
    if monitoring_policies:
        for policy in monitoring_policies:
            integration.add_monitoring_policy(policy)
    
    # Start the integration
    await integration.start()
    
    return integration