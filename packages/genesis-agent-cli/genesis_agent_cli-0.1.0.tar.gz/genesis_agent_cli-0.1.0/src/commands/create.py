"""
Create command - Create flows from agent specifications.

This command supports both the enhanced format (with agentGoal, KPIs, etc.) and
the standard format, including multi-agent orchestration patterns.
"""

import click
import json
from pathlib import Path
from typing import Optional

from src.converters.flow_converter import FlowConverter
from src.services.config import Config
from src.services.genesis_studio_api import GenesisStudioAPI
from src.services.variable_resolver import VariableResolver


@click.command(name="create")
@click.option(
    "--template", "-t", required=True, help="Path to enhanced or v2 template YAML file"
)
@click.option("--name", "-n", help="Flow name (defaults to template name)")
@click.option("--folder", "-f", help="Folder ID to create flow in")
@click.option(
    "--output", "-o", help="Save flow to file instead of creating in Genesis Studio"
)
@click.option(
    "--validate-only",
    "-v",
    is_flag=True,
    help="Only validate the flow without creating it",
)
@click.option(
    "--show-metadata", is_flag=True, help="Display agent metadata (goal, KPIs, etc.)"
)
@click.option(
    "--var", 
    multiple=True, 
    help="Set runtime variable (format: key=value). Can be used multiple times."
)
@click.option(
    "--var-file",
    type=click.Path(exists=True),
    help="Load variables from JSON or YAML file"
)
@click.option(
    "--tweak",
    multiple=True,
    help="Apply tweaks to components (format: component_id.field=value)"
)
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.pass_obj
def create(
    config: Config,
    template: str,
    name: Optional[str],
    folder: Optional[str],
    output: Optional[str],
    validate_only: bool,
    show_metadata: bool,
    var: tuple,
    var_file: Optional[str],
    tweak: tuple,
    debug: bool,
):
    """
    Create a Genesis Studio flow from an agent specification.

    This command supports:
    - Enhanced format with full metadata (agentGoal, KPIs, tags, etc.)
    - Multi-agent orchestration with agent-as-tool pattern
    - Backward compatibility with v2 format

    Enhanced format includes:
    - Agent goal and KPIs
    - Target user and value generation
    - Multi-agent dependencies and reusability
    - Complete audit and security configuration

    Examples:

        # Create multi-agent orchestrator
        genesis-agent create -t templates/healthcare/benefit-check-agent.yaml

        # Show agent metadata
        genesis-agent create -t templates/healthcare/prior-auth-agent.yaml --show-metadata

        # Save flow to file
        genesis-agent create -t template.yaml -o flow.json
    """
    try:
        # Check template exists
        template_path = Path(template)
        if not template_path.exists():
            click.echo(f"❌ Template file not found: {template}", err=True)
            return

        # Create variable resolver
        variable_resolver = VariableResolver()
        
        # Load variables from file if provided
        if var_file:
            click.echo(f"📄 Loading variables from: {var_file}")
            variable_resolver.load_variables_from_file(var_file)
            
        # Parse CLI variables
        if var:
            cli_vars = {}
            for var_def in var:
                if '=' not in var_def:
                    click.echo(f"❌ Invalid variable format: {var_def}. Expected format: key=value", err=True)
                    return
                key, value = var_def.split('=', 1)
                # Try to parse value as JSON
                try:
                    cli_vars[key] = json.loads(value)
                except json.JSONDecodeError:
                    # If not valid JSON, treat as string
                    cli_vars[key] = value
            variable_resolver.set_variables(cli_vars)
            
        # Show loaded variables if debug
        if debug and variable_resolver.variables:
            click.echo("\n🔧 Loaded Variables:")
            for key, value in variable_resolver.variables.items():
                click.echo(f"  - {key}: {value}")

        # Create converter with config and variable resolver
        converter = FlowConverter(config, variable_resolver)

        # Parse specification to check format
        spec = converter.parser.parse_specification(str(template_path))

        # Display metadata if requested
        if show_metadata:
            click.echo("\n📋 Agent Metadata:")
            click.echo(f"  - ID: {spec.id if hasattr(spec, 'id') else 'N/A'}")
            click.echo(f"  - Name: {spec.name if hasattr(spec, 'name') else 'N/A'}")

            if hasattr(spec, "agentGoal"):
                click.echo(f"  - Goal: {spec.agentGoal}")
                click.echo(f"  - Kind: {spec.kind}")
                click.echo(f"  - Target User: {spec.targetUser}")
                click.echo(f"  - Value Generation: {spec.valueGeneration}")

                if spec.tags:
                    click.echo(f"  - Tags: {', '.join(spec.tags)}")

                if spec.reusability:
                    click.echo("\n🔄 Reusability:")
                    click.echo(f"  - As Tools: {spec.reusability.asTools}")
                    if spec.reusability.provides:
                        click.echo(
                            f"  - Tool Name: {spec.reusability.provides.toolName}"
                        )
                        click.echo(
                            f"  - Tool Description: {spec.reusability.provides.toolDescription}"
                        )
                    if spec.reusability.dependencies:
                        click.echo("  - Dependencies:")
                        for dep in spec.reusability.dependencies:
                            click.echo(f"    - {dep.agentId} ({dep.version})")

                if hasattr(spec, "kpis") and spec.kpis:
                    click.echo("\n📊 KPIs:")
                    for kpi in spec.kpis:
                        click.echo(f"  - {kpi.name}: {kpi.description}")
                        if kpi.target:
                            click.echo(f"    Target: {kpi.target} {kpi.unit or ''}")

        # Convert template to flow
        click.echo(f"\n🔄 Converting template: {template_path.name}")
        flow = converter.convert_sync(str(template_path))
        
        # Apply tweaks if provided
        if tweak:
            click.echo("\n⚙️  Applying tweaks...")
            try:
                tweaks_dict = variable_resolver.create_tweaks_from_cli(list(tweak))
                flow = converter.apply_tweaks(flow, tweaks_dict)
                if debug:
                    click.echo("Applied tweaks:")
                    for component_id, fields in tweaks_dict.items():
                        for field, value in fields.items():
                            click.echo(f"  - {component_id}.{field} = {value}")
            except ValueError as e:
                click.echo(f"❌ Tweak error: {e}", err=True)
                return
        
        # Check for undefined variables
        undefined_vars = variable_resolver.get_undefined_variables()
        if undefined_vars:
            click.echo("\n⚠️  Undefined variables found:")
            for var in undefined_vars:
                click.echo(f"  - {var}")
            click.echo("\nThese variables will remain as placeholders for Langflow to resolve.")

        # Set flow name
        if name:
            flow["name"] = name
        elif not flow.get("name"):
            flow["name"] = template_path.stem.replace("-", " ").title()

        # Validate flow
        click.echo("🔍 Validating flow structure...")
        errors = converter.validate_flow(flow)

        if errors:
            click.echo("❌ Validation errors:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            return
        else:
            click.echo("✅ Flow validation passed!")

        # Display flow statistics
        data = flow.get("data", {})
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])

        click.echo(f"\n📊 Flow Statistics:")
        click.echo(f"  - Nodes: {len(nodes)}")
        click.echo(f"  - Edges: {len(edges)}")

        # Check for multi-agent pattern
        agent_tool_refs = [n for n in nodes if n.get("type") == "AgentTool"]
        if agent_tool_refs:
            click.echo(f"  - Agent References: {len(agent_tool_refs)}")
            click.echo("  ✨ Multi-agent orchestration detected!")

        if debug:
            # Display node types
            click.echo("\n🔧 Node Types:")
            node_types = {}
            for node in nodes:
                node_type = node.get("type", "Unknown")
                node_types[node_type] = node_types.get(node_type, 0) + 1

            for node_type, count in sorted(node_types.items()):
                click.echo(f"  - {node_type}: {count}")

            # Show agent references
            if agent_tool_refs:
                click.echo("\n🤖 Agent References:")
                for ref in agent_tool_refs:
                    config = ref.get("data", {}).get("node", {}).get("template", {})
                    agent_id = config.get("agent_id", {}).get("value", "Unknown")
                    tool_name = config.get("tool_name", {}).get("value", "Unknown")
                    click.echo(f"  - {tool_name}: {agent_id}")

        if validate_only:
            click.echo("\n✅ Validation complete (--validate-only flag set)")
            return

        # Save to file or create in Genesis Studio
        if output:
            # Save to file
            output_path = Path(output)
            click.echo(f"\n💾 Saving flow to: {output_path}")

            with open(output_path, "w") as f:
                json.dump(flow, f, indent=2)

            click.echo("✅ Flow saved successfully!")

        else:
            # Create in Genesis Studio
            click.echo("\n🚀 Creating flow in Genesis Studio...")

            api = GenesisStudioAPI(config)

            # Set folder if provided
            if folder:
                flow["folder"] = folder

            # Create flow using async
            import asyncio
            from src.services.genesis_studio_api import FlowCreate

            async def create_flow_async():
                flow_create = FlowCreate(
                    name=flow.get("name", "Untitled Flow"),
                    description=flow.get("description"),
                    data=flow.get("data", {}),
                    endpoint_name=flow.get("endpoint_name"),
                    is_component=flow.get("is_component", False),
                )
                return await api.create_flow(flow_create)

            try:
                result = asyncio.run(create_flow_async())

                flow_id = result.id
                click.echo(f"✅ Flow created successfully!")
                click.echo(f"🆔 Flow ID: {flow_id}")

                # Display URL if available
                base_url = config.genesis_studio_url
                if base_url:
                    flow_url = f"{base_url}/flow/{flow_id}"
                    click.echo(f"🔗 Open in Genesis Studio: {flow_url}")

                # Show multi-agent tip
                if agent_tool_refs:
                    click.echo(
                        "\n💡 Tip: Make sure the referenced agents exist in Genesis Studio"
                    )
                    click.echo("   for the multi-agent orchestration to work properly.")
            except Exception as e:
                click.echo(f"❌ Failed to create flow: {e}", err=True)

    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        if debug:
            import traceback

            traceback.print_exc()


# Register command with CLI
def register(cli):
    """Register the create command with the CLI."""
    cli.add_command(create)
