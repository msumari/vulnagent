# VulnAgent

A Proof of concept Agentic vulnerability management system.

## Components

### 1. Agent (Bedrock AgentCore + Strands)

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

### 2. Curator (Lambda Function)

Processes AWS Inspector vulnerability findings via EventBridge.

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
├── curator/              # Lambda function for Inspector events
│   ├── template.yaml     # SAM template
│   ├── src/handler.py    # Lambda handler
│   └── test-event.json   # Sample Inspector event
└── requirements.txt      # Python dependencies
```
