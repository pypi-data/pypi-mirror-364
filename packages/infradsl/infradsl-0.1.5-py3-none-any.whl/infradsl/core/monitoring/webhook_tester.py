"""
Webhook Testing Utilities

This module provides utilities for testing webhook configurations and
troubleshooting notification delivery.
"""

import asyncio
import aiohttp
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict

from .notifications import (
    NotificationManager,
    NotificationEvent,
    NotificationPriority,
    NotificationChannel,
    SlackNotifier,
    DiscordNotifier,
    TeamsNotifier,
    WebhookNotifier
)


class WebhookTester:
    """Webhook testing and validation utility"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_webhook_url(self, url: str, webhook_type: str = "generic") -> Dict[str, Any]:
        """Test a webhook URL with a simple payload"""
        print(f"🧪 Testing {webhook_type} webhook: {url[:50]}...")
        
        test_payload = self._create_test_payload(webhook_type)
        
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=test_payload, timeout=10) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    result = {
                        "webhook_type": webhook_type,
                        "url": url,
                        "status_code": response.status,
                        "response_time_ms": round(response_time, 2),
                        "success": self._is_success_status(response.status, webhook_type),
                        "response_headers": dict(response.headers),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                    try:
                        response_text = await response.text()
                        if response_text:
                            result["response_body"] = response_text[:500]  # Truncate long responses
                    except:
                        result["response_body"] = None
                    
                    return result
                    
        except asyncio.TimeoutError:
            return {
                "webhook_type": webhook_type,
                "url": url,
                "status_code": None,
                "response_time_ms": None,
                "success": False,
                "error": "Request timeout (10s)",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "webhook_type": webhook_type,
                "url": url,
                "status_code": None,
                "response_time_ms": None,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def _create_test_payload(self, webhook_type: str) -> Dict[str, Any]:
        """Create appropriate test payload for webhook type"""
        if webhook_type == "slack":
            return {
                "text": "🧪 InfraDSL Webhook Test",
                "username": "InfraDSL Test",
                "icon_emoji": ":test_tube:",
                "attachments": [{
                    "color": "good",
                    "text": "This is a test message from InfraDSL webhook tester.",
                    "footer": "InfraDSL Webhook Tester",
                    "ts": int(time.time())
                }]
            }
        elif webhook_type == "discord":
            return {
                "username": "InfraDSL Test",
                "content": "🧪 **InfraDSL Webhook Test**",
                "embeds": [{
                    "title": "Webhook Test",
                    "description": "This is a test message from InfraDSL webhook tester.",
                    "color": 0x00FF00,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "footer": {"text": "InfraDSL Webhook Tester"}
                }]
            }
        elif webhook_type == "teams":
            return {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": "InfraDSL Webhook Test",
                "themeColor": "00FF00",
                "sections": [{
                    "activityTitle": "🧪 InfraDSL Webhook Test",
                    "activitySubtitle": "Testing webhook connectivity",
                    "facts": [
                        {"name": "Test Type", "value": "Webhook Connectivity"},
                        {"name": "Timestamp", "value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")},
                        {"name": "Status", "value": "Test Message"}
                    ]
                }]
            }
        else:  # generic webhook
            return {
                "test": True,
                "message": "InfraDSL webhook test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "webhook_type": webhook_type,
                "test_id": str(uuid.uuid4())
            }
    
    def _is_success_status(self, status_code: int, webhook_type: str) -> bool:
        """Check if status code indicates success for webhook type"""
        if webhook_type == "discord":
            return status_code == 204  # Discord returns 204 for successful webhooks
        else:
            return 200 <= status_code < 300  # General 2xx success range
    
    async def test_notification_manager(self, manager: NotificationManager) -> Dict[str, Any]:
        """Test a configured NotificationManager"""
        print("🧪 Testing NotificationManager configuration...")
        
        # Create a test event
        test_event = NotificationEvent(
            id=str(uuid.uuid4()),
            event_type="webhook_test",
            resource_id="test-resource-123",
            resource_name="test-webhook",
            resource_type="TestResource",
            message="This is a test notification from InfraDSL webhook tester",
            details={"test": True, "timestamp": datetime.now(timezone.utc).isoformat()},
            timestamp=datetime.now(timezone.utc),
            priority=NotificationPriority.LOW,
            project="test-project",
            environment="testing",
            tags=["test", "webhook"]
        )
        
        # Send notification and measure results
        start_time = time.time()
        results = await manager.send_notification(test_event)
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        
        return {
            "test_event_id": test_event.id,
            "total_time_ms": round(total_time, 2),
            "channels_tested": len(results),
            "successful_channels": sum(1 for success in results.values() if success),
            "failed_channels": sum(1 for success in results.values() if not success),
            "results_by_channel": {channel.value: success for channel, success in results.items()},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def validate_webhook_configs(self, webhooks: Dict[str, str]) -> List[Dict[str, Any]]:
        """Validate multiple webhook configurations"""
        print(f"🔍 Validating {len(webhooks)} webhook configurations...")
        
        results = []
        for webhook_type, url in webhooks.items():
            if url and not url.startswith("http"):
                results.append({
                    "webhook_type": webhook_type,
                    "url": url,
                    "success": False,
                    "error": "Invalid URL format - must start with http:// or https://",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                continue
            
            if url and "PLACEHOLDER" not in url.upper():
                result = await self.test_webhook_url(url, webhook_type)
                results.append(result)
            else:
                results.append({
                    "webhook_type": webhook_type,
                    "url": url,
                    "success": False,
                    "error": "Placeholder URL - replace with actual webhook URL",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
        
        return results
    
    def print_test_results(self, results: List[Dict[str, Any]]):
        """Print formatted test results"""
        print("\n📊 Webhook Test Results")
        print("=" * 40)
        
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"🔗 Total Tested: {len(results)}")
        
        if successful:
            print("\n✅ Successful Webhooks:")
            for result in successful:
                webhook_type = result["webhook_type"].upper()
                response_time = result.get("response_time_ms", "N/A")
                status = result.get("status_code", "N/A")
                print(f"   {webhook_type}: {status} ({response_time}ms)")
        
        if failed:
            print("\n❌ Failed Webhooks:")
            for result in failed:
                webhook_type = result["webhook_type"].upper()
                error = result.get("error", f"HTTP {result.get('status_code', 'Error')}")
                print(f"   {webhook_type}: {error}")
    
    def generate_test_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a detailed test report"""
        successful = len([r for r in results if r.get("success", False)])
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        report = f"""
# InfraDSL Webhook Test Report

**Test Summary:**
- Total webhooks tested: {total}
- Successful: {successful}
- Failed: {total - successful}
- Success rate: {success_rate:.1f}%
- Test timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

## Detailed Results:

"""
        
        for result in results:
            webhook_type = result["webhook_type"].upper()
            url = result["url"][:50] + "..." if len(result["url"]) > 50 else result["url"]
            
            report += f"### {webhook_type}\n"
            report += f"- URL: `{url}`\n"
            report += f"- Status: {'✅ Success' if result.get('success') else '❌ Failed'}\n"
            
            if result.get("status_code"):
                report += f"- HTTP Status: {result['status_code']}\n"
            if result.get("response_time_ms"):
                report += f"- Response Time: {result['response_time_ms']}ms\n"
            if result.get("error"):
                report += f"- Error: {result['error']}\n"
            
            report += "\n"
        
        return report


async def quick_webhook_test(webhook_url: str, webhook_type: str = "generic") -> bool:
    """Quick test of a single webhook URL"""
    tester = WebhookTester()
    result = await tester.test_webhook_url(webhook_url, webhook_type)
    
    success = result.get("success", False)
    if success:
        print(f"✅ {webhook_type.upper()} webhook test successful ({result.get('response_time_ms', 'N/A')}ms)")
    else:
        error = result.get("error", f"HTTP {result.get('status_code', 'Error')}")
        print(f"❌ {webhook_type.upper()} webhook test failed: {error}")
    
    return success


async def test_all_webhooks(slack_url: str = None, discord_url: str = None, 
                          teams_url: str = None, webhook_url: str = None) -> Dict[str, bool]:
    """Test all provided webhook URLs"""
    tester = WebhookTester()
    
    webhooks = {}
    if slack_url:
        webhooks["slack"] = slack_url
    if discord_url:
        webhooks["discord"] = discord_url
    if teams_url:
        webhooks["teams"] = teams_url
    if webhook_url:
        webhooks["generic"] = webhook_url
    
    results = await tester.validate_webhook_configs(webhooks)
    tester.print_test_results(results)
    
    return {r["webhook_type"]: r.get("success", False) for r in results}


if __name__ == "__main__":
    # Example usage
    async def main():
        print("🧪 InfraDSL Webhook Tester")
        print("========================")
        
        # Test individual webhook (replace with your actual URL)
        await quick_webhook_test(
            "https://httpbin.org/post",  # Test endpoint
            "generic"
        )
        
        # Test multiple webhooks
        webhook_results = await test_all_webhooks(
            slack_url="https://httpbin.org/post",  # Replace with actual Slack webhook
            discord_url="https://httpbin.org/status/204",  # Replace with actual Discord webhook
            teams_url="https://httpbin.org/post",  # Replace with actual Teams webhook
        )
        
        print(f"\n📊 Overall Results: {sum(webhook_results.values())}/{len(webhook_results)} webhooks working")
    
    asyncio.run(main())