#!/usr/bin/env python3
"""
LEGO Principle Demo - Progressive Infrastructure Building

This example demonstrates how InfraDSL allows you to progressively add 
components to your infrastructure without recreating or modifying the base VM.

Start simple, then add components like LEGO blocks!
"""

from infradsl import GoogleCloud, InstanceSize, Region
from infradsl.notifications import notify_discord

# Configure notifications
notify_discord(
    "https://discord.com/api/webhooks/1396177973232799785/2Otw6rl5L9ThFam9_iNGOMj-GTJTvYpv7xqr_qs1133e6NDbKP8ttxt0fmkNLkbpncPG"
)

# WEEK 1: Start with a simple VM
# This creates the base infrastructure
vm = (
    GoogleCloud.VM("web-app")
    .ubuntu(22_04)
    .size(InstanceSize.SMALL)
    .zone(Region.EUROPE_WEST1_B)
    .disk(20)
    .public_ip(True)
    .environment("development")
    .labels(project="lego-demo", purpose="web-app")
)

# WEEK 2: Add database (LEGO component - no VM recreation!)
# When you uncomment the lines below and run `infra apply`, 
# InfraDSL will:
# - Keep your VM exactly as it is
# - Create a new managed database
# - Configure networking between VM and database
# - Zero downtime!

# vm = (
#     GoogleCloud.VM("web-app")
#     .ubuntu(22_04)
#     .size(InstanceSize.SMALL)
#     .zone(Region.EUROPE_WEST1_B)
#     .disk(20)
#     .public_ip(True)
#     .environment("development")
#     .labels(project="lego-demo", purpose="web-app")
#     .database("postgres", size="small")  # <-- LEGO: Add database
# )

# WEEK 3: Add load balancer (LEGO component - no VM recreation!)
# vm = (
#     GoogleCloud.VM("web-app")
#     .ubuntu(22_04)
#     .size(InstanceSize.SMALL)
#     .zone(Region.EUROPE_WEST1_B)
#     .disk(20)
#     .public_ip(True)
#     .environment("development")
#     .labels(project="lego-demo", purpose="web-app")
#     .database("postgres", size="small")
#     .load_balancer()  # <-- LEGO: Add load balancer
# )

# WEEK 4: Add monitoring (LEGO component - no VM recreation!)
# vm = (
#     GoogleCloud.VM("web-app")
#     .ubuntu(22_04)
#     .size(InstanceSize.SMALL)
#     .zone(Region.EUROPE_WEST1_B)
#     .disk(20)
#     .public_ip(True)
#     .environment("development")
#     .labels(project="lego-demo", purpose="web-app")
#     .database("postgres", size="small")
#     .load_balancer()
#     .monitoring(alerts=True)  # <-- LEGO: Add monitoring
# )

# WEEK 5: Expand disk (In-place update - no VM recreation!)
# vm = (
#     GoogleCloud.VM("web-app")
#     .ubuntu(22_04)
#     .size(InstanceSize.SMALL)
#     .zone(Region.EUROPE_WEST1_B)
#     .disk(100)  # <-- LEGO: Disk expansion in-place
#     .public_ip(True)
#     .environment("development")
#     .labels(project="lego-demo", purpose="web-app")
#     .database("postgres", size="small")
#     .load_balancer()
#     .monitoring(alerts=True)
# )

# WEEK 6: Add SSL certificate (LEGO component - no VM recreation!)
# vm = (
#     GoogleCloud.VM("web-app")
#     .ubuntu(22_04)
#     .size(InstanceSize.SMALL)
#     .zone(Region.EUROPE_WEST1_B)
#     .disk(100)
#     .public_ip(True)
#     .environment("development")
#     .labels(project="lego-demo", purpose="web-app")
#     .database("postgres", size="small")
#     .load_balancer()
#     .monitoring(alerts=True)
#     .ssl_cert("myapp.com")  # <-- LEGO: Add SSL certificate
# )

print("🧱 LEGO Principle Demo")
print("=" * 50)
print()
print("This VM demonstrates the LEGO principle:")
print("✅ Start simple with a basic VM")
print("✅ Add components progressively") 
print("✅ Never recreate the base VM")
print("✅ Zero downtime operations")
print()
print("To see LEGO in action:")
print("1. Run 'infra apply' to create the base VM")
print("2. Uncomment the WEEK 2 code and run 'infra apply' again")
print("3. Notice that the VM is never recreated!")
print("4. Continue with WEEK 3, 4, 5, 6...")
print()
print("Each week adds new capabilities without touching")
print("the original VM - just like building with LEGO blocks!")