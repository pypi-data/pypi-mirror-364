"""Run command for executing flows."""

import click
import json
from typing import Dict, Any, Optional
import asyncio

from src.services.config import Config
from src.services.studio_api import StudioAPI
from src.services.variable_resolver import VariableResolver


@click.command()
@click.argument('flow_id')
@click.option('--input', '-i', help='Input data as JSON string')
@click.option('--file', '-f', type=click.Path(exists=True), help='Input data from JSON file')
@click.option('--output', '-o', help='Save output to file')
@click.option('--stream', is_flag=True, help='Stream output in real-time')
@click.option('--tweak', '-t', multiple=True, help='Apply runtime tweaks (format: component_id.field=value)')
@click.option('--var', '-v', multiple=True, help='Set runtime variables (format: key=value)')
@click.option('--var-file', type=click.Path(exists=True), help='Load variables from JSON/YAML file')
@click.option('--timeout', default=300, help='Execution timeout in seconds')
@click.pass_context
def run(ctx, flow_id: str, input: Optional[str], file: Optional[str], 
        output: Optional[str], stream: bool, tweak: tuple, var: tuple,
        var_file: Optional[str], timeout: int):
    """Run a flow with optional input data and runtime tweaks.
    
    Examples:
        # Run with inline input
        genesis-agent run my-flow --input '{"question": "What is 2+2?"}'
        
        # Run with tweaks
        genesis-agent run my-flow --tweak agent-main.temperature=0.3
        
        # Run with variables
        genesis-agent run my-flow --var model=gpt-4 --var temperature=0.7
        
        # Run with variable file
        genesis-agent run my-flow --var-file production.yaml
    """
    config = Config.load()
    
    try:
        asyncio.run(_run_flow(
            config, flow_id, input, file, output, stream, 
            tweak, var, var_file, timeout
        ))
    except Exception as e:
        click.echo(f"Error running flow: {str(e)}", err=True)
        ctx.exit(1)


async def _run_flow(config: Config, flow_id: str, input_str: Optional[str], 
                    input_file: Optional[str], output_file: Optional[str], 
                    stream: bool, tweaks: tuple, variables: tuple,
                    var_file: Optional[str], timeout: int):
    """Execute a flow with the given parameters."""
    api = StudioAPI(config)
    
    # Prepare input data
    input_data = {}
    if input_str:
        try:
            input_data = json.loads(input_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in --input parameter")
    elif input_file:
        with open(input_file, 'r') as f:
            input_data = json.load(f)
    
    # Prepare variables
    all_variables = {}
    
    # Load from file first
    if var_file:
        all_variables.update(VariableResolver.load_from_file(var_file))
        click.echo(f"Loaded variables from {var_file}")
    
    # Then apply command-line variables (these override file variables)
    for var_str in variables:
        var_dict = VariableResolver.parse_var_string(var_str)
        # Merge nested dictionaries
        _deep_merge(all_variables, var_dict)
    
    # Prepare tweaks
    tweak_dict = {}
    for tweak_str in tweaks:
        if '=' not in tweak_str:
            raise ValueError(f"Invalid tweak format: {tweak_str}. Expected: component_id.field=value")
        key, value = tweak_str.split('=', 1)
        # Parse value
        try:
            # Try to parse as JSON first (for complex values)
            value = json.loads(value)
        except:
            # Otherwise treat as string and convert numbers/booleans
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            else:
                try:
                    # Try int
                    value = int(value)
                except:
                    try:
                        # Try float
                        value = float(value)
                    except:
                        # Keep as string
                        pass
        tweak_dict[key] = value
    
    # Apply tweaks to flow if needed
    if tweaks or all_variables:
        click.echo("Applying runtime modifications...")
        
        # Get the flow
        flow = await api.get_flow(flow_id)
        if not flow:
            raise ValueError(f"Flow '{flow_id}' not found")
        
        # Create resolver with variables
        resolver = VariableResolver(all_variables)
        resolver.tweaks = tweak_dict
        
        # Resolve variables in the flow
        if all_variables:
            flow = resolver.resolve_flow(flow)
            if resolver.undefined_vars:
                click.echo(f"⚠️  Warning: Undefined variables: {', '.join(resolver.undefined_vars)}")
        
        # Apply tweaks
        if tweak_dict:
            flow = resolver.apply_tweaks(flow)
            click.echo(f"Applied {len(tweak_dict)} tweaks")
            for key, value in tweak_dict.items():
                click.echo(f"  - {key} = {value}")
        
        # Update the flow
        updated = await api.update_flow(flow_id, flow)
        if not updated:
            raise ValueError("Failed to update flow with tweaks")
    
    # Run the flow
    click.echo(f"\n🚀 Running flow '{flow_id}'...")
    
    if stream:
        click.echo("Streaming output:")
        click.echo("-" * 50)
        
        async for event in api.run_flow_stream(flow_id, input_data, timeout=timeout):
            if event.get('type') == 'error':
                click.echo(f"\n❌ Error: {event.get('message', 'Unknown error')}", err=True)
            elif event.get('type') == 'token':
                click.echo(event.get('token', ''), nl=False)
            elif event.get('type') == 'result':
                click.echo("\n" + "-" * 50)
                _display_result(event.get('data', {}), output_file)
            else:
                # Debug output
                if ctx.obj.get('debug'):
                    click.echo(f"\nDebug: {json.dumps(event)}")
    else:
        result = await api.run_flow(flow_id, input_data, timeout=timeout)
        
        if result.get('success'):
            click.echo("✅ Flow executed successfully!")
            _display_result(result.get('outputs', {}), output_file)
        else:
            click.echo(f"❌ Flow execution failed: {result.get('error', 'Unknown error')}", err=True)


def _display_result(result: Dict[str, Any], output_file: Optional[str]):
    """Display or save the result."""
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        click.echo(f"Output saved to {output_file}")
    else:
        click.echo("\nOutput:")
        click.echo(json.dumps(result, indent=2))


def _deep_merge(target: dict, source: dict):
    """Deep merge source into target."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value