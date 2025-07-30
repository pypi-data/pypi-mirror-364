"""
Configuration management for the Todo MCP system.

This module provides configuration settings using Pydantic BaseModel
for environment variable parsing and validation with support for
development, testing, and production environments.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Environment(str, Enum):
    """Environment types for configuration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class TodoConfig(BaseModel):
    """
    Configuration settings for the Todo MCP system.
    
    Uses Pydantic BaseModel with custom environment variable
    parsing and type conversion functionality.
    """
    
    # Environment settings
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Current environment (development, testing, production)"
    )
    
    # Data storage settings
    data_directory: Path = Field(
        default=Path("data"),
        description="Directory for storing task markdown files"
    )
    
    # Performance settings
    max_cache_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of tasks to keep in memory cache"
    )
    
    # File monitoring settings
    file_watch_enabled: bool = Field(
        default=True,
        description="Enable file system monitoring for external changes"
    )
    
    # Backup settings
    backup_enabled: bool = Field(
        default=True,
        description="Enable automatic backup of task files"
    )
    
    backup_directory: Path = Field(
        default=Path("data/backups"),
        description="Directory for storing backup files"
    )
    
    backup_retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Number of days to retain backup files"
    )
    
    # Logging settings
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    log_file: Optional[Path] = Field(
        default=None,
        description="Log file path (None for console only)"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    # Performance monitoring
    performance_monitoring: bool = Field(
        default=False,
        description="Enable performance monitoring and metrics"
    )
    
    # MCP server settings
    server_name: str = Field(
        default="todo-mcp-server",
        description="MCP server name for identification"
    )
    
    server_version: str = Field(
        default="0.1.0",
        description="MCP server version"
    )
    
    # Task management settings
    max_task_title_length: int = Field(
        default=200,
        ge=10,
        le=500,
        description="Maximum length for task titles"
    )
    
    max_task_description_length: int = Field(
        default=5000,
        ge=100,
        le=50000,
        description="Maximum length for task descriptions"
    )
    
    default_task_priority: str = Field(
        default="medium",
        description="Default priority for new tasks"
    )
    
    # File system settings
    task_file_extension: str = Field(
        default=".md",
        description="File extension for task files"
    )
    
    auto_save_interval: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Auto-save interval in seconds"
    )

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in allowed_levels:
            raise ValueError(f'log_level must be one of {allowed_levels}')
        return v.upper()

    @field_validator('default_task_priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate default task priority."""
        allowed_priorities = {'low', 'medium', 'high', 'urgent'}
        if v.lower() not in allowed_priorities:
            raise ValueError(f'default_task_priority must be one of {allowed_priorities}')
        return v.lower()

    @field_validator('task_file_extension')
    @classmethod
    def validate_file_extension(cls, v: str) -> str:
        """Validate file extension starts with a dot."""
        if not v.startswith('.'):
            v = '.' + v
        return v

    @model_validator(mode='before')
    @classmethod
    def validate_environment_specific_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment-specific configuration adjustments."""
        if isinstance(values, dict):
            env = values.get('environment', Environment.DEVELOPMENT)
            
            # Convert string environment to enum if needed
            if isinstance(env, str):
                try:
                    env = Environment(env.lower())
                    values['environment'] = env
                except ValueError:
                    pass  # Let the field validator handle the error
            
            if env == Environment.DEVELOPMENT:
                # Development environment settings
                if 'log_level' not in values:
                    values['log_level'] = 'DEBUG'
                if 'file_watch_enabled' not in values:
                    values['file_watch_enabled'] = True
                if 'performance_monitoring' not in values:
                    values['performance_monitoring'] = True
                if 'backup_enabled' not in values:
                    values['backup_enabled'] = True
                    
            elif env == Environment.TESTING:
                # Testing environment settings
                if 'log_level' not in values:
                    values['log_level'] = 'WARNING'
                if 'file_watch_enabled' not in values:
                    values['file_watch_enabled'] = False
                if 'performance_monitoring' not in values:
                    values['performance_monitoring'] = False
                if 'backup_enabled' not in values:
                    values['backup_enabled'] = False
                if 'max_cache_size' not in values:
                    values['max_cache_size'] = 100
                else:
                    values['max_cache_size'] = min(values['max_cache_size'], 100)
                    
            elif env == Environment.PRODUCTION:
                # Production environment settings
                if 'log_level' not in values:
                    values['log_level'] = 'INFO'
                if 'file_watch_enabled' not in values:
                    values['file_watch_enabled'] = True
                if 'performance_monitoring' not in values:
                    values['performance_monitoring'] = False
                if 'backup_enabled' not in values:
                    values['backup_enabled'] = True
                if 'max_cache_size' not in values:
                    values['max_cache_size'] = 1000
                else:
                    values['max_cache_size'] = max(values['max_cache_size'], 500)
                    
        return values

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization setup."""
        # Ensure data directories exist
        self.data_directory.mkdir(parents=True, exist_ok=True)
        (self.data_directory / "tasks").mkdir(exist_ok=True)
        (self.data_directory / "templates").mkdir(exist_ok=True)
        
        if self.backup_enabled:
            self.backup_directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> 'TodoConfig':
        """
        Create configuration from environment variables.
        
        Environment variables should be prefixed with TODO_MCP_
        For example: TODO_MCP_ENVIRONMENT=production
        """
        env_vars = {}
        prefix = "TODO_MCP_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                
                # Handle boolean values
                if value.lower() in ('true', '1', 'yes', 'on'):
                    env_vars[config_key] = True
                elif value.lower() in ('false', '0', 'no', 'off'):
                    env_vars[config_key] = False
                # Handle integer values
                elif value.isdigit():
                    env_vars[config_key] = int(value)
                # Handle Path values
                elif config_key.endswith('_directory') or config_key.endswith('_file'):
                    env_vars[config_key] = Path(value)
                else:
                    env_vars[config_key] = value
        
        return cls(**env_vars)

    def get_environment_info(self) -> Dict[str, Any]:
        """Get current environment configuration summary."""
        return {
            "environment": self.environment if isinstance(self.environment, str) else self.environment.value,
            "data_directory": str(self.data_directory),
            "log_level": self.log_level,
            "cache_size": self.max_cache_size,
            "file_watch_enabled": self.file_watch_enabled,
            "backup_enabled": self.backup_enabled,
            "performance_monitoring": self.performance_monitoring,
        }

    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        "extra": "forbid"
    }


def create_config(environment: Optional[str] = None) -> TodoConfig:
    """
    Create a TodoConfig instance with optional environment override.
    
    Args:
        environment: Optional environment override (development, testing, production)
        
    Returns:
        Configured TodoConfig instance
    """
    # Start with environment variables
    config = TodoConfig.from_env()
    
    # Override environment if specified
    if environment:
        try:
            env_enum = Environment(environment.lower())
            config = TodoConfig(environment=env_enum, **config.model_dump(exclude={'environment'}))
        except ValueError:
            raise ValueError(f"Invalid environment: {environment}. Must be one of {list(Environment)}")
    
    return config


# Global configuration instance
config = create_config()