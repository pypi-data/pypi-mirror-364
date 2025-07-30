"""
Google Cloud DNS Service Implementation
"""

import logging
from typing import Any, Dict, List, Optional

from ....core.exceptions import ProviderException
from ....core.interfaces.provider import ResourceMetadata, ResourceQuery
from .base import BaseGCPService

logger = logging.getLogger(__name__)


class DNSService(BaseGCPService):
    """Google Cloud DNS service implementation"""
    
    def __init__(self, provider):
        super().__init__(provider)
        self._dns_client = None
        
    def _get_dns_client(self):
        """Get or create Cloud DNS client"""
        if not self._dns_client:
            try:
                from google.cloud import dns
                self._dns_client = dns.Client(project=self.provider._project_id)
            except ImportError:
                raise ProviderException(
                    "google-cloud-dns is required for DNS operations. "
                    "Install with: pip install google-cloud-dns"
                )
            except Exception as e:
                raise ProviderException(f"Failed to initialize DNS client: {e}")
        return self._dns_client
        
    def create_managed_zone(self, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Create a Cloud DNS managed zone or manage records in existing zone"""
        try:
            operation_mode = config.get("operation_mode", "create_zone")
            
            if operation_mode == "manage_records":
                return self._manage_existing_zone_records(config, metadata)
            else:
                return self._create_new_zone(config, metadata)
                
        except Exception as e:
            raise ProviderException(f"Failed to create DNS managed zone: {e}")
            
    def _create_new_zone(self, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Create a new Cloud DNS managed zone"""
        dns_client = self._get_dns_client()
        
        zone_name = metadata.name
        dns_name = config.get("dns_name")
        description = config.get("description", f"Managed zone for {dns_name}")
        
        # Create the zone
        zone = dns_client.zone(
            name=zone_name,
            dns_name=dns_name,
            description=description
        )
        
        # Configure visibility (private/public)
        if config.get("visibility") == "private":
            # Private zones require VPC networks
            networks = config.get("private_visibility_config", {}).get("networks", [])
            # Note: Private zones are handled by the google-cloud-dns library differently
            # This is a simplified implementation
            zone.create(visibility="private")
        else:
            zone.create()
        
        # Reload the zone to get the created data
        zone.reload()
        
        # Configure DNSSEC if enabled
        if config.get("dnssec_config"):
            try:
                # DNSSEC configuration would be applied here
                # This is a simplified implementation
                pass
            except Exception as e:
                logger.warning(f"Failed to configure DNSSEC: {e}")
        
        # Create DNS records
        if config.get("records"):
            self._create_dns_records(zone, config["records"])
        
        return {
            "id": metadata.name,  # Use resource name for consistent cache keys
            "name": metadata.name,  # Resource name
            "zone_name": zone.name,  # Actual GCP zone name
            "dns_name": zone.dns_name,
            "description": zone.description,
            "name_servers": zone.name_servers,
            "creation_time": zone.created.isoformat() if zone.created else None
        }
        
    def _manage_existing_zone_records(self, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Manage records in an existing DNS zone"""
        dns_client = self._get_dns_client()
        
        existing_zone_name = config.get("existing_zone_name")
        if not existing_zone_name:
            raise ProviderException("existing_zone_name is required for record management")
            
        # Get the existing zone
        zone = dns_client.zone(existing_zone_name)
        
        if not zone.exists():
            raise ProviderException(f"Zone '{existing_zone_name}' not found")
            
        # Load zone details
        zone.reload()
        
        # Fix record names to be relative to the actual zone DNS name
        if config.get("records"):
            fixed_records = self._fix_record_names_for_zone(config["records"], zone.dns_name)
            self._create_dns_records(zone, fixed_records)
            
        return {
            "id": metadata.name,  # Use standard resource name for consistent cache keys
            "zone_id": zone.name,  # Original zone ID  
            "name": metadata.name,  # Resource name, not zone name
            "dns_name": zone.dns_name,
            "description": zone.description,
            "name_servers": zone.name_servers,
            "creation_time": zone.created.isoformat() if zone.created else None,
            "operation_mode": "manage_records",
            "resource_name": metadata.name
        }
        
    def _fix_record_names_for_zone(self, records: List[Dict[str, Any]], zone_dns_name: str) -> List[Dict[str, Any]]:
        """Fix record names to be relative to the actual zone DNS name"""
        fixed_records = []
        
        for record_config in records:
            fixed_record = record_config.copy()
            record_name = record_config.get("name", "")
            
            # If the record name contains a different zone name, fix it
            if record_name and not record_name.endswith(zone_dns_name):
                # Extract the subdomain part (everything before the first dot)
                if "." in record_name:
                    subdomain = record_name.split(".")[0]
                    # Create the correct FQDN for this zone
                    if subdomain == zone_dns_name.rstrip("."):
                        # This is the zone apex
                        fixed_record["name"] = zone_dns_name
                    else:
                        # This is a subdomain
                        fixed_record["name"] = f"{subdomain}.{zone_dns_name}"
                else:
                    # Simple subdomain name
                    fixed_record["name"] = f"{record_name}.{zone_dns_name}"
            
            fixed_records.append(fixed_record)
            
        return fixed_records
            
    def _create_dns_records(self, zone, records: List[Dict[str, Any]]):
        """Create DNS records in the zone"""
        try:
            changes = zone.changes()
            
            for record_config in records:
                name = record_config.get("name")
                record_type = record_config.get("type")
                ttl = record_config.get("ttl", 300)
                rrdatas = record_config.get("rrdatas", [])
                
                if name and record_type and rrdatas:
                    # Create the record set
                    record_set = zone.resource_record_set(
                        name=name,
                        record_type=record_type,
                        ttl=ttl,
                        rrdatas=rrdatas
                    )
                    changes.add_record_set(record_set)
            
            # Apply all changes
            if changes.additions or changes.deletions:
                changes.create()
                
        except Exception as e:
            logger.warning(f"Failed to create DNS records: {e}")
            
    def get_managed_zone(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Get a managed zone by name"""
        try:
            dns_client = self._get_dns_client()
            zone = dns_client.zone(zone_name)
            
            if zone.exists():
                return {
                    "id": zone.name,
                    "name": zone.name,
                    "dns_name": zone.dns_name,
                    "description": zone.description,
                    "name_servers": zone.name_servers,
                    "creation_time": zone.created.isoformat() if zone.created else None
                }
            return None
            
        except Exception as e:
            logger.debug(f"Failed to get managed zone {zone_name}: {e}")
            return None
            
    def list_managed_zones(self, query: Optional[ResourceQuery] = None) -> List[Dict[str, Any]]:
        """List all managed zones"""
        try:
            dns_client = self._get_dns_client()
            zones = []
            
            for zone in dns_client.list_zones():
                zones.append({
                    "id": zone.name,
                    "name": zone.name,
                    "dns_name": zone.dns_name,
                    "description": zone.description,
                    "name_servers": zone.name_servers,
                    "creation_time": zone.created.isoformat() if zone.created else None
                })
                
            return zones
            
        except Exception as e:
            logger.error(f"Failed to list managed zones: {e}")
            return []
            
    def update_managed_zone(self, zone_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a managed zone"""
        try:
            dns_client = self._get_dns_client()
            zone = dns_client.zone(zone_name)
            
            if not zone.exists():
                raise ProviderException(f"Managed zone {zone_name} not found")
                
            # Handle record updates
            if "records" in updates:
                self._update_dns_records(zone, updates["records"])
                
            # Return updated zone info
            return self.get_managed_zone(zone_name)
            
        except Exception as e:
            raise ProviderException(f"Failed to update managed zone {zone_name}: {e}")
            
    def _update_dns_records(self, zone, new_records: List[Dict[str, Any]]):
        """Update DNS records in the zone"""
        try:
            # This is a simplified implementation
            # In practice, you'd need to diff existing records vs new records
            changes = zone.changes()
            
            # For now, we'll just add new records
            # A full implementation would handle updates and deletions
            for record_config in new_records:
                name = record_config.get("name")
                record_type = record_config.get("type")
                ttl = record_config.get("ttl", 300)
                rrdatas = record_config.get("rrdatas", [])
                
                if name and record_type and rrdatas:
                    record_set = zone.resource_record_set(
                        name=name,
                        record_type=record_type,
                        ttl=ttl,
                        rrdatas=rrdatas
                    )
                    changes.add_record_set(record_set)
                    
            if changes.additions:
                changes.create()
                
        except Exception as e:
            logger.warning(f"Failed to update DNS records: {e}")
            
    def delete_managed_zone(self, zone_name: str) -> None:
        """Delete a managed zone"""
        try:
            dns_client = self._get_dns_client()
            zone = dns_client.zone(zone_name)
            
            if zone.exists():
                zone.delete()
            else:
                logger.warning(f"Managed zone {zone_name} not found for deletion")
                
        except Exception as e:
            raise ProviderException(f"Failed to delete managed zone {zone_name}: {e}")
            
    def estimate_cost(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Estimate cost for DNS managed zone"""
        # Cloud DNS pricing is typically $0.50/month per hosted zone
        # plus $0.40 per million queries
        base_cost = 0.50  # Monthly hosted zone cost
        
        return {
            "hourly": base_cost / (30 * 24),  # Approximate hourly cost
            "monthly": base_cost
        }
        
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate DNS configuration"""
        errors = []
        
        if not config.get("dns_name"):
            errors.append("dns_name is required")
        else:
            dns_name = config["dns_name"]
            if not dns_name.endswith("."):
                errors.append("dns_name must end with a dot (.)")
                
        return errors
        
    def preview_create(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Preview DNS zone creation"""
        return {
            "action": "create_dns_managed_zone",
            "dns_name": config.get("dns_name"),
            "description": config.get("description"),
            "estimated_name_servers": 4,  # GCP provides 4 name servers
            "estimated_records": len(config.get("records", []))
        }