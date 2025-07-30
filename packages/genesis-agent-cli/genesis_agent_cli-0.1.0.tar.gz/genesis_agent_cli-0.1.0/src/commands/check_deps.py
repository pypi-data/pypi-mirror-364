"""Check dependencies command for validating agent dependencies."""

import asyncio
from pathlib import Path
from typing import Dict, List, Set, Tuple

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from src.models.agent_spec_enhanced import AgentSpecV2Enhanced
from src.services.config import Config
from src.services.genesis_studio_api import GenesisStudioAPI

console = Console()


@click.command()
@click.argument(
    "spec_file",
    type=click.Path(exists=True, path_type=Path),
    required=False,
)
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help="Check dependencies for all templates in the templates directory",
)
@click.option(
    "--show-available",
    is_flag=True,
    help="Show all available agents in Genesis Studio",
)
@click.pass_obj
def check_deps(
    config: Config,
    spec_file: Path = None,
    all: bool = False,
    show_available: bool = False,
) -> None:
    """Check if agent dependencies are available in Genesis Studio.

    This command helps you verify that all required agent dependencies
    are deployed before creating or updating an agent.
    """
    asyncio.run(_check_deps(config, spec_file, all, show_available))


async def _check_deps(
    config: Config,
    spec_file: Path = None,
    check_all: bool = False,
    show_available: bool = False,
) -> None:
    """Check dependencies implementation."""
    api = GenesisStudioAPI(config)

    # Get available agents from Genesis Studio
    console.print("Fetching available agents from Genesis Studio...")
    try:
        available_agents = await api.list_flows()
        available_agent_ids = {agent.id for agent in available_agents}
        available_agent_names = {agent.name: agent.id for agent in available_agents}
    except Exception as e:
        console.print(f"[red]Error fetching agents: {e}[/red]")
        return

    console.print(
        f"Found [cyan]{len(available_agents)}[/cyan] agents in Genesis Studio\n"
    )

    # Show available agents if requested
    if show_available:
        _show_available_agents(available_agents)
        return

    # Check dependencies
    if check_all:
        # Check all templates
        template_dir = Path("templates")
        spec_files = list(template_dir.rglob("*.yaml"))
        console.print(f"Checking dependencies for {len(spec_files)} templates...\n")

        results = []
        for spec_file in spec_files:
            result = await _check_single_spec(
                spec_file, available_agent_ids, available_agent_names
            )
            if result:
                results.append(result)

        _show_dependency_summary(results)

    elif spec_file:
        # Check single file
        result = await _check_single_spec(
            spec_file, available_agent_ids, available_agent_names
        )
        if result:
            _show_single_result(result)

    else:
        console.print(
            "[yellow]Please specify a spec file or use --all to check all templates[/yellow]"
        )


async def _check_single_spec(
    spec_file: Path, available_ids: Set[str], available_names: Dict[str, str]
) -> Dict:
    """Check dependencies for a single specification."""
    try:
        with open(spec_file, "r") as f:
            spec_data = yaml.safe_load(f)

        # Parse specification - try enhanced format first, then v2
        spec = None
        try:
            # Try parsing as enhanced format (all our templates use this)
            spec = AgentSpecV2Enhanced(**spec_data)
        except Exception:
            # If parsing fails, work with raw data
            spec = None
            spec_data = spec_data or {}

        agent_id = spec_data.get("id", "unknown")
        agent_name = spec_data.get("name", "Unknown")

        # Collect dependencies
        dependencies = []
        missing_deps = []
        available_deps = []

        # From reusability.dependencies
        if spec:
            # Handle enhanced format
            if (
                hasattr(spec, "reusability")
                and spec.reusability
                and spec.reusability.dependencies
            ):
                for dep in spec.reusability.dependencies:
                    dep_info = {
                        "agent_id": dep.agentId,
                        "version": dep.version,
                        "required": getattr(dep, "required", True),
                        "source": "reusability.dependencies",
                    }
                    dependencies.append(dep_info)

                # Check if available
                if dep.agentId in available_ids:
                    available_deps.append(dep_info)
                else:
                    # Try to extract short name and check
                    if dep.agentId.startswith("urn:agent:"):
                        parts = dep.agentId.split(":")
                        if len(parts) >= 4:
                            short_name = parts[3]
                            if short_name in available_names:
                                available_deps.append(dep_info)
                            else:
                                missing_deps.append(dep_info)
                    else:
                        missing_deps.append(dep_info)

        # From component $ref: references
        if "components" in spec_data:
            for component in spec_data["components"]:
                if component.get("type", "").startswith("$ref:"):
                    ref_name = component["type"].replace("$ref:", "")
                    dep_info = {
                        "agent_id": ref_name,
                        "version": "*",
                        "required": True,
                        "source": f"component: {component.get('name', 'unnamed')}",
                    }
                    dependencies.append(dep_info)

                    # Check if available
                    if ref_name in available_names:
                        available_deps.append(dep_info)
                    else:
                        missing_deps.append(dep_info)

        # From orchestration flow
        if "orchestration" in spec_data and "flow" in spec_data.get(
            "orchestration", {}
        ):
            for step in spec_data["orchestration"]["flow"]:
                if step.get("agent", "").startswith("$ref:"):
                    ref_name = step["agent"].replace("$ref:", "")
                    dep_info = {
                        "agent_id": ref_name,
                        "version": "*",
                        "required": True,
                        "source": f"orchestration step: {step.get('step', 'unnamed')}",
                    }
                    dependencies.append(dep_info)

                    if ref_name in available_names:
                        available_deps.append(dep_info)
                    else:
                        missing_deps.append(dep_info)

        return {
            "file": spec_file,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "total_deps": len(dependencies),
            "available": len(available_deps),
            "missing": len(missing_deps),
            "dependencies": dependencies,
            "missing_deps": missing_deps,
            "available_deps": available_deps,
        }

    except Exception as e:
        console.print(f"[red]Error checking {spec_file}: {e}[/red]")
        return None


def _show_available_agents(agents: List) -> None:
    """Show all available agents."""
    table = Table(title="Available Agents in Genesis Studio", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("Updated")

    for agent in sorted(agents, key=lambda x: x.name):
        table.add_row(
            agent.id[:20] + "..." if len(agent.id) > 20 else agent.id,
            agent.name,
            (
                (agent.description or "")[:50] + "..."
                if agent.description and len(agent.description) > 50
                else agent.description or ""
            ),
            (
                agent.updated_at.strftime("%Y-%m-%d")
                if hasattr(agent, "updated_at") and agent.updated_at
                else "N/A"
            ),
        )

    console.print(table)


def _show_single_result(result: Dict) -> None:
    """Show dependency check result for a single file."""
    status_icon = "✓" if result["missing"] == 0 else "✗"
    status_color = "green" if result["missing"] == 0 else "red"

    panel = Panel(
        f"[bold]{result['agent_name']}[/bold]\n"
        f"ID: {result['agent_id']}\n"
        f"File: {result['file']}",
        title=f"[{status_color}]{status_icon} Agent Dependencies[/{status_color}]",
        border_style=status_color,
    )
    console.print(panel)

    if result["total_deps"] == 0:
        console.print("[dim]No dependencies declared[/dim]\n")
        return

    # Show dependency tree
    tree = Tree("Dependencies")

    # Available dependencies
    if result["available_deps"]:
        available_branch = tree.add("[green]✓ Available[/green]")
        for dep in result["available_deps"]:
            dep_text = f"{dep['agent_id']} ({dep['source']})"
            if dep["version"] != "*":
                dep_text += f" version: {dep['version']}"
            available_branch.add(f"[green]{dep_text}[/green]")

    # Missing dependencies
    if result["missing_deps"]:
        missing_branch = tree.add("[red]✗ Missing[/red]")
        for dep in result["missing_deps"]:
            dep_text = f"{dep['agent_id']} ({dep['source']})"
            if dep["version"] != "*":
                dep_text += f" version: {dep['version']}"
            if not dep["required"]:
                dep_text += " [dim](optional)[/dim]"
            missing_branch.add(f"[red]{dep_text}[/red]")

    console.print(tree)
    console.print()

    # Summary
    console.print(f"Total dependencies: [cyan]{result['total_deps']}[/cyan]")
    console.print(f"Available: [green]{result['available']}[/green]")
    console.print(
        f"Missing: [{'red' if result['missing'] > 0 else 'green'}]{result['missing']}[/{'red' if result['missing'] > 0 else 'green'}]"
    )

    if result["missing"] > 0:
        console.print(
            "\n[yellow]⚠ Some dependencies are missing. Deploy them before creating this agent.[/yellow]"
        )


def _show_dependency_summary(results: List[Dict]) -> None:
    """Show summary of all dependency checks."""
    # Group by status
    all_satisfied = [r for r in results if r["missing"] == 0]
    have_missing = [r for r in results if r["missing"] > 0]

    console.print(f"[bold]Dependency Check Summary[/bold]\n")
    console.print(f"Total templates checked: [cyan]{len(results)}[/cyan]")
    console.print(f"All dependencies satisfied: [green]{len(all_satisfied)}[/green]")
    console.print(f"Missing dependencies: [red]{len(have_missing)}[/red]\n")

    if have_missing:
        # Show agents with missing dependencies
        table = Table(title="Agents with Missing Dependencies", show_header=True)
        table.add_column("Agent", style="cyan")
        table.add_column("Missing", style="red", justify="center")
        table.add_column("Missing Dependencies")

        for result in sorted(have_missing, key=lambda x: x["missing"], reverse=True):
            missing_names = [dep["agent_id"] for dep in result["missing_deps"]]
            table.add_row(
                result["agent_name"],
                str(result["missing"]),
                ", ".join(missing_names[:3])
                + ("..." if len(missing_names) > 3 else ""),
            )

        console.print(table)
        console.print()

        # Show deployment order suggestion
        console.print("[bold]Suggested Deployment Order:[/bold]")

        # Build dependency graph
        dep_graph = {}
        all_agents = set()

        for result in results:
            agent_name = result["agent_name"]
            all_agents.add(agent_name)
            deps = [d["agent_id"] for d in result.get("dependencies", [])]
            dep_graph[agent_name] = deps

        # Find deployment order
        deployment_order = _topological_sort(dep_graph)

        for i, agent in enumerate(deployment_order, 1):
            console.print(f"{i}. {agent}")


def _topological_sort(graph: Dict[str, List[str]]) -> List[str]:
    """Perform topological sort to find deployment order."""
    # Count in-degrees
    in_degree = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1

    # Find nodes with no dependencies
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)

        # Remove this node from graph
        if node in graph:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

    # Add any remaining nodes (cycles)
    for node in graph:
        if node not in result:
            result.append(node)

    return result
