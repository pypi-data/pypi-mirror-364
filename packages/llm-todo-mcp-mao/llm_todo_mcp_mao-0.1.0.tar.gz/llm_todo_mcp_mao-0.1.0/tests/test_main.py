"""
Tests for the main entry point and CLI functionality.

This module tests the command-line interface, server startup logic,
and graceful shutdown handling.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from todo_mcp.__main__ import (
    cli,
    serve,
    config_info,
    validate,
    setup_logging,
    ServerManager,
    display_startup_info,
)
from todo_mcp.config import TodoConfig, Environment


class TestCLI:
    """Test cases for the CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Todo MCP Server" in result.output
        assert "AI Agent Task Management System" in result.output

    def test_cli_with_environment_option(self):
        """Test CLI with environment option."""
        runner = CliRunner()
        
        with patch('todo_mcp.__main__.serve') as mock_serve:
            result = runner.invoke(cli, ['--environment', 'production'])
            
            assert result.exit_code == 0
            # Check that serve was called (since no subcommand defaults to serve)
            mock_serve.assert_called_once()

    def test_cli_with_data_dir_option(self):
        """Test CLI with data directory option."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('todo_mcp.__main__.serve') as mock_serve:
                result = runner.invoke(cli, ['--data-dir', temp_dir])
                
                assert result.exit_code == 0
                mock_serve.assert_called_once()

    def test_cli_with_log_level_option(self):
        """Test CLI with log level option."""
        runner = CliRunner()
        
        with patch('todo_mcp.__main__.serve') as mock_serve:
            result = runner.invoke(cli, ['--log-level', 'DEBUG'])
            
            assert result.exit_code == 0
            mock_serve.assert_called_once()

    def test_cli_with_cache_size_option(self):
        """Test CLI with cache size option."""
        runner = CliRunner()
        
        with patch('todo_mcp.__main__.serve') as mock_serve:
            result = runner.invoke(cli, ['--cache-size', '500'])
            
            assert result.exit_code == 0
            mock_serve.assert_called_once()

    def test_cli_with_flags(self):
        """Test CLI with boolean flags."""
        runner = CliRunner()
        
        with patch('todo_mcp.__main__.serve') as mock_serve:
            result = runner.invoke(cli, [
                '--no-file-watch',
                '--no-backup',
                '--performance-monitoring'
            ])
            
            assert result.exit_code == 0
            mock_serve.assert_called_once()

    def test_cli_invalid_cache_size(self):
        """Test CLI with invalid cache size."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--cache-size', '0'])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_cli_invalid_log_level(self):
        """Test CLI with invalid log level."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--log-level', 'INVALID'])
        
        assert result.exit_code != 0
        assert "Invalid value" in result.output


class TestServeCommand:
    """Test cases for the serve command."""

    @patch('todo_mcp.__main__.asyncio.run')
    @patch('todo_mcp.__main__.setup_logging')
    @patch('todo_mcp.__main__.display_startup_info')
    def test_serve_command_basic(self, mock_display, mock_setup_logging, mock_asyncio_run):
        """Test basic serve command functionality."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(cli, [
                '--data-dir', temp_dir,
                'serve'
            ])
            
            assert result.exit_code == 0
            mock_setup_logging.assert_called_once()
            mock_display.assert_called_once()
            mock_asyncio_run.assert_called_once()

    @patch('todo_mcp.__main__.asyncio.run')
    @patch('todo_mcp.__main__.setup_logging')
    @patch('todo_mcp.__main__.display_startup_info')
    def test_serve_command_test_mode(self, mock_display, mock_setup_logging, mock_asyncio_run):
        """Test serve command with test mode."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(cli, [
                '--data-dir', temp_dir,
                'serve',
                '--test-mode'
            ])
            
            assert result.exit_code == 0
            mock_setup_logging.assert_called_once()
            mock_display.assert_called_once()
            mock_asyncio_run.assert_called_once()


class TestConfigInfoCommand:
    """Test cases for the config-info command."""

    @patch('todo_mcp.__main__.display_startup_info')
    def test_config_info_command(self, mock_display):
        """Test config-info command."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(cli, [
                '--data-dir', temp_dir,
                'config-info'
            ])
            
            assert result.exit_code == 0
            mock_display.assert_called_once()


class TestValidateCommand:
    """Test cases for the validate command."""

    def test_validate_command_success(self):
        """Test validate command with valid setup."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(cli, [
                '--data-dir', temp_dir,
                'validate'
            ])
            
            assert result.exit_code == 0
            assert "Configuration validation completed successfully" in result.output

    def test_validate_command_creates_directories(self):
        """Test validate command creates missing directories."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "nonexistent"
            
            # Ensure directory doesn't exist initially
            assert not data_dir.exists()
            
            result = runner.invoke(cli, [
                '--data-dir', str(data_dir),
                '--environment', 'production',  # Production enables backup
                'validate'
            ])
            
            assert result.exit_code == 0
            assert data_dir.exists()
            # The directory is created by model_post_init, so it exists when validate runs
            assert "Data directory exists" in result.output

    def test_validate_command_with_log_file(self):
        """Test validate command with log file option."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "logs" / "app.log"
            
            result = runner.invoke(cli, [
                '--data-dir', temp_dir,
                '--log-file', str(log_file),
                'validate'
            ])
            
            assert result.exit_code == 0
            assert log_file.parent.exists()


class TestServerManager:
    """Test cases for ServerManager class."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield TodoConfig(
                data_directory=Path(temp_dir),
                environment=Environment.TESTING
            )

    @pytest.fixture
    def server_manager(self, config):
        """Create a ServerManager instance."""
        return ServerManager(config)

    @pytest.mark.asyncio
    async def test_server_manager_startup(self, server_manager):
        """Test ServerManager startup process."""
        with patch('todo_mcp.__main__.TodoMCPServer') as mock_server_class:
            mock_server = AsyncMock()
            mock_server_class.return_value = mock_server
            
            await server_manager.startup()
            
            assert server_manager.server is not None
            mock_server_class.assert_called_once_with(server_manager.config)

    @pytest.mark.asyncio
    async def test_server_manager_startup_validation_failure(self, server_manager):
        """Test ServerManager startup with validation failure."""
        # Mock the write test to fail
        with patch('todo_mcp.__main__.TodoMCPServer'):
            with patch.object(Path, 'write_text', side_effect=PermissionError("Permission denied")):
                with pytest.raises(RuntimeError, match="not writable"):
                    await server_manager.startup()

    @pytest.mark.asyncio
    async def test_server_manager_run_without_startup(self, server_manager):
        """Test ServerManager run without startup."""
        with pytest.raises(RuntimeError, match="not initialized"):
            await server_manager.run()

    @pytest.mark.asyncio
    async def test_server_manager_shutdown(self, server_manager):
        """Test ServerManager shutdown process."""
        mock_server = AsyncMock()
        server_manager.server = mock_server
        
        await server_manager.shutdown()
        
        mock_server.shutdown.assert_called_once()
        assert server_manager._shutdown_event.is_set()

    @pytest.mark.asyncio
    async def test_server_manager_shutdown_with_error(self, server_manager):
        """Test ServerManager shutdown with error."""
        mock_server = AsyncMock()
        mock_server.shutdown.side_effect = Exception("Shutdown error")
        server_manager.server = mock_server
        
        # The shutdown method catches and logs errors but doesn't re-raise them
        await server_manager.shutdown()
        
        mock_server.shutdown.assert_called_once()
        assert server_manager._shutdown_event.is_set()

    def test_server_manager_signal_handlers(self, server_manager):
        """Test signal handler setup."""
        with patch('signal.signal') as mock_signal:
            server_manager.setup_signal_handlers()
            
            # Should set up handlers for SIGINT and SIGTERM
            assert mock_signal.call_count == 2


class TestSetupLogging:
    """Test cases for logging setup."""

    def test_setup_logging_console_only(self):
        """Test logging setup with console output only."""
        config = TodoConfig(environment=Environment.DEVELOPMENT)
        
        with patch('logging.basicConfig') as mock_basic_config:
            setup_logging(config)
            
            mock_basic_config.assert_called_once()
            args, kwargs = mock_basic_config.call_args
            assert kwargs['level'] == 10  # DEBUG level for development

    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            config = TodoConfig(
                environment=Environment.PRODUCTION,
                log_file=log_file
            )
            
            with patch('logging.basicConfig') as mock_basic_config:
                with patch('logging.FileHandler') as mock_file_handler:
                    setup_logging(config)
                    
                    mock_basic_config.assert_called_once()
                    args, kwargs = mock_basic_config.call_args
                    assert len(kwargs['handlers']) == 2  # Console + file
                    mock_file_handler.assert_called_once_with(log_file)

    def test_setup_logging_development_environment(self):
        """Test logging setup for development environment."""
        config = TodoConfig(environment=Environment.DEVELOPMENT)
        
        with patch('logging.basicConfig') as mock_basic_config:
            setup_logging(config)
            
            mock_basic_config.assert_called_once()


class TestDisplayStartupInfo:
    """Test cases for startup info display."""

    def test_display_startup_info(self):
        """Test startup info display."""
        config = TodoConfig(environment=Environment.DEVELOPMENT)
        
        with patch('rich.console.Console') as mock_console_class:
            mock_console = MagicMock()
            mock_console_class.return_value = mock_console
            
            display_startup_info(config, mock_console)
            
            mock_console.print.assert_called_once()


class TestConfigurationOverrides:
    """Test cases for configuration overrides through CLI."""

    def test_environment_override(self):
        """Test environment configuration override."""
        runner = CliRunner()
        
        with patch('todo_mcp.__main__.create_config') as mock_create_config:
            mock_config = MagicMock()
            mock_create_config.return_value = mock_config
            
            with patch('todo_mcp.__main__.serve'):
                runner.invoke(cli, ['--environment', 'production'])
                
                mock_create_config.assert_called_once_with('production')

    def test_multiple_overrides(self):
        """Test multiple configuration overrides."""
        runner = CliRunner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('todo_mcp.__main__.TodoConfig') as mock_config_class:
                mock_config = MagicMock()
                mock_config.model_dump.return_value = {}
                mock_config_class.return_value = mock_config
                
                with patch('todo_mcp.__main__.create_config') as mock_create_config:
                    mock_create_config.return_value = mock_config
                    
                    with patch('todo_mcp.__main__.serve'):
                        runner.invoke(cli, [
                            '--environment', 'testing',
                            '--data-dir', temp_dir,
                            '--log-level', 'ERROR',
                            '--cache-size', '200',
                            '--no-file-watch',
                            '--no-backup',
                            '--performance-monitoring'
                        ])
                        
                        mock_create_config.assert_called_once_with('testing')
                        mock_config_class.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])