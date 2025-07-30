#!/usr/bin/env python3
"""
Auto-Remediation Demo

This demo shows the comprehensive auto-remediation system with
safety checks, approval workflows, and rollback capabilities.
"""

import asyncio
import json
from datetime import datetime, timezone

from infradsl.core.monitoring import (
    AutoRemediationEngine,
    DriftResult,
    RemediationRequest,
    SafetyCheck,
    ApprovalWorkflow,
    RemediationStatus,
    SafetyLevel,
    AutoRemediationIntegration,
    setup_auto_remediation_integration,
    MonitoringPolicy,
    NotificationManager,
    DriftMonitoringDaemon,
)
from infradsl.core.reconciliation.policies import ReconciliationAction


def demo_basic_auto_remediation():
    """Demo basic auto-remediation engine"""
    print("🔧 Testing basic auto-remediation engine...")
    
    # Create auto-remediation engine
    remediation_engine = AutoRemediationEngine(
        enable_auto_approval=True,
        max_concurrent_remediations=3,
    )
    
    print(f"✅ Created auto-remediation engine")
    print(f"   Safety checks: {len(remediation_engine.safety_checks)}")
    print(f"   Approval workflows: {len(remediation_engine.approval_workflows)}")
    print(f"   Auto-approval enabled: {remediation_engine.enable_auto_approval}")
    
    # Create test drift result
    drift_result = DriftResult(
        resource_id="vm-test-123",
        resource_name="test-vm",
        resource_type="VirtualMachine",
        drift_detected=True,
        drift_details={
            "configuration": {
                "expected": {"instance_type": "t3.medium"},
                "actual": {"instance_type": "t3.small"}
            }
        },
        check_timestamp=datetime.now(timezone.utc),
        policy_name="test_policy"
    )
    
    # Test safety level assessment
    safety_level = remediation_engine._assess_safety_level(drift_result)
    print(f"✅ Safety level assessed: {safety_level.value}")
    
    # Test proposed action determination
    proposed_action = remediation_engine._determine_remediation_action(drift_result)
    print(f"✅ Proposed action: {proposed_action.value}")
    
    # Get statistics
    stats = remediation_engine.get_statistics()
    print(f"📊 Initial stats: {stats}")
    
    return remediation_engine, drift_result


async def demo_remediation_request_workflow():
    """Demo remediation request workflow"""
    print("\n🔄 Testing remediation request workflow...")
    
    # Create remediation engine
    remediation_engine = AutoRemediationEngine(
        enable_auto_approval=True,
        max_concurrent_remediations=2,
    )
    
    # Create test drift results with different safety levels
    drift_results = [
        DriftResult(
            resource_id="vm-dev-001",
            resource_name="development-vm",
            resource_type="VirtualMachine",
            drift_detected=True,
            drift_details={"config": "minor_change"},
            check_timestamp=datetime.now(timezone.utc),
        ),
        DriftResult(
            resource_id="vm-prod-001",
            resource_name="production-vm",
            resource_type="VirtualMachine",
            drift_detected=True,
            drift_details={"security": "firewall_change"},
            check_timestamp=datetime.now(timezone.utc),
        ),
        DriftResult(
            resource_id="db-crit-001",
            resource_name="critical-database",
            resource_type="Database",
            drift_detected=True,
            drift_details={"encryption": "key_rotation_needed"},
            check_timestamp=datetime.now(timezone.utc),
        ),
    ]
    
    # Create remediation requests
    requests = []
    for i, drift_result in enumerate(drift_results):
        request = await remediation_engine.request_remediation(
            drift_result=drift_result,
            requested_by=f"user-{i+1}",
            force_manual_approval=False
        )
        requests.append(request)
        print(f"✅ Created request {request.id}: {request.status.value} (Safety: {request.safety_level.value})")
    
    # Check pending requests
    pending_requests = remediation_engine.list_pending_requests()
    print(f"📋 Pending requests: {len(pending_requests)}")
    
    # Approve some requests
    for i, request in enumerate(requests):
        if request.status == RemediationStatus.PENDING and i < 2:  # Approve first 2
            approved = await remediation_engine.approve_remediation(
                request.id,
                f"manager-{i+1}",
                execute_immediately=True
            )
            print(f"✅ Request {request.id} approved: {approved}")
    
    # Reject one request
    if len(requests) > 2:
        rejected = await remediation_engine.reject_remediation(
            requests[2].id,
            "security-team",
            "Security review required"
        )
        print(f"✅ Request {requests[2].id} rejected: {rejected}")
    
    # Wait for executions to complete
    await asyncio.sleep(3)
    
    # Check final statistics
    stats = remediation_engine.get_statistics()
    print(f"📊 Final stats: {stats}")
    
    return remediation_engine, requests


def demo_custom_safety_checks():
    """Demo custom safety checks"""
    print("\n🛡️  Testing custom safety checks...")
    
    # Create remediation engine
    remediation_engine = AutoRemediationEngine()
    
    # Create custom safety check
    def check_resource_tags(resource, context):
        """Check if resource has required tags"""
        labels = getattr(resource.metadata, 'labels', {}) or {}
        required_tags = ['owner', 'environment', 'cost-center']
        return all(tag in labels for tag in required_tags)
    
    custom_check = SafetyCheck(
        name="required_tags",
        description="Ensure resource has required tags",
        check_function=check_resource_tags,
        severity=SafetyLevel.MEDIUM
    )
    
    remediation_engine.add_safety_check(custom_check)
    print(f"✅ Added custom safety check: {custom_check.name}")
    
    # Create custom approval workflow
    def auto_approve_dev_resources(drift_result):
        """Auto-approve development resources"""
        return hasattr(drift_result, 'environment') and getattr(drift_result, 'environment') == 'development'
    
    custom_workflow = ApprovalWorkflow(
        name="dev_auto_approve",
        description="Auto-approve development resources",
        required_approvers=[],
        timeout_minutes=5,
        auto_approve_conditions=[auto_approve_dev_resources]
    )
    
    remediation_engine.add_approval_workflow(custom_workflow)
    print(f"✅ Added custom approval workflow: {custom_workflow.name}")
    
    # Test safety checks count
    print(f"📊 Total safety checks: {len(remediation_engine.safety_checks)}")
    print(f"📊 Total approval workflows: {len(remediation_engine.approval_workflows)}")
    
    return remediation_engine


async def demo_integration_system():
    """Demo the full integration system"""
    print("\n🔗 Testing full integration system...")
    
    # Setup auto-remediation integration
    integration = await setup_auto_remediation_integration(
        enable_auto_remediation=True,
        enable_auto_approval=True,
        monitoring_policies=[
            MonitoringPolicy(
                name="dev_resources",
                resource_filter={"environment": "development"},
                check_interval=60,
                priority="low",
                auto_remediate=True,
                notification_channels=["slack"]
            ),
            MonitoringPolicy(
                name="prod_resources",
                resource_filter={"environment": "production"},
                check_interval=300,
                priority="high",
                auto_remediate=False,  # No auto-remediation for production
                notification_channels=["slack", "email"]
            )
        ]
    )
    
    print(f"✅ Integration setup completed")
    
    # Check status
    status = integration.get_status()
    print(f"📊 Integration status:")
    print(f"   Auto-remediation enabled: {status['auto_remediation_enabled']}")
    print(f"   Auto-approval enabled: {status['auto_approval_enabled']}")
    print(f"   Drift daemon state: {status['drift_daemon_status']['state']}")
    print(f"   Monitoring policies: {len(status['drift_daemon_status']['policies'])}")
    
    # Test enabling/disabling features
    integration.disable_auto_remediation()
    print("✅ Auto-remediation disabled")
    
    integration.enable_auto_remediation()
    print("✅ Auto-remediation enabled")
    
    integration.disable_auto_approval()
    print("✅ Auto-approval disabled")
    
    integration.enable_auto_approval()  
    print("✅ Auto-approval enabled")
    
    # Test request management
    pending_requests = integration.get_pending_requests()
    print(f"📋 Pending requests: {len(pending_requests)}")
    
    # Stop integration
    await integration.stop()
    print("✅ Integration stopped")
    
    return integration


async def demo_rollback_capabilities():
    """Demo rollback capabilities"""
    print("\n↩️  Testing rollback capabilities...")
    
    # Create remediation engine
    remediation_engine = AutoRemediationEngine(
        enable_auto_approval=True
    )
    
    # Create drift result
    drift_result = DriftResult(
        resource_id="vm-rollback-test",
        resource_name="rollback-test-vm",
        resource_type="VirtualMachine",
        drift_detected=True,
        drift_details={
            "configuration": {
                "old_value": "original_config",
                "new_value": "changed_config"
            }
        },
        check_timestamp=datetime.now(timezone.utc),
    )
    
    # Request remediation
    request = await remediation_engine.request_remediation(
        drift_result=drift_result,
        requested_by="test-user"
    )
    
    print(f"✅ Created request: {request.id}")
    print(f"   Rollback plan created: {request.rollback_plan is not None}")
    
    # Approve and execute
    await remediation_engine.approve_remediation(request.id, "test-approver")
    
    # Wait for execution
    await asyncio.sleep(3)
    
    # Check if completed
    request_status = remediation_engine.get_request_status(request.id)
    print(f"📊 Request status: {request_status['status']}")
    
    # Test rollback (if completed)
    if request_status['status'] == RemediationStatus.COMPLETED.value:
        rollback_success = await remediation_engine.rollback_remediation(
            request.id,
            "test-rollback-user",
            "Testing rollback functionality"
        )
        print(f"✅ Rollback executed: {rollback_success}")
        
        # Check final status
        final_status = remediation_engine.get_request_status(request.id)
        print(f"📊 Final status: {final_status['status']}")
    
    return remediation_engine


async def main():
    """Main demo function"""
    print("🎯 InfraDSL Auto-Remediation Demo")
    print("=" * 50)
    
    # Run demos
    remediation_engine, drift_result = demo_basic_auto_remediation()
    await demo_remediation_request_workflow()
    demo_custom_safety_checks()
    await demo_integration_system()
    await demo_rollback_capabilities()
    
    print("\n🎉 All auto-remediation demos completed successfully!")
    print("\nKey Features Demonstrated:")
    print("✅ AutoRemediationEngine - Core remediation logic")
    print("✅ Safety Checks - Automated safety validation")
    print("✅ Approval Workflows - Flexible approval processes")
    print("✅ Request Management - Complete request lifecycle")
    print("✅ Integration System - Full monitoring integration")
    print("✅ Rollback Capabilities - Safe rollback mechanisms")
    print("✅ Statistics & Monitoring - Comprehensive tracking")
    
    print("\nNext Steps:")
    print("1. Configure real safety checks for your environment")
    print("2. Set up approval workflows with actual users")
    print("3. Integrate with your notification systems")
    print("4. Test with real infrastructure resources")
    print("5. Enable auto-remediation for appropriate environments")


if __name__ == "__main__":
    asyncio.run(main())