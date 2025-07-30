"""
Drift detection and management
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.nexus.engine import NexusEngine

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class DriftCommand(BaseCommand):
    """Detect and manage infrastructure drift"""

    @property
    def name(self) -> str:
        return "drift"

    @property
    def description(self) -> str:
        return "Detect and manage infrastructure drift"

    def register(self, subparsers) -> None:
        """Register command arguments"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Detect and manage infrastructure drift",
        )

        subcommands = parser.add_subparsers(dest="drift_action", help="Drift actions")

        # Check command
        check_parser = subcommands.add_parser("check", help="Check for drift")
        check_parser.add_argument(
            "file", type=Path, nargs="?", help="Infrastructure file to check (optional)"
        )
        check_parser.add_argument(
            "--summary-only",
            action="store_true",
            help="Show only summary, skip detailed drift information",
        )

        # Fix command
        fix_parser = subcommands.add_parser("fix", help="Fix detected drift")
        fix_parser.add_argument("file", type=Path, help="Infrastructure file to fix")
        fix_parser.add_argument(
            "--auto-approve", action="store_true", help="Skip confirmation prompts"
        )

        # Report command
        report_parser = subcommands.add_parser("report", help="Generate drift report")
        report_parser.add_argument(
            "file",
            type=Path,
            nargs="?",
            help="Infrastructure file to report on (optional)",
        )
        report_parser.add_argument("--output", type=Path, help="Output file for report")

        self.add_common_arguments(parser)

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the drift command"""
        if not args.drift_action:
            console.error("No drift action specified. Use 'check', 'fix', or 'report'")
            return 1

        try:
            if args.drift_action == "check":
                return self._check_drift(args, config, console)
            elif args.drift_action == "fix":
                return self._fix_drift(args, config, console)
            elif args.drift_action == "report":
                return self._generate_report(args, config, console)
            else:
                console.error(f"Unknown drift action: {args.drift_action}")
                return 1

        except Exception as e:
            raise CommandError(f"Failed to execute drift command: {e}")

    def _check_drift(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Check for infrastructure drift"""
        console.info("Checking for infrastructure drift...")

        # Load resources if file provided
        resources = []
        if args.file:
            if not args.file.exists():
                console.error(f"Infrastructure file not found: {args.file}")
                return 1
            resources = self._load_infrastructure(args.file, console)

        # Initialize engine
        engine = NexusEngine()

        with console.status("Analyzing drift..."):
            drift_report = self._analyze_drift(resources, engine, console)

        # Display results
        self._display_drift_report(drift_report, console, not args.summary_only)

        # Return non-zero if drift detected
        return 1 if drift_report["has_drift"] else 0

    def _fix_drift(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Fix detected drift"""
        infrastructure_file = args.file

        if not infrastructure_file.exists():
            console.error(f"Infrastructure file not found: {infrastructure_file}")
            return 1

        console.info(f"Fixing drift in: {infrastructure_file}")

        # Load resources
        resources = self._load_infrastructure(infrastructure_file, console)

        # Initialize engine
        engine = NexusEngine()

        # Analyze drift
        with console.status("Analyzing drift..."):
            drift_report = self._analyze_drift(resources, engine, console)

        if not drift_report["has_drift"]:
            console.success("No drift detected")
            return 0

        # Display drift
        self._display_drift_report(drift_report, console, True)

        # Confirm fix
        if not args.auto_approve:
            if not console.confirm("Fix the detected drift?"):
                console.info("Drift fix cancelled")
                return 0

        # Fix drift
        return self._apply_drift_fixes(drift_report, engine, console)

    def _generate_report(
        self, args: Namespace, config: "CLIConfig", console: "Console"
    ) -> int:
        """Generate drift report"""
        console.info("Generating drift report...")

        # Load resources if file provided
        resources = []
        if args.file:
            if not args.file.exists():
                console.error(f"Infrastructure file not found: {args.file}")
                return 1
            resources = self._load_infrastructure(args.file, console)

        # Initialize engine
        engine = NexusEngine()

        with console.status("Analyzing drift..."):
            drift_report = self._analyze_drift(resources, engine, console)

        # Generate report
        report_content = self._generate_drift_report(drift_report)

        # Save or display report
        if args.output:
            with open(args.output, "w") as f:
                f.write(report_content)
            console.success(f"Drift report saved to: {args.output}")
        else:
            console.output(report_content)

        return 0

    def _load_infrastructure(self, file_path: Path, console: "Console") -> List[Any]:
        """Load infrastructure resources from Python file"""
        import importlib.util
        from dotenv import load_dotenv

        # Load .env file if it exists - same as apply command
        env_path = file_path.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            console.debug(f"Loaded environment from {env_path}")
        else:
            # Also check current working directory
            if Path(".env").exists():
                load_dotenv()
                console.debug("Loaded environment from .env")

        spec = importlib.util.spec_from_file_location("infrastructure", file_path)
        if spec is None or spec.loader is None:
            raise CommandError(f"Cannot load infrastructure file: {file_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract resources from module
        resources = []
        for name in dir(module):
            obj = getattr(module, name)
            if hasattr(obj, "_resource_type") and hasattr(obj, "name"):
                resources.append(obj)

        console.debug(f"Loaded {len(resources)} resources from {file_path}")
        return resources

    def _analyze_drift(
        self, resources: List[Any], engine: NexusEngine, console: "Console"
    ) -> Dict[str, Any]:
        """Analyze drift in resources"""
        drift_report = {
            "has_drift": False,
            "total_resources": len(resources),
            "drifted_resources": [],
            "missing_resources": [],
            "extra_resources": [],
            "ok_resources": [],
        }

        for resource in resources:
            # Get current state
            current_state = self._get_current_state(resource)
            desired_state = self._get_desired_state(resource)

            if current_state is None:
                drift_report["missing_resources"].append(
                    {
                        "resource": resource,
                        "name": resource.name,
                        "type": resource._resource_type,
                        "drift_type": "missing",
                    }
                )
                drift_report["has_drift"] = True
            elif self._has_drift(current_state, desired_state):
                drift_details = self._get_drift_details(current_state, desired_state)
                drift_report["drifted_resources"].append(
                    {
                        "resource": resource,
                        "name": resource.name,
                        "type": resource._resource_type,
                        "drift_type": "configuration",
                        "drift_details": drift_details,
                    }
                )
                drift_report["has_drift"] = True
            else:
                drift_report["ok_resources"].append(
                    {
                        "resource": resource,
                        "name": resource.name,
                        "type": resource._resource_type,
                    }
                )

        return drift_report

    def _get_current_state(self, resource: Any) -> Dict[str, Any] | None:
        """Get current state of resource from provider using universal state detection"""
        try:
            # Check if resource has a provider attached
            if hasattr(resource, "_provider") and resource._provider:
                # Use universal state detector
                from ...core.services.state_detection import create_state_detector

                state_detector = create_state_detector(resource._provider)
                return state_detector.get_current_state(resource)

            return None
        except Exception as e:
            # Log the error but don't fail - assume resource doesn't exist
            import logging

            logger = logging.getLogger(__name__)
            logger.debug(f"Error checking current state for {resource.name}: {e}")
            return None

    def _has_drift(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if there is drift between current and desired state using fingerprint comparison"""
        # Generate fingerprints for comparison
        current_fingerprint = self._generate_fingerprint(current)
        desired_fingerprint = self._generate_fingerprint(desired)

        return current_fingerprint != desired_fingerprint

    def _get_drift_details(
        self, current: Dict[str, Any], desired: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get detailed drift information"""
        details = []

        # Only check relevant fields for drift
        relevant_fields = [
            "name",
            "region",
            "zone",
            "size",
            "image",
            "backups",
            "ipv6",
            "monitoring",
            "additional_disks",
            "tags",
            "machine_type",
            "disk_size_gb",
            "public_ip",
        ]

        for key in relevant_fields:
            if key in desired:
                current_value = current.get(key)
                desired_value = desired.get(key)

                if key == "tags":
                    # Special handling for tags - normalize for comparison
                    current_normalized = self._normalize_tags_for_fingerprint(
                        current_value or []
                    )
                    desired_normalized = self._normalize_tags_for_fingerprint(
                        desired_value or []
                    )
                    if current_normalized != desired_normalized:
                        details.append(
                            {
                                "field": key,
                                "current": current_normalized,
                                "desired": desired_normalized,
                            }
                        )
                elif current_value != desired_value:
                    details.append(
                        {
                            "field": key,
                            "current": current_value,
                            "desired": desired_value,
                        }
                    )

        return details

    def _display_drift_report(
        self, drift_report: Dict[str, Any], console: "Console", detailed: bool = False
    ) -> None:
        """Display drift report"""
        if not drift_report["has_drift"]:
            console.success("No drift detected")
            return

        console.info(
            f"Drift detected in {len(drift_report['drifted_resources'])} resources"
        )

        # Missing resources
        if drift_report["missing_resources"]:
            console.info("")
            console.info(
                f"Missing resources ({len(drift_report['missing_resources'])}):"
            )
            for item in drift_report["missing_resources"]:
                console.info(f"  - {item['name']} ({item['type']})")

        # Drifted resources
        if drift_report["drifted_resources"]:
            console.info("")
            console.info(
                f"Drifted resources ({len(drift_report['drifted_resources'])}):"
            )
            for item in drift_report["drifted_resources"]:
                console.info(f"  ~ {item['name']} ({item['type']})")
                if detailed and item.get("drift_details"):
                    for detail in item["drift_details"]:
                        if detail["field"] == "spec":
                            console.info(f"    {detail['field']}:")
                            if detail["current"] is not None:
                                console.info("      Current: None")
                            if detail["desired"] is not None:
                                console.info("      Desired:")
                                self._display_spec_details(
                                    detail["desired"], console, "        "
                                )
                        else:
                            console.info(
                                f"    {detail['field']}: {detail['current']} -> {detail['desired']}"
                            )

        # Extra resources
        if drift_report["extra_resources"]:
            console.info("")
            console.info(f"Extra resources ({len(drift_report['extra_resources'])}):")
            for item in drift_report["extra_resources"]:
                console.info(f"  + {item['name']} ({item['type']})")

        # OK resources
        if detailed and drift_report["ok_resources"]:
            console.info("")
            console.info(f"OK resources ({len(drift_report['ok_resources'])}):")
            for item in drift_report["ok_resources"]:
                console.info(f"  ✓ {item['name']} ({item['type']})")

    def _apply_drift_fixes(
        self, drift_report: Dict[str, Any], engine: NexusEngine, console: "Console"
    ) -> int:
        """Apply fixes for detected drift"""
        console.info("Applying drift fixes...")

        fixed_count = 0
        failed_count = 0

        # Fix missing resources
        for item in drift_report["missing_resources"]:
            try:
                with console.status(f"Creating {item['name']}..."):
                    # Use the resource's create method directly
                    if hasattr(item["resource"], "create"):
                        item["resource"].create()
                        console.success(f"Created {item['name']}")
                        fixed_count += 1
                    else:
                        console.error(
                            f"Resource {item['name']} does not support creation"
                        )
                        failed_count += 1
            except Exception as e:
                console.error(f"Error creating {item['name']}: {e}")
                if console.verbosity >= 2:
                    import traceback

                    console.error(traceback.format_exc())
                failed_count += 1

        # Fix drifted resources
        for item in drift_report["drifted_resources"]:
            try:
                with console.status(f"Updating {item['name']}..."):
                    # Use the resource's update method directly
                    if hasattr(item["resource"], "update"):
                        item["resource"].update()
                        console.success(f"Updated {item['name']}")
                        fixed_count += 1
                    else:
                        console.error(
                            f"Resource {item['name']} does not support updates"
                        )
                        failed_count += 1
            except Exception as e:
                console.error(f"Error updating {item['name']}: {e}")
                if console.verbosity >= 2:
                    import traceback

                    console.error(traceback.format_exc())
                failed_count += 1

        # Summary
        console.info("")
        console.info(f"Drift fix completed: {fixed_count} fixed, {failed_count} failed")

        return 1 if failed_count > 0 else 0

    def _display_spec_details(
        self, spec: Dict[str, Any], console: "Console", indent: str = ""
    ) -> None:
        """Display spec details in a formatted way"""
        for key, value in spec.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                # Handle complex list items like additional_disks
                console.info(f"{indent}{key}:")
                for i, item in enumerate(value):
                    console.info(f"{indent}  - {i+1}:")
                    for k, v in item.items():
                        console.info(f"{indent}    {k}: {v}")
            elif isinstance(value, list):
                console.info(f"{indent}{key}: {', '.join(str(v) for v in value)}")
            else:
                console.info(f"{indent}{key}: {value}")

    def _generate_drift_report(self, drift_report: Dict[str, Any]) -> str:
        """Generate formatted drift report"""
        report = "# Infrastructure Drift Report\\n\\n"

        if not drift_report["has_drift"]:
            report += "✅ No drift detected\\n"
            return report

        report += f"## Summary\\n"
        report += f"- Total resources: {drift_report['total_resources']}\\n"
        report += f"- Drifted resources: {len(drift_report['drifted_resources'])}\\n"
        report += f"- Missing resources: {len(drift_report['missing_resources'])}\\n"
        report += f"- Extra resources: {len(drift_report['extra_resources'])}\\n"
        report += f"- OK resources: {len(drift_report['ok_resources'])}\\n\\n"

        # Details
        if drift_report["drifted_resources"]:
            report += "## Drifted Resources\\n\\n"
            for item in drift_report["drifted_resources"]:
                report += f"### {item['name']} ({item['type']})\\n"
                if item.get("drift_details"):
                    for detail in item["drift_details"]:
                        report += f"- {detail['field']}: `{detail['current']}` → `{detail['desired']}`\\n"
                report += "\\n"

        return report

    def _get_desired_state(self, resource: Any) -> Dict[str, Any]:
        """Extract desired state from resource configuration"""
        # For VirtualMachine resources, use the provider-specific configuration
        if (
            hasattr(resource, "_resource_type")
            and resource._resource_type == "VirtualMachine"
        ):
            # Get the provider-specific config to match the format returned by the provider
            if hasattr(resource, "_to_provider_config"):
                provider_config = resource._to_provider_config()
            else:
                # Determine provider type and get appropriate config
                provider_config = self._extract_provider_config(resource)

            # Normalize the provider config to match the format from list_resources
            return self._normalize_desired_config(provider_config, resource)
        else:
            # Try to get the state from the resource's spec or configuration
            if hasattr(resource, "to_dict"):
                return resource.to_dict()
            elif hasattr(resource, "spec") and hasattr(resource.spec, "to_dict"):
                return resource.spec.to_dict()
            else:
                # Extract common fields from the resource
                desired = {
                    "name": getattr(resource, "name", ""),
                    "region": getattr(resource, "region", None),
                    "size": getattr(resource, "size", None),
                    "image": getattr(resource, "image", None),
                    "backups": getattr(resource, "backups", False),
                    "ipv6": getattr(resource, "ipv6", True),
                    "monitoring": getattr(resource, "monitoring", True),
                    "user_data": getattr(resource, "user_data", None),
                    "tags": getattr(resource, "tags", []),
                }
                # Remove None values
                return {k: v for k, v in desired.items() if v is not None}

    def _extract_provider_config(self, resource: Any) -> Dict[str, Any]:
        """Extract provider-specific configuration from VirtualMachine resource"""
        # Determine provider type from resource's provider
        if hasattr(resource, "_provider") and resource._provider:
            if isinstance(resource._provider, str):
                # Provider is a string name
                provider_type = resource._provider.lower()
            else:
                # Provider is a provider object
                provider_type = (
                    resource._provider.config.type.value
                    if hasattr(resource._provider.config.type, "value")
                    else str(resource._provider.config.type)
                )

            if provider_type.lower() == "gcp":
                return self._extract_gcp_config(resource)
            elif provider_type.lower() == "digitalocean":
                return self._extract_do_config(resource)
            elif provider_type.lower() == "aws":
                return self._extract_aws_config(resource)

        # Fallback to DigitalOcean config
        return self._extract_do_config(resource)

    def _extract_do_config(self, resource: Any) -> Dict[str, Any]:
        """Extract DigitalOcean-specific configuration from VirtualMachine resource"""
        # Use the VirtualMachine's internal method to get DO config
        if hasattr(resource, "_to_digitalocean_config"):
            return resource._to_digitalocean_config()
        else:
            # Fallback manual extraction
            spec = getattr(resource, "spec", None)
            if spec:
                # Map InstanceSize to DigitalOcean size
                size_mapping = {
                    "nano": "s-1vcpu-512mb-10gb",
                    "micro": "s-1vcpu-1gb",
                    "small": "s-1vcpu-2gb",
                    "medium": "s-2vcpu-4gb",
                    "large": "s-4vcpu-8gb",
                    "xlarge": "s-8vcpu-16gb",
                }

                instance_size = getattr(spec, "instance_size", None)
                size_slug = size_mapping.get(
                    instance_size.value if instance_size else "small", "s-1vcpu-2gb"
                )

                return {
                    "name": resource.name,
                    "size": size_slug,
                    "image": "ubuntu-22-04-x64",  # Default mapping
                    "region": getattr(resource._provider.config, "region", "nyc1"),
                    "tags": self._extract_tags(resource),
                }
            return {}

    def _extract_gcp_config(self, resource: Any) -> Dict[str, Any]:
        """Extract GCP-specific configuration from VirtualMachine resource"""
        # Use the VirtualMachine's internal method to get GCP config
        if hasattr(resource, "_to_gcp_config"):
            return resource._to_gcp_config()
        else:
            # Fallback manual extraction
            spec = getattr(resource, "spec", None)
            if spec:
                # Map InstanceSize to GCP machine types
                size_mapping = {
                    "nano": "e2-micro",
                    "micro": "e2-small",
                    "small": "e2-medium",
                    "medium": "e2-standard-2",
                    "large": "e2-standard-4",
                    "xlarge": "e2-standard-8",
                }

                instance_size = getattr(spec, "instance_size", None)
                machine_type = size_mapping.get(
                    instance_size.value if instance_size else "small", "e2-medium"
                )

                image_family = getattr(spec, "image_family", "ubuntu-2204-lts")
                zone = getattr(resource._provider.config, "zone", "us-central1-a")
                region = (
                    zone.rsplit("-", 1)[0]
                    if zone
                    else getattr(resource._provider.config, "region", "us-central1")
                )

                return {
                    "name": resource.name,
                    "machine_type": machine_type,
                    "image_family": image_family,
                    "zone": zone,
                    "region": region,
                    "disk_size_gb": getattr(spec, "disk_size_gb", 20),
                    "public_ip": getattr(spec, "public_ip", True),
                    "tags": self._extract_tags(resource),
                }
            return {}

    def _extract_aws_config(self, resource: Any) -> Dict[str, Any]:
        """Extract AWS-specific configuration from VirtualMachine resource"""
        # Use the VirtualMachine's internal method to get AWS config
        if hasattr(resource, "_to_aws_config"):
            return resource._to_aws_config()
        else:
            # Fallback manual extraction for AWS
            spec = getattr(resource, "spec", None)
            if spec:
                # Map InstanceSize to AWS instance types
                size_mapping = {
                    "nano": "t3.nano",
                    "micro": "t3.micro",
                    "small": "t3.small",
                    "medium": "t3.medium",
                    "large": "t3.large",
                    "xlarge": "t3.xlarge",
                }

                instance_size = getattr(spec, "instance_size", None)
                instance_type = size_mapping.get(
                    instance_size.value if instance_size else "small", "t3.small"
                )

                return {
                    "name": resource.name,
                    "instance_type": instance_type,
                    "image": "ubuntu-22-04-x64",  # Default mapping
                    "region": getattr(resource._provider.config, "region", "us-east-1"),
                    "tags": self._extract_tags(resource),
                }
            return {}

    def _normalize_desired_config(
        self, provider_config: Dict[str, Any], resource: Any
    ) -> Dict[str, Any]:
        """Normalize desired config to match provider list_resources format"""
        # Use the cleaned tags from _extract_tags instead of provider_config
        tag_list = self._extract_tags(resource)

        # Determine provider type for normalization
        provider_type = "digitalocean"  # default
        if hasattr(resource, "_provider") and resource._provider:
            provider_type = (
                resource._provider.config.type.value
                if hasattr(resource._provider.config.type, "value")
                else str(resource._provider.config.type)
            )

        if provider_type.lower() == "gcp":
            # Extract region from zone if available
            zone = provider_config.get("zone", "us-central1-a")
            region = zone.rsplit("-", 1)[0] if zone else "us-central1"

            return {
                "name": provider_config.get("name", resource.name),
                "region": region,
                "zone": zone,
                "size": provider_config.get(
                    "machine_type", provider_config.get("size", "e2-small")
                ),
                "machine_type": provider_config.get(
                    "machine_type", provider_config.get("size", "e2-small")
                ),
                "image": provider_config.get(
                    "image_family", provider_config.get("image", "ubuntu-2204-lts")
                ),
                "disk_size_gb": provider_config.get("disk_size_gb", 20),
                "public_ip": provider_config.get("public_ip", True),
                "backups": provider_config.get("backups", False),
                "ipv6": provider_config.get("ipv6", False),
                "monitoring": provider_config.get("monitoring", True),
                "user_data": provider_config.get("user_data"),
                "tags": tag_list,
                "labels": provider_config.get("labels", {}),
            }
        else:
            # DigitalOcean format (default)
            return {
                "name": provider_config.get("name", resource.name),
                "region": provider_config.get("region", "nyc1"),
                "size": provider_config.get("size", "s-1vcpu-2gb"),
                "image": provider_config.get("image", "ubuntu-22-04-x64"),
                "backups": provider_config.get("backups", False),
                "ipv6": provider_config.get("ipv6", True),
                "monitoring": provider_config.get("monitoring", True),
                "user_data": provider_config.get("user_data"),
                "tags": tag_list,
                "additional_disks": provider_config.get("additional_disks", []),
            }

    def _extract_tags(self, resource: Any) -> List[str]:
        """Extract tags from resource"""
        tags = []

        # Add management tags
        if hasattr(resource, "name"):
            tags.append(f"infradsl.id:{resource.name}")
            tags.append(f"infradsl.type:{resource._resource_type}")

        # Add user-defined tags
        if hasattr(resource, "tags"):
            tags.extend(resource.tags)

        return tags

    def _generate_fingerprint(self, resource_state: Dict[str, Any]) -> str:
        """Generate a fingerprint from resource state for comparison"""
        import hashlib
        import json

        # Extract only the relevant fields for comparison
        # Ignore fields that change naturally (timestamps, IDs, dynamic IPs, etc.)
        relevant_fields = {
            "name": resource_state.get("name"),
            "region": resource_state.get("region"),
            "size": resource_state.get("size"),
            "image": resource_state.get("image"),
            "backups": resource_state.get("backups", False),
            "ipv6": resource_state.get("ipv6", True),
            "monitoring": resource_state.get("monitoring", True),
            # user_data excluded - not retrievable from cloud providers after creation
            # Include additional disks for LEGO principle - adding/removing disks should be detected
            "additional_disks": resource_state.get("additional_disks", []),
            # Normalize tags - filter out auto-generated ones and sort for consistent comparison
            "tags": self._normalize_tags_for_fingerprint(
                resource_state.get("tags", [])
            ),
        }

        # Create a deterministic JSON string and hash it
        fingerprint_data = json.dumps(relevant_fields, sort_keys=True)
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    def _normalize_tags_for_fingerprint(self, tags: List[str]) -> List[str]:
        """Normalize tags for fingerprint comparison"""
        normalized = []

        for tag in tags:
            # Skip auto-generated tags (UUIDs, boolean values)
            if self._is_auto_generated_tag(tag):
                continue

            # Handle infradsl tags - include ALL management tags for consistency
            if tag.startswith("infradsl.") or (
                (":" in tag and tag.split(":", 1)[0].startswith("infradsl."))
            ):
                # Include ALL management tags for consistent fingerprint comparison
                normalized.append(tag)
            else:
                # Extract meaningful tag values for comparison (user-defined tags)
                if ":" in tag:
                    # Key-value tag - extract just the value part for comparison
                    _, value = tag.split(":", 1)
                    normalized.append(value)
                else:
                    # Plain tag value
                    normalized.append(tag)

        return sorted(normalized)

    def _is_auto_generated_tag(self, tag: str) -> bool:
        """Check if a tag is auto-generated and should be ignored in fingerprint"""
        import re
        import uuid

        # Skip UUID-like tags
        if re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", tag
        ):
            return True

        # Skip boolean value tags
        if tag in ["true", "false", "True", "False"]:
            return True

        # Skip infradsl.created tags (timestamps)
        if tag.startswith("infradsl.created:"):
            return True

        return False
