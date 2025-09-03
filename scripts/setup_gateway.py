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
    print(f"MCP Endpoint: {gateway['mcp_url']}")
    print(f"Gateway ID: {gateway['gateway_id']}")
    print(f"\nOAuth Credentials:")
    print(f"  Client ID: {cognito_result['client_info']['client_id']}")
    print(f"  Client Secret: {cognito_result['client_info']['client_secret']}")
    print(f"  Scope: {cognito_result['client_info']['scope']}")
    print(f"  Domain: {cognito_result['client_info']['domain']}")

    # Save gateway info for later use
    gateway_info = {
        "gateway_id": gateway["gateway_id"],
        "mcp_url": gateway["mcp_url"],
        "client_id": cognito_result["client_info"]["client_id"],
        "client_secret": cognito_result["client_info"]["client_secret"],
        "domain": cognito_result["client_info"]["domain"],
    }

    import json

    with open("gateway_config.json", "w") as f:
        json.dump(gateway_info, f, indent=2)

    print(f"\n💾 Gateway configuration saved to gateway_config.json")

    return gateway, cognito_result


if __name__ == "__main__":
    gateway, cognito_result = create_vulnagent_gateway()
