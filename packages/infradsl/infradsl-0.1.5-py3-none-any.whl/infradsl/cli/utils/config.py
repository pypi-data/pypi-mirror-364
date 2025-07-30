"""
CLI configuration management
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CLIConfig:
    """CLI configuration"""

    project: Optional[str] = None
    environment: Optional[str] = None
    provider_configs: Optional[Dict[str, Dict[str, Any]]] = None
    default_region: Optional[str] = None
    default_output_format: str = "table"
    auto_approve: bool = False
    timeout: int = 300

    def __post_init__(self):
        if self.provider_configs is None:
            self.provider_configs = {}

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "CLIConfig":
        """Load configuration from file"""
        if config_path is None:
            # Try to find config file in current directory or home
            config_path = Path.cwd() / "infradsl.yaml"
            if not config_path.exists():
                config_path = Path.home() / ".infradsl" / "config.yaml"

        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "r") as f:
                if config_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f)

            return cls(**data)
        except Exception:
            # If config file is invalid, return default config
            return cls()

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file"""
        if config_path is None:
            config_path = Path.cwd() / "infradsl.yaml"

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            yaml.dump(asdict(self), f, default_flow_style=False)

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider-specific configuration"""
        if self.provider_configs is None:
            return {}
        return self.provider_configs.get(provider, {})

    def set_provider_config(self, provider: str, config: Dict[str, Any]) -> None:
        """Set provider-specific configuration"""
        if self.provider_configs is None:
            self.provider_configs = {}
        self.provider_configs[provider] = config
