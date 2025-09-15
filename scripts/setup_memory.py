#!/usr/bin/env python3
"""
Setup AgentCore Memory for VulnAgent
"""

from bedrock_agentcore.memory import MemoryClient
import json

def setup_vuln_memory():
    """Setup AgentCore Memory for vulnerability management"""
    client = MemoryClient(region_name="us-east-1")
    
    memory = client.create_memory_and_wait(
        name="VulnAgentMemory",
        description="Memory for vulnerability remediation knowledge",
        strategies=[{
            "semanticMemoryStrategy": {
                "name": "VulnRemediation", 
                "namespaces": ["/vuln/remediation/{actorId}"]
            }
        }]
    )
    
    memory_id = memory.get("id")
    
    # Save memory ID for agent use
    with open("memory_config.json", "w") as f:
        json.dump({"memory_id": memory_id}, f, indent=2)
    
    print(f"✅ Memory created: {memory_id}")
    return memory_id

if __name__ == "__main__":
    setup_vuln_memory()
