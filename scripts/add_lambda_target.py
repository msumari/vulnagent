#!/usr/bin/env python3

import json
import sys
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

def add_curator_lambda_target(lambda_arn):
    """Add curator Lambda function as a target to the Gateway"""
    
    # Load gateway configuration
    with open("gateway_config.json", "r") as f:
        gateway_config = json.load(f)
    
    gateway_id = gateway_config["gateway_id"]
    
    # Initialize the Gateway client
    client = GatewayClient(region_name="us-east-1")
    
    print(f"Using Lambda ARN: {lambda_arn}")
    
    # Define vulnerability analysis tools
    target_payload = {
        "lambdaArn": lambda_arn,
        "toolSchema": {
            "inlinePayload": [
                {
                    "name": "analyze_vulnerability_finding",
                    "description": "Analyze AWS Inspector vulnerability finding",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "findingArn": {
                                "type": "string",
                                "description": "AWS Inspector finding ARN"
                            },
                            "severity": {
                                "type": "string",
                                "description": "Vulnerability severity level"
                            },
                            "title": {
                                "type": "string",
                                "description": "Vulnerability title/description"
                            }
                        },
                        "required": ["findingArn"]
                    }
                },
                {
                    "name": "process_inspector_event",
                    "description": "Process Inspector EventBridge event",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "event": {
                                "type": "object",
                                "description": "Complete Inspector EventBridge event"
                            }
                        },
                        "required": ["event"]
                    }
                }
            ]
        }
    }
    
    # Create gateway object
    gateway = {
        "gatewayId": gateway_id,
        "mcp_url": gateway_config["mcp_url"]
    }
    
    # Create Lambda target
    print("Adding Lambda target to Gateway...")
    lambda_target = client.create_mcp_gateway_target(
        gateway=gateway,
        name="vulnerability-analyzer",
        target_type="lambda",
        target_payload=target_payload,
        credentials=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}]
    )
    
    print(f"✅ Lambda target added successfully!")
    print(f"Target ID: {lambda_target.get('target_id', 'N/A')}")
    print(f"Available tools:")
    for tool in target_payload["toolSchema"]["inlinePayload"]:
        print(f"  - {tool['name']}: {tool['description']}")
    
    return lambda_target

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_lambda_target_simple.py <lambda_arn>")
        print("Example: python add_lambda_target_simple.py arn:aws:lambda:us-east-1:123456789012:function:my-function")
        sys.exit(1)
    
    lambda_arn = sys.argv[1]
    add_curator_lambda_target(lambda_arn)
