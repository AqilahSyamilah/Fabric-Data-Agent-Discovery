import os
import time

from dotenv import load_dotenv
from fabric_data_agent_client import FabricDataAgentClient


# Load configuration from .env
load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
DATA_AGENT_URL = os.getenv("DATA_AGENT_URL")


if not TENANT_ID:
    raise ValueError("TENANT_ID is missing from .env")

if not DATA_AGENT_URL:
    raise ValueError("DATA_AGENT_URL is missing from .env")


# Create Fabric Data Agent client
fabric_client = FabricDataAgentClient(
    tenant_id=TENANT_ID,
    data_agent_url=DATA_AGENT_URL
)


def ask_fabric(question):

    start_time = time.perf_counter()

    answer = fabric_client.ask(
        question,
        timeout=120
    )

    response_time = (
        time.perf_counter()
        - start_time
    )

    return {
        "answer": str(answer),
        "response_time": round(
            response_time,
            2
        )
    }