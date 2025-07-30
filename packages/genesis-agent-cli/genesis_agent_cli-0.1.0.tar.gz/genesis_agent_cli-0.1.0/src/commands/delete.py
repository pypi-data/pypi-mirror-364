"""Delete command for removing agents."""

import asyncio

import click
from rich.console import Console
from rich.prompt import Confirm

from src.services.config import Config
from src.services.genesis_studio_api import GenesisStudioAPI

console = Console()


@click.command()
@click.argument("agent_id")
@click.option("--force", "-f", is_flag=True, help="Skip confirmation prompt")
@click.pass_obj
def delete(config: Config, agent_id: str, force: bool) -> None:
    """Delete an agent from Genesis Studio."""
    asyncio.run(_delete_agent(config, agent_id, force))


async def _delete_agent(config: Config, agent_id: str, force: bool) -> None:
    """Delete agent implementation."""
    api = GenesisStudioAPI(config)

    # Fetch agent details first
    console.print(f"Fetching agent details for [cyan]{agent_id}[/cyan]...")
    try:
        flow = await api.get_flow(agent_id)
    except Exception as e:
        console.print(f"[red]Error fetching agent: {e}[/red]")
        raise click.Abort()

    # Display agent information
    console.print(f"\n[bold]Agent to delete:[/bold]")
    console.print(f"  ID: [cyan]{flow.id}[/cyan]")
    console.print(f"  Name: [cyan]{flow.name}[/cyan]")
    if flow.description:
        console.print(f"  Description: {flow.description}")
    if flow.endpoint_name:
        console.print(f"  Endpoint: [green]{flow.endpoint_name}[/green]")

    # Confirm deletion
    if not force:
        if not Confirm.ask(
            "\n[yellow]Are you sure you want to delete this agent?[/yellow]"
        ):
            console.print("[dim]Deletion cancelled[/dim]")
            return

    # Delete the agent
    console.print(f"\nDeleting agent [cyan]{flow.name}[/cyan]...")
    try:
        await api.delete_flow(agent_id)
        console.print(f"[green]✓ Agent deleted successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error deleting agent: {e}[/red]")
        raise click.Abort()
