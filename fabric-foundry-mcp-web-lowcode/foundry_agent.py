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

    response = openai_client.responses.create(
        input=question
    )

    return response.output_text