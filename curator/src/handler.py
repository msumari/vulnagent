import json


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    # Only handle Gateway tool calls
    tool_name = getattr(context, "bedrockagentcoreToolName", None)
    
    if tool_name:
        return handle_gateway_tool_call(event, tool_name)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Only Gateway tool calls supported"}),
        }


def handle_gateway_tool_call(event, tool_name):
    """Handle tool calls from AgentCore Gateway"""
    print(f"Gateway tool call: {tool_name}")

    if tool_name == "analyze_vulnerability_finding":
        return analyze_vulnerability_finding(event)
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": f"Unknown tool: {tool_name}"}),
        }


def analyze_vulnerability_finding(params):
    """Analyze a specific vulnerability finding"""
    # TODO: Implement vulnerability finding analysis logic

    analysis = {
        "findingArn": finding_arn,
        "severity": severity,
        "title": title,
        "riskLevel": get_risk_level(severity),
        "recommendations": get_recommendations(severity, title),
    }

    return {"statusCode": 200, "body": json.dumps(analysis)}








def get_risk_level(severity):
    """Determine risk level based on severity"""
    severity_map = {
        "CRITICAL": "VERY_HIGH",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
        "INFORMATIONAL": "VERY_LOW",
    }
    return severity_map.get(severity.upper(), "UNKNOWN")


def get_recommendations(severity, title):
    """Generate recommendations based on vulnerability"""
    recommendations = []

    if "CRITICAL" in severity.upper() or "HIGH" in severity.upper():
        recommendations.append("Immediate patching required")
        recommendations.append("Consider temporary mitigation measures")

    if "CVE" in title.upper():
        recommendations.append("Check vendor security advisories")

    recommendations.append("Update vulnerability management tracking")

    return recommendations
