# VulnAgent

A Proof of concept Agentic vulnerability management system.

## Components

### 1. Gateway (Bedrock AgentCore Gateway)

MCP-compatible gateway that exposes vulnerability management tools to AI agents.

**Setup:**

```bash
# Create gateway
python scripts/setup_gateway.py

# Add curator Lambda as target
python scripts/add_lambda_target.py <lambda-function-arn>
```

**Note:** Gateway configuration is saved to `gateway_config.json` (excluded from git for security).

### 2. Agent (Bedrock AgentCore + Strands)

AI agent using Claude 3 Haiku for vulnerability analysis, built with Strands framework for agentic workflows.

**Setup:**

```bash
# Set AWS profile
export AWS_PROFILE=************

# Run agent
python agent.py
```

**Test:**

```bash
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Explain how machine learning models work in simple terms"}'
```

### 3. Curator (Lambda Function)

Processes AWS Inspector vulnerability findings via EventBridge AND serves as MCP tools via Gateway.

**Deploy:**

```bash
cd curator
sam build
sam deploy --guided
```

**Test locally:**

```bash
cd curator
sam local invoke InspectorVulnFunction -e test-event.json
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+
- AWS SAM CLI
- Bedrock access

## Project Structure

```
├── agent.py              # Main agent application
├── scripts/              # Setup and deployment scripts
│   ├── setup_gateway.py  # Gateway setup script
│   └── add_lambda_target.py # Add Lambda as Gateway target
├── gateway_config.json   # Gateway configuration (generated, git-ignored)
├── curator/              # Lambda function for Inspector events
│   ├── template.yaml     # SAM template
│   ├── src/handler.py    # Lambda handler (supports EventBridge + Gateway)
│   └── test-event.json   # Sample Inspector event
└── requirements.txt      # Python dependencies
```
