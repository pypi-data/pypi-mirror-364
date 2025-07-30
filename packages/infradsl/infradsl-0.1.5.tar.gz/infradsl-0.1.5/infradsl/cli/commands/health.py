"""
Health check commands
"""

from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.nexus.engine import NexusEngine
from ...core.nexus.resource_tracker import ResourceTracker

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class HealthCommand(BaseCommand):
    """Check infrastructure health"""
    
    @property
    def name(self) -> str:
        return "health"
    
    @property
    def description(self) -> str:
        return "Check infrastructure health"
    
    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Check infrastructure health and status"
        )
        
        parser.add_argument(
            "--detailed",
            action="store_true",
            help="Show detailed health information"
        )
        
        parser.add_argument(
            "--resource",
            help="Check specific resource health"
        )
        
        parser.add_argument(
            "--type",
            help="Filter by resource type"
        )
        
        parser.add_argument(
            "--project",
            help="Filter by project"
        )
        
        parser.add_argument(
            "--environment",
            help="Filter by environment"
        )
        
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Watch health status continuously"
        )
        
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Watch interval in seconds (default: 30)"
        )
        
        self.add_common_arguments(parser)
    
    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the health command"""
        try:
            if args.watch:
                return self._watch_health(args, config, console)
            else:
                return self._check_health(args, config, console)
                
        except Exception as e:
            raise CommandError(f"Failed to check health: {e}")
    
    def _check_health(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Check infrastructure health"""
        console.info("Checking infrastructure health...")
        
        # Initialize components
        engine = NexusEngine()
        tracker = ResourceTracker()
        
        # Get resources to check
        resources = self._get_resources_to_check(args, tracker, console)
        
        if not resources:
            console.info("No resources found to check")
            return 0
        
        # Check health
        with console.status("Checking resource health..."):
            health_report = self._check_resource_health(resources, engine, console)
        
        # Display results
        self._display_health_report(health_report, console, args.detailed)
        
        # Return appropriate exit code
        if health_report["unhealthy_count"] > 0:
            return 1
        elif health_report["warning_count"] > 0:
            return 2
        else:
            return 0
    
    def _watch_health(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Watch health status continuously"""
        import time
        
        console.info(f"Watching health status (interval: {args.interval}s)")
        console.info("Press Ctrl+C to stop watching")
        
        try:
            while True:
                # Clear screen
                console.print("\\033[H\\033[J", end="")
                
                # Check health
                self._check_health(args, config, console)
                
                # Wait for interval
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            console.info("\\nHealth watching stopped")
            return 0
    
    def _get_resources_to_check(self, args: Namespace, tracker: ResourceTracker, console: "Console") -> List[Dict[str, Any]]:
        """Get resources to check based on filters"""
        if args.resource:
            # Check specific resource
            resource = tracker.get_resource(args.resource)
            return [resource] if resource else []
        
        # Get all resources
        resources = tracker.list_resources()
        
        # Apply filters
        if args.type:
            resources = [r for r in resources if r.get("type") == args.type]
        
        if args.project:
            resources = [r for r in resources if r.get("project") == args.project]
        
        if args.environment:
            resources = [r for r in resources if r.get("environment") == args.environment]
        
        return resources
    
    def _check_resource_health(self, resources: List[Dict[str, Any]], engine: NexusEngine, console: "Console") -> Dict[str, Any]:
        """Check health of resources"""
        health_report = {
            "total_count": len(resources),
            "healthy_count": 0,
            "unhealthy_count": 0,
            "warning_count": 0,
            "unknown_count": 0,
            "resources": []
        }
        
        for resource in resources:
            try:
                # Get resource health
                health_status = self._get_resource_health(resource, engine)
                
                resource_health = {
                    "name": resource["name"],
                    "type": resource["type"],
                    "status": health_status["status"],
                    "health": health_status["health"],
                    "messages": health_status.get("messages", []),
                    "checks": health_status.get("checks", [])
                }
                
                health_report["resources"].append(resource_health)
                
                # Update counters
                if health_status["health"] == "healthy":
                    health_report["healthy_count"] += 1
                elif health_status["health"] == "unhealthy":
                    health_report["unhealthy_count"] += 1
                elif health_status["health"] == "warning":
                    health_report["warning_count"] += 1
                else:
                    health_report["unknown_count"] += 1
                    
            except Exception as e:
                # Mark as unknown on error
                resource_health = {
                    "name": resource["name"],
                    "type": resource["type"],
                    "status": "error",
                    "health": "unknown",
                    "messages": [f"Health check failed: {e}"],
                    "checks": []
                }
                
                health_report["resources"].append(resource_health)
                health_report["unknown_count"] += 1
        
        return health_report
    
    def _get_resource_health(self, resource: Dict[str, Any], engine: NexusEngine) -> Dict[str, Any]:
        """Get health status for a single resource"""
        # This would integrate with actual provider health checks
        # For now, return mock health data
        
        resource_name = resource["name"]
        resource_type = resource["type"]
        
        # Mock health checks
        checks = [
            {
                "name": "Resource Exists",
                "status": "pass",
                "message": f"{resource_name} exists in provider"
            },
            {
                "name": "Resource Running",
                "status": "pass",
                "message": f"{resource_name} is in running state"
            },
            {
                "name": "Connectivity",
                "status": "pass",
                "message": f"{resource_name} is reachable"
            }
        ]
        
        # Determine overall health
        failed_checks = [c for c in checks if c["status"] == "fail"]
        warning_checks = [c for c in checks if c["status"] == "warning"]
        
        if failed_checks:
            health = "unhealthy"
        elif warning_checks:
            health = "warning"
        else:
            health = "healthy"
        
        return {
            "status": "running",
            "health": health,
            "checks": checks,
            "messages": []
        }
    
    def _display_health_report(self, health_report: Dict[str, Any], console: "Console", detailed: bool = False) -> None:
        """Display health report"""
        # Summary
        console.info(f"Health Summary:")
        console.info(f"  Total: {health_report['total_count']}")
        console.info(f"  Healthy: {health_report['healthy_count']}")
        console.info(f"  Unhealthy: {health_report['unhealthy_count']}")
        console.info(f"  Warning: {health_report['warning_count']}")
        console.info(f"  Unknown: {health_report['unknown_count']}")
        
        # Overall status
        if health_report["unhealthy_count"] > 0:
            console.error(f"\\n❌ {health_report['unhealthy_count']} resources are unhealthy")
        elif health_report["warning_count"] > 0:
            console.warning(f"\\n⚠️  {health_report['warning_count']} resources have warnings")
        else:
            console.success("\\n✅ All resources are healthy")
        
        # Group resources by health status
        healthy_resources = [r for r in health_report["resources"] if r["health"] == "healthy"]
        unhealthy_resources = [r for r in health_report["resources"] if r["health"] == "unhealthy"]
        warning_resources = [r for r in health_report["resources"] if r["health"] == "warning"]
        unknown_resources = [r for r in health_report["resources"] if r["health"] == "unknown"]
        
        # Display unhealthy resources
        if unhealthy_resources:
            console.info("\\nUnhealthy Resources:")
            for resource in unhealthy_resources:
                console.error(f"  ❌ {resource['name']} ({resource['type']})")
                if detailed:
                    self._display_resource_health_details(resource, console, "    ")
        
        # Display warning resources
        if warning_resources:
            console.info("\\nWarning Resources:")
            for resource in warning_resources:
                console.warning(f"  ⚠️  {resource['name']} ({resource['type']})")
                if detailed:
                    self._display_resource_health_details(resource, console, "    ")
        
        # Display unknown resources
        if unknown_resources:
            console.info("\\nUnknown Resources:")
            for resource in unknown_resources:
                console.info(f"  ❓ {resource['name']} ({resource['type']})")
                if detailed:
                    self._display_resource_health_details(resource, console, "    ")
        
        # Display healthy resources in detailed mode
        if detailed and healthy_resources:
            console.info("\\nHealthy Resources:")
            for resource in healthy_resources:
                console.success(f"  ✅ {resource['name']} ({resource['type']})")
                self._display_resource_health_details(resource, console, "    ")
    
    def _display_resource_health_details(self, resource: Dict[str, Any], console: "Console", indent: str = "") -> None:
        """Display detailed health information for a resource"""
        # Display messages
        if resource.get("messages"):
            for message in resource["messages"]:
                console.info(f"{indent}{message}")
        
        # Display checks
        if resource.get("checks"):
            for check in resource["checks"]:
                status_icon = "✅" if check["status"] == "pass" else ("⚠️" if check["status"] == "warning" else "❌")
                console.info(f"{indent}{status_icon} {check['name']}: {check['message']}")
        
        console.info("")