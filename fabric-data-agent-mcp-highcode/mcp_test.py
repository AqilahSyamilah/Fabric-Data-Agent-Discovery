import asyncio
import os
from wsgiref import headers
import httpx

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


load_dotenv(override=True)

FABRIC_MCP_URL = os.getenv("FABRIC_MCP_URL")

if not FABRIC_MCP_URL:
    raise ValueError(
        "FABRIC_MCP_URL is missing from .env"
    )


async def main():

    # ==================================================
    # 1. Authenticate using Azure CLI
    # ==================================================

    credential = AzureCliCredential()

    print("Getting Fabric access token...")

    token = credential.get_token(
        "https://api.fabric.microsoft.com/.default"
    )

    print("Fabric token obtained successfully.")


    # ==================================================
    # 2. Authorization Header
    # ==================================================

    headers = {
        "Authorization": f"Bearer {token.token}"
    }


    # ==================================================
    # 3. Create Authenticated HTTP Client
    # ==================================================

    async with httpx.AsyncClient(
        headers=headers,
        timeout=httpx.Timeout(120.0)
    ) as http_client:

        print("Connecting directly to Fabric MCP...")


        # ==================================================
        # 4. Connect to Fabric MCP Server
        # ==================================================

        async with streamable_http_client(
            FABRIC_MCP_URL,
            http_client=http_client
        ) as (
            read_stream,
            write_stream,
            _
        ):


            # ==================================================
            # 5. Create MCP Client Session
            # ==================================================

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                print("Initializing MCP session...")

                init_result = await session.initialize()

                print(
                    "MCP session initialized successfully."
                )

                # # Test MCP ping directly
                # print("\nTesting MCP ping...")

                # try:
                #     await session.send_ping()
                #     print("MCP ping successful.")

                # except Exception as error:
                #     print(
                #         "MCP ping failed:",
                #         type(error).__name__,
                #         ":",
                #         error
                #     )

                print(
                    f"Protocol version: "
                    f"{init_result.protocolVersion}"
                )


                # ==================================================
                # 6. Discover MCP Tools
                # ==================================================

                print("\nRetrieving MCP tools...")

                tools = await session.list_tools()

                print("\nAvailable MCP Tools:")
                print("=" * 50)

                for tool in tools.tools:

                    print(
                        f"\nTool name: {tool.name}"
                    )

                    if tool.description:
                        print(
                            f"Description: "
                            f"{tool.description}"
                        )

                    print(
                        f"Input schema: "
                        f"{tool.inputSchema}"
                    )


                # ==================================================
                # 7. Interactive Question Loop
                # ==================================================

                while True:

                    question = input(
                        "\nAsk Fabric Data Agent "
                        "(type 'exit' to stop): "
                    ).strip()

                    if question.lower() in {
                        "exit",
                        "quit",
                        "q",
                        "bye"
                    }:
                        print("Program ended.")
                        break

                    if not question:
                        continue

                    print(
                        f"\nAsking: {question}"
                    )


                    # ==================================================
                    # 8. Call Fabric Data Agent MCP Tool
                    # ==================================================

                    try:

                        tool_result = await session.call_tool(
                            "DataAgent_Retail_Data_Agent",
                            {
                                "userQuestion": question
                            }
                        )


                        # ==================================================
                        # 9. Display Response
                        # ==================================================

                        print("\nTool response:")
                        print("=" * 50)

                        for block in tool_result.content:

                            if getattr(
                                block,
                                "type",
                                None
                            ) == "text":

                                print(block.text)


                    except Exception as error:

                        print(
                            "\nTool call failed:",
                            type(error).__name__,
                            ":",
                            error
                        )


if __name__ == "__main__":
    asyncio.run(main())