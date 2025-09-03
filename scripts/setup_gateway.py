from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient


def create_vulnagent_gateway():
    """Create a Gateway for VulnAgent with Cognito EZ Auth"""

    # Initialize the Gateway client
    client = GatewayClient(region_name="us-east-1")

    # EZ Auth - automatically sets up Cognito OAuth
    print("Setting up Cognito OAuth...")
    cognito_result = client.create_oauth_authorizer_with_cognito("vulnagent-gateway")

    # Create the gateway with semantic search enabled
    print("Creating Gateway...")
    gateway = client.create_mcp_gateway(
        name="vulnagent-gateway",
        role_arn=None,  # Will be created automatically
        authorizer_config=cognito_result["authorizer_config"],
        enable_semantic_search=True,
    )

    print(f"✅ Gateway created successfully!")
    
    # Debug: Print the actual gateway response structure
    print(f"Gateway response type: {type(gateway)}")
    print(f"Gateway response: {gateway}")
    
    # Handle different possible response structures
    if isinstance(gateway, dict):
        gateway_id = gateway.get('gatewayId') or gateway.get('gateway_id')
        if not gateway_id:
            # Try to extract from ARN if available
            gateway_arn = gateway.get('gatewayArn') or gateway.get('arn')
            if gateway_arn:
                gateway_id = gateway_arn.split('/')[-1]
    else:
        # If it's an object, try to access attributes
        gateway_id = getattr(gateway, 'gatewayId', None) or getattr(gateway, 'gateway_id', None)
    
    if not gateway_id:
        raise Exception("Could not extract gateway ID from response")
    
    # Construct MCP URL
    mcp_url = f"https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
    
    print(f"MCP Endpoint: {mcp_url}")
    print(f"Gateway ID: {gateway_id}")
    print(f"\nOAuth Credentials:")
    print(f"  Client ID: {cognito_result['client_info']['client_id']}")
    print(f"  Client Secret: {cognito_result['client_info']['client_secret']}")
    print(f"  Scope: {cognito_result['client_info']['scope']}")
    
    # Get domain from cognito_result or construct it
    domain = cognito_result['client_info'].get('domain')
    if not domain:
        # Extract domain from the cognito_result structure
        # The domain should be in the format: agentcore-{hash}.auth.us-east-1.amazoncognito.com
        # We can extract it from other cognito info or construct it
        domain_prefix = cognito_result.get('domain_name', 'agentcore-214b416c')  # fallback
        domain = f"{domain_prefix}.auth.us-east-1.amazoncognito.com"
    
    print(f"  Domain: {domain}")
    
    # Save gateway info for later use
    gateway_info = {
        "gateway_id": gateway_id,
        "mcp_url": mcp_url,
        "client_id": cognito_result["client_info"]["client_id"],
        "client_secret": cognito_result["client_info"]["client_secret"],
        "domain": domain,
    }

    import json

    with open("gateway_config.json", "w") as f:
        json.dump(gateway_info, f, indent=2)

    print(f"\n💾 Gateway configuration saved to gateway_config.json")

    return gateway, cognito_result


if __name__ == "__main__":
    gateway, cognito_result = create_vulnagent_gateway()
