#!/usr/bin/env python3
"""
InfraDSL Core Configuration

Provides configuration management for the InfraDSL platform.
Handles user settings, authentication, and platform configuration.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def get_config_path() -> Path:
    """Get the path to the InfraDSL configuration file"""
    config_dir = Path.home() / ".infradsl"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def get_config() -> Dict[str, Any]:
    """
    Load InfraDSL configuration
    
    Returns:
        Configuration dictionary
    """
    config_path = get_config_path()
    
    if not config_path.exists():
        return {}
        
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        # If config is corrupted, return empty dict
        return {}


def set_config(config: Dict[str, Any]) -> bool:
    """
    Save InfraDSL configuration
    
    Args:
        config: Configuration dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def update_config(updates: Dict[str, Any]) -> bool:
    """
    Update specific configuration values
    
    Args:
        updates: Dictionary of updates to apply
        
    Returns:
        True if successful, False otherwise
    """
    config = get_config()
    
    # Deep merge updates
    def deep_merge(base: Dict, updates: Dict) -> Dict:
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    updated_config = deep_merge(config, updates)
    return set_config(updated_config)


def get_user_config() -> Dict[str, Any]:
    """
    Get user-specific configuration
    
    Returns:
        User configuration dictionary
    """
    config = get_config()
    return config.get('user', {})


def set_user_config(user_config: Dict[str, Any]) -> bool:
    """
    Set user-specific configuration
    
    Args:
        user_config: User configuration to save
        
    Returns:
        True if successful, False otherwise
    """
    return update_config({'user': user_config})


def get_auth_config() -> Dict[str, Any]:
    """
    Get authentication configuration
    
    Returns:
        Authentication configuration dictionary
    """
    config = get_config()
    return config.get('auth', {})


def set_auth_config(auth_config: Dict[str, Any]) -> bool:
    """
    Set authentication configuration
    
    Args:
        auth_config: Authentication configuration to save
        
    Returns:
        True if successful, False otherwise
    """
    return update_config({'auth': auth_config})


def get_registry_config() -> Dict[str, Any]:
    """
    Get registry configuration
    
    Returns:
        Registry configuration dictionary
    """
    config = get_config()
    return config.get('registry', {})


def set_registry_config(registry_config: Dict[str, Any]) -> bool:
    """
    Set registry configuration
    
    Args:
        registry_config: Registry configuration to save
        
    Returns:
        True if successful, False otherwise
    """
    return update_config({'registry': registry_config})


def clear_config() -> bool:
    """
    Clear all configuration
    
    Returns:
        True if successful, False otherwise
    """
    config_path = get_config_path()
    
    try:
        if config_path.exists():
            config_path.unlink()
        return True
    except Exception:
        return False


# Default configuration values
DEFAULT_CONFIG = {
    'user': {
        'name': '',
        'email': '',
        'workspace': ''
    },
    'auth': {
        'provider': 'firebase',
        'auto_refresh': True
    },
    'registry': {
        'url': 'https://registry.infradsl.dev',
        'auto_update': True
    },
    'cli': {
        'output_format': 'table',
        'color': True,
        'verbose': False
    }
}