import json
import boto3

# Initialize Inspector2 client
inspector_client = boto3.client("inspector2")


def lambda_handler(event, context):
    # Get tool name from context
    tool_name = getattr(context, "bedrockagentcoreToolName", None)
    
    # If no tool name, assume this is a Gateway call for our main tool
    if not tool_name:
        tool_name = "analyze_vulnerability_finding"
    
    # Strip target prefix if present
    if "___" in tool_name:
        tool_name = tool_name.split("___")[-1]
    
    return handle_gateway_tool_call(event, tool_name)


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


def get_inspector_findings(severity_filter=None, max_results=20):
    """Fetch findings from Inspector2"""
    try:
        filters = {}
        if severity_filter:
            filters["severity"] = [{"comparison": "EQUALS", "value": severity_filter}]

        response = inspector_client.list_findings(
            filterCriteria=filters, maxResults=max_results
        )

        findings = []
        for finding in response.get("findings", []):
            findings.append(
                {
                    "findingArn": finding.get("findingArn"),
                    "severity": finding.get("severity"),
                    "title": finding.get("title"),
                    "description": finding.get("description"),
                    "type": finding.get("type"),
                    "status": finding.get("status"),
                }
            )

        return findings
    except Exception as e:
        print(f"Error fetching Inspector findings: {e}")
        return []


def analyze_vulnerability_finding(params):
    """Fetch and analyze vulnerability findings from Inspector2"""
    # Fetch findings directly from Inspector2 (no parameters needed)
    findings = get_inspector_findings()

    # Analyze each finding
    analyzed_findings = []
    for finding in findings:
        analyzed_finding = {
            "findingArn": finding.get("findingArn"),
            "severity": finding.get("severity"),
            "title": finding.get("title"),
            "description": finding.get("description"),
            "type": finding.get("type"),
            "status": finding.get("status"),
            "riskLevel": get_risk_level(finding.get("severity", "UNKNOWN")),
            "recommendations": get_recommendations(
                finding.get("severity", "UNKNOWN"), finding.get("title", "")
            ),
        }
        analyzed_findings.append(analyzed_finding)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"findings": analyzed_findings, "count": len(analyzed_findings)}
        ),
    }


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
