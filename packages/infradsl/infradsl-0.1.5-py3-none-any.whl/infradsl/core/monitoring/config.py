"""
Monitoring Configuration - Configuration helpers for monitoring and notifications

This module provides configuration classes and utilities for setting up
monitoring and notification systems.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from .daemon import MonitoringPolicy
from .notifications import NotificationChannel, NotificationPriority, NotificationRule


@dataclass
class SlackConfig:
    """Slack notification configuration"""
    webhook_url: str
    channel: Optional[str] = None
    enabled: bool = True


@dataclass
class EmailConfig:
    """Email notification configuration"""
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    from_email: str
    use_tls: bool = True
    enabled: bool = True


@dataclass
class WebhookConfig:
    """Webhook notification configuration"""
    webhook_url: str
    headers: Optional[Dict[str, str]] = None
    enabled: bool = True


@dataclass
class DiscordConfig:
    """Discord notification configuration"""
    webhook_url: str
    username: Optional[str] = None
    enabled: bool = True


@dataclass
class TeamsConfig:
    """Microsoft Teams notification configuration"""
    webhook_url: str
    enabled: bool = True


@dataclass
class MonitoringConfig:
    """Complete monitoring configuration"""
    # Daemon settings
    default_interval: int = 300  # 5 minutes
    max_concurrent_checks: int = 10
    enable_intelligent_caching: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    # Notification settings
    slack: Optional[SlackConfig] = None
    email: Optional[EmailConfig] = None
    webhook: Optional[WebhookConfig] = None
    discord: Optional[DiscordConfig] = None
    teams: Optional[TeamsConfig] = None
    
    # Monitoring policies
    policies: List[Dict[str, Any]] = None
    
    # Custom rules
    notification_rules: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.policies is None:
            self.policies = []
        if self.notification_rules is None:
            self.notification_rules = []


class MonitoringConfigManager:
    """Configuration manager for monitoring systems"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_file()
        self.config: Optional[MonitoringConfig] = None
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path"""
        home_dir = Path.home()
        config_dir = home_dir / ".infradsl"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "monitoring.json")
    
    def load_config(self) -> MonitoringConfig:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Convert to config object
                self.config = self._dict_to_config(config_data)
                return self.config
            except Exception as e:
                print(f"Error loading config from {self.config_file}: {e}")
        
        # Return default config
        self.config = MonitoringConfig()
        return self.config
    
    def save_config(self, config: MonitoringConfig):
        """Save configuration to file"""
        try:
            config_data = self._config_to_dict(config)
            
            # Ensure directory exists
            config_dir = Path(self.config_file).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.config = config
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            print(f"Error saving config to {self.config_file}: {e}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> MonitoringConfig:
        """Convert dictionary to MonitoringConfig"""
        config = MonitoringConfig()
        
        # Basic settings
        config.default_interval = data.get("default_interval", 300)
        config.max_concurrent_checks = data.get("max_concurrent_checks", 10)
        config.enable_intelligent_caching = data.get("enable_intelligent_caching", True)
        config.cache_ttl = data.get("cache_ttl", 3600)
        
        # Slack config
        if "slack" in data and data["slack"]:
            slack_data = data["slack"]
            config.slack = SlackConfig(
                webhook_url=slack_data["webhook_url"],
                channel=slack_data.get("channel"),
                enabled=slack_data.get("enabled", True)
            )
        
        # Email config
        if "email" in data and data["email"]:
            email_data = data["email"]
            config.email = EmailConfig(
                smtp_server=email_data["smtp_server"],
                smtp_port=email_data["smtp_port"],
                username=email_data["username"],
                password=email_data["password"],
                from_email=email_data["from_email"],
                use_tls=email_data.get("use_tls", True),
                enabled=email_data.get("enabled", True)
            )
        
        # Webhook config
        if "webhook" in data and data["webhook"]:
            webhook_data = data["webhook"]
            config.webhook = WebhookConfig(
                webhook_url=webhook_data["webhook_url"],
                headers=webhook_data.get("headers"),
                enabled=webhook_data.get("enabled", True)
            )
        
        # Policies and rules
        config.policies = data.get("policies", [])
        config.notification_rules = data.get("notification_rules", [])
        
        return config
    
    def _config_to_dict(self, config: MonitoringConfig) -> Dict[str, Any]:
        """Convert MonitoringConfig to dictionary"""
        data = {
            "default_interval": config.default_interval,
            "max_concurrent_checks": config.max_concurrent_checks,
            "enable_intelligent_caching": config.enable_intelligent_caching,
            "cache_ttl": config.cache_ttl,
            "policies": config.policies,
            "notification_rules": config.notification_rules,
        }
        
        # Add notification configs
        if config.slack:
            data["slack"] = asdict(config.slack)
        
        if config.email:
            data["email"] = asdict(config.email)
        
        if config.webhook:
            data["webhook"] = asdict(config.webhook)
        
        if config.discord:
            data["discord"] = asdict(config.discord)
        
        if config.teams:
            data["teams"] = asdict(config.teams)
        
        return data
    
    def get_config(self) -> MonitoringConfig:
        """Get current configuration"""
        if self.config is None:
            return self.load_config()
        return self.config
    
    def create_sample_config(self) -> MonitoringConfig:
        """Create a sample configuration"""
        config = MonitoringConfig(
            default_interval=300,
            max_concurrent_checks=10,
            enable_intelligent_caching=True,
            cache_ttl=3600,
            slack=SlackConfig(
                webhook_url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                channel="#infrastructure-alerts"
            ),
            email=EmailConfig(
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                username="your-email@gmail.com",
                password="your-app-password",
                from_email="infradsl@yourcompany.com"
            ),
            webhook=WebhookConfig(
                webhook_url="https://your-webhook-endpoint.com/infradsl",
                headers={"Authorization": "Bearer your-token"}
            ),
            policies=[
                {
                    "name": "critical_resources",
                    "resource_filter": {
                        "environment": "production",
                        "labels": {"tier": "critical"}
                    },
                    "check_interval": 60,  # 1 minute
                    "priority": "high",
                    "auto_remediate": True,
                    "notification_channels": ["slack", "email"]
                },
                {
                    "name": "development_resources",
                    "resource_filter": {
                        "environment": "development"
                    },
                    "check_interval": 900,  # 15 minutes
                    "priority": "low",
                    "auto_remediate": False,
                    "notification_channels": ["slack"]
                }
            ],
            notification_rules=[
                {
                    "name": "critical_drift_all_channels",
                    "channels": ["slack", "email", "webhook"],
                    "event_types": ["drift_detected"],
                    "priority_threshold": "critical",
                    "filters": {},
                    "rate_limit": 5
                },
                {
                    "name": "high_drift_slack_email",
                    "channels": ["slack", "email"],
                    "event_types": ["drift_detected"],
                    "priority_threshold": "high",
                    "filters": {},
                    "rate_limit": 10
                }
            ]
        )
        
        return config


def create_monitoring_policies_from_config(policies_config: List[Dict[str, Any]]) -> List[MonitoringPolicy]:
    """Create MonitoringPolicy objects from configuration"""
    policies = []
    
    for policy_config in policies_config:
        policy = MonitoringPolicy(
            name=policy_config["name"],
            resource_filter=policy_config.get("resource_filter", {}),
            check_interval=policy_config.get("check_interval", 300),
            priority=policy_config.get("priority", "medium"),
            auto_remediate=policy_config.get("auto_remediate", False),
            notification_channels=policy_config.get("notification_channels", [])
        )
        policies.append(policy)
    
    return policies


def create_notification_rules_from_config(rules_config: List[Dict[str, Any]]) -> List[NotificationRule]:
    """Create NotificationRule objects from configuration"""
    rules = []
    
    for rule_config in rules_config:
        # Convert channel strings to enum values
        channels = []
        for channel_str in rule_config.get("channels", []):
            if channel_str == "slack":
                channels.append(NotificationChannel.SLACK)
            elif channel_str == "email":
                channels.append(NotificationChannel.EMAIL)
            elif channel_str == "webhook":
                channels.append(NotificationChannel.WEBHOOK)
            elif channel_str == "teams":
                channels.append(NotificationChannel.TEAMS)
            elif channel_str == "discord":
                channels.append(NotificationChannel.DISCORD)
        
        # Convert priority string to enum
        priority_str = rule_config.get("priority_threshold", "medium")
        priority = NotificationPriority.MEDIUM
        if priority_str == "low":
            priority = NotificationPriority.LOW
        elif priority_str == "high":
            priority = NotificationPriority.HIGH
        elif priority_str == "critical":
            priority = NotificationPriority.CRITICAL
        
        rule = NotificationRule(
            name=rule_config["name"],
            channels=channels,
            event_types=rule_config.get("event_types", []),
            priority_threshold=priority,
            filters=rule_config.get("filters", {}),
            template_name=rule_config.get("template_name"),
            rate_limit=rule_config.get("rate_limit"),
            enabled=rule_config.get("enabled", True)
        )
        rules.append(rule)
    
    return rules


# Global configuration manager
_config_manager = None


def get_config_manager() -> MonitoringConfigManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = MonitoringConfigManager()
    return _config_manager