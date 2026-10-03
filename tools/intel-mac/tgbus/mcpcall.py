#!/usr/bin/env python3
"""Вызов инструмента живого Telegram MCP-демона (streamable HTTP, localhost) без перезапуска сессии.
  mcpcall.py --list
  mcpcall.py <tool> '<json-аргументы>'
"""
import asyncio, json, sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:8765/mcp"

async def main():
    async with streamablehttp_client(URL) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            if sys.argv[1] == "--list":
                tools = (await s.list_tools()).tools
                print(len(tools), "tools:", " ".join(sorted(t.name for t in tools)))
                return 0
            res = await s.call_tool(sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
            for c in res.content:
                print(getattr(c, "text", c))
            return 1 if res.isError else 0

sys.exit(asyncio.run(main()))
