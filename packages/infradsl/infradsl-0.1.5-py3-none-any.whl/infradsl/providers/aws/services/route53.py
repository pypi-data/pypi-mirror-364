"""
AWS Route53 Service
"""

import logging
from typing import Any, Dict, List, Optional

from .base import BaseAWSService
from ....core.interfaces.provider import ResourceQuery

logger = logging.getLogger(__name__)


class Route53Service(BaseAWSService):
    """AWS Route53 service implementation"""
    
    def create_zone(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create or configure Route53 zone"""
        route53 = self._get_client("route53")

        zone_name = config.get("existing_zone") or config["name"]

        # Get hosted zone ID
        hosted_zone_id = None
        if config.get("existing_zone"):
            # Find existing zone
            zones = route53.list_hosted_zones()["HostedZones"]
            for zone in zones:
                if zone["Name"].rstrip(".") == zone_name.rstrip("."):
                    hosted_zone_id = zone["Id"].split("/")[-1]
                    break

        if not hosted_zone_id:
            # Create new zone
            response = route53.create_hosted_zone(
                Name=zone_name, CallerReference=f"infradsl-{config['name']}"
            )
            hosted_zone_id = response["HostedZone"]["Id"].split("/")[-1]

        # Create records
        records = config.get("records", [])
        if records:
            changes = []
            for record in records:
                # Process record configurations
                change = {"Action": "UPSERT", "ResourceRecordSet": record}
                changes.append(change)

            if changes:
                route53.change_resource_record_sets(
                    HostedZoneId=hosted_zone_id, ChangeBatch={"Changes": changes}
                )

        return {"HostedZoneId": hosted_zone_id}

    def update_zone(self, zone_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update Route53 zone"""
        return self.create_zone(config)

    def delete_zone(self, zone_id: str) -> None:
        """Delete Route53 zone"""
        pass

    def get_zone(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get Route53 zone by ID"""
        try:
            route53 = self._get_client("route53")
            response = route53.get_hosted_zone(Id=zone_id)
            zone = response["HostedZone"]
            
            return {
                "Id": zone["Id"],
                "Name": zone["Name"].rstrip("."),
                "Status": "active",
                "name": zone["Name"].rstrip("."),
                "type": "Route53",
                "provider": "aws",
                "state": "active",
            }
        except Exception:
            return None

    def list_zones(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List Route53 hosted zones"""
        route53 = self._get_client("route53")
        zones = []

        try:
            response = route53.list_hosted_zones()
            if "HostedZones" in response:
                for zone in response["HostedZones"]:
                    zone_info = {
                        "Id": zone["Id"],
                        "Name": zone["Name"].rstrip("."),
                        "Status": "active",
                        "Tags": [],
                        "ResourceRecordSetCount": zone.get("ResourceRecordSetCount", 0),
                        "name": zone["Name"].rstrip("."),
                        "type": "Route53",
                        "provider": "aws",
                        "state": "active",
                    }
                    zones.append(zone_info)
        except Exception as e:
            logger.error(f"Error listing Route53 zones: {e}")

        return zones

    def tag_zone(self, zone_id: str, tags: Dict[str, str]) -> None:
        """Tag Route53 zone"""
        pass

    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview Route53 zone creation"""
        return {
            "zone_name": config.get("existing_zone") or config.get("name"),
            "records_count": len(config.get("records", [])),
        }

    def preview_update(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Preview Route53 zone update"""
        return {
            "zone_id": resource_id,
            "records_changes": updates.get("records", []),
        }

    def get_delete_warnings(self) -> List[str]:
        """Get warnings for Route53 zone deletion"""
        return [
            "All DNS records in the zone will be deleted",
            "Domain resolution will stop working",
        ]

    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate Route53 zone cost"""
        return {"monthly": 0.50}  # Basic hosted zone cost