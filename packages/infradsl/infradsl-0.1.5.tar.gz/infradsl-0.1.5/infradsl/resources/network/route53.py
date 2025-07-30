"""
AWS Route53 DNS
"""

from typing import Any, Dict, List, Optional, Union
from ...core.nexus.base_resource import BaseResource, ResourceSpec


class Route53(BaseResource):
    """
    AWS Route53 DNS with fluent API

    Usage:
        dns = AWS.Route53("my-dns")
              .use_existing_zone("example.com")
              .cloudfront_routing(ec="d123.cloudfront.net", eg="d456.cloudfront.net")
              .apex_alias("d123.cloudfront.net")
              .create()
    """

    def __init__(self, name: str):
        super().__init__(name)
        self._config = {
            "name": name,
            "existing_zone": None,
            "zone_id": None,
            "records": [],
            "routing_config": {},
            "apex_alias": None,
            "subdomain_aliases": {},
        }
        self._hosted_zone_id = None

    def _create_spec(self) -> ResourceSpec:
        """Create the resource-specific specification"""
        return ResourceSpec()

    def _validate_spec(self) -> None:
        """Validate the resource specification"""
        pass

    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        config = self._config.copy()
        
        # Resolve CloudFront domain names in records
        if "records" in config:
            resolved_records = []
            for record in config["records"]:
                resolved_record = record.copy()
                
                # Handle regular ResourceRecords
                if "ResourceRecords" in resolved_record:
                    resolved_resource_records = []
                    for rr in resolved_record["ResourceRecords"]:
                        resolved_rr = rr.copy()
                        # Check if Value is a CloudFront resource object
                        if hasattr(rr.get("Value"), "domain_name"):
                            cloudfront_resource = rr["Value"]
                            cloudfront_domain = cloudfront_resource.domain_name
                            
                            # If domain_name property is None, try getting it from provider_data
                            if not cloudfront_domain and cloudfront_resource.status.provider_data:
                                cloudfront_domain = cloudfront_resource.status.provider_data.get("DomainName")
                            
                            if cloudfront_domain:
                                resolved_rr["Value"] = cloudfront_domain
                            else:
                                # Domain name not available yet - this should not happen if dependencies are properly handled
                                raise ValueError(f"CloudFront domain name not available for record {record.get('Name', 'unknown')}. CloudFront resource: {cloudfront_resource.metadata.name}, Status: {cloudfront_resource.status.state}")
                        resolved_resource_records.append(resolved_rr)
                    resolved_record["ResourceRecords"] = resolved_resource_records
                
                # Handle Alias records
                if "AliasTarget" in resolved_record:
                    alias_target = resolved_record["AliasTarget"].copy()
                    # Check if DNSName is a CloudFront resource object
                    if hasattr(alias_target.get("DNSName"), "domain_name"):
                        cloudfront_resource = alias_target["DNSName"]
                        cloudfront_domain = cloudfront_resource.domain_name
                        
                        # If domain_name property is None, try getting it from provider_data
                        if not cloudfront_domain and cloudfront_resource.status.provider_data:
                            cloudfront_domain = cloudfront_resource.status.provider_data.get("DomainName")
                        
                        if cloudfront_domain:
                            alias_target["DNSName"] = cloudfront_domain
                        else:
                            raise ValueError(f"CloudFront domain name not available for alias record {record.get('Name', 'unknown')}. CloudFront resource: {cloudfront_resource.metadata.name}, Status: {cloudfront_resource.status.state}")
                    resolved_record["AliasTarget"] = alias_target
                
                resolved_records.append(resolved_record)
            config["records"] = resolved_records
        
        # Resolve CloudFront domain name in apex alias
        if "apex_alias" in config and hasattr(config["apex_alias"], "domain_name"):
            cloudfront_domain = config["apex_alias"].domain_name
            if cloudfront_domain:
                config["apex_alias"] = cloudfront_domain
            else:
                raise ValueError("CloudFront domain name not available for apex alias")
        
        return config

    def _provider_create(self) -> Dict[str, Any]:
        """Provider-specific create implementation"""
        if not self._provider:
            raise ValueError(
                "Provider not configured. Use AWS.Route53() to create this resource."
            )

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance. Use AWS.Route53() to create this resource."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        # Create the zone using the provider
        result = provider.create_route53_zone(self._config)

        # Store the zone ID for later use
        if result and "HostedZoneId" in result:
            self._hosted_zone_id = result["HostedZoneId"]

        return result

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Provider-specific update implementation"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        zone_name = self._config["existing_zone"] or self.metadata.name
        return provider.update_route53_zone(zone_name, self._config)

    def _provider_destroy(self) -> None:
        """Provider-specific destroy implementation"""
        if not self._provider:
            raise ValueError("Provider not configured.")

        if isinstance(self._provider, str):
            raise ValueError(
                f"Provider '{self._provider}' is not resolved to an actual provider instance."
            )

        # Type cast to help type checker
        from typing import cast

        provider = cast("Any", self._provider)

        if not self._config["existing_zone"]:
            provider.delete_route53_zone(self.metadata.name)

    def use_existing_zone(self, domain_name: str) -> "Route53":
        """Use an existing hosted zone"""
        self._config["existing_zone"] = domain_name
        return self

    def cloudfront_routing(self, **subdomain_mapping) -> "Route53":
        """
        Configure CloudFront routing for subdomains

        Args:
            **subdomain_mapping: mapping of subdomain prefixes to CloudFront domain names or CloudFront objects
                                (e.g., ec="d123.cloudfront.net", eg="d456.cloudfront.net", or ec=cdn_resource)
        """
        self._config["routing_config"] = subdomain_mapping

        # Create CNAME records for each subdomain
        for subdomain, cloudfront_target in subdomain_mapping.items():
            # Handle CloudFront resource objects
            if hasattr(cloudfront_target, "domain_name"):
                # Store the resource reference to resolve domain name later
                cloudfront_domain = cloudfront_target
            else:
                # Handle string domain names
                cloudfront_domain = cloudfront_target

            record = {
                "Name": f"{subdomain}.{self._config['existing_zone']}",
                "Type": "CNAME",
                "TTL": 300,
                "ResourceRecords": [{"Value": cloudfront_domain}],
            }
            self._config["records"].append(record)

        return self

    def apex_alias(self, cloudfront_target) -> "Route53":
        """
        Set up apex domain alias to CloudFront

        Args:
            cloudfront_target: CloudFront domain name or CloudFront resource object to alias to
        """
        # Handle CloudFront resource objects
        if hasattr(cloudfront_target, "domain_name"):
            cloudfront_domain = cloudfront_target
        else:
            cloudfront_domain = cloudfront_target

        self._config["apex_alias"] = cloudfront_domain

        # Create A alias record for the apex domain (apex domains can't be CNAME)
        record = {
            "Name": self._config["existing_zone"],
            "Type": "A",
            "AliasTarget": {
                "DNSName": cloudfront_domain,
                "EvaluateTargetHealth": False,
                "HostedZoneId": "Z2FDTNDATAQYW2",  # CloudFront hosted zone ID
            },
        }
        self._config["records"].append(record)

        return self

    def subdomain_alias(
        self, subdomain: str, target_domain: str, target_zone_id: Optional[str] = None
    ) -> "Route53":
        """
        Create subdomain alias

        Args:
            subdomain: subdomain name (e.g., 'www')
            target_domain: target domain name
            target_zone_id: target hosted zone ID (defaults to CloudFront zone)
        """
        if target_zone_id is None:
            target_zone_id = "Z2FDTNDATAQYW2"  # CloudFront hosted zone ID

        self._config["subdomain_aliases"][subdomain] = {
            "target_domain": target_domain,
            "target_zone_id": target_zone_id,
        }

        # Create A and AAAA records for the subdomain
        for record_type in ["A", "AAAA"]:
            record = {
                "Name": f"{subdomain}.{self._config['existing_zone']}",
                "Type": record_type,
                "AliasTarget": {
                    "DNSName": target_domain,
                    "EvaluateTargetHealth": False,
                    "HostedZoneId": target_zone_id,
                },
            }
            self._config["records"].append(record)

        return self

    def a_record(self, name: str, value: str, ttl: int = 300) -> "Route53":
        """Add an A record"""
        record = {
            "Name": name,
            "Type": "A",
            "TTL": ttl,
            "ResourceRecords": [{"Value": value}],
        }
        self._config["records"].append(record)
        return self

    def cname_record(self, name: str, value: str, ttl: int = 300) -> "Route53":
        """Add a CNAME record"""
        record = {
            "Name": name,
            "Type": "CNAME",
            "TTL": ttl,
            "ResourceRecords": [{"Value": value}],
        }
        self._config["records"].append(record)
        return self

    def mx_record(
        self, name: str, value: str, priority: int = 10, ttl: int = 300
    ) -> "Route53":
        """Add an MX record"""
        record = {
            "Name": name,
            "Type": "MX",
            "TTL": ttl,
            "ResourceRecords": [{"Value": f"{priority} {value}"}],
        }
        self._config["records"].append(record)
        return self

    def txt_record(self, name: str, value: str, ttl: int = 300) -> "Route53":
        """Add a TXT record"""
        record = {
            "Name": name,
            "Type": "TXT",
            "TTL": ttl,
            "ResourceRecords": [{"Value": f'"{value}"'}],
        }
        self._config["records"].append(record)
        return self

    def health_check(self, record_name: str, health_check_id: str) -> "Route53":
        """Add health check to a record"""
        # Find the record and add health check
        for record in self._config["records"]:
            if record["Name"] == record_name:
                record["HealthCheckId"] = health_check_id
                if "AliasTarget" in record:
                    record["AliasTarget"]["EvaluateTargetHealth"] = True
                break
        return self

    @property
    def hosted_zone_id(self) -> Optional[str]:
        """Get the hosted zone ID"""
        return self._hosted_zone_id

    @property
    def _resource_type(self) -> str:
        """Get resource type name for state detection"""
        return "Route53"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "config": self._config,
                "hosted_zone_id": self._hosted_zone_id,
            }
        )
        return base_dict
