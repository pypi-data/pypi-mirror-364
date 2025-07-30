# Runtime Variables and Tweaks Demo

This document demonstrates the runtime variables and tweaks functionality in Genesis Agent CLI.

## Example 1: Basic Variable Usage

### 1. Create an agent with variables

```yaml
# save as my-agent.yaml
id: "urn:agent:genesis:configurable_agent:1"
name: "Configurable Agent"
description: "Agent with runtime variables"

# Define variables
variables:
  - name: "llm_provider"
    type: "string"
    default: "OpenAI"
    description: "LLM provider"
  - name: "model_name"
    type: "string"
    default: "gpt-3.5-turbo"
    description: "Model to use"
  - name: "temperature"
    type: "float"
    default: 0.7
    description: "Generation temperature"
  - name: "max_tokens"
    type: "integer"
    default: 1000
    description: "Maximum tokens"

components:
  - id: "agent-main"
    type: "genesis:agent"
    config:
      agent_llm: "{llm_provider}"
      model_name: "{model_name}"
      temperature: "{temperature}"
      max_tokens: "{max_tokens}"
      system_prompt: "You are a helpful assistant using {model_name} model."
```

### 2. Create with different variable values

```bash
# Use defaults
genesis-agent create -t my-agent.yaml

# Override at creation time
genesis-agent create -t my-agent.yaml \
  --var model_name=gpt-4 \
  --var temperature=0.3

# Use environment variables
export LLM_PROVIDER=Azure
genesis-agent create -t my-agent.yaml \
  --var llm_provider='${LLM_PROVIDER}'
```

## Example 2: Variable Files

### 1. Create variable files for different environments

```json
// dev-vars.json
{
  "llm_provider": "OpenAI",
  "model_name": "gpt-3.5-turbo",
  "temperature": 0.9,
  "max_tokens": 500,
  "api_endpoint": "https://api-dev.example.com"
}
```

```yaml
# prod-vars.yaml
llm_provider: Azure
model_name: gpt-4
temperature: 0.3
max_tokens: 2000
api_endpoint: https://api.example.com
azure:
  deployment_name: prod-gpt4
  api_version: "2023-05-15"
```

### 2. Use variable files

```bash
# Development
genesis-agent create -t my-agent.yaml --var-file dev-vars.json

# Production
genesis-agent create -t my-agent.yaml --var-file prod-vars.yaml

# Override specific values
genesis-agent create -t my-agent.yaml \
  --var-file prod-vars.yaml \
  --var temperature=0.5
```

## Example 3: Runtime Tweaks

### 1. Run flow with tweaks

```bash
# Create flow
genesis-agent create -t my-agent.yaml
# Note the flow ID returned (e.g., flow-123)

# Run with tweaks
genesis-agent run flow-123 \
  --tweak agent-main.temperature=0.1 \
  --tweak agent-main.model_name=gpt-4 \
  --input '{"question": "What is 2+2?"}'

# Combine variables and tweaks
genesis-agent run flow-123 \
  --var api_key='${MY_API_KEY}' \
  --tweak agent-main.max_tokens=500 \
  --tweak agent-main.temperature=0.5
```

## Example 4: Complex Healthcare Agent

### 1. Healthcare agent with configurable components

```yaml
# healthcare-agent.yaml
id: "urn:agent:genesis:clinical_validator:1"
name: "Clinical Validator"

variables:
  - name: "llm_config"
    type: "object"
    default:
      provider: "OpenAI"
      model: "gpt-4"
      temperature: 0.1
  - name: "rxnorm_threshold"
    type: "float"
    default: 0.85
  - name: "knowledge_hub"
    type: "string"
    default: "clinical-guidelines-v2"
  - name: "validation_mode"
    type: "string"
    default: "strict"

components:
  - id: "validator"
    type: "genesis:agent"
    config:
      agent_llm: "{llm_config.provider}"
      model_name: "{llm_config.model}"
      temperature: "{llm_config.temperature}"
      system_prompt: |
        You are a clinical validator in {validation_mode} mode.
        Use RxNorm threshold of {rxnorm_threshold}.
  
  - id: "rxnorm-tool"
    type: "genesis:rxnorm"
    config:
      confidence_threshold: "{rxnorm_threshold}"
  
  - id: "knowledge-search"
    type: "genesis:knowledge_hub_search"
    config:
      hub_name: "{knowledge_hub}"
```

### 2. Environment-specific configurations

```yaml
# environments/staging.yaml
llm_config:
  provider: "Azure"
  model: "gpt-35-turbo"
  temperature: 0.2
rxnorm_threshold: 0.9
knowledge_hub: "clinical-guidelines-staging"
validation_mode: "moderate"

# environments/production.yaml
llm_config:
  provider: "Azure"
  model: "gpt-4"
  temperature: 0.1
rxnorm_threshold: 0.95
knowledge_hub: "clinical-guidelines-prod"
validation_mode: "strict"
```

### 3. Deploy to different environments

```bash
# Staging deployment
genesis-agent create -t healthcare-agent.yaml \
  --var-file environments/staging.yaml \
  --var llm_config.api_key='${AZURE_STAGING_KEY}'

# Production deployment
genesis-agent create -t healthcare-agent.yaml \
  --var-file environments/production.yaml \
  --var llm_config.api_key='${AZURE_PROD_KEY}'

# Ad-hoc testing with relaxed settings
genesis-agent create -t healthcare-agent.yaml \
  --var validation_mode=relaxed \
  --var rxnorm_threshold=0.7 \
  --var llm_config.temperature=0.5
```

## Example 5: Dynamic Multi-Agent Orchestration

### 1. Orchestrator with configurable agents

```yaml
# orchestrator.yaml
id: "urn:agent:genesis:pa_orchestrator:1"
name: "PA Orchestrator"

variables:
  - name: "agents"
    type: "object"
    default:
      classifier: "urn:agent:genesis:classification_agent:1"
      extractor: "urn:agent:genesis:extraction_agent:1"
      validator: "urn:agent:genesis:clinical_validator:1"
  - name: "parallel_execution"
    type: "boolean"
    default: true
  - name: "timeout_seconds"
    type: "integer"
    default: 300

components:
  - id: "orchestrator"
    type: "genesis:agent"
    config:
      system_prompt: |
        Orchestrate PA processing using:
        - Classifier: {agents.classifier}
        - Extractor: {agents.extractor}
        - Validator: {agents.validator}
        
        Execution mode: {"parallel" if {parallel_execution} else "sequential"}
        Timeout: {timeout_seconds} seconds
  
  - id: "classifier-agent"
    type: "$ref:{agents.classifier}"
    asTools: true
  
  - id: "extractor-agent"
    type: "$ref:{agents.extractor}"
    asTools: true
  
  - id: "validator-agent"
    type: "$ref:{agents.validator}"
    asTools: true
```

### 2. Switch between agent versions

```bash
# Use v1 agents
genesis-agent create -t orchestrator.yaml

# Use v2 agents
genesis-agent create -t orchestrator.yaml \
  --var agents.classifier=urn:agent:genesis:classification_agent:2 \
  --var agents.extractor=urn:agent:genesis:extraction_agent:2 \
  --var agents.validator=urn:agent:genesis:clinical_validator:2

# Use custom timeout and sequential execution for debugging
genesis-agent create -t orchestrator.yaml \
  --var parallel_execution=false \
  --var timeout_seconds=600
```

## Best Practices

1. **Use variable files for environments**: Keep environment-specific configs in separate files
2. **Leverage environment variables for secrets**: Use `${ENV_VAR}` syntax for API keys
3. **Document variables**: Always provide descriptions for variables
4. **Set sensible defaults**: Ensure agents work with default values
5. **Use type hints**: Specify variable types for validation
6. **Test with tweaks**: Use runtime tweaks for quick testing without recreating flows

## Troubleshooting

### Common Issues

1. **Undefined variable warning**
   ```bash
   ⚠️  Warning: Undefined variables: api_key, endpoint
   ```
   Solution: Provide all required variables or check for typos

2. **Type mismatch**
   ```bash
   Error: Variable 'temperature' expects float, got string
   ```
   Solution: Ensure numeric values aren't quoted unnecessarily

3. **Nested variable not found**
   ```bash
   Error: Cannot resolve {config.missing.key}
   ```
   Solution: Check variable structure matches usage

### Debug Mode

Enable debug output to see variable resolution:

```bash
export GENESIS_DEBUG=true
genesis-agent create -t my-agent.yaml --var model=gpt-4
```

This will show:
- Variables loaded from files
- Environment variables resolved  
- Final resolved values
- Any undefined variables