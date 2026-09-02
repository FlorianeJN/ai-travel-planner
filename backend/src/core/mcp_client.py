import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

MCP_URL = os.getenv("MCP_SERVER_URL", "http://mcp_server:5000/sse")


async def load_mcp_tools():
    client = MultiServerMCPClient(
        {"travel_tools": {"transport": "sse", "url": MCP_URL}}
    )

    return await client.get_tools()
