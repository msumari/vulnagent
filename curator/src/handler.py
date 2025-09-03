import json

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event, indent=2)}")
    
    # Check if this is a Gateway tool call
    tool_name = getattr(context, 'bedrockagentcoreToolName', None)
    
    if tool_name:
        return handle_gateway_tool_call(event, tool_name)
    else:
        return handle_inspector_event(event)

def handle_gateway_tool_call(event, tool_name):
    """Handle tool calls from AgentCore Gateway"""
    print(f"Gateway tool call: {tool_name}")
    
    if tool_name == "analyze_vulnerability_finding":
        return analyze_vulnerability_finding(event)
    elif tool_name == "process_inspector_event":
        return process_inspector_event(event.get('event', {}))
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Unknown tool: {tool_name}'})
        }

def analyze_vulnerability_finding(params):
    """Analyze a specific vulnerability finding"""
    finding_arn = params.get('findingArn', '')
    severity = params.get('severity', 'UNKNOWN')
    title = params.get('title', 'Unknown vulnerability')
    
    analysis = {
        'findingArn': finding_arn,
        'severity': severity,
        'title': title,
        'riskLevel': get_risk_level(severity),
        'recommendations': get_recommendations(severity, title)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(analysis)
    }

def process_inspector_event(inspector_event):
    """Process a complete Inspector EventBridge event"""
    detail = inspector_event.get('detail', {})
    return analyze_vulnerability_finding({
        'findingArn': detail.get('findingArn', ''),
        'severity': detail.get('severity', ''),
        'title': detail.get('title', '')
    })

def handle_inspector_event(event):
    """Handle direct Inspector EventBridge events"""
    detail = event.get('detail', {})
    finding_arn = detail.get('findingArn', '')
    severity = detail.get('severity', '')
    title = detail.get('title', '')
    
    print(f"Inspector Event - Finding: {title}, Severity: {severity}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Inspector finding processed',
            'findingArn': finding_arn
        })
    }

def get_risk_level(severity):
    """Determine risk level based on severity"""
    severity_map = {
        'CRITICAL': 'VERY_HIGH',
        'HIGH': 'HIGH', 
        'MEDIUM': 'MEDIUM',
        'LOW': 'LOW',
        'INFORMATIONAL': 'VERY_LOW'
    }
    return severity_map.get(severity.upper(), 'UNKNOWN')

def get_recommendations(severity, title):
    """Generate recommendations based on vulnerability"""
    recommendations = []
    
    if 'CRITICAL' in severity.upper() or 'HIGH' in severity.upper():
        recommendations.append("Immediate patching required")
        recommendations.append("Consider temporary mitigation measures")
    
    if 'CVE' in title.upper():
        recommendations.append("Check vendor security advisories")
    
    recommendations.append("Update vulnerability management tracking")
    
    return recommendations
