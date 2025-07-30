"""
Region and Zone constants for cloud providers

This module provides typed constants for regions and zones across different cloud providers,
enabling IDE autocompletion and reducing string-based errors.
"""

from enum import Enum


class Region(Enum):
    """GCP Regions and Zones"""
    
    # US Regions
    US_CENTRAL1 = "us-central1"
    US_CENTRAL1_A = "us-central1-a"
    US_CENTRAL1_B = "us-central1-b"
    US_CENTRAL1_C = "us-central1-c"
    US_CENTRAL1_F = "us-central1-f"
    
    US_EAST1 = "us-east1"
    US_EAST1_B = "us-east1-b"
    US_EAST1_C = "us-east1-c"
    US_EAST1_D = "us-east1-d"
    
    US_EAST4 = "us-east4"
    US_EAST4_A = "us-east4-a"
    US_EAST4_B = "us-east4-b"
    US_EAST4_C = "us-east4-c"
    
    US_WEST1 = "us-west1"
    US_WEST1_A = "us-west1-a"
    US_WEST1_B = "us-west1-b"
    US_WEST1_C = "us-west1-c"
    
    US_WEST2 = "us-west2"
    US_WEST2_A = "us-west2-a"
    US_WEST2_B = "us-west2-b"
    US_WEST2_C = "us-west2-c"
    
    US_WEST3 = "us-west3"
    US_WEST3_A = "us-west3-a"
    US_WEST3_B = "us-west3-b"
    US_WEST3_C = "us-west3-c"
    
    US_WEST4 = "us-west4"
    US_WEST4_A = "us-west4-a"
    US_WEST4_B = "us-west4-b"
    US_WEST4_C = "us-west4-c"
    
    # Europe Regions
    EUROPE_NORTH1 = "europe-north1"
    EUROPE_NORTH1_A = "europe-north1-a"
    EUROPE_NORTH1_B = "europe-north1-b"
    EUROPE_NORTH1_C = "europe-north1-c"
    
    EUROPE_WEST1 = "europe-west1"
    EUROPE_WEST1_B = "europe-west1-b"
    EUROPE_WEST1_C = "europe-west1-c"
    EUROPE_WEST1_D = "europe-west1-d"
    
    EUROPE_WEST2 = "europe-west2"
    EUROPE_WEST2_A = "europe-west2-a"
    EUROPE_WEST2_B = "europe-west2-b"
    EUROPE_WEST2_C = "europe-west2-c"
    
    EUROPE_WEST3 = "europe-west3"
    EUROPE_WEST3_A = "europe-west3-a"
    EUROPE_WEST3_B = "europe-west3-b"
    EUROPE_WEST3_C = "europe-west3-c"
    
    EUROPE_WEST4 = "europe-west4"
    EUROPE_WEST4_A = "europe-west4-a"
    EUROPE_WEST4_B = "europe-west4-b"
    EUROPE_WEST4_C = "europe-west4-c"
    
    EUROPE_WEST6 = "europe-west6"
    EUROPE_WEST6_A = "europe-west6-a"
    EUROPE_WEST6_B = "europe-west6-b"
    EUROPE_WEST6_C = "europe-west6-c"
    
    EUROPE_WEST8 = "europe-west8"
    EUROPE_WEST8_A = "europe-west8-a"
    EUROPE_WEST8_B = "europe-west8-b"
    EUROPE_WEST8_C = "europe-west8-c"
    
    EUROPE_WEST9 = "europe-west9"
    EUROPE_WEST9_A = "europe-west9-a"
    EUROPE_WEST9_B = "europe-west9-b"
    EUROPE_WEST9_C = "europe-west9-c"
    
    EUROPE_WEST10 = "europe-west10"
    EUROPE_WEST10_A = "europe-west10-a"
    EUROPE_WEST10_B = "europe-west10-b"
    EUROPE_WEST10_C = "europe-west10-c"
    
    EUROPE_WEST12 = "europe-west12"
    EUROPE_WEST12_A = "europe-west12-a"
    EUROPE_WEST12_B = "europe-west12-b"
    EUROPE_WEST12_C = "europe-west12-c"
    
    EUROPE_CENTRAL2 = "europe-central2"
    EUROPE_CENTRAL2_A = "europe-central2-a"
    EUROPE_CENTRAL2_B = "europe-central2-b"
    EUROPE_CENTRAL2_C = "europe-central2-c"
    
    EUROPE_SOUTHWEST1 = "europe-southwest1"
    EUROPE_SOUTHWEST1_A = "europe-southwest1-a"
    EUROPE_SOUTHWEST1_B = "europe-southwest1-b"
    EUROPE_SOUTHWEST1_C = "europe-southwest1-c"
    
    # Asia Pacific Regions
    ASIA_EAST1 = "asia-east1"
    ASIA_EAST1_A = "asia-east1-a"
    ASIA_EAST1_B = "asia-east1-b"
    ASIA_EAST1_C = "asia-east1-c"
    
    ASIA_EAST2 = "asia-east2"
    ASIA_EAST2_A = "asia-east2-a"
    ASIA_EAST2_B = "asia-east2-b"
    ASIA_EAST2_C = "asia-east2-c"
    
    ASIA_NORTHEAST1 = "asia-northeast1"
    ASIA_NORTHEAST1_A = "asia-northeast1-a"
    ASIA_NORTHEAST1_B = "asia-northeast1-b"
    ASIA_NORTHEAST1_C = "asia-northeast1-c"
    
    ASIA_NORTHEAST2 = "asia-northeast2"
    ASIA_NORTHEAST2_A = "asia-northeast2-a"
    ASIA_NORTHEAST2_B = "asia-northeast2-b"
    ASIA_NORTHEAST2_C = "asia-northeast2-c"
    
    ASIA_NORTHEAST3 = "asia-northeast3"
    ASIA_NORTHEAST3_A = "asia-northeast3-a"
    ASIA_NORTHEAST3_B = "asia-northeast3-b"
    ASIA_NORTHEAST3_C = "asia-northeast3-c"
    
    ASIA_SOUTH1 = "asia-south1"
    ASIA_SOUTH1_A = "asia-south1-a"
    ASIA_SOUTH1_B = "asia-south1-b"
    ASIA_SOUTH1_C = "asia-south1-c"
    
    ASIA_SOUTH2 = "asia-south2"
    ASIA_SOUTH2_A = "asia-south2-a"
    ASIA_SOUTH2_B = "asia-south2-b"
    ASIA_SOUTH2_C = "asia-south2-c"
    
    ASIA_SOUTHEAST1 = "asia-southeast1"
    ASIA_SOUTHEAST1_A = "asia-southeast1-a"
    ASIA_SOUTHEAST1_B = "asia-southeast1-b"
    ASIA_SOUTHEAST1_C = "asia-southeast1-c"
    
    ASIA_SOUTHEAST2 = "asia-southeast2"
    ASIA_SOUTHEAST2_A = "asia-southeast2-a"
    ASIA_SOUTHEAST2_B = "asia-southeast2-b"
    ASIA_SOUTHEAST2_C = "asia-southeast2-c"
    
    # Australia
    AUSTRALIA_SOUTHEAST1 = "australia-southeast1"
    AUSTRALIA_SOUTHEAST1_A = "australia-southeast1-a"
    AUSTRALIA_SOUTHEAST1_B = "australia-southeast1-b"
    AUSTRALIA_SOUTHEAST1_C = "australia-southeast1-c"
    
    AUSTRALIA_SOUTHEAST2 = "australia-southeast2"
    AUSTRALIA_SOUTHEAST2_A = "australia-southeast2-a"
    AUSTRALIA_SOUTHEAST2_B = "australia-southeast2-b"
    AUSTRALIA_SOUTHEAST2_C = "australia-southeast2-c"
    
    # South America
    SOUTHAMERICA_EAST1 = "southamerica-east1"
    SOUTHAMERICA_EAST1_A = "southamerica-east1-a"
    SOUTHAMERICA_EAST1_B = "southamerica-east1-b"
    SOUTHAMERICA_EAST1_C = "southamerica-east1-c"
    
    SOUTHAMERICA_WEST1 = "southamerica-west1"
    SOUTHAMERICA_WEST1_A = "southamerica-west1-a"
    SOUTHAMERICA_WEST1_B = "southamerica-west1-b"
    SOUTHAMERICA_WEST1_C = "southamerica-west1-c"
    
    # Canada
    NORTHAMERICA_NORTHEAST1 = "northamerica-northeast1"
    NORTHAMERICA_NORTHEAST1_A = "northamerica-northeast1-a"
    NORTHAMERICA_NORTHEAST1_B = "northamerica-northeast1-b"
    NORTHAMERICA_NORTHEAST1_C = "northamerica-northeast1-c"
    
    NORTHAMERICA_NORTHEAST2 = "northamerica-northeast2"
    NORTHAMERICA_NORTHEAST2_A = "northamerica-northeast2-a"
    NORTHAMERICA_NORTHEAST2_B = "northamerica-northeast2-b"
    NORTHAMERICA_NORTHEAST2_C = "northamerica-northeast2-c"


# Backward compatibility aliases
GCPRegion = Region
Zone = Region


# AWS Regions (for future expansion)
class AWSRegion(Enum):
    """AWS Regions"""
    
    US_EAST_1 = "us-east-1"
    US_EAST_2 = "us-east-2"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    
    EU_WEST_1 = "eu-west-1"
    EU_WEST_2 = "eu-west-2"
    EU_WEST_3 = "eu-west-3"
    EU_CENTRAL_1 = "eu-central-1"
    EU_NORTH_1 = "eu-north-1"
    
    AP_SOUTHEAST_1 = "ap-southeast-1"
    AP_SOUTHEAST_2 = "ap-southeast-2"
    AP_NORTHEAST_1 = "ap-northeast-1"
    AP_NORTHEAST_2 = "ap-northeast-2"
    AP_SOUTH_1 = "ap-south-1"


# DigitalOcean Regions (for future expansion)
class DORegion(Enum):
    """DigitalOcean Regions"""
    
    NYC1 = "nyc1"
    NYC2 = "nyc2"
    NYC3 = "nyc3"
    
    AMS2 = "ams2"
    AMS3 = "ams3"
    
    SFO1 = "sfo1"
    SFO2 = "sfo2"
    SFO3 = "sfo3"
    
    SGP1 = "sgp1"
    LON1 = "lon1"
    FRA1 = "fra1"
    TOR1 = "tor1"
    BLR1 = "blr1"
    SYD1 = "syd1"