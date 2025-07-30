#!/usr/bin/env python3
"""
NoLimit City Infrastructure Setup
=================================

Creates complete infrastructure for NoLimit City gaming platform including:
- Domain registration with DNS setup
- SSL certificates with automatic validation
- CloudFront CDN distributions for gaming content
- S3 bucket policies for secure access
- Route53 DNS routing configuration

Usage:
    infra preview nolimitcity/dns_creation.py     # Preview changes
    infra apply nolimitcity/dns_creation.py --production  # Apply to AWS
"""

from infradsl import AWS, DriftAction

DOMAIN = "ad2cieaxtyw.com"
SUBDOMAINS = {"cdn": ["ec", "nc"], "game": ["eg", "ng"]}
REFERENCE_DISTRIBUTIONS = {"cdn": "E1L4Q3EMY24Z8R", "game": "E2V4BM77LJFYB6"}
ORIGIN_IDS = {
    "game": "production.nolimitcity.com",
    "cdn": "nl-games-ureg.s3.eu-west-1.amazonaws.com-origin",
}

CERT = ""

# CDN distributions
cdn = (
    AWS.CloudFront(f"cdn-{DOMAIN.replace('.', '-')}")
    .copy_from(REFERENCE_DISTRIBUTIONS["cdn"])
    .clear_domains()
    .custom_domain(f"{SUBDOMAINS['cdn'][0]}.{DOMAIN}")
    .custom_domain(f"{SUBDOMAINS['cdn'][1]}.{DOMAIN}")
    .target_origin_id(ORIGIN_IDS["cdn"])
    .ssl_certificate(CERT)
    .drift_policy(DriftAction.IGNORE)
)

game_cdn = (
    AWS.CloudFront(f"game-{DOMAIN.replace('.', '-')}")
    .copy_from(REFERENCE_DISTRIBUTIONS["game"])
    .origin(
        domain_name=ORIGIN_IDS["cdn"],
        origin_id="nl-games-ureg.s3.eu-west-1.amazonaws.com",
    )
    .clear_domains()
    .custom_domain(f"{SUBDOMAINS['game'][0]}.{DOMAIN}")
    .custom_domain(f"{SUBDOMAINS['game'][1]}.{DOMAIN}")
    .target_origin_id(ORIGIN_IDS["game"])
    .ssl_certificate(CERT)
    .enable_all_methods()
    .drift_policy(DriftAction.IGNORE)
)

# S3 bucket policy
bucket = (
    AWS.S3("nl-games-ureg-policy")
    .existing_bucket("nl-games-ureg")
    .allow_cloudfront(cdn)
    .depends_on(cdn)
    .drift_policy(DriftAction.IGNORE)
)

# DNS routing
dns = (
    AWS.Route53(f"dns-{DOMAIN}")
    .use_existing_zone(DOMAIN)
    .drift_policy(DriftAction.IGNORE)
    .cloudfront_routing(
        ec=cdn.domain_name,
        eg=game_cdn.domain_name,
        nc=cdn.domain_name,
        ng=game_cdn.domain_name,
    )
    .apex_alias(cdn.domain_name)
    .depends_on(cdn)
    .depends_on(game_cdn)
)
