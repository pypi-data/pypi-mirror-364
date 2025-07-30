"""
Entry point for the Todo MCP server.

This module provides the main entry point and command-line interface
for starting the MCP server with Click integration and graceful
startup/shutdown handling.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from .config import TodoConfig, Environment, create_config
from .server import TodoMCPServer


class ServerManager:
    """Manages server lifecycle with graceful startup and shutdown."""
    
    def __init__(self, config: TodoConfig):
        self.config = config
        self.server: Optional[TodoMCPServer] = None
        self.logger = logging.getLogger(__name__)
        self._shutdown_event = asyncio.Event()
        
    def setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum: int, frame) -> None:
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    async def startup(self) -> None:
        """Initialize and start the server."""
        self.logger.info("Initializing Todo MCP Server...")
        
        try:
            # Create server instance
            self.server = TodoMCPServer(self.config)
            
            # Validate configuration
            await self._validate_setup()
            
            self.logger.info("Server initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize server: {e}")
            raise
            
    async def _validate_setup(self) -> None:
        """Validate server setup and configuration."""
        # Check data directory exists and is writable
        if not self.config.data_directory.exists():
            self.logger.info(f"Creating data directory: {self.config.data_directory}")
            self.config.data_directory.mkdir(parents=True, exist_ok=True)
            
        # Check if directory is writable
        test_file = self.config.data_directory / ".write_test"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            raise RuntimeError(f"Data directory is not writable: {e}")
            
        # Validate backup directory if enabled
        if self.config.backup_enabled:
            if not self.config.backup_directory.exists():
                self.logger.info(f"Creating backup directory: {self.config.backup_directory}")
                self.config.backup_directory.mkdir(parents=True, exist_ok=True)
                
    async def run(self) -> None:
        """Run the server with graceful shutdown handling."""
        if not self.server:
            raise RuntimeError("Server not initialized. Call startup() first.")
            
        try:
            # Start the server
            self.logger.info("Starting MCP server...")
            await self.server.run()
            
        except asyncio.CancelledError:
            self.logger.info("Server run cancelled")
        except Exception as e:
            self.logger.error(f"Server run error: {e}")
            raise
            
    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        self.logger.info("Shutting down server...")
        
        if self.server:
            try:
                await self.server.shutdown()
                self.logger.info("Server shutdown completed")
            except Exception as e:
                self.logger.error(f"Error during server shutdown: {e}")
                
        self._shutdown_event.set()


def setup_logging(config: TodoConfig) -> None:
    """
    Set up logging configuration based on config.
    
    Args:
        config: TodoConfig instance with logging settings
    """
    # Configure rich handler for console output
    console = Console()
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=config.environment == Environment.DEVELOPMENT,
        markup=True,
        rich_tracebacks=True,
    )
    
    handlers = [rich_handler]
    
    # Add file handler if specified
    if config.log_file:
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(
            logging.Formatter(config.log_format)
        )
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        handlers=handlers,
        format="%(message)s",
    )


def display_startup_info(config: TodoConfig, console: Console) -> None:
    """Display startup information in a formatted panel."""
    
    # Create configuration table
    config_table = Table(show_header=False, box=None)
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="white")
    
    config_table.add_row("Environment", config.environment)
    config_table.add_row("Data Directory", str(config.data_directory))
    config_table.add_row("Log Level", config.log_level)
    config_table.add_row("Cache Size", str(config.max_cache_size))
    config_table.add_row("File Watch", "Enabled" if config.file_watch_enabled else "Disabled")
    config_table.add_row("Backup", "Enabled" if config.backup_enabled else "Disabled")
    config_table.add_row("Performance Monitoring", "Enabled" if config.performance_monitoring else "Disabled")
    
    # Display in a panel
    panel = Panel(
        config_table,
        title=f"Todo MCP Server v{config.server_version}",
        subtitle="Configuration",
        border_style="blue"
    )
    
    console.print(panel)


@click.group(invoke_without_command=True)
@click.option(
    "--environment", "-e",
    type=click.Choice(["development", "testing", "production"], case_sensitive=False),
    help="Environment to run in"
)
@click.option(
    "--data-dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help="Directory for storing task files"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    help="Logging level"
)
@click.option(
    "--log-file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    help="Log file path"
)
@click.option(
    "--cache-size",
    type=click.IntRange(1, 10000),
    help="Maximum cache size"
)
@click.option(
    "--no-file-watch",
    is_flag=True,
    help="Disable file system monitoring"
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Disable backup functionality"
)
@click.option(
    "--performance-monitoring",
    is_flag=True,
    help="Enable performance monitoring"
)
@click.pass_context
def cli(
    ctx: click.Context,
    environment: Optional[str] = None,
    data_dir: Optional[Path] = None,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    cache_size: Optional[int] = None,
    no_file_watch: bool = False,
    no_backup: bool = False,
    performance_monitoring: bool = False,
) -> None:
    """
    Todo MCP Server - AI Agent Task Management System
    
    A Model Context Protocol (MCP) server that provides comprehensive
    task management tools for AI agents with Markdown-based storage.
    """
    # Create configuration with overrides
    config_overrides = {}
    
    if data_dir:
        config_overrides['data_directory'] = data_dir
    if log_level:
        config_overrides['log_level'] = log_level.upper()
    if log_file:
        config_overrides['log_file'] = log_file
    if cache_size:
        config_overrides['max_cache_size'] = cache_size
    if no_file_watch:
        config_overrides['file_watch_enabled'] = False
    if no_backup:
        config_overrides['backup_enabled'] = False
    if performance_monitoring:
        config_overrides['performance_monitoring'] = True
        
    # Create configuration
    config = create_config(environment)
    
    # Apply overrides
    if config_overrides:
        config = TodoConfig(**{**config.model_dump(), **config_overrides})
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    
    # If no subcommand, run the server
    if ctx.invoked_subcommand is None:
        ctx.invoke(serve)


@cli.command()
@click.option(
    "--test-mode",
    is_flag=True,
    help="Run in test mode with sample data"
)
@click.pass_context
def serve(ctx: click.Context, test_mode: bool = False) -> None:
    """Start the MCP server."""
    config: TodoConfig = ctx.obj['config']
    
    # Setup logging
    setup_logging(config)
    
    # Display startup information
    console = Console()
    display_startup_info(config, console)
    
    if test_mode:
        console.print("[yellow]Running in test mode[/yellow]")
    
    # Create and run server
    async def run_server():
        server_manager = ServerManager(config)
        server_manager.setup_signal_handlers()
        
        try:
            await server_manager.startup()
            await server_manager.run()
        except KeyboardInterrupt:
            console.print("\n[yellow]Received interrupt signal[/yellow]")
        except Exception as e:
            console.print(f"[red]Server error: {e}[/red]")
            sys.exit(1)
        finally:
            await server_manager.shutdown()
    
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        console.print("\n[green]Server stopped gracefully[/green]")
        sys.exit(0)


@cli.command()
@click.pass_context
def config_info(ctx: click.Context) -> None:
    """Display current configuration information."""
    config: TodoConfig = ctx.obj['config']
    console = Console()
    
    display_startup_info(config, console)
    
    # Additional detailed info
    env_info = config.get_environment_info()
    
    detail_table = Table(title="Detailed Configuration")
    detail_table.add_column("Setting", style="cyan")
    detail_table.add_column("Value", style="white")
    detail_table.add_column("Description", style="dim")
    
    detail_table.add_row("Server Name", config.server_name, "MCP server identifier")
    detail_table.add_row("Task File Extension", config.task_file_extension, "File extension for task files")
    detail_table.add_row("Max Title Length", str(config.max_task_title_length), "Maximum task title length")
    detail_table.add_row("Max Description Length", str(config.max_task_description_length), "Maximum task description length")
    detail_table.add_row("Default Priority", config.default_task_priority, "Default priority for new tasks")
    detail_table.add_row("Auto Save Interval", f"{config.auto_save_interval}s", "Auto-save interval in seconds")
    
    if config.backup_enabled:
        detail_table.add_row("Backup Directory", str(config.backup_directory), "Backup files location")
        detail_table.add_row("Backup Retention", f"{config.backup_retention_days} days", "Backup retention period")
    
    console.print(detail_table)


@cli.command()
@click.pass_context
def validate(ctx: click.Context) -> None:
    """Validate configuration and data directory setup."""
    config: TodoConfig = ctx.obj['config']
    console = Console()
    
    console.print("[blue]Validating configuration...[/blue]")
    
    # Validate data directory
    if not config.data_directory.exists():
        console.print(f"[yellow]Data directory does not exist: {config.data_directory}[/yellow]")
        console.print("[green]Creating data directory...[/green]")
        config.data_directory.mkdir(parents=True, exist_ok=True)
    else:
        console.print(f"[green]✓[/green] Data directory exists: {config.data_directory}")
    
    # Check write permissions
    test_file = config.data_directory / ".write_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
        console.print("[green]✓[/green] Data directory is writable")
    except Exception as e:
        console.print(f"[red]✗[/red] Data directory is not writable: {e}")
        sys.exit(1)
    
    # Validate backup directory if enabled
    if config.backup_enabled:
        if not config.backup_directory.exists():
            console.print(f"[yellow]Backup directory does not exist: {config.backup_directory}[/yellow]")
            console.print("[green]Creating backup directory...[/green]")
            config.backup_directory.mkdir(parents=True, exist_ok=True)
        else:
            console.print(f"[green]✓[/green] Backup directory exists: {config.backup_directory}")
    
    # Validate log file directory if specified
    if config.log_file:
        log_dir = config.log_file.parent
        if not log_dir.exists():
            console.print(f"[yellow]Log directory does not exist: {log_dir}[/yellow]")
            console.print("[green]Creating log directory...[/green]")
            log_dir.mkdir(parents=True, exist_ok=True)
        else:
            console.print(f"[green]✓[/green] Log directory exists: {log_dir}")
    
    console.print("[green]Configuration validation completed successfully![/green]")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()