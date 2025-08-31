from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent(model="anthropic.claude-3-haiku-20240307-v1:0")


@app.entrypoint
def invoke(payload):
    user_input = payload.get("prompt", "Tell me about agentic AI")
    result = agent(user_input)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
