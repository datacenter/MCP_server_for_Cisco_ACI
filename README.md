# MCP (Model Context Protocol) for Cisco APIC

This project provides a simple MCP (Model Context Protocol) server that interacts with a Cisco APIC controller.
If you'd like to understand how this works in detail, please check out [this blog post](https://medium.com/@cpaggen/putting-ai-to-work-with-your-cisco-application-centric-infrastructure-fabric-a-mcp-server-for-aci-838e6fe62022)

- Tested with **Claude Desktop** and **Visual Studio Code** in Agent mode with Copilot.
- The server runs in **STDIO mode**, intended for local execution.

## Features

- Exposes two tools for APIC interaction (see `app/main.py` for details).
- Easily configurable via environment variables.

## Setup

1. **Specify APIC credentials** in the `.env` file.
2. **Register the MCP server** with Claude or VS Code.

   Create a `mcp.json` file like this:

   ```json
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
   ```

3. Instruct Claude Desktop or VS Code to use it:
   - See [Claude Desktop Quickstart](https://modelcontextprotocol.io/quickstart/user)
   - See [VS Code Copilot MCP Servers](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)

4. **Install MCP client tools locally** if you invoke the MCP server with `uv run mcp` as above.
   - Use ```uv add "mcp[cli]"``` or ```pip install "mcp[cli]"```

## Docker Support

You can run the server directly using UV, or build a Docker image and run it as a container. If using Docker, adapt the `mcp.json` config accordingly.

> **Note:** Local installation of MCP client tools is recommended for debugging the server code.
