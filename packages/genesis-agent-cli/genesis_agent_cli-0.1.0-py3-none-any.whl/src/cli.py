"""Main CLI entry point for genesis-agent."""

import os
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console

from src.commands import (
    create,
    delete,
    list_agents,
    publish,
    check_deps,
)
from src.services.config import Config, load_config

console = Console()


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
    envvar="GENESIS_AGENT_CONFIG",
)
@click.pass_context
def cli(ctx: click.Context, config: Optional[Path]) -> None:
    """Genesis Agent CLI - Manage AI agents using specifications."""
    # Load configuration
    try:
        ctx.obj = load_config(config)
    except Exception as e:
        console.print(f"[red]Error loading configuration: {e}[/red]")
        ctx.exit(1)


# Register commands
cli.add_command(check_deps)
cli.add_command(create)
cli.add_command(list_agents)
cli.add_command(delete)
cli.add_command(publish)


@cli.command()
@click.pass_obj
def config_check(config: Config) -> None:
    """Check and display current configuration."""
    console.print("[bold]Genesis Agent CLI Configuration[/bold]\n")
    console.print(f"Genesis Studio URL: {config.genesis_studio_url}")
    console.print(f"API Key: {'[Set]' if config.api_key else '[Not Set]'}")
    console.print(f"Config File: {config.config_path or '[Default]'}")


@cli.command()
def version() -> None:
    """Show CLI version."""
    from src import __version__

    console.print(f"genesis-agent version {__version__}")


if __name__ == "__main__":
    cli()
