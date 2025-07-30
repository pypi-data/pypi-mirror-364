#!/usr/bin/env python3
"""
Multi-Channel Notifications Example

Send notifications to Discord, Slack, Teams, and custom webhooks simultaneously!
"""

from infradsl import GoogleCloud, InstanceSize, Region
from infradsl.notifications import notify_all

# Configure multiple notification channels at once! 🚀
notify_all(
    discord="https://discord.com/api/webhooks/1396177973232799785/2Otw6rl5L9ThFam9_iNGOMj-GTJTvYpv7xqr_qs1133e6NDbKP8ttxt0fmkNLkbpncPG",
    # slack="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",     # Uncomment to add Slack
    # teams="https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK",   # Uncomment to add Teams
    # webhook="https://your-api.com/infradsl-webhook"                  # Uncomment to add custom webhook
)

# Production VM with comprehensive monitoring
production_vm = (
    GoogleCloud.VM("prod-web-server")
    .ubuntu(22_04)
    .size(InstanceSize.MEDIUM)
    .zone(Region.EUROPE_WEST1_B)
    .disk(50)
    .public_ip(True)
    .environment("production")
    .labels(
        team="platform",
        service="web",
        criticality="high",
        monitoring="enabled"
    )
)

# Development VM with basic monitoring  
dev_vm = (
    GoogleCloud.VM("dev-test-server")
    .ubuntu(22_04)
    .size(InstanceSize.SMALL)
    .zone(Region.EUROPE_WEST1_B) 
    .disk(20)
    .public_ip(True)
    .environment("development")
    .labels(
        team="dev",
        purpose="testing",
        temporary="true"
    )
)

print("🎯 Multi-channel notifications configured!")
print("📱 Notifications will be sent to:")
print("   ✅ Discord (configured)")
print("   ➖ Slack (add your webhook URL)")
print("   ➖ Teams (add your webhook URL)")
print("   ➖ Custom Webhook (add your endpoint)")
print("\n🏗️ Infrastructure configured:")
print(f"   🏭 Production VM: {production_vm.name}")
print(f"   🧪 Development VM: {dev_vm.name}")
print("\n💡 Tips:")
print("   • Uncomment webhook URLs above to enable more channels")
print("   • All VMs automatically get lifecycle notifications")
print("   • Production environments get higher priority alerts")
print("\n▶️ Run 'infra apply' to deploy and start receiving notifications!")