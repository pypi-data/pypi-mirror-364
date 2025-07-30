# Genesis Agent CLI

A powerful command-line interface for creating, managing, and deploying AI agents in Genesis Studio. This CLI enables you to define agents using YAML specifications and seamlessly integrate them with the Genesis platform.

## Features

- **Native Genesis Studio Integration**: Create flows that work directly with Genesis Studio
- **Enhanced Agent Specifications**: Support for v2 agent format with comprehensive metadata
- **Component Validation**: Automatic validation against Genesis Studio's component registry
- **Dynamic Component Mapping**: Real-time mapping of Genesis types to Langflow components
- **Healthcare Templates**: Pre-built templates for healthcare workflows
- **Multi-Agent Support**: Create orchestrators that use other agents as tools

## Installation

```bash
pip install -e .
```

## Quick Start

1. **Check Genesis Studio configuration**:
```bash
genesis-agent config-check
```

2. **Create an agent from a template**:
```bash
genesis-agent create -t templates/healthcare/agents/medication-extractor.yaml
```

3. **List your agents**:
```bash
genesis-agent list
```

## Commands

### Configuration
```bash
# Check current configuration and connection
genesis-agent config-check

# Show CLI version
genesis-agent version
```

### Creating Agents
```bash
# Create a flow from template
genesis-agent create -t <template-path>

# Create with custom name
genesis-agent create -t template.yaml -n "My Custom Agent"

# Create in specific folder
genesis-agent create -t template.yaml -f <folder-id>

# Show agent metadata (goal, KPIs, etc.)
genesis-agent create -t template.yaml --show-metadata

# Create with runtime variables
genesis-agent create -t template.yaml --var key=value --var temperature=0.7

# Create with variables from file
genesis-agent create -t template.yaml --var-file variables.json

# Create with tweaks
genesis-agent create -t template.yaml --tweak component-id.field=value

# Save flow to file instead of creating in Genesis Studio
genesis-agent create -t template.yaml -o flow.json

# Validate only (don't create)
genesis-agent create -t template.yaml --validate-only

# Enable debug output
genesis-agent create -t template.yaml --debug
```

### Managing Agents
```bash
# List all agents/flows in Genesis Studio
genesis-agent list

# List with different formats
genesis-agent list -f table    # Default table format
genesis-agent list -f detailed # Detailed view
genesis-agent list -f json     # JSON output

# Limit number of results
genesis-agent list -l 10

# Delete an agent/flow
genesis-agent delete <agent-id>

# Delete without confirmation prompt
genesis-agent delete <agent-id> -f
```

### Dependency Checking
```bash
# Check dependencies for a specific template
genesis-agent check-deps <template-path>

# Check dependencies for all templates
genesis-agent check-deps --all

# Show all available agents in Genesis Studio
genesis-agent check-deps --show-available
```

### Publishing Agents
```bash
# Publish an agent as a container image
genesis-agent publish <agent-id> -t myorg/agent:v1

# Publish and push to registry
genesis-agent publish <agent-id> -t myorg/agent:v1 --push

# Use custom base image
genesis-agent publish <agent-id> -t myorg/agent:v1 --base-image python:3.11
```

## Template Format (v2 Enhanced)

The CLI uses an enhanced v2 specification format that includes comprehensive metadata for enterprise agent management.

### Basic Structure
```yaml
# Agent Metadata
id: "urn:agent:genesis:example:1"
name: "Example Agent"
fullyQualifiedName: "genesis.autonomize.ai.example"
description: "Agent description"
domain: "autonomize.ai"
subDomain: "examples"
version: "1.0.0"
environment: "production"
agentOwner: "team@example.com"
agentOwnerDisplayName: "Team Name"
email: "team@example.com"
status: "ACTIVE"

# Tags for categorization
tags:
  - "example"
  - "reusable"
  - "healthcare"

# Agent Configuration
kind: "Single Agent"  # Single Agent, Multi Agent, Orchestrator
agentGoal: "Clear description of what the agent accomplishes"
targetUser: "internal"  # internal, external, both
valueGeneration: "ProcessAutomation"  # ProcessAutomation, InsightGeneration, DecisionSupport, ContentCreation
interactionMode: "RequestResponse"  # RequestResponse, MultiTurnConversation, Streaming, Batch
runMode: "RealTime"  # RealTime, Scheduled, EventDriven
agencyLevel: "ModelDrivenWorkflow"  # StaticWorkflow, ModelDrivenWorkflow, AdaptiveWorkflow, Autonomous
toolsUse: true
learningCapability: "None"  # None, Contextual, Persistent, Continuous

# Components using the "provides" pattern
components:
  - id: "input"
    name: "User Input"
    kind: "Data"
    type: "genesis:chat_input"
    description: "Receive user input"
    provides:
      - useAs: "input"
        in: "main-agent"
        description: "User query to agent"
    
  - id: "main-agent"
    name: "Main Agent"
    kind: "Agent"
    type: "genesis:agent"  # Using default Agent component
    description: "Process user requests"
    config:
      agent_llm: "OpenAI"  # Built-in LLM provider
      model_name: "gpt-4"
      temperature: 0.7
      system_prompt: |
        You are a helpful assistant.
    provides:
      - useAs: "input"
        in: "output"
        description: "Agent response"
    
  - id: "output"
    name: "Response Output"
    kind: "Data"
    type: "genesis:chat_output"
    description: "Display agent response"
```

### Healthcare Agent Example
```yaml
id: "urn:agent:genesis:medication_extractor:1"
name: "Medication Extractor"
fullyQualifiedName: "genesis.autonomize.ai.medication_extractor"
description: "Extracts medication information from clinical text"
kind: "Single Agent"
agentGoal: "Extract medications with dosages, frequencies, and routes from clinical text"

# Reusability configuration
reusability:
  asTools: true
  standalone: true
  provides:
    toolName: "MedicationExtractor"
    toolDescription: "Extracts medications from clinical text"
    inputSchema:
      type: "object"
      properties:
        clinical_text:
          type: "string"
    outputSchema:
      type: "object"
      properties:
        medications:
          type: "array"

components:
  - id: "agent-main"
    type: "genesis:agent"
    config:
      agent_llm: "OpenAI"
      model_name: "gpt-4"
      system_prompt: |
        Extract all medications with dosages...
```

### Multi-Agent Orchestrator Example
```yaml
kind: "Multi Agent"
agentGoal: "Coordinate multiple agents to process complex requests"

# Define dependencies on other agents
reusability:
  dependencies:
    - agentId: "urn:agent:genesis:document_processor:1"
      version: ">=1.0.0"
    - agentId: "urn:agent:genesis:medication_extractor:1"
      version: ">=1.0.0"

components:
  # Reference other agents as tools
  - id: "doc-processor"
    type: "$ref:document_processor"
    asTools: true
    provides:
      - useAs: "tools"
        in: "coordinator"
        
  - id: "med-extractor"
    type: "$ref:medication_extractor"
    asTools: true
    provides:
      - useAs: "tools"
        in: "coordinator"
```

## Component Types

### Core Components
- `genesis:agent` - Default agent with built-in LLM configuration
- `genesis:chat_input` - User input component
- `genesis:chat_output` - Response output component
- `genesis:memory` - Conversation memory
- `genesis:conversation_memory` - Persistent conversation tracking

### Healthcare Components
- `genesis:rxnorm` - RxNorm medication extraction
- `genesis:icd10` - ICD-10 diagnosis code validation
- `genesis:cpt_code` - CPT procedure code validation
- `genesis:knowledge_hub_search` - Search clinical documents
- `genesis:encoder_pro` - Medical coding service
- `genesis:pa_lookup` - Prior authorization lookup
- `genesis:qnext_auth_history` - Claims and authorization history

### Tool Components
- `genesis:calculator` - Mathematical calculations
- `genesis:api_component` - Generic API integration
- `genesis:file_reader` - Read files from URLs or paths
- `genesis:form_recognizer` - OCR and document extraction

## Runtime Variables and Tweaks

### Runtime Variables

The Genesis Agent CLI supports runtime configuration variables that can be substituted in agent specifications at flow creation time. This feature allows for dynamic configuration without modifying the agent spec files.

#### Variable Types

1. **Runtime Variables**: Defined using `{variable_name}` syntax
2. **Environment Variables**: Defined using `${ENV_VAR}` syntax
3. **Nested Variables**: Access nested values with dot notation `{config.api_key}`

#### Using Variables in Templates

Variables can be used anywhere in your agent specification:

```yaml
name: {agent_name}
description: A configurable agent for {purpose}

components:
  - id: "agent-main"
    type: "genesis:agent"
    config:
      agent_llm: "{llm_provider}"
      model_name: "{model_name}"
      temperature: {temperature}
      api_key: "${OPENAI_API_KEY}"  # Environment variable
      system_prompt: |
        {system_prompt_template}
        Your goal is to {agent_goal}.
```

#### Setting Variables via CLI

Variables can be provided through multiple methods:

1. **Command-line arguments**:
   ```bash
   genesis-agent create -t template.yaml \
     --var agent_name="My Assistant" \
     --var temperature=0.7 \
     --var 'config={"timeout": 30}'
   ```

2. **Variable file** (JSON or YAML):
   ```bash
   genesis-agent create -t template.yaml --var-file variables.json
   ```

   Example `variables.json`:
   ```json
   {
     "agent_name": "Advanced Assistant",
     "llm_provider": "OpenAI",
     "model_name": "gpt-4",
     "temperature": 0.5,
     "agent_goal": "help users with complex tasks"
   }
   ```

3. **Environment variables**:
   ```bash
   export OPENAI_API_KEY="sk-..."
   export LLM_MODEL="gpt-4"
   genesis-agent create -t template.yaml
   ```

#### Type Preservation

When a variable represents the entire value, its type is preserved:
- `{count}` with value `42` → `42` (integer)
- `{enabled}` with value `true` → `true` (boolean)
- `{items}` with value `["a", "b"]` → `["a", "b"]` (array)

When embedded in a string, variables are converted to strings:
- `"Count: {count}"` with value `42` → `"Count: 42"`

### Tweaks

Tweaks allow you to modify specific component configurations after the flow is created. This is useful for adjusting parameters without editing the template.

#### Applying Tweaks

Use the `--tweak` flag to modify component fields:

```bash
genesis-agent create -t template.yaml \
  --tweak agent-main.temperature=0.3 \
  --tweak agent-main.max_tokens=2000 \
  --tweak 'agent-main.system_prompt="New system prompt"'
```

Format: `component_id.field_name=value`

#### Tweaks with Variables

Tweaks can also use variables:

```bash
genesis-agent create -t template.yaml \
  --var new_temp=0.3 \
  --tweak agent-main.temperature={new_temp}
```

### Complete Example

Here's a complete example using variables and tweaks:

1. **Create a template** (`agent-template.yaml`):
   ```yaml
   name: {agent_name}
   components:
     - id: chat-input
       type: genesis:chat_input
       config:
         sender_name: {user_name}
       provides:
         - in: main-agent
           useAs: input
           
     - id: main-agent
       type: genesis:agent
       config:
         agent_llm: {llm_provider}
         model_name: {model_name}
         temperature: {temperature}
         system_prompt: |
           You are {agent_role}.
           {additional_instructions}
       provides:
         - in: chat-output
           useAs: input
           
     - id: chat-output
       type: genesis:chat_output
       config:
         sender_name: {agent_name}
   ```

2. **Create variables file** (`prod-vars.json`):
   ```json
   {
     "agent_name": "Production Assistant",
     "user_name": "User",
     "llm_provider": "Azure OpenAI",
     "model_name": "gpt-4",
     "temperature": 0.3,
     "agent_role": "a helpful production assistant",
     "additional_instructions": "Always be professional and concise."
   }
   ```

3. **Create the flow with tweaks**:
   ```bash
   genesis-agent create -t agent-template.yaml \
     --var-file prod-vars.json \
     --var agent_name="Custom Assistant" \
     --tweak main-agent.temperature=0.1 \
     --tweak main-agent.max_tokens=1500
   ```

### Undefined Variables

If a variable is referenced but not defined, it will be kept as a placeholder for Langflow to potentially resolve:
- Template: `{undefined_var}`
- Output: `{undefined_var}` (preserved)

The CLI will warn you about undefined variables during creation.

## Available Templates

### Healthcare Agents
- `medication-extractor` - Extract medications from clinical text
- `clinical-validator` - Validate clinical requests against guidelines
- `eligibility-checker` - Verify insurance eligibility
- `prior-auth-agent` - Process prior authorization requests
- `document-processor` - Extract text from healthcare documents
- `accumulator-check-agent` - Check deductibles and OOP maximums
- `benefit-check-agent` - Comprehensive benefit validation
- `eoc-check-agent` - Evidence of Coverage validation
- `pa-coordinator` - Coordinate PA processing with multiple agents

### Healthcare Orchestrators
- `benefit-check-flow` - Multi-agent benefit verification
- `prior-auth-workflow` - End-to-end PA processing

### Examples
- `simple-calculator-agent` - Basic math calculations
- `calculator-agent-enhanced` - Advanced calculator with memory

## Configuration

The CLI stores configuration in `.genesis-agent.yaml` in your current directory:

```yaml
genesis_studio:
  url: http://localhost:7860
  api_key: your-api-key

# Optional LLM integration for enhanced features
llm_integration:
  enabled: true
  provider: openai
  config:
    api_key: your-openai-key
```

Environment variables are also supported:
- `GENESIS_STUDIO_URL`
- `GENESIS_STUDIO_API_KEY`
- `OPENAI_API_KEY`

## Development

### Runtime Configuration Roadmap

The Genesis Agent CLI is designed to support runtime configuration through:

1. **Variables System**: Define configurable parameters in agent specs
2. **Tweaks Integration**: Override values at runtime via Langflow
3. **Environment Support**: Different configs for dev/staging/prod

Current implementation status:
- Template structure supports variables ✅
- Flow converter preserves variable references ✅
- Runtime substitution pending implementation ⏳
- Langflow tweaks integration pending ⏳

### Project Structure
```
genesis-agent-cli/
├── src/
│   ├── commands/          # CLI commands
│   ├── converters/        # Flow converters
│   ├── models/            # Agent specification models
│   ├── parsers/           # YAML parsers
│   ├── registry/          # Component registry
│   └── services/          # API services
├── templates/             # Agent templates
│   ├── healthcare/        # Healthcare-specific agents
│   └── examples/          # Example agents
└── tests/                 # Test suite
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_flow_converter.py
```

### Adding New Templates
1. Create YAML file in appropriate template directory
2. Use v2 enhanced format with full metadata
3. Check dependencies with `genesis-agent check-deps`
4. Test flow creation and execution

## Troubleshooting

### Common Issues

1. **Component not found**: Ensure Genesis Studio is running and accessible
2. **Authentication errors**: Check API key configuration
3. **Template validation errors**: Verify component types match Genesis Studio
4. **Edge connection issues**: Ensure proper handle types (use "other" for tools)

### Debug Mode
```bash
# Enable debug logging
export GENESIS_DEBUG=true
genesis-agent create -t template.yaml
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is proprietary to Autonomize AI.