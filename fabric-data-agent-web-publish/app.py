from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from fabric_data_agent_client import FabricDataAgentClient

from pathlib import Path
import os
import time


# ==============================
# LOAD ENVIRONMENT VARIABLES
# ==============================

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print("Looking for .env at:", ENV_PATH)
print(".env exists:", ENV_PATH.is_file())

load_dotenv(dotenv_path=ENV_PATH)

TENANT_ID = os.getenv("TENANT_ID")
DATA_AGENT_URL = os.getenv("DATA_AGENT_URL")

print("TENANT_ID loaded:", bool(TENANT_ID))
print("DATA_AGENT_URL loaded:", bool(DATA_AGENT_URL))


if not TENANT_ID:
    raise ValueError("TENANT_ID is missing from .env")

if not DATA_AGENT_URL:
    raise ValueError("DATA_AGENT_URL is missing from .env")

# Flask
app = Flask(__name__)


# Connect to Fabric Data Agent
print("Connecting to Fabric Data Agent...")

fabric_client = FabricDataAgentClient(
    tenant_id=TENANT_ID,
    data_agent_url=DATA_AGENT_URL
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        }), 400


    try:

        print("\nQuestion:")
        print(question)

        # Start timing
        start_time = time.perf_counter()


        # Ask the REAL Fabric Data Agent
        answer = fabric_client.ask(
            question
        )


        # Stop timing
        elapsed_time = time.perf_counter() - start_time


        print("\nFabric answer:")
        print(answer)

        print(
            f"\nResponse time: "
            f"{elapsed_time:.2f} seconds"
        )


        return jsonify({
            "answer": answer,
            "response_time": round(elapsed_time, 2)
        })


    except Exception as e:

        print("\nFabric Data Agent Error:")
        print(str(e))

        return jsonify({
            "answer": "Unable to get a response from Fabric Data Agent.",
            "error": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001,
        use_reloader=False
    )