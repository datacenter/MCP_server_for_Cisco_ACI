This is a simple MCP (Model Context Protocol) that interacts with a Cisco APIC controller.
It's been tested with Claude Desktop and Visual Studio Code in Agent mode with CoPilot.
The server runs in STDIO mode which means it's meant to run locally on your computer.

It exposes two tools that are self-explanatory, just inspect main.py to find out.

Specify your APIC credentials in the .env file then register the MCP server with Claude or VS Code.
To do so, create a mcp.json file such as this one:

```
{
  "servers": {
    "ciscoApicServer": {
      "type": "stdio",
      "command": "C:\\Users\\cpaggen\\.local\\bin\\uv.EXE",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "C:\\MCP\\app\\main.py"
      ]
    }
  }
}

and instruct Claude Desktop or VS Code to use it (see the documentation, it's quite straightforward)
Make sure you install the MCP client tools locally if you decide to invoke the MCP server with "uv run mcp" as shown above.

Note that you run the server directly using UV, or you can build a Docker image and run it as a container.
In that case, you'll need to adapt the mcp.json config accordingly.

Local installation of MCP client tools is recommended for debugging the server code.