#!/usr/bin/env python3
"""
Add DNS Records to Existing Zone Example

This example shows how to add records to an existing DNS zone
rather than creating a new zone.
"""

from infradsl import GCP

# Configure GCP provider
GCP.configure("commandly-c1336", "eu-north1")

# Add records to your existing zone
existing_zone_record = (
    GCP.CloudDNS("api-records-v2")  # Resource name for tracking
    .existing_zone("infradsl-dev-zone")  # Your existing GCP zone name
    .cname_record("api-v2", "infradsl.dev")  # api-v2.infradsl.dev -> infradsl.dev
    .a_record("app-v2", "203.0.113.15")  # app-v2.infradsl.dev -> 203.0.113.15
    .txt_record(
        "_verification-v2", "domain-verification-code-67890"
    )  # verification record
)

# Example with staging environment label (use different record names)
staging_records = (
    GCP.CloudDNS("staging-api-records-v2")
    .existing_zone("infradsl-dev-zone")
    .a_record("staging-v2", "203.0.113.25")
    .cname_record("staging-api-v2", "staging.infradsl.dev")
    .staging()
)

# You can also manage records for private zones
# private_zone_records = (
#     GCP.CloudDNS("internal-records")
#     .existing_zone("internal-zone-name")
#     .a_record("database", "10.0.1.100")
#     .a_record("redis", "10.0.1.101")
#     .cname_record("db", "database.internal.mycompany.net")
# )
