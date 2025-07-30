from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class DNSVisibility(Enum):
    """DNS zone visibility"""
    PUBLIC = "public"
    PRIVATE = "private"


class RecordType(Enum):
    """DNS record types"""
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    SRV = "SRV"
    NS = "NS"
    PTR = "PTR"
    CAA = "CAA"
    SPF = "SPF"


@dataclass
class DNSRecord:
    """Individual DNS record"""
    name: str
    type: RecordType
    ttl: int
    rrdatas: List[str]
    
    
@dataclass
class MXRecord:
    """MX record with priority"""
    priority: int
    server: str
    
    def to_rrdata(self) -> str:
        """Convert to DNS rrdata format"""
        return f"{self.priority} {server}"


@dataclass 
class SRVRecord:
    """SRV record with service parameters"""
    priority: int
    weight: int
    port: int
    target: str
    
    def to_rrdata(self) -> str:
        """Convert to DNS rrdata format"""
        return f"{self.priority} {self.weight} {self.port} {self.target}"


class DNSOperationMode(Enum):
    """DNS operation modes"""
    CREATE_ZONE = "create_zone"  # Create new zone with records
    MANAGE_RECORDS = "manage_records"  # Only manage records in existing zone


@dataclass
class CloudDNSSpec(ResourceSpec):
    """Specification for Cloud DNS zone with records"""
    
    # Zone configuration
    dns_name: str
    description: str = ""
    visibility: DNSVisibility = DNSVisibility.PUBLIC
    
    # Operation mode
    operation_mode: DNSOperationMode = DNSOperationMode.CREATE_ZONE
    existing_zone_name: Optional[str] = None  # For record-only operations
    
    # Private zone configuration
    networks: List[str] = field(default_factory=list)
    
    # DNSSEC
    dnssec_enabled: bool = False
    dnssec_state: str = "off"  # off, on, transfer
    
    # Records
    records: List[DNSRecord] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class CloudDNS(BaseResource):
    """
    GCP Cloud DNS managed zone with Rails-like conventions.
    
    Examples:
        # Create new zone with records
        dns = (CloudDNS("example-com")
               .zone("example.com")
               .a_record("www", "203.0.113.1")
               .a_record("app", "203.0.113.2")
               .mx_record([10, "mail.example.com"])
               .txt_record("@", "v=spf1 include:_spf.google.com ~all"))
        
        # Add records to existing zone
        existing_dns = (CloudDNS("api-records")
                       .existing_zone("my-existing-zone")
                       .a_record("api", "203.0.113.10")
                       .cname_record("app", "api.example.com"))
        
        # Private zone for internal services
        internal_dns = (CloudDNS("internal-zone")
                       .zone("internal.mycompany.net")
                       .private(["my-vpc"])
                       .a_record("database", "10.0.1.100")
                       .a_record("redis", "10.0.1.101")
                       .cname_record("db", "database.internal.mycompany.net"))
        
        # Production zone with full configuration
        prod_dns = (CloudDNS("prod-zone")
                   .zone("myapp.com")
                   .dnssec()
                   .a_record("@", ["203.0.113.1", "203.0.113.2"])  # Multiple IPs
                   .a_record("www", ["203.0.113.1", "203.0.113.2"])
                   .aaaa_record("@", "2001:db8::1")
                   .aaaa_record("www", "2001:db8::1")
                   .mx_records([
                       [10, "mail1.myapp.com"],
                       [20, "mail2.myapp.com"]
                   ])
                   .txt_record("@", [
                       "v=spf1 include:_spf.google.com ~all",
                       "google-site-verification=abc123"
                   ])
                   .cname_record("blog", "myapp.ghost.io")
                   .srv_record("_sip._tcp", 10, 60, 5060, "sip.myapp.com")
                   .caa_record("@", "issue", "letsencrypt.org")
                   .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: CloudDNSSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "CloudDNS"
        
    def _create_spec(self) -> CloudDNSSpec:
        # Initialize with a sensible default DNS name
        spec = CloudDNSSpec(dns_name=f"{self.name}.example.com.")
        return spec
        
    def _validate_spec(self) -> None:
        """Validate DNS specification"""
        if not self.spec.dns_name:
            raise ValueError("DNS zone name is required")
            
        if not self.spec.dns_name.endswith("."):
            self.spec.dns_name += "."
            
        # Validate private zones have networks
        if self.spec.visibility == DNSVisibility.PRIVATE and not self.spec.networks:
            raise ValueError("Private DNS zones require at least one network")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "operation_mode": self.spec.operation_mode.value,
            "records": [self._record_to_config(record) for record in self.spec.records],
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }
        
        # Add zone-specific config based on operation mode
        if self.spec.operation_mode == DNSOperationMode.CREATE_ZONE:
            config.update({
                "zone_name": self.metadata.name,
                "dns_name": self.spec.dns_name,
                "description": self.spec.description or f"DNS zone for {self.spec.dns_name}",
                "visibility": self.spec.visibility.value,
            })
        elif self.spec.operation_mode == DNSOperationMode.MANAGE_RECORDS:
            config.update({
                "existing_zone_name": self.spec.existing_zone_name,
            })

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config
        
    def _record_to_config(self, record: DNSRecord) -> Dict[str, Any]:
        """Convert DNS record to configuration"""
        return {
            "name": record.name,
            "type": record.type.value,
            "ttl": record.ttl,
            "rrdatas": record.rrdatas
        }

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Cloud DNS configuration"""
        if self.spec.operation_mode == DNSOperationMode.MANAGE_RECORDS:
            config = {
                "resource_type": "dns_managed_zone"  # Use same resource type for both modes
            }
        else:
            config = {
                "resource_type": "dns_managed_zone"
            }
            
            # Private zone configuration (only for new zones)
            if self.spec.visibility == DNSVisibility.PRIVATE:
                config["private_visibility_config"] = {
                    "networks": [{"network_url": net} for net in self.spec.networks]
                }
                
            # DNSSEC configuration (only for new zones)
            if self.spec.dnssec_enabled:
                config["dnssec_config"] = {
                    "state": self.spec.dnssec_state,
                    "default_key_specs": [
                        {"algorithm": "rsasha256", "key_length": 2048, "key_type": "keySigning"},
                        {"algorithm": "rsasha256", "key_length": 1024, "key_type": "zoneSigning"}
                    ]
                }

        return config
        
    # Fluent interface methods
    
    # Zone configuration
    
    def zone(self, dns_name: str) -> Self:
        """Set DNS zone name for new zone creation (chainable)"""
        self.spec.dns_name = dns_name
        if not dns_name.endswith("."):
            self.spec.dns_name += "."
        self.spec.operation_mode = DNSOperationMode.CREATE_ZONE
        return self
        
    def existing_zone(self, zone_name: str) -> Self:
        """Target an existing zone for record management (chainable)"""
        self.spec.existing_zone_name = zone_name
        self.spec.operation_mode = DNSOperationMode.MANAGE_RECORDS
        
        # Resolve DNS name from existing zone to ensure consistent fingerprints
        self._resolve_existing_zone_dns_name(zone_name)
                
        return self
        
    def _resolve_existing_zone_dns_name(self, zone_name: str) -> None:
        """Resolve DNS name from existing zone for consistent fingerprint calculation"""
        # First try hardcoded mappings for known zones (most reliable for fingerprint consistency)
        zone_mappings = {
            "infradsl-dev-zone": "infradsl.dev."
        }
        
        if zone_name in zone_mappings:
            self.spec.dns_name = zone_mappings[zone_name]
            return
        
        # Try provider lookup as fallback
        if self._provider:
            try:
                from typing import cast
                provider = cast("ProviderInterface", self._provider)
                zone_info = provider.dns.get_managed_zone(zone_name)
                if zone_info and "dns_name" in zone_info:
                    self.spec.dns_name = zone_info["dns_name"]
                    return
            except Exception:
                # If lookup fails, DNS name will be resolved during provider operations
                pass
        
    def description(self, desc: str) -> Self:
        """Set zone description (chainable)"""
        self.spec.description = desc
        return self
        
    def public(self) -> Self:
        """Make zone public (chainable)"""
        self.spec.visibility = DNSVisibility.PUBLIC
        self.spec.networks = []
        return self
        
    def private(self, networks: List[str]) -> Self:
        """Make zone private for specific networks (chainable)"""
        self.spec.visibility = DNSVisibility.PRIVATE
        self.spec.networks = networks.copy()
        return self
        
    def dnssec(self, enabled: bool = True) -> Self:
        """Enable DNSSEC (chainable)"""
        self.spec.dnssec_enabled = enabled
        self.spec.dnssec_state = "on" if enabled else "off"
        return self
        
    # Record management helpers
    
    def _add_record(self, name: str, record_type: RecordType, ttl: int, 
                   rrdatas: Union[str, List[str]]) -> Self:
        """Add DNS record"""
        if isinstance(rrdatas, str):
            rrdatas = [rrdatas]
            
        # Handle @ symbol for zone apex
        if name == "@":
            name = self.spec.dns_name
        elif not name.endswith("."):
            name = f"{name}.{self.spec.dns_name}"
            
        record = DNSRecord(
            name=name,
            type=record_type,
            ttl=ttl,
            rrdatas=rrdatas
        )
        
        self.spec.records.append(record)
        return self
        
    # A records
    
    def a_record(self, name: str, ip: Union[str, List[str]], ttl: int = 300) -> Self:
        """Add A record (chainable)"""
        return self._add_record(name, RecordType.A, ttl, ip)
        
    def aaaa_record(self, name: str, ipv6: Union[str, List[str]], ttl: int = 300) -> Self:
        """Add AAAA record (chainable)"""
        return self._add_record(name, RecordType.AAAA, ttl, ipv6)
        
    # CNAME records
    
    def cname_record(self, name: str, target: str, ttl: int = 300) -> Self:
        """Add CNAME record (chainable)"""
        if not target.endswith("."):
            target += "."
        return self._add_record(name, RecordType.CNAME, ttl, target)
        
    def alias(self, name: str, target: str, ttl: int = 300) -> Self:
        """Alias for CNAME record (chainable)"""
        return self.cname_record(name, target, ttl)
        
    # MX records
    
    def mx_record(self, priority_server: List[Union[int, str]], ttl: int = 300) -> Self:
        """Add single MX record (chainable)"""
        priority = priority_server[0]
        server = priority_server[1]
        if not server.endswith("."):
            server += "."
        rrdata = f"{priority} {server}"
        return self._add_record("@", RecordType.MX, ttl, rrdata)
        
    def mx_records(self, records: List[List[Union[int, str]]], ttl: int = 300) -> Self:
        """Add multiple MX records (chainable)"""
        rrdatas = []
        for priority, server in records:
            if not server.endswith("."):
                server += "."
            rrdatas.append(f"{priority} {server}")
        return self._add_record("@", RecordType.MX, ttl, rrdatas)
        
    # TXT records
    
    def txt_record(self, name: str, value: Union[str, List[str]], ttl: int = 300) -> Self:
        """Add TXT record (chainable)"""
        if isinstance(value, str):
            value = [value]
        # Quote TXT values
        quoted_values = [f'"{v}"' if not v.startswith('"') else v for v in value]
        return self._add_record(name, RecordType.TXT, ttl, quoted_values)
        
    def spf_record(self, spf_value: str, ttl: int = 300) -> Self:
        """Add SPF record (as TXT) (chainable)"""
        return self.txt_record("@", spf_value, ttl)
        
    def dkim_record(self, selector: str, dkim_value: str, ttl: int = 300) -> Self:
        """Add DKIM record (chainable)"""
        return self.txt_record(f"{selector}._domainkey", dkim_value, ttl)
        
    def dmarc_record(self, dmarc_value: str, ttl: int = 300) -> Self:
        """Add DMARC record (chainable)"""
        return self.txt_record("_dmarc", dmarc_value, ttl)
        
    # SRV records
    
    def srv_record(self, service: str, priority: int, weight: int, port: int, 
                  target: str, ttl: int = 300) -> Self:
        """Add SRV record (chainable)"""
        if not target.endswith("."):
            target += "."
        rrdata = f"{priority} {weight} {port} {target}"
        return self._add_record(service, RecordType.SRV, ttl, rrdata)
        
    # CAA records
    
    def caa_record(self, name: str, flag: str, tag: str, value: str = None, ttl: int = 300) -> Self:
        """Add CAA record (chainable)"""
        if flag == "issue" or flag == "issuewild":
            rrdata = f'0 {flag} "{tag}"'
        else:
            rrdata = f'0 {flag} "{value}"' if value else f'0 {flag} "{tag}"'
        return self._add_record(name, RecordType.CAA, ttl, rrdata)
        
    # Common patterns
    
    def google_mx(self, ttl: int = 300) -> Self:
        """Add Google Workspace MX records (chainable)"""
        return self.mx_records([
            [1, "aspmx.l.google.com"],
            [5, "alt1.aspmx.l.google.com"],
            [5, "alt2.aspmx.l.google.com"],
            [10, "alt3.aspmx.l.google.com"],
            [10, "alt4.aspmx.l.google.com"]
        ], ttl)
        
    def office365_mx(self, domain_key: str, ttl: int = 300) -> Self:
        """Add Office 365 MX records (chainable)"""
        return self.mx_record([0, f"{domain_key}.mail.protection.outlook.com"], ttl)
        
    def sendgrid_cname(self, ttl: int = 300) -> Self:
        """Add SendGrid CNAME records (chainable)"""
        return (self
                .cname_record("em", "u123456.wl.sendgrid.net", ttl)
                .cname_record("s1._domainkey", "s1.domainkey.u123456.wl.sendgrid.net", ttl)
                .cname_record("s2._domainkey", "s2.domainkey.u123456.wl.sendgrid.net", ttl))
                
    def mailgun_records(self, subdomain: str = "mg", ttl: int = 300) -> Self:
        """Add Mailgun DNS records (chainable)"""
        return (self
                .mx_records([
                    [10, "mxa.mailgun.org"],
                    [10, "mxb.mailgun.org"]
                ], ttl)
                .txt_record(subdomain, "v=spf1 include:mailgun.org ~all", ttl)
                .cname_record(f"email.{subdomain}", "mailgun.org", ttl))
                
    # Verification records
    
    def google_verification(self, code: str, ttl: int = 300) -> Self:
        """Add Google site verification (chainable)"""
        return self.txt_record("@", f"google-site-verification={code}", ttl)
        
    def domain_verification(self, provider: str, code: str, ttl: int = 300) -> Self:
        """Add domain verification record (chainable)"""
        return self.txt_record("@", f"{provider}-domain-verification={code}", ttl)
        
    # Labels
    
    def label(self, key: str, value: str) -> Self:
        """Add a label (chainable)"""
        self.spec.labels[key] = value
        return self
        
    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set multiple labels (chainable)"""
        if labels_dict:
            self.spec.labels.update(labels_dict)
        if labels:
            self.spec.labels.update(labels)
        return self
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .dnssec()
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return self.label("environment", "staging")
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .label("environment", "development")
                .txt_record("_warning", "Development DNS zone - Do not use in production"))
                
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the DNS zone or manage records in existing zone via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the DNS zone via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the DNS zone via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )
        
    # Convenience methods
    
    def get_zone_name(self) -> str:
        """Get fully qualified zone name"""
        return self.spec.dns_name
        
    def get_nameservers(self) -> List[str]:
        """Get zone nameservers (from provider after creation)"""
        if self.status.provider_data and "nameservers" in self.status.provider_data:
            return self.status.provider_data["nameservers"]
        return []