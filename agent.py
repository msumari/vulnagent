#!/usr/bin/env python3
"""
VulnAgent - Agentic Vulnerability Management System
"""

import json
import requests
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from strands_tools import workflow

app = BedrockAgentCoreApp()

# Specialized agent system prompts for multi-agent workflow
VULN_GATHERER_SYSTEM_PROMPT = """
You are VulnAgent, a specialized vulnerability analysis assistant designed to provide security insights and recommendations. Your role is to:

1. Analyze AWS Inspector vulnerability findings and security assessments
2. Provide risk-based analysis and prioritization guidance  
3. Generate actionable security recommendations and best practices
4. Use available vulnerability analysis tools to gather detailed information

Key Responsibilities:
- Process vulnerability findings from AWS Inspector and other security tools
- Assess risk levels based on severity, exploitability, and potential business impact
- Provide specific recommendations and suggested next steps
- Maintain clear, actionable communication about security findings
- Focus on practical guidance rather than immediate remediation requirements

Decision Protocol:
- For vulnerability analysis → Use analyze_vulnerability_finding tool when available
- For Inspector events → Use process_inspector_event tool when available  
- Always provide risk assessment with clear reasoning
- Include prioritized recommendations based on severity and impact
- Suggest investigation steps and monitoring approaches

Focus on providing valuable security insights and practical recommendations that help users understand and prioritize their vulnerability management efforts.
"""

VULN_REMEDIATION_SYSTEM_PROMPT = """
You are VulnRemediator, a specialized remediation planning assistant designed to create urgency-based security fixes. Your role is to:

1. Analyze vulnerability findings and assess remediation urgency based on risk factors
2. Generate executable remediation scripts and detailed procedures
3. Provide risk-based prioritization and resource allocation guidance
4. Create human-reviewable remediation plans with rollback capabilities

Key Responsibilities:
- Create detailed remediation plans with executable code and procedures
- Assess business impact and determine remediation urgency using risk matrices
- Generate secure remediation scripts using code interpreter sandbox
- Consider operational impact and maintenance windows for remediation timing
- Learn from past remediation successes and failures to improve recommendations

Decision Protocol:
- For script generation → Use agent_core_code_interpreter for secure execution testing
- For urgency assessment → Consider CVSS scores, exploitability, business context, and exposure
- For learning → Use agent_core_memory to improve future remediation strategies
- Always provide human-reviewable remediation plans with clear risk justification
- Include rollback procedures and validation steps for each remediation

Focus on practical, executable remediation with clear risk-based prioritization and human oversight integration.
"""

VULN_CRITIC_SYSTEM_PROMPT = """
You are VulnCritic, a specialized remediation validation assistant designed to evaluate security fix quality and worthiness. Your role is to:

1. Review remediation plans for completeness, security best practices, and effectiveness
2. Assess whether vulnerability remediation effort is justified by the actual risk
3. Validate that proposed fixes address root causes rather than just symptoms
4. Provide constructive improvement recommendations for remediation quality

Key Responsibilities:
- Evaluate remediation plans against established security best practices and frameworks
- Determine if remediation effort and complexity match the actual vulnerability risk
- Identify potential gaps, unintended consequences, or incomplete fixes
- Validate that remediation addresses the vulnerability's root cause effectively
- Provide specific, actionable improvement recommendations

Decision Protocol:
- For validation → Use agent_core_code_interpreter to test remediation logic and effectiveness
- For best practices → Reference stored security knowledge and industry standards from memory
- For effort assessment → Balance fix complexity against vulnerability impact and business risk
- Always provide constructive critique with specific improvements and reasoning
- Include assessment of whether the vulnerability warrants the proposed remediation effort

Focus on ensuring high-quality, justified remediation that follows security best practices and provides genuine risk reduction.
"""


def get_access_token():
    """Get OAuth access token for Gateway authentication"""
    try:
        with open("gateway_config.json", "r") as f:
            config = json.load(f)

        client_id = config["client_id"]
        client_secret = config["client_secret"]
        domain = config["domain"]

        # OAuth client credentials flow
        token_url = f"https://{domain}/oauth2/token"

        response = requests.post(
            token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "vulnagent-gateway/invoke",
            },
        )

        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"OAuth failed: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"Authentication error: {e}")
        return None


def create_vuln_agent():
    """Create vulnerability agent with MCP Gateway tools"""
    try:
        with open("gateway_config.json", "r") as f:
            config = json.load(f)

        mcp_url = config["mcp_url"]
        access_token = get_access_token()

        if not access_token:
            print("Failed to get access token, falling back to basic mode")
            return None, None

        # Create MCP client for Gateway with OAuth
        gateway_client = MCPClient(
            lambda: streamablehttp_client(
                mcp_url, headers={"Authorization": f"Bearer {access_token}"}
            )
        )

        with gateway_client:
            tools = gateway_client.list_tools_sync()
            # Add workflow tool to existing tools
            tools.append(workflow)

            agent = Agent(
                model="anthropic.claude-3-haiku-20240307-v1:0",
                tools=tools,
                system_prompt=VULN_GATHERER_SYSTEM_PROMPT,
            )

            return agent, gateway_client

    except Exception as e:
        print(f"Gateway connection failed: {e}")
        return None, None


def create_vulnagent_multiagent_workflow():
    """Create VulnAgent multi-agent workflow using existing infrastructure"""
    try:
        agent, gateway_client = create_vuln_agent()
        
        if agent and gateway_client:
            with gateway_client:
                # Create vulnerability management workflow
                workflow_result = agent.tool.workflow(
                    action="create",
                    workflow_id="vulnerability_management",
                    tasks=[
                        {
                            "task_id": "gather_vulnerabilities",
                            "description": "Gather and analyze vulnerability findings",
                            "system_prompt": VULN_GATHERER_SYSTEM_PROMPT,
                            "dependencies": [],
                            "priority": 5
                        },
                        {
                            "task_id": "plan_remediation", 
                            "description": "Create urgency-based remediation plans",
                            "system_prompt": VULN_REMEDIATION_SYSTEM_PROMPT,
                            "dependencies": ["gather_vulnerabilities"],
                            "priority": 4
                        },
                        {
                            "task_id": "critique_remediation",
                            "description": "Validate remediation quality and worthiness",
                            "system_prompt": VULN_CRITIC_SYSTEM_PROMPT,
                            "dependencies": ["plan_remediation"],
                            "priority": 3
                        }
                    ]
                )
                return agent, gateway_client, workflow_result
        else:
            # Fallback mode with workflow capability
            workflow_result = agent.tool.workflow(
                action="create",
                workflow_id="vulnerability_management",
                tasks=[
                    {
                        "task_id": "gather_vulnerabilities",
                        "description": "Gather and analyze vulnerability findings",
                        "system_prompt": VULN_GATHERER_SYSTEM_PROMPT,
                        "dependencies": [],
                        "priority": 5
                    },
                    {
                        "task_id": "plan_remediation", 
                        "description": "Create urgency-based remediation plans",
                        "system_prompt": VULN_REMEDIATION_SYSTEM_PROMPT,
                        "dependencies": ["gather_vulnerabilities"],
                        "priority": 4
                    },
                    {
                        "task_id": "critique_remediation",
                        "description": "Validate remediation quality and worthiness",
                        "system_prompt": VULN_CRITIC_SYSTEM_PROMPT,
                        "dependencies": ["plan_remediation"],
                        "priority": 3
                    }
                ]
            )
            return agent, None, workflow_result
            
    except Exception as e:
        return None, None, {"error": str(e)}
    """Process vulnerability management requests"""
    user_input = payload.get("prompt", "Analyze vulnerability status")

@app.entrypoint
def invoke(payload):
    """Process vulnerability management requests - supports both single agent and workflow modes"""
    user_input = payload.get("prompt", "Analyze vulnerability status")
    workflow_mode = payload.get("workflow_mode", False)
    
    try:
        if workflow_mode:
            # Multi-agent workflow mode
            agent, gateway_client, workflow_result = create_vulnagent_multiagent_workflow()
            
            if agent:
                if gateway_client:
                    with gateway_client:
                        # Start workflow execution
                        start_result = agent.tool.workflow(
                            action="start", 
                            workflow_id="vulnerability_management"
                        )
                        return {"result": start_result, "workflow_created": workflow_result}
                else:
                    # Fallback workflow execution
                    start_result = agent.tool.workflow(
                        action="start", 
                        workflow_id="vulnerability_management"
                    )
                    return {"result": start_result, "workflow_created": workflow_result}
            else:
                return {"error": "Failed to create workflow"}
        else:
            # Original single agent mode
            agent, gateway_client = create_vuln_agent()

            if agent and gateway_client:
                with gateway_client:
                    result = agent(user_input)
                    return {"result": result.message}
            else:
                # Fallback to basic agent with workflow capability
                basic_agent = Agent(
                    model="anthropic.claude-3-haiku-20240307-v1:0",
                    tools=[workflow],
                    system_prompt=VULN_GATHERER_SYSTEM_PROMPT,
                )
                result = basic_agent(user_input)
                return {"result": result.message}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run()
