"""
Tests for configuration management.

This module tests the TodoConfig class and its environment-specific
behavior, validation rules, and environment variable parsing.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from todo_mcp.config import TodoConfig, Environment, create_config


class TestTodoConfig:
    """Test cases for TodoConfig class."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = TodoConfig()
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.data_directory == Path("data")
        assert config.max_cache_size == 1000
        assert config.file_watch_enabled is True
        assert config.backup_enabled is True
        assert config.log_level == "DEBUG"  # Development default
        assert config.server_name == "todo-mcp-server"
        assert config.server_version == "0.1.0"

    def test_development_environment_defaults(self):
        """Test development environment specific defaults."""
        config = TodoConfig(environment=Environment.DEVELOPMENT)
        
        assert config.log_level == "DEBUG"
        assert config.file_watch_enabled is True
        assert config.performance_monitoring is True
        assert config.backup_enabled is True

    def test_testing_environment_defaults(self):
        """Test testing environment specific defaults."""
        config = TodoConfig(environment=Environment.TESTING)
        
        assert config.log_level == "WARNING"
        assert config.file_watch_enabled is False
        assert config.performance_monitoring is False
        assert config.backup_enabled is False
        assert config.max_cache_size <= 100

    def test_production_environment_defaults(self):
        """Test production environment specific defaults."""
        config = TodoConfig(environment=Environment.PRODUCTION)
        
        assert config.log_level == "INFO"
        assert config.file_watch_enabled is True
        assert config.performance_monitoring is False
        assert config.backup_enabled is True
        assert config.max_cache_size >= 500

    def test_log_level_validation(self):
        """Test log level validation."""
        # Valid log levels
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            config = TodoConfig(log_level=level)
            assert config.log_level == level
            
        # Case insensitive
        config = TodoConfig(log_level='debug')
        assert config.log_level == 'DEBUG'
        
        # Invalid log level
        with pytest.raises(ValidationError):
            TodoConfig(log_level='INVALID')

    def test_priority_validation(self):
        """Test default task priority validation."""
        # Valid priorities
        for priority in ['low', 'medium', 'high', 'urgent']:
            config = TodoConfig(default_task_priority=priority)
            assert config.default_task_priority == priority
            
        # Case insensitive
        config = TodoConfig(default_task_priority='HIGH')
        assert config.default_task_priority == 'high'
        
        # Invalid priority
        with pytest.raises(ValidationError):
            TodoConfig(default_task_priority='invalid')

    def test_file_extension_validation(self):
        """Test file extension validation."""
        # Extension with dot
        config = TodoConfig(task_file_extension='.md')
        assert config.task_file_extension == '.md'
        
        # Extension without dot (should be added)
        config = TodoConfig(task_file_extension='md')
        assert config.task_file_extension == '.md'

    def test_numeric_field_validation(self):
        """Test numeric field validation with bounds."""
        # Valid values
        config = TodoConfig(max_cache_size=500)
        assert config.max_cache_size == 500
        
        # Below minimum
        with pytest.raises(ValidationError):
            TodoConfig(max_cache_size=0)
            
        # Above maximum
        with pytest.raises(ValidationError):
            TodoConfig(max_cache_size=20000)

    def test_directory_creation(self):
        """Test that directories are created during initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "test_data"
            backup_dir = Path(temp_dir) / "test_backups"
            
            config = TodoConfig(
                data_directory=data_dir,
                backup_directory=backup_dir,
                backup_enabled=True
            )
            
            # Check that directories were created
            assert data_dir.exists()
            assert (data_dir / "tasks").exists()
            assert (data_dir / "templates").exists()
            assert backup_dir.exists()

    def test_backup_disabled_no_directory_creation(self):
        """Test that backup directory is not created when backup is disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir) / "test_backups"
            
            config = TodoConfig(
                backup_directory=backup_dir,
                backup_enabled=False
            )
            
            # Backup directory should not be created
            assert not backup_dir.exists()

    def test_get_environment_info(self):
        """Test environment info retrieval."""
        config = TodoConfig(environment=Environment.PRODUCTION)
        info = config.get_environment_info()
        
        assert info["environment"] == "production"
        assert "data_directory" in info
        assert "log_level" in info
        assert "cache_size" in info
        assert isinstance(info["file_watch_enabled"], bool)
        assert isinstance(info["backup_enabled"], bool)
        assert isinstance(info["performance_monitoring"], bool)


class TestEnvironmentVariableParsing:
    """Test cases for environment variable parsing."""

    def test_from_env_basic(self):
        """Test basic environment variable parsing."""
        env_vars = {
            'TODO_MCP_ENVIRONMENT': 'production',
            'TODO_MCP_LOG_LEVEL': 'ERROR',
            'TODO_MCP_MAX_CACHE_SIZE': '2000',
            'TODO_MCP_FILE_WATCH_ENABLED': 'false',
            'TODO_MCP_DATA_DIRECTORY': '/custom/data'
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = TodoConfig.from_env()
            
            assert config.environment == Environment.PRODUCTION
            assert config.log_level == 'ERROR'
            assert config.max_cache_size == 2000
            assert config.file_watch_enabled is False
            assert config.data_directory == Path('/custom/data')

    def test_from_env_boolean_parsing(self):
        """Test boolean environment variable parsing."""
        test_cases = [
            ('true', True),
            ('True', True),
            ('1', True),
            ('yes', True),
            ('on', True),
            ('false', False),
            ('False', False),
            ('0', False),
            ('no', False),
            ('off', False),
        ]
        
        for env_value, expected in test_cases:
            env_vars = {'TODO_MCP_BACKUP_ENABLED': env_value}
            
            with patch.dict(os.environ, env_vars, clear=False):
                config = TodoConfig.from_env()
                assert config.backup_enabled == expected

    def test_from_env_integer_parsing(self):
        """Test integer environment variable parsing."""
        env_vars = {
            'TODO_MCP_MAX_CACHE_SIZE': '1500',
            'TODO_MCP_BACKUP_RETENTION_DAYS': '60',
            'TODO_MCP_AUTO_SAVE_INTERVAL': '45'
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = TodoConfig.from_env()
            
            assert config.max_cache_size == 1500
            assert config.backup_retention_days == 60
            assert config.auto_save_interval == 45

    def test_from_env_path_parsing(self):
        """Test Path environment variable parsing."""
        env_vars = {
            'TODO_MCP_DATA_DIRECTORY': '/custom/data',
            'TODO_MCP_BACKUP_DIRECTORY': '/custom/backups',
            'TODO_MCP_LOG_FILE': '/var/log/todo.log'
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = TodoConfig.from_env()
            
            assert config.data_directory == Path('/custom/data')
            assert config.backup_directory == Path('/custom/backups')
            assert config.log_file == Path('/var/log/todo.log')

    def test_from_env_no_prefix_ignored(self):
        """Test that environment variables without prefix are ignored."""
        env_vars = {
            'LOG_LEVEL': 'ERROR',  # No TODO_MCP_ prefix
            'TODO_MCP_LOG_LEVEL': 'DEBUG'
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = TodoConfig.from_env()
            assert config.log_level == 'DEBUG'  # Only prefixed var is used


class TestCreateConfig:
    """Test cases for create_config function."""

    def test_create_config_default(self):
        """Test create_config with default parameters."""
        config = create_config()
        assert isinstance(config, TodoConfig)

    def test_create_config_with_environment(self):
        """Test create_config with environment override."""
        config = create_config(environment='production')
        assert config.environment == Environment.PRODUCTION

    def test_create_config_invalid_environment(self):
        """Test create_config with invalid environment."""
        with pytest.raises(ValueError, match="Invalid environment"):
            create_config(environment='invalid')

    def test_create_config_case_insensitive_environment(self):
        """Test create_config with case insensitive environment."""
        config = create_config(environment='PRODUCTION')
        assert config.environment == Environment.PRODUCTION
        
        config = create_config(environment='Testing')
        assert config.environment == Environment.TESTING

    def test_create_config_with_env_vars_and_override(self):
        """Test create_config with both env vars and environment override."""
        env_vars = {
            'TODO_MCP_ENVIRONMENT': 'development',
            'TODO_MCP_LOG_LEVEL': 'ERROR'
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = create_config(environment='production')
            
            # Environment should be overridden
            assert config.environment == Environment.PRODUCTION
            # But other env vars should still be used
            assert config.log_level == 'ERROR'


class TestConfigValidation:
    """Test cases for configuration validation."""

    def test_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError):
            TodoConfig(unknown_field="value")

    def test_validate_assignment(self):
        """Test that assignment validation works."""
        config = TodoConfig()
        
        # Valid assignment
        config.log_level = 'ERROR'
        assert config.log_level == 'ERROR'
        
        # Invalid assignment
        with pytest.raises(ValidationError):
            config.log_level = 'INVALID'

    def test_environment_specific_validation_override(self):
        """Test that environment-specific settings can be overridden."""
        # Testing environment with custom log level
        config = TodoConfig(
            environment=Environment.TESTING,
            log_level='DEBUG'  # Override testing default
        )
        
        assert config.environment == Environment.TESTING
        assert config.log_level == 'DEBUG'
        assert config.file_watch_enabled is False  # Still uses testing default

    def test_path_field_types(self):
        """Test that Path fields accept both strings and Path objects."""
        # String path
        config1 = TodoConfig(data_directory="/custom/path")
        assert config1.data_directory == Path("/custom/path")
        
        # Path object
        config2 = TodoConfig(data_directory=Path("/custom/path"))
        assert config2.data_directory == Path("/custom/path")


if __name__ == "__main__":
    pytest.main([__file__])