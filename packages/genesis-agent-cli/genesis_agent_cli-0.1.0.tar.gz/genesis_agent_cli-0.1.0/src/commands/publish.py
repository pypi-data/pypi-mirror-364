"""Publish command for containerizing agents."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import click
import docker
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.services.config import Config
from src.services.container_builder import ContainerBuilder
from src.services.genesis_studio_api import GenesisStudioAPI

console = Console()


@click.command()
@click.argument("agent_id")
@click.option(
    "--tag", "-t", required=True, help="Docker image tag (e.g., myorg/agent:v1)"
)
@click.option("--push", is_flag=True, help="Push image to registry after building")
@click.option(
    "--base-image", default="genesis-studio-service:latest", help="Base image to use"
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    help="Output directory for Dockerfile",
)
@click.pass_obj
def publish(
    config: Config,
    agent_id: str,
    tag: str,
    push: bool,
    base_image: str,
    output_dir: Optional[Path],
) -> None:
    """Publish an agent as a container image."""
    asyncio.run(_publish_agent(config, agent_id, tag, push, base_image, output_dir))


async def _publish_agent(
    config: Config,
    agent_id: str,
    tag: str,
    push: bool,
    base_image: str,
    output_dir: Optional[Path],
) -> None:
    """Publish agent implementation."""
    api = GenesisStudioAPI(config)

    # Fetch agent details
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Fetching agent {agent_id}...", total=None)
        try:
            flow = await api.get_flow(agent_id)
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]Error fetching agent: {e}[/red]")
            raise click.Abort()

    console.print(f"\n[bold]Publishing agent:[/bold]")
    console.print(f"  Name: [cyan]{flow.name}[/cyan]")
    console.print(f"  Tag: [cyan]{tag}[/cyan]")
    console.print(f"  Base image: [cyan]{base_image}[/cyan]")

    # Build container
    builder = ContainerBuilder()

    try:
        # Create build context
        console.print("\nCreating build context...")
        build_dir = builder.create_build_context(
            flow=flow,
            base_image=base_image,
            output_dir=output_dir,
        )

        # Build image
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Building container image...", total=None)

            image = builder.build_image(
                build_dir=build_dir,
                tag=tag,
                progress_callback=lambda msg: progress.console.print(
                    f"  [dim]{msg}[/dim]"
                ),
            )

            progress.update(task, completed=True)

        console.print(f"\n[green]✓ Container image built successfully![/green]")
        console.print(f"  Image: [cyan]{tag}[/cyan]")
        console.print(f"  Size: [cyan]{_format_size(image.attrs['Size'])}[/cyan]")

        # Push if requested
        if push:
            console.print(f"\nPushing image to registry...")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                task = progress.add_task(f"Pushing {tag}...", total=None)

                builder.push_image(
                    tag=tag,
                    progress_callback=lambda msg: progress.console.print(
                        f"  [dim]{msg}[/dim]"
                    ),
                )

                progress.update(task, completed=True)

            console.print(f"[green]✓ Image pushed successfully![/green]")

        # Show run command
        console.print(f"\n[bold]To run the agent:[/bold]")
        console.print(f"  docker run -p 7860:7860 {tag}")

        # Save Dockerfile if output directory specified
        if output_dir:
            console.print(f"\n[dim]Dockerfile saved to: {build_dir}/Dockerfile[/dim]")

    except Exception as e:
        console.print(f"[red]Error building container: {e}[/red]")
        raise click.Abort()
    finally:
        # Cleanup temporary build directory if not output directory
        if not output_dir and build_dir and build_dir.exists():
            import shutil

            shutil.rmtree(build_dir)


def _format_size(size_bytes: int) -> str:
    """Format byte size to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
