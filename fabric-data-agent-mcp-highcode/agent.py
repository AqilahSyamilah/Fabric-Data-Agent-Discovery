import httpx
import asyncio
import os
from dotenv import load_dotenv
from agent_framework import Agent, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential, get_bearer_token_provider

load_dotenv(override=True)

EXIT_WORDS = {
    "exit",
    "quit",
    "q",
    "bye"
}

def build_fabric_header_provider(credential):
    """
    Get a fresh Microsoft Fabric bearer token
    for every MCP request.
    """

    get_token = get_bearer_token_provider(
        credential,
        "https://api.fabric.microsoft.com/.default"
    )

    def provide(_kwargs):
        return {
            "Authorization": f"Bearer {get_token()}"
        }

    return provide

async def main():

    # ==================================================
    # 1. Authentication
    # ==================================================

    credential = AzureCliCredential()

    # ==================================================
    # 2. Fabric Data Agent MCP Tool
    # ==================================================

    fabric_tool = MCPStreamableHTTPTool(
        name="retail_data_agent",
        url=os.environ["FABRIC_MCP_URL"],
        description=(
            "Query the Microsoft Fabric Retail Data Agent "
            "for factual information about retail sales, "
            "stores, products, customers and inventory."
        ),
        header_provider=build_fabric_header_provider(
            credential
        ),
        load_prompts=False
    )

    # ==================================================
    # 3. Foundry Model
    # ==================================================

    chat_client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=credential
)
    # ==================================================
    # 4. Build Agent
    # ==================================================

    async with fabric_tool:

        agent = Agent(
            client=chat_client,

            name="retail-fabric-mcp-agent",

            instructions=(
                "You are a retail analytics assistant. "
                "When the user asks for factual retail data, "
                "use the retail_data_agent MCP tool. "
                "Never invent sales, store, product, customer "
                "or inventory values. "
                "If the MCP tool cannot provide the answer, "
                "say that the Fabric Data Agent could not "
                "retrieve the requested information."
            ),

            tools=fabric_tool
        )
        # ==================================================
        # 5. Conversation Session
        # ==================================================

        session = agent.create_session()

        print("\nRetail Fabric MCP Agent ready.")
        print(
            "Ask questions about your retail data."
        )
        print(
            "Type 'exit', 'quit', 'q' or 'bye' to stop.\n"
        )
        # ==================================================
        # 6. Interactive Loop
        # ==================================================

        while True:

            try:

                user_input = input(
                    ">>> "
                ).strip()

            except (
                EOFError,
                KeyboardInterrupt
            ):

                print("\nGoodbye!")
                break

            if not user_input:
                continue

            if user_input.lower() in EXIT_WORDS:

                print("Goodbye!")
                break

            try:

                result = await agent.run(
                    user_input,
                    session=session
                )

                print(
                    f"\n{result}\n"
                )

            except Exception as error:

                print(
                    f"\n[Error] {error}\n"
                )

if __name__ == "__main__":

    asyncio.run(main())