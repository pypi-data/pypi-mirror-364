#!/usr/bin/env python3
"""
Super Simple VM with Discord Notifications

One-liner notification setup - Rails-like simplicity!
"""

from infradsl import GCP, GoogleCloud, InstanceSize, Region
from infradsl.notifications import notify_discord

# Configure GCP provider (required)
GCP.configure(project="your-project-id", region="us-central1")

# One line to configure Discord notifications for ALL lifecycle events! 🎉
notify_discord(
    "https://discord.com/api/webhooks/1396177973232799785/2Otw6rl5L9ThFam9_iNGOMj-GTJTvYpv7xqr_qs1133e6NDbKP8ttxt0fmkNLkbpncPG"
)

# Create your VM - notifications are automatic!
# vm = (
#     GoogleCloud.VM("simple-notif-vm")
#     .ubuntu(22_04)
#     .size(InstanceSize.SMALL)
#     .zone(Region.EUROPE_WEST1_B)
#     .disk(20)
#     .public_ip(True)
#     .environment("development")
#     .labels(project="demo", notifications="auto")
# )

# Create DNS record using GCP factory (with provider attached)
dns_record = (
    GCP.CloudDNS("test-api-zone")
    .zone("example.com")                          # Domain name (not GCP zone!)
    .cname_record("api", "infradsl.dev")         # api.example.com -> infradsl.dev
    .staging()
)