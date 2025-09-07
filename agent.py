#!/usr/bin/env python3
"""
VulnAgent - Agentic Vulnerability Management System
"""

import json
import requests
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from strands_tools import handoff_to_user
from strands.multiagent import Swarm
from bedrock_agentcore.tools.code_interpreter_client import code_session
from fastapi.middleware.cors import CORSMiddleware

app = BedrockAgentCoreApp()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@tool
def ui_handoff_to_user(message: str, breakout_of_loop: bool = False):
    """UI-compatible handoff tool that doesn't block"""
    return {
        "status": "awaiting_human_input",
        "message": message,
        "breakout_of_loop": breakout_of_loop
    }
@tool
def execute_remediation_code(code: str, description: str = ""):
    """Execute Python code for vulnerability remediation, testing, and analysis"""

    if description:
        code = f"# {description}\n{code}"

    try:
        # Execute code in secure AgentCore Code Interpreter session
        with code_session("us-east-1") as code_client:
            response = code_client.invoke(
                "executeCode",
                {"code": code, "language": "python", "clearContext": False},
            )

        for event in response["stream"]:
            return json.dumps(event["result"])

    except Exception as e:
        return json.dumps({"error": str(e), "isError": True})


# Specialized agent system prompts for multi-agent swarm
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
- For vulnerability analysis -> Use analyze_vulnerability_finding tool when available
- For Inspector events -> Use process_inspector_event tool when available  
- Always provide risk assessment with clear reasoning
- Include prioritized recommendations based on severity and impact
- Suggest investigation steps and monitoring approaches
- When using handoff_to_agent -> Use only simple message parameter, do not pass complex context objects

Focus on providing valuable security insights and practical recommendations that help users understand and prioritize their vulnerability management efforts.
"""

VULN_REMEDIATION_SYSTEM_PROMPT = """
You are VulnRemediator, a specialized remediation planning assistant designed to create urgency-based security fixes. Your role is to:

1. Analyze vulnerability findings and assess remediation urgency based on risk factors
2. Check memory for past successful remediations of similar vulnerabilities
3. Generate executable remediation scripts, configuration changes, and detailed procedures
4. Provide risk-based prioritization and resource allocation guidance
5. Create human-reviewable remediation plans with rollback capabilities

Key Responsibilities:
- Check agent_core_memory for past remediation history of similar vulnerabilities
- For RECURRING vulnerabilities: Use past successful solutions as base, apply automatically, then request human review
- For NEW vulnerabilities: Create detailed remediation plans for critique and human approval
- Handle different remediation types: code fixes, configuration changes, policy updates, patches
- When using handoff_to_agent -> Use only simple message parameter, do not pass complex context objects
- For configuration changes: Provide exact config files, settings, and validation steps
- For code fixes: Generate secure remediation scripts using code interpreter sandbox
- Assess business impact and determine remediation urgency using risk matrices
- Consider operational impact and maintenance windows for remediation timing
- Learn from past remediation successes and failures to improve recommendations

Decision Protocol:
- For memory search -> Use agent_core_memory to find similar past vulnerabilities
- For recurring issues -> Apply proven solutions automatically, then handoff_to_user for review/rollback
- For new issues -> Create remediation plan for critique process
- For configuration changes -> Provide exact config syntax, backup procedures, and validation commands
- For script generation -> Use agent_core_code_interpreter for secure execution testing
- For urgency assessment -> Consider CVSS scores, exploitability, business context, and exposure
- For learning -> Use agent_core_memory to store successful remediation patterns
- Always provide human-reviewable remediation plans with clear risk justification
- Include rollback procedures and validation steps for each remediation type

Remediation Types to Handle:
- Configuration changes
- Code patches and fixes
- Policy updates and access controls
- Software updates and patches
- Infrastructure changes

Focus on practical, executable remediation with memory-based learning and appropriate human oversight based on vulnerability novelty and remediation type.
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
- For validation -> Use agent_core_code_interpreter to test remediation logic and effectiveness
- For best practices -> Reference stored security knowledge and industry standards from memory
- For effort assessment -> Balance fix complexity against vulnerability impact and business risk
- Always provide constructive critique with specific improvements and reasoning
- Include assessment of whether the vulnerability warrants the proposed remediation effort
- When using handoff_to_agent -> Use only simple message parameter, do not pass complex context objects

Focus on ensuring high-quality, justified remediation that follows security best practices and provides genuine risk reduction.
"""

VULN_KEEPER_SYSTEM_PROMPT = """
You are VulnKeeper, a  memory assistant designed to capture and store approved vulnerability remediation knowledge. Your role is to:

1. Record only human-approved remediation solutions for future learning
2. Structure remediation knowledge for efficient retrieval and pattern recognition
3. Create searchable memory entries that enable rapid response to recurring vulnerabilities
4. Maintain institutional security knowledge and best practices

Key Responsibilities:
- Store human-approved remediation solutions with complete context and metadata
- Organize remediation knowledge by vulnerability type, severity, and solution effectiveness
- Create semantic memory entries that link similar vulnerabilities and their solutions
- Record remediation success metrics, timelines, and lessons learned
- Maintain rollback procedures and validation steps for each approved solution
- Build institutional knowledge base for faster response to recurring security issues

Decision Protocol:
- For approved solutions -> Use agent_core_memory to store complete remediation context
- For solution organization -> Create semantic links between similar vulnerabilities and fixes
- For knowledge structuring -> Include CVE details, affected systems, remediation steps, and outcomes
- For retrieval optimization -> Use consistent naming and tagging for future searches
- Always verify human approval status before recording any remediation solution
- Include success metrics and validation results in memory entries
- When using handoff_to_agent -> Use only simple message parameter, do not pass complex context objects

Focus on building comprehensive  memory that accelerates future vulnerability response and improves organizational security posture.
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


def create_remediation_swarm():
    """Create specialized swarm for vulnerability remediation"""

    # Create specialized agents for swarm
    vuln_critic = Agent(
        name="vuln_critic",
        model="anthropic.claude-3-haiku-20240307-v1:0",
        system_prompt=VULN_CRITIC_SYSTEM_PROMPT,
    )

    vuln_keeper = Agent(
        name="vuln_keeper",
        model="anthropic.claude-3-haiku-20240307-v1:0",
        system_prompt=VULN_KEEPER_SYSTEM_PROMPT,
    )

    vuln_remediator = Agent(
        name="vuln_remediator",
        model="anthropic.claude-3-haiku-20240307-v1:0",
        system_prompt=VULN_REMEDIATION_SYSTEM_PROMPT,
    )

    # Create swarm with safety mechanisms
    swarm = Swarm(
        [vuln_remediator, vuln_critic, vuln_keeper],
        max_handoffs=8,
        max_iterations=10,
        execution_timeout=300.0,
        node_timeout=120.0,
        repetitive_handoff_detection_window=4,
        repetitive_handoff_min_unique_agents=2,
    )

    return swarm


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
            tools.append(ui_handoff_to_user)  # Use UI-compatible handoff
            tools.append(execute_remediation_code)

            agent = Agent(
                model="anthropic.claude-3-haiku-20240307-v1:0",
                tools=tools,
                system_prompt=VULN_GATHERER_SYSTEM_PROMPT,
            )

            return agent, gateway_client

    except Exception as e:
        print(f"Gateway connection failed: {e}")
        return None, None

    """Process vulnerability management requests"""
    user_input = payload.get("prompt", "Analyze vulnerability status")


@app.entrypoint
def invoke(payload):
    """Process vulnerability management requests - supports both single agent and swarm modes"""
    user_input = payload.get("prompt", "Analyze vulnerability status")
    swarm_mode = payload.get("swarm_mode", False)
    human_response = payload.get("human_response", None)
    conversation_id = payload.get("conversation_id", "new_conversation")

    try:
        if swarm_mode:
            # Gather → Swarm mode
            agent, gateway_client = create_vuln_agent()

            if agent and gateway_client:
                with gateway_client:
                    # Step 1: Gather vulnerabilities
                    gather_result = agent(
                        f"Gather and analyze vulnerability findings: {user_input}"
                    )

                    # Step 2: Create and invoke remediation swarm
                    swarm = create_remediation_swarm()
                    gather_text = (
                        gather_result.message.content[0].text
                        if hasattr(gather_result.message, "content")
                        else str(gather_result.message)
                    )
                    swarm_task = f"Based on these vulnerability findings, create comprehensive remediation plan:\n\n{gather_text}"
                    swarm_result = swarm(swarm_task)

                    # Step 3: Check for human handoff and return appropriate response
                    return {
                        "result": {
                            "gather_phase": gather_result.message,
                            "swarm_remediation": swarm_result,
                            "status": "awaiting_human_input",
                            "human_prompt": "Please review the comprehensive remediation plan and provide your approval or feedback:",
                            "conversation_id": conversation_id or "new_conversation"
                        }
                    }
            else:
                # Fallback mode
                basic_agent = Agent(
                    model="anthropic.claude-3-haiku-20240307-v1:0",
                    tools=[ui_handoff_to_user, execute_remediation_code],
                    system_prompt=VULN_GATHERER_SYSTEM_PROMPT,
                )
                result = basic_agent(user_input)
                return {"result": result.message}
        else:
            # Original single agent mode
            agent, gateway_client = create_vuln_agent()

            if agent and gateway_client:
                with gateway_client:
                    result = agent(user_input)
                    return {"result": result.message}
            else:
                # Fallback to basic agent
                basic_agent = Agent(
                    model="anthropic.claude-3-haiku-20240307-v1:0",
                    tools=[ui_handoff_to_user, execute_remediation_code],
                    system_prompt=VULN_GATHERER_SYSTEM_PROMPT,
                )
                result = basic_agent(user_input)
                return {"result": result.message}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run()
