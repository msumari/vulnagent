# VulnAgent

A Proof of Concept Agentic Vulnerability Management System built with AWS Bedrock AgentCore, featuring MCP Gateway integration and real-time vulnerability analysis tools.

## 🎯 Overview

VulnAgent demonstrates advanced agentic AI capabilities for vulnerability management, combining:

- **AI-Powered Analysis**: Claude 3 Haiku for intelligent vulnerability assessment
- **MCP Integration**: Model Context Protocol for tool access via Bedrock AgentCore Gateway
- **AWS Native**: Full integration with AWS Inspector, Lambda, and AgentCore Runtime
- **Human-in-the-Loop**: Interactive approval/decline workflow for remediation plans
- **Multi-Agent Swarm**: Specialized agents for gathering, remediation, criticism, and knowledge keeping
- **Context-Aware AI**: Intelligent responses based on human decisions

## 🏗️ Architecture

```
Inspector ← Lambda (Curator) → MCP Gateway → VulnAgent → Analysis & Human Approval → Remediation
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

AI agent using Claude 3 Haiku for vulnerability analysis, built with Strands framework using swarm architecture.

**Features:**

- ✅ MCP Gateway integration with OAuth
- ✅ Gather → Swarm multi-agent collaboration
- ✅ Autonomous agent handoffs with `handoff_to_agent`
- ✅ Shared context between specialized agents
- ✅ Vulnerability analysis with CVSS scoring
- ✅ Risk-based prioritization
- ✅ Actionable security recommendations
- ✅ Human-in-the-loop approval workflow
- ✅ Context-aware human decision handling

**Architecture:**

```
VulnGatherer (Entry Point) → Swarm[VulnRemediator, VulnCritic, VulnKeeper] → Human Approval/Decline → Final Response
```

**Human Interaction Flow:**

- **Approve**: Proceeds with comprehensive remediation plan
- **Decline**: Provides context-aware vulnerability analysis without remediation steps

**Setup:**

```bash
# Set AWS credentials
export AWS_PROFILE=your-profile

# Run agent locally
python agent.py

# Test single agent mode
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Analyze CVE-2024-12345 - SQL Injection vulnerability, severity HIGH"}'

# Test swarm mode
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Create comprehensive remediation plan", "swarm_mode": true}'
```

### 3. **Web UI**

Interactive web interface for vulnerability analysis and human decision making.

**Features:**

- ✅ Real-time vulnerability analysis
- ✅ Human approval/decline workflow with radio buttons
- ✅ Clean results display with proper text extraction
- ✅ Elegant UI design

**Setup:**

```bash
# Start the agent backend
python agent.py

# Start the web interface
cd ui
npm install
npm run dev

# Then visit http://localhost:3000
```

**Usage:**

1. Enter vulnerability prompt or use default
2. Enable/disable swarm mode
3. Click "Analyze Vulnerabilities"
4. Review the remediation plan
5. Choose "Approve" or "Decline"
6. View final results

### 4. **Curator (Lambda Function)**

Fetches AWS Inspector vulnerability findings directly and serves as MCP tools via Gateway.

**Features:**

- ✅ Direct Inspector2 integration via boto3
- ✅ MCP tool endpoints for vulnerability analysis

**Tools Available:**

- `analyze_vulnerability_finding`: Fetch and analyze Inspector2 findings

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
# Start backend
python agent.py &

# Start frontend
cd ui
npm install
npm run dev

# Visit http://localhost:3000 for Web UI
# Or test via curl
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Analyze vulnerability findings"}'
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
├── agent.py                    # Main agent with MCP Gateway integration & human workflow
├── ui/                        # Web interface for human interaction
│   ├── index.html             # Main UI with approval/decline workflow
│   ├── main.js                # JavaScript for API calls and UI logic
│   ├── style.css              # Styling with elegant button design
│   └── package.json           # Node.js dependencies and scripts
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

### ✅ **Professional Vulnerability Analysis**

- Risk-based severity assessment
- Business impact evaluation
- Prioritized recommendations
- Actionable next steps

### ✅ **AWS Native Architecture**

- Inspector → Lambda integration
- AgentCore Runtime deployment
- ECR container registry integration
- IAM role-based security

## 🧪 Testing

### Local Testing

```bash
# Test single agent mode
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Analyze vulnerability findings"}'

# Test swarm mode
curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "Analyze vulnerability findings and create remediation plan", "swarm_mode": true}'
```

### Runtime Testing

```bash
# Test single agent mode
agentcore invoke '{"prompt": "Analyze vulnerability findings"}'

# Test swarm mode
agentcore invoke '{"prompt": "Analyze vulnerability findings and create remediation plan", "swarm_mode": true}'
```

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
- Human workflow supports both approval and decline paths with appropriate responses
- UI provides clean, elegant interface for decision making
- Multi-agent swarm architecture enables specialized vulnerability management roles

## Known Issues

### Workflow Mode Model Access Error

**Issue**: When using `workflow_mode=true`, the system encountered:

```
Error executing task gather_vulnerabilities: An error occurred (AccessDeniedException) when calling the ConverseStream operation: You don't have access to the model with the specified model ID.
```

**Root Cause**: The workflow tool attempts to create multiple agent instances simultaneously, which may exceed model quota limits or encounter permission issues when multiple agents try to access `anthropic.claude-3-haiku-20240307-v1:0` concurrently.

**Solution**: Replaced workflow approach with **SWARM** architecture using Strands multi-agent swarm.

### Current Gather → Swarm Implementation

**Status**: WORKING - Multi-agent collaboration functional

**Architecture**:

```
VulnGatherer (Entry Point) → Swarm[VulnRemediator, VulnCritic, VulnKeeper] → Human Approval
```

**Achievements**:

- Autonomous agent collaboration with `handoff_to_agent` tool
- Shared context and knowledge between specialized agents
- Vulnerability analysis with CVSS scoring
- Comprehensive remediation plans with security best practices
- No model access conflicts (each agent has own model instance)

**Current Issues**:

- Gateway memory integration.
- `execute_remediation_code` tool causes reference errors in swarm context
- Occasional gateway connection timeouts during OAuth token retrieval

**Status**: Under active development - core functionality working with minor reliability issues.

---

**VulnAgent** - A Proof of Concept demonstrating agentic vulnerability management with AWS Bedrock AgentCore.
