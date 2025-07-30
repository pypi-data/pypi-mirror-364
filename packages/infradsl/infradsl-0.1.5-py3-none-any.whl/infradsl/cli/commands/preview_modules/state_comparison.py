"""
State Comparison Module - handles state comparison and fingerprint generation
"""

import hashlib
import json
import uuid
from typing import Any, Dict, List


class StateComparison:
    """Handles state comparison and fingerprint generation for resources"""

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

    def needs_update(self, current: Dict[str, Any], desired: Dict[str, Any]) -> bool:
        """Check if resource needs update using fingerprint comparison"""
        # Special handling for imported resources - if found in cache, they're already correct
        if current.get('_imported_resource'):
            return False
            
        # Generate fingerprints for comparison
        current_fingerprint = self.generate_fingerprint(current)
        desired_fingerprint = self.generate_fingerprint(desired)

        return current_fingerprint != desired_fingerprint

    def generate_fingerprint(self, resource_state: Dict[str, Any]) -> str:
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

    def generate_fingerprint_for_resource_type(self, resource_state: Dict[str, Any], resource_type: str) -> str:
        """Generate a fingerprint based on resource type"""
        if resource_type == "CloudDNS":
            return self._generate_dns_fingerprint(resource_state)
        elif resource_type == "VirtualMachine":
            return self.generate_fingerprint(resource_state)  # Use existing VM logic
        else:
            return self.generate_fingerprint(resource_state)  # Fallback to general logic

    def _generate_dns_fingerprint(self, resource_state: Dict[str, Any]) -> str:
        """Generate fingerprint for CloudDNS resources"""
        relevant_fields = {
            "name": resource_state.get("name"),
            "dns_name": resource_state.get("dns_name"),
            "operation_mode": resource_state.get("operation_mode"),
            "existing_zone_name": resource_state.get("existing_zone_name"),
            "dnssec_enabled": resource_state.get("dnssec_enabled", False),
            "records": sorted(
                [
                    {
                        "name": record.get("name"),
                        "type": record.get("type"),
                        "ttl": record.get("ttl"),
                        "rrdatas": sorted(record.get("rrdatas", []))
                    }
                    for record in resource_state.get("records", [])
                ],
                key=lambda x: (x.get("name", ""), x.get("type", ""))
            )
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