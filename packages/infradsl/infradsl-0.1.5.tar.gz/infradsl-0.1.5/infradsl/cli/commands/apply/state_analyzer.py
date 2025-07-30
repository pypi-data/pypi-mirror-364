"""
State Analyzer - handles state comparison and fingerprinting
"""

import hashlib
import json
import uuid
from typing import Any, Dict, List

from .lego_analyzer import LEGOAnalyzer


class StateAnalyzer:
    """Analyzes resource state and determines changes needed using LEGO principle"""

    def __init__(self):
        self.lego_analyzer = LEGOAnalyzer()

    def get_desired_state(self, resource: Any) -> Dict[str, Any]:
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

    def needs_replacement(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if resource needs replacement"""
        # Special handling for imported resources - if found in cache, they're already correct
        if current.get('_imported_resource'):
            return False
            
        # Check for changes that require replacement
        immutable_fields = ["name", "region", "zone", "instance_type"]

        for field in immutable_fields:
            if current.get(field) != desired.get(field):
                return True

        return False

    def should_recreate_for_disk_changes(
        self, resource: Any, current: Dict[str, Any], desired: Dict[str, Any]
    ) -> bool:
        """Check if VM should be recreated for disk changes - LEGO principle: avoid recreation"""
        # LEGO PRINCIPLE: Never recreate VMs for disk changes
        # Disk additions/expansions should be handled as additive operations
        
        # Only applies to VirtualMachine resources
        if (
            not hasattr(resource, "_resource_type")
            or resource._resource_type != "VirtualMachine"
        ):
            return False

        # Check if there are disk changes
        current_disks = current.get("additional_disks", [])
        desired_disks = desired.get("additional_disks", [])
        
        # Check disk size changes
        current_disk_size = current.get("disk_size_gb", 20)
        desired_disk_size = desired.get("disk_size_gb", 20)

        if current_disks != desired_disks or current_disk_size != desired_disk_size:
            # LEGO PRINCIPLE: Disk changes are additive, not recreative
            # - Disk expansions: in-place resize (supported by all major providers)
            # - Additional disks: attach new disks without touching VM
            # - Database workloads: never recreate to prevent data loss
            
            # Never recreate for databases
            if hasattr(resource, "is_database") and resource.is_database():
                return False
            
            # LEGO: Disk size increases are in-place operations
            if desired_disk_size > current_disk_size:
                return False  # Use in-place disk expansion
            
            # LEGO: Additional disks are additive operations  
            if len(desired_disks) > len(current_disks):
                return False  # Use disk attachment
            
            # Only recreate if disks are being removed or shrunk (rare case)
            return False  # Even then, prefer detachment over recreation

        return False

    def analyze_changes_with_lego(self, current_resource: Any, desired_resource: Any) -> Dict[str, Any]:
        """Analyze changes using LEGO principle for smart change categorization"""
        # Use LEGO analyzer to get detailed change breakdown
        lego_changes = self.lego_analyzer.analyze_lego_changes(current_resource, desired_resource)
        
        # Generate execution plan
        execution_plan = self.lego_analyzer.get_execution_plan(lego_changes)
        
        # Get user-friendly explanation
        explanation = self.lego_analyzer.explain_lego_benefits(lego_changes)
        
        return {
            "changes": lego_changes,
            "execution_plan": execution_plan,
            "explanation": explanation,
            "use_lego": self.lego_analyzer.should_use_lego_approach(lego_changes),
            "requires_confirmation": any(
                step.get("requires_confirmation", False) for step in execution_plan
            )
        }

    def needs_update(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if resource needs update using fingerprint comparison"""
        # Special handling for imported resources - if found in cache, they're already correct
        if current.get('_imported_resource'):
            return False
            
        # Generate fingerprints for comparison
        current_fingerprint = self._generate_fingerprint(current)
        desired_fingerprint = self._generate_fingerprint(desired)

        return current_fingerprint != desired_fingerprint

    def needs_lego_update(self, current_resource: Any, desired_resource: Any) -> bool:
        """Check if resource needs LEGO-style update (additive changes only)"""
        lego_analysis = self.analyze_changes_with_lego(current_resource, desired_resource)
        
        # Only needs update if there are changes that aren't just fingerprint differences
        changes = lego_analysis["changes"]
        
        has_changes = (
            len(changes.get("additive_components", [])) > 0 or
            len(changes.get("in_place_updates", [])) > 0 or
            len(changes.get("component_updates", [])) > 0 or
            len(changes.get("component_removals", [])) > 0 or
            len(changes.get("vm_modifications", [])) > 0
        )
        
        return has_changes

    def _generate_fingerprint(self, resource_state: Dict[str, Any]) -> str:
        """Generate a fingerprint from resource state for comparison"""
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
        # Skip boolean tags like 'true', 'false'
        if tag.lower() in ["true", "false"]:
            return True

        # Skip UUID tags
        try:
            uuid.UUID(tag)
            return True
        except ValueError:
            pass

        # Be more conservative - only skip if it looks like a generated resource ID
        # Don't skip the actual resource name as it's part of the configuration
        return False

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
                    "region": getattr(spec, "region", "nyc1"),
                    "backups": getattr(spec, "backups", False),
                    "ipv6": getattr(spec, "ipv6", True),
                    "monitoring": getattr(spec, "monitoring", True),
                    "user_data": getattr(spec, "user_data", None),
                    "tags": self._extract_tags(resource),
                }
            return {}

    def _extract_gcp_config(self, resource: Any) -> Dict[str, Any]:
        """Extract GCP-specific configuration from VirtualMachine resource"""
        # Use the VirtualMachine's internal method to get GCP config
        if hasattr(resource, "_to_gcp_config"):
            return resource._to_gcp_config()
        else:
            # Fallback manual extraction for GCP
            spec = getattr(resource, "spec", None)
            if spec:
                # Map InstanceSize to GCP machine types
                size_mapping = {
                    "nano": "f1-micro",
                    "micro": "f1-micro",
                    "small": "e2-small",
                    "medium": "e2-medium",
                    "large": "e2-standard-4",
                    "xlarge": "e2-standard-8",
                }

                instance_size = getattr(spec, "instance_size", None)
                machine_type = size_mapping.get(
                    instance_size.value if instance_size else "small", "e2-small"
                )

                # Map image to GCP image family
                image_version = getattr(spec, "image_version", "22.04")
                image_family = f"ubuntu-{image_version.replace('.', '')}-lts"

                # Get region information - prefer spec.region first (like preview command)
                region_from_spec = getattr(spec, "region", None)
                if region_from_spec:
                    default_region = region_from_spec
                elif hasattr(resource, "_provider") and resource._provider:
                    if isinstance(resource._provider, str):
                        # Provider is a string, use default region
                        default_region = "us-central1"
                    elif hasattr(resource._provider, "config"):
                        # Provider is an object, get region from config
                        default_region = getattr(
                            resource._provider.config, "region", "us-central1"
                        )
                    else:
                        default_region = "us-central1"
                else:
                    default_region = "us-central1"

                # Get zone from provider_config if set, otherwise default
                zone = getattr(spec, "provider_config", {}).get(
                    "zone", f"{default_region}-a"
                )
                region = zone.rsplit("-", 1)[0] if zone else default_region

                return {
                    "name": resource.name,
                    "size": machine_type,
                    "image": image_family,
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

                # Get region safely
                default_region = "us-east-1"
                if hasattr(resource, "_provider") and resource._provider:
                    if isinstance(resource._provider, str):
                        default_region = "us-east-1"
                    elif hasattr(resource._provider, "config"):
                        default_region = getattr(resource._provider.config, "region", "us-east-1")

                return {
                    "name": resource.name,
                    "size": instance_type,
                    "image": "ubuntu-22-04-x64",  # Default mapping
                    "region": default_region,
                    "tags": self._extract_tags(resource),
                }
            return {}

    def _extract_tags(self, resource: Any) -> List[str]:
        """Extract and normalize tags: include all tags that actually get created"""
        tags = []

        # Use the resource's metadata.to_tags() method if available
        if hasattr(resource, "metadata") and hasattr(resource.metadata, "to_tags"):
            tag_dict = resource.metadata.to_tags()

            # Include ALL tags that actually get created (management + user-defined)
            for key, value in tag_dict.items():
                tags.append(f"{key}:{value}")

        return sorted(tags)

    def _normalize_desired_config(
        self, provider_config: Dict[str, Any], resource: Any
    ) -> Dict[str, Any]:
        """Normalize desired config to match provider list_resources format"""
        # Use the cleaned tags from _extract_tags instead of provider_config
        tag_list = self._extract_tags(resource)

        # Determine provider type for normalization
        provider_type = "digitalocean"  # default
        if hasattr(resource, "_provider") and resource._provider:
            if isinstance(resource._provider, str):
                provider_type = resource._provider.lower()
            else:
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