import asyncio
import json
import logging
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Silencia logs para que a unica saida em stdout seja o JSON final.
logging.disable(logging.CRITICAL)


async def main() -> dict:
    params = StdioServerParameters(command=sys.executable, args=["servidor_mcp.py"])
    # Descarta o stderr do servidor MCP (logs do rich) para nao poluir a saida.
    devnull = open(os.devnull, "w")
    async with stdio_client(params, errlog=devnull) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            nomes = [t.name for t in tools.tools]

            criar = await session.call_tool("criar_tarefa", {"titulo": "tarefa via mcp"})
            listar = await session.call_tool("listar_tarefas", {})

            criar_resultado = json.loads(criar.content[0].text)

            listar_text = listar.content[0].text
            listar_resultado = json.loads(listar_text)
            if not isinstance(listar_resultado, list):
                listar_resultado = [json.loads(c.text) for c in listar.content]

            return {
                "tools": nomes,
                "criar_resultado": criar_resultado,
                "listar_resultado": listar_resultado,
            }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main())))
