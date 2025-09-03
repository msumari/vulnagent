# VulnAgent

A Proof of Concept Agentic Vulnerability Management System built with AWS Bedrock AgentCore, featuring MCP Gateway integration and real-time vulnerability analysis tools.

## 🎯 Overview

VulnAgent demonstrates advanced agentic AI capabilities for vulnerability management, combining:

- **AI-Powered Analysis**: Claude 3 Haiku for intelligent vulnerability assessment
- **MCP Integration**: Model Context Protocol for tool access via Bedrock AgentCore Gateway
- **AWS Native**: Full integration with AWS Inspector, Lambda, and AgentCore Runtime

## 🏗️ Architecture

```
AWS Inspector → EventBridge → Lambda (Curator) → MCP Gateway → VulnAgent → Analysis & Recommendations
```

## 🚀 Components

### 1. **Gateway (Bedrock AgentCore Gateway)**

MCP-compatible gateway with OAuth authentication that exposes vulnerability management tools.

**Features:**

- ✅ OAuth 2.0 with Cognito authentication
- ✅ Semantic search enabled
- ✅ Lambda target integration

**Setup:**

```bash
# Create gateway with OAuth
python scripts/setup_gateway.py

# Add curator Lambda as target
python scripts/add_lambda_target.py <lambda-function-arn>
```

**Configuration:** Auto-generated in `gateway_config.json`

### 2. **Agent (Bedrock AgentCore + Strands)**

AI agent using Claude 3 Haiku for vulnerability analysis, built with Strands framework.

**Features:**

- ✅ MCP Gateway integration with OAuth
- ✅ Professional vulnerability analysis
- ✅ Risk-based prioritization
- ✅ Actionable security recommendations

**Setup:**

```bash
# Set AWS credentials
export AWS_PROFILE=your-profile

# Run agent locally
python agent.py

# Test agent
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Analyze CVE-2024-12345 - SQL Injection vulnerability, severity HIGH"}'
```

### 3. **Curator (Lambda Function)**

Processes AWS Inspector vulnerability findings and serves as MCP tools via Gateway.

**Features:**

- ✅ EventBridge integration for Inspector events
- ✅ MCP tool endpoints for vulnerability analysis

**Tools Available:**

- `analyze_vulnerability_finding`: Analyze specific vulnerabilities
- `process_inspector_event`: Process Inspector EventBridge events

**Deploy:**

```bash
cd curator
sam build
sam deploy --guided
```

## 🔧 Setup Instructions

### Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+
- AWS SAM CLI
- Bedrock access
- Docker (for runtime deployment)

### Quick Start

1. **Deploy Curator Lambda:**

```bash
cd curator
sam build && sam deploy --guided
```

2. **Setup Gateway with OAuth:**

```bash
python scripts/setup_gateway.py
# ✅ Auto-generates gateway_config.json with OAuth credentials
```

3. **Add Lambda Target:**

```bash
python scripts/add_lambda_target.py <your-lambda-arn>
```

4. **Test Locally:**

```bash
python agent.py &
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Test Gateway connection and analyze vulnerabilities"}'
```

5. **Deploy to Runtime:**

```bash
# Build and push container
docker build -t vulnagent:latest .
docker tag vulnagent:latest <your-account-id>.dkr.ecr.<region>.amazonaws.com/bedrock-agentcore-agent:latest
docker push <your-account-id>.dkr.ecr.<region>.amazonaws.com/bedrock-agentcore-agent:latest
```

For complete runtime deployment instructions, see: https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

## 📁 Project Structure

```
├── agent.py                    # Main agent with MCP Gateway integration
├── scripts/                   # Setup and deployment scripts
│   ├── setup_gateway.py       # Gateway setup with OAuth
│   └── add_lambda_target.py   # Add Lambda as Gateway target
├── gateway_config.json        # Auto-generated Gateway config with OAuth
├── curator/                   # Lambda function for Inspector events
│   ├── template.yaml          # SAM template
│   ├── src/handler.py         # Dual-mode Lambda handler
│   └── test-event.json        # Sample Inspector event
├── Dockerfile                 # Container for AgentCore Runtime
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🎯 Key Features Demonstrated

### ✅ **Complete MCP Integration**

- OAuth 2.0 authentication with Cognito
- Real-time tool access via Gateway
- Proper error handling and fallback modes

### ✅ **Professional Vulnerability Analysis**

- Risk-based severity assessment
- Business impact evaluation
- Prioritized recommendations
- Actionable next steps

### ✅ **AWS Native Architecture**

- Inspector → EventBridge → Lambda pipeline
- AgentCore Runtime deployment
- ECR container registry integration
- IAM role-based security

## 🧪 Testing

### Local Testing

```bash
# Start agent
python agent.py

# Test vulnerability analysis
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Analyze CVE-2024-9999 - Remote Code Execution, severity CRITICAL"}'
```

### Runtime Testing

For runtime deployment and testing, follow the complete guide at:
https://strandsagents.com/latest/documentation/docs/user-guide/deploy/deploy_to_bedrock_agentcore/

## 📊 Sample Output

```json
{
  "result": {
    "role": "assistant",
    "content": [
      {
        "text": "Risk Assessment:\n- This is a Medium severity vulnerability involving outdated package version\n- Component: 'hudson' version 1.476 → upgrade to 2.263\n\nRecommendations:\n1. Upgrade package immediately\n2. Review other dependencies\n3. Implement automated update process\n4. Monitor for new findings\n\nNext Steps:\n- Plan upgrade with dev/ops teams\n- Verify successful upgrade\n- Expand review to other components"
      }
    ]
  }
}
```

## 📝 Notes

- Gateway configuration auto-generates with proper OAuth credentials
- Setup scripts handle domain extraction and client secret capture

---

**VulnAgent** - A Proof of Concept demonstrating agentic vulnerability management with AWS Bedrock AgentCore.
