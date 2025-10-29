"""Configuration management for Preset Qualifier Project."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager for the project."""

    def __init__(self, config_file: str = None):
        """Initialize configuration from YAML file."""
        if config_file is None:
            # Default to config/default.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_file = project_root / "config" / "default.yaml"

        self.config_file = Path(config_file)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing configuration file: {e}")

    def get(self, key: str, default=None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_path(self, key: str) -> Path:
        """Get path configuration value as Path object."""
        path_str = self.get(key)
        if path_str:
            # Resolve relative to project root
            project_root = Path(__file__).parent.parent.parent
            return project_root / path_str
        return None

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in configuration."""
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return True
        except (KeyError, TypeError):
            return False


# Global configuration instance
config = Config()