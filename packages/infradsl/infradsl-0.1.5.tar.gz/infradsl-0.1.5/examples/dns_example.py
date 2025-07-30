#!/usr/bin/env python3
"""
Simple GCP Cloud DNS Example
"""

from infradsl import GCP

# Configure GCP provider
GCP.configure("commandly-c1336", "eu-north1")

# Create a DNS zone with CNAME record
# Note: Using a test subdomain to avoid conflicts with existing zones
import uuid

zone_id = f"test-zone-{str(uuid.uuid4())[:8]}"
dns_record = (
    GCP.CloudDNS(zone_id)
    .zone("example-test.com.")
    .cname_record("api", "infradsl.dev")  # api.example-test.com -> infradsl.dev
    .staging()
)
