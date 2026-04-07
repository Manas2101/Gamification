"""
Configuration Module
====================

Application configuration management and logging setup.

Handles loading configuration from:
    - Environment variables
    - YAML configuration files
    - Default values

Example:
    >>> from src.utils.config import Config, setup_logging
    >>> setup_logging()
    >>> config = Config()
    >>> token = config.get("GITHUB_TOKEN")

Author: DevOps Transformation Team
"""

import os
import logging
from typing import Any, Dict, Optional
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_logging(
    level: str = "INFO",
    log_file: str = None,
    format_string: str = None
):
    """
    Configure application logging.
    
    Sets up logging with console output and optional file output.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional path to log file.
        format_string: Optional custom format string.
    """
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Get numeric level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=numeric_level,
        format=format_string,
        handlers=handlers
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


class Config:
    """
    Application configuration manager.
    
    Loads and provides access to configuration values from
    environment variables and YAML files.
    
    Attributes:
        settings (dict): Loaded settings from YAML
        
    Example:
        >>> config = Config()
        >>> db_path = config.get("DB_PATH", "metrics.db")
        >>> github_token = config.github_token
    """
    
    # Default configuration values
    DEFAULTS = {
        'DB_PATH': 'metrics.db',
        'REGISTRY_DIR': 'apps',
        'LOG_LEVEL': 'INFO',
        'API_TIMEOUT': 30,
        'ENABLE_DOCS_GENERATION': False
    }
    
    def __init__(self, settings_path: str = None):
        """
        Initialize configuration.
        
        Args:
            settings_path: Path to settings.yaml file.
                          Defaults to config/settings.yaml.
        """
        self.settings = {}
        self._load_settings(settings_path)
    
    def _load_settings(self, settings_path: str = None):
        """
        Load settings from YAML file.
        
        Args:
            settings_path: Path to settings file.
        """
        if settings_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent.parent
            settings_path = project_root / "config" / "settings.yaml"
        
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    self.settings = yaml.safe_load(f) or {}
                logging.debug(f"Loaded settings from {settings_path}")
            except Exception as e:
                logging.warning(f"Could not load settings: {e}")
                self.settings = {}
        else:
            logging.debug(f"Settings file not found: {settings_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Checks in order:
        1. Environment variables
        2. Settings file
        3. Default values
        4. Provided default
        
        Args:
            key: Configuration key.
            default: Default value if not found.
            
        Returns:
            Configuration value.
        """
        # Check environment variable first
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        
        # Check settings file
        if key in self.settings:
            return self.settings[key]
        
        # Check defaults
        if key in self.DEFAULTS:
            return self.DEFAULTS[key]
        
        return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get boolean configuration value.
        
        Args:
            key: Configuration key.
            default: Default value.
            
        Returns:
            Boolean value.
        """
        value = self.get(key, default)
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get integer configuration value.
        
        Args:
            key: Configuration key.
            default: Default value.
            
        Returns:
            Integer value.
        """
        value = self.get(key, default)
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    # Convenience properties for common settings
    
    @property
    def datasight_token(self) -> Optional[str]:
        """Get DataSight API bearer token."""
        return self.get("DATASIGHT_BEARER_TOKEN")
    
    @property
    def teambook_token(self) -> Optional[str]:
        """Get TeamBook API bearer token."""
        return self.get("TEAMBOOK_BEARER_TOKEN")
    
    @property
    def github_token(self) -> Optional[str]:
        """Get GitHub API token."""
        return self.get("GITHUB_TOKEN")
    
    @property
    def llm_token(self) -> Optional[str]:
        """Get LLM Gateway token."""
        return self.get("AM_TOKEN")
    
    @property
    def db_path(self) -> str:
        """Get database file path."""
        return self.get("DB_PATH", "metrics.db")
    
    @property
    def registry_dir(self) -> str:
        """Get registry directory path."""
        return self.get("REGISTRY_DIR", "apps")
    
    @property
    def enable_docs_generation(self) -> bool:
        """Check if docs generation is enabled."""
        return self.get_bool("ENABLE_DOCS_GENERATION", False)
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.get("LOG_LEVEL", "INFO")
    
    @property
    def hygiene_config(self) -> Dict:
        """Get hygiene configuration from settings.yaml."""
        return self.settings.get("hygiene", {
            "max_branch_age_days": 30,
            "max_pr_lines_changed": 400,
            "max_pr_review_hours": 24,
            "required_pr_pattern": r"^(feat|fix|chore|docs|refactor|test|ci)(\(.*\))?: .{10,}",
            "protected_branches": ["main", "master", "release/*"],
            "allow_direct_push_to_main": False
        })
    
    @property
    def mongodb_uri(self) -> str:
        """Get MongoDB connection URI."""
        return self.get("MONGODB_URI", "")
    
    @property
    def mongodb_database(self) -> str:
        """Get MongoDB database name."""
        return self.get("MONGODB_DATABASE", "devops_metrics")
    
    @property
    def use_mongodb(self) -> bool:
        """Check if MongoDB should be used instead of SQLite."""
        return bool(self.mongodb_uri)
    
    def validate(self) -> Dict[str, bool]:
        """
        Validate required configuration.
        
        Returns:
            Dictionary with validation status for each required config.
        """
        return {
            'datasight_token': bool(self.datasight_token),
            'github_token': bool(self.github_token),
            'db_path': bool(self.db_path),
            'registry_dir': os.path.exists(self.registry_dir)
        }
    
    def is_valid(self) -> bool:
        """
        Check if all required configuration is present.
        
        Returns:
            True if all required config is valid.
        """
        validation = self.validate()
        # Only datasight_token is strictly required
        return validation['datasight_token']
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary.
        
        Sensitive values are masked.
        
        Returns:
            Configuration dictionary.
        """
        return {
            'db_path': self.db_path,
            'registry_dir': self.registry_dir,
            'log_level': self.log_level,
            'enable_docs_generation': self.enable_docs_generation,
            'datasight_token': '***' if self.datasight_token else None,
            'github_token': '***' if self.github_token else None,
            'llm_token': '***' if self.llm_token else None
        }
