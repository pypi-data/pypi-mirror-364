"""List command for displaying existing agents."""

import asyncio
from datetime import datetime
from typing import List

import click
from rich.console import Console
from rich.table import Table

from src.services.config import Config
from src.services.genesis_studio_api import Flow, GenesisStudioAPI

console = Console()


@click.command("list")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "detailed", "json"]),
    default="table",
    help="Output format",
)
@click.option("--limit", "-l", type=int, help="Limit number of results")
@click.pass_obj
def list_agents(config: Config, format: str, limit: int) -> None:
    """List all agents in Genesis Studio."""
    asyncio.run(_list_agents(config, format, limit))


async def _list_agents(config: Config, format: str, limit: int) -> None:
    """List agents implementation."""
    api = GenesisStudioAPI(config)

    # Fetch flows
    console.print("Fetching agents from Genesis Studio...")
    try:
        flows = await api.list_flows()
    except Exception as e:
        console.print(f"[red]Error fetching agents: {e}[/red]")
        raise click.Abort()

    # Apply limit if specified
    if limit:
        flows = flows[:limit]

    # Display based on format
    if format == "table":
        _display_table(flows)
    elif format == "detailed":
        _display_detailed(flows)
    elif format == "json":
        _display_json(flows)

    # Summary
    console.print(f"\n[dim]Total agents: {len(flows)}[/dim]")


def _display_table(flows: List[Flow]) -> None:
    """Display flows in table format."""
    table = Table(title="Genesis Studio Agents")

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="dim")
    table.add_column("Endpoint", style="green")
    table.add_column("Updated", style="blue")

    for flow in flows:
        # Parse updated time
        updated = "N/A"
        if flow.updated_at:
            try:
                dt = datetime.fromisoformat(flow.updated_at.replace("Z", "+00:00"))
                updated = dt.strftime("%Y-%m-%d %H:%M")
            except:
                updated = flow.updated_at[:19]  # Just take the date part

        table.add_row(
            str(flow.id)[:8] + "...",
            flow.name[:30] + "..." if len(flow.name) > 30 else flow.name,
            (
                (
                    flow.description[:40] + "..."
                    if len(flow.description) > 40
                    else flow.description
                )
                if flow.description
                else ""
            ),
            flow.endpoint_name or "",
            updated,
        )

    console.print(table)


def _display_detailed(flows: List[Flow]) -> None:
    """Display flows in detailed format."""
    for i, flow in enumerate(flows):
        if i > 0:
            console.print("\n" + "─" * 60 + "\n")

        console.print(f"[bold cyan]Agent: {flow.name}[/bold cyan]")
        console.print(f"  ID: {flow.id}")
        if flow.description:
            console.print(f"  Description: {flow.description}")
        if flow.endpoint_name:
            console.print(f"  Endpoint: [green]{flow.endpoint_name}[/green]")
        console.print(f"  Is Component: {flow.is_component}")
        if flow.updated_at:
            console.print(f"  Updated: {flow.updated_at}")
        if flow.folder_id:
            console.print(f"  Folder ID: {flow.folder_id}")

        # Show component counts if data is available
        if flow.data:
            nodes = flow.data.get("nodes", [])
            edges = flow.data.get("edges", [])
            console.print(f"  Components: {len(nodes)} nodes, {len(edges)} connections")

            # Count component types
            component_types = {}
            for node in nodes:
                node_type = node.get("data", {}).get("type", "Unknown")
                component_types[node_type] = component_types.get(node_type, 0) + 1

            if component_types:
                console.print("  Component Types:")
                for comp_type, count in component_types.items():
                    console.print(f"    - {comp_type}: {count}")


def _display_json(flows: List[Flow]) -> None:
    """Display flows in JSON format."""
    import json

    flows_data = [
        {
            "id": str(flow.id),
            "name": flow.name,
            "description": flow.description,
            "endpoint_name": flow.endpoint_name,
            "is_component": flow.is_component,
            "updated_at": flow.updated_at,
            "folder_id": str(flow.folder_id) if flow.folder_id else None,
            "user_id": str(flow.user_id) if flow.user_id else None,
        }
        for flow in flows
    ]

    console.print_json(json.dumps(flows_data, indent=2))
