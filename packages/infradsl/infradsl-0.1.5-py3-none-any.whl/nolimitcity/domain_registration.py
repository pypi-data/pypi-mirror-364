#!/usr/bin/env python3

"""
# Domain Registration and SSL Certificate Setup

This Python script automates the process of domain registration and SSL certificate creation using AWS services through InfraDSL.

## Features

- Automatic domain name registration with AWS Route 53
- SSL certificate generation via AWS Certificate Manager
- DNS validation for the SSL certificate
- CloudFront CDN compatibility
- Privacy protection for domain registration
- Configurable contact information

## Usage

The script will:
1. Generate a random domain name (or use a specified one)
2. Register the domain with AWS Route 53
3. Create a wildcard SSL certificate for the domain
4. Set up automatic DNS validation
5. Make the certificate compatible with CloudFront

## Configuration

Update the following variables according to your needs:
    - DOMAIN: The domain name to register
    - CONTACT_EMAIL: The email address to use for contact information
    - CONTACT_NAME: The name to use for contact information
    - CONTACT_PHONE: The phone number to use for contact information

"""

from infradsl import AWS

# Configure AWS provider
AWS.configure(region="us-east-1")

import random
import string


def generate_random_domain(length=10):
    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for _ in range(length)) + ".com"


# Configuration (customize these for your setup)
DOMAIN = generate_random_domain()
CONTACT_EMAIL = "bia@nolimitcity.com"
CONTACT_NAME = "bia andersson"
CONTACT_PHONE = "+46708339809"

# Step 1: Domain registration with automatic DNS setup
domain = (
    AWS.DomainRegistration(DOMAIN)
    .domain(DOMAIN)
    .contact(
        email=CONTACT_EMAIL,
        first_name=CONTACT_NAME.split()[0],
        last_name=CONTACT_NAME.split()[1],
        organization="Nolimit City Stockholm AB",
        phone=CONTACT_PHONE,
        address="Kungsgatan 49",
        city="Stockholm",
        zip_code="611 32",
        country="SE",
        state="Stockholm",
    )
    .duration(1)
    .privacy(True)
    .auto_renew(False)
)

# Step 2: SSL Certificate with automatic DNS validation
certificate = (
    AWS.CertificateManager("nolimitcity-domains")
    .domain(domain.domain_name)
    .wildcard()
    .dns_validation()
    .auto_renew(False)
    .cloudfront_compatible()
    .depends_on(domain)
)

print(f"The domain {DOMAIN} has been registered!")
print(f"The SSL certificate for {DOMAIN} has been created!")
print(
    f"The ARN of the Certificate Manager Certificate is: {certificate.certificate_arn}"
)
