"""
Application configuration management.
"""

import json
from typing import Any, Dict
from pathlib import Path


class Config:
    """Application configuration manager."""

    DEFAULT_CONFIG = {
        'connection': {
            'default_baudrate': 38400,
            'timeout': 3.0,
            'auto_reconnect': True,
            'reconnect_delay': 2.0
        },
        'gui': {
            'theme': 'dark',
            'window_width': 1280,
            'window_height': 720,
            'default_refresh_rate': 10  # Hz
        },
        'logging': {
            'auto_start': False,
            'default_pids': [0x0C, 0x0D, 0x05, 0x11]  # RPM, Speed, Temp, Throttle
        },
        'elm327': {
            'default_protocol': '0',  # Auto
            'echo': False,
            'headers': False,
            'spaces': True
        }
    }

    def __init__(self, config_file: str = None):
        """
        Initialize configuration.

        Args:
            config_file: Path to config JSON file
        """
        if config_file is None:
            config_file = 'config/app_config.json'

        self.config_file = Path(config_file)
        self.config = self.DEFAULT_CONFIG.copy()

        # Load from file if exists
        self.load()

    def load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._merge_config(self.config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {str(e)}")

    def save(self):
        """Save configuration to file."""
        # Ensure directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'connection.default_baudrate')
            default: Default value if key not found

        Returns:
            Configuration value.
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set value
        config[keys[-1]] = value

    def _merge_config(self, base: Dict, overlay: Dict):
        """
        Recursively merge overlay config into base.

        Args:
            base: Base configuration
            overlay: Overlay configuration
        """
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
