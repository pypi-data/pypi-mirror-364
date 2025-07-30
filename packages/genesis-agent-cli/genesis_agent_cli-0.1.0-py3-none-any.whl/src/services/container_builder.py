"""Container builder service for creating Docker images from agents."""

import json
import tempfile
from pathlib import Path
from typing import Callable, Optional

import docker
from docker.models.images import Image

from src.services.genesis_studio_api import Flow


class ContainerBuilder:
    """Builds Docker containers for agents."""

    def __init__(self):
        """Initialize container builder."""
        self.docker_client = docker.from_env()

    def create_build_context(
        self,
        flow: Flow,
        base_image: str,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Create Docker build context for agent.

        Args:
            flow: Agent flow
            base_image: Base Docker image
            output_dir: Optional output directory

        Returns:
            Path to build directory
        """
        # Create build directory
        if output_dir:
            build_dir = output_dir / f"agent-{flow.id}"
            build_dir.mkdir(parents=True, exist_ok=True)
        else:
            build_dir = Path(tempfile.mkdtemp(prefix="genesis-agent-"))

        # Create agent configuration
        agent_config = {
            "id": str(flow.id),
            "name": flow.name,
            "description": flow.description,
            "endpoint_name": flow.endpoint_name,
            "data": flow.data,
        }

        # Save agent configuration
        config_path = build_dir / "agent-config.json"
        with open(config_path, "w") as f:
            json.dump(agent_config, f, indent=2)

        # Create Dockerfile
        dockerfile_content = self._create_dockerfile(base_image, flow)
        dockerfile_path = build_dir / "Dockerfile"
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content)

        # Create entrypoint script
        entrypoint_content = self._create_entrypoint_script()
        entrypoint_path = build_dir / "entrypoint.sh"
        with open(entrypoint_path, "w") as f:
            f.write(entrypoint_content)
        entrypoint_path.chmod(0o755)

        return build_dir

    def build_image(
        self,
        build_dir: Path,
        tag: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Image:
        """Build Docker image.

        Args:
            build_dir: Build directory with Dockerfile
            tag: Image tag
            progress_callback: Optional callback for build progress

        Returns:
            Built Docker image
        """
        # Build image
        image, build_logs = self.docker_client.images.build(
            path=str(build_dir),
            tag=tag,
            rm=True,  # Remove intermediate containers
            decode=True,  # Decode build logs
        )

        # Process build logs
        for log in build_logs:
            if progress_callback and "stream" in log:
                progress_callback(log["stream"].strip())

        return image

    def push_image(
        self,
        tag: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Push Docker image to registry.

        Args:
            tag: Image tag
            progress_callback: Optional callback for push progress
        """
        # Parse repository and tag
        if ":" in tag:
            repository, tag_name = tag.rsplit(":", 1)
        else:
            repository = tag
            tag_name = "latest"

        # Push image
        push_logs = self.docker_client.images.push(
            repository=repository,
            tag=tag_name,
            stream=True,
            decode=True,
        )

        # Process push logs
        for log in push_logs:
            if progress_callback:
                if "status" in log:
                    status = log["status"]
                    if "progress" in log:
                        status += f" {log['progress']}"
                    progress_callback(status)

    def _create_dockerfile(self, base_image: str, flow: Flow) -> str:
        """Create Dockerfile content."""
        return f"""# Genesis Agent Container
# Agent: {flow.name}
# ID: {flow.id}

FROM {base_image}

# Set working directory
WORKDIR /app

# Copy agent configuration
COPY agent-config.json /app/config/agents/
COPY entrypoint.sh /app/

# Set environment variables
ENV AGENT_ID={flow.id}
ENV AGENT_NAME="{flow.name}"
ENV LANGFLOW_AUTO_LOGIN=false
ENV LANGFLOW_LOAD_FLOWS_PATH=/app/config/agents/agent-config.json

# Expose Langflow port
EXPOSE 7860

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
"""

    def _create_entrypoint_script(self) -> str:
        """Create entrypoint script."""
        return """#!/bin/bash
set -e

echo "Starting Genesis Agent: $AGENT_NAME"
echo "Agent ID: $AGENT_ID"

# Start Langflow with the agent configuration
exec uv run langflow run --host 0.0.0.0 --port 7860
"""
