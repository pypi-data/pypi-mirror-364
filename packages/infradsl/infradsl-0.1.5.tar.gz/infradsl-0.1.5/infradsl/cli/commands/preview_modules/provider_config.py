"""
Provider Config Module - handles provider-specific configuration extraction
"""

from typing import Any, Dict, List


class ProviderConfig:
    """Handles provider-specific configuration extraction from resources"""

    def extract_provider_config(self, resource: Any) -> Dict[str, Any]:
        """Extract provider-specific configuration from resource"""
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
                provider_config = self._extract_by_provider_type(resource)

            # Normalize the provider config to match the format from list_resources
            return self._normalize_desired_config(provider_config, resource)
        else:
            # Try to get the state from the resource's spec or configuration
            if hasattr(resource, "to_dict") and callable(getattr(resource, "to_dict")):
                try:
                    return resource.to_dict()
                except TypeError:
                    # Handle case where to_dict requires arguments
                    pass
            elif hasattr(resource, "spec") and hasattr(resource.spec, "to_dict") and callable(getattr(resource.spec, "to_dict")):
                try:
                    return resource.spec.to_dict()
                except TypeError:
                    # Handle case where to_dict requires arguments
                    pass
            
            # Fallback to extracting common fields
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

    def _extract_by_provider_type(self, resource: Any) -> Dict[str, Any]:
        """Extract provider-specific configuration based on provider type"""
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

                # Get region information - prefer spec.region first
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