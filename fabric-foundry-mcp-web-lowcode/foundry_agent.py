import os

from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient


load_dotenv()

PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME")

if not PROJECT_ENDPOINT:
    raise ValueError(
        "FOUNDRY_PROJECT_ENDPOINT is missing from .env"
    )

if not AGENT_NAME:
    raise ValueError(
        "FOUNDRY_AGENT_NAME is missing from .env"
    )


credential = InteractiveBrowserCredential()

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential
)

openai_client = project.get_openai_client(
    agent_name=AGENT_NAME
)


def ask_agent(question):

    # First request
    response = openai_client.responses.create(
        input=question
    )

    print("\n=== FIRST RESPONSE ===")
    print(response.output)

    approval_inputs = []

    # Check for MCP approval request
    for item in response.output:

        if getattr(item, "type", None) == "mcp_approval_request":

            print("\nMCP approval requested")
            print("Tool:", item.name)
            print("Arguments:", item.arguments)

            approval_inputs.append({
                "type": "mcp_approval_response",
                "approval_request_id": item.id,
                "approve": True
            })

    # Continue response after approval
    if approval_inputs:

        response = openai_client.responses.create(
            input=approval_inputs,
            previous_response_id=response.id
        )

        print("\n=== FINAL RESPONSE ===")
        print(response.output)

    print("\n=== OUTPUT TEXT ===")
    print(repr(response.output_text))

    return response.output_text