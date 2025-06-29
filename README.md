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
2. If you want Claude or VS Code to run the Python code directly (no container), install [UV](https://docs.astral.sh/uv/)
3. **Register the MCP server** with Claude or VS Code.

   For VS Code, create a `.vscode/mcp.json` file like this in your workspace:

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

## Screenshots

Below are some screenshots demonstrating the MCP server in action and its integration with Claude Desktop and VS Code:

| MCP Server Registered | Tool Registered in Claude | Claude Tools List |
|----------------------|--------------------------|------------------|
| ![MCP Server Registered](screenshots/01a-mcp_server_registered.png) | ![Tool Registered in Claude](screenshots/01b-tool_registered_in_claude.png) | ![Claude Tools List](screenshots/01c-claude_tools_list.png) |

| MCP Server Output | Sample Question in VS Code | Sample Question in Claude |
|-------------------|---------------------------|--------------------------|
| ![MCP Server Output](screenshots/02-mcp_server_output.png) | ![Sample Question VS Code](screenshots/03a-sample_question_vscode.png) | ![Sample Claude Question](screenshots/03b-sample_claude_question.png) |

| How to Use ACI Backup |
|----------------------|
| ![How to Use ACI Backup](screenshots/04-how_to_use_aci_backup.png) |

These images illustrate the registration process, available tools, and example interactions.
