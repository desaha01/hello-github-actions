# MCP Client Integration Examples

This document provides examples of how to integrate the Karate MCP Server with various MCP clients.

## Claude Desktop Integration

To use the Karate MCP Server with Claude Desktop, add the following to your Claude configuration file:

### macOS/Linux
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "karate": {
      "command": "python3",
      "args": [
        "/absolute/path/to/karate_mcp_server.py",
        "/absolute/path/to/project"
      ],
      "env": {}
    }
  }
}
```

### Windows
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "karate": {
      "command": "python",
      "args": [
        "C:\\path\\to\\karate_mcp_server.py",
        "C:\\path\\to\\project"
      ],
      "env": {}
    }
  }
}
```

## Cline (VS Code Extension) Integration

Add to `.vscode/cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "karate": {
      "command": "python3",
      "args": ["karate_mcp_server.py", "."],
      "disabled": false,
      "autoApprove": ["list_karate_features"]
    }
  }
}
```

## Generic MCP Client Configuration

For other MCP clients, use this standard configuration:

```json
{
  "name": "karate",
  "transport": {
    "type": "stdio",
    "command": "python3",
    "args": ["/path/to/karate_mcp_server.py", "/path/to/project"]
  }
}
```

## Environment Variables

You can pass environment variables to the server:

```json
{
  "mcpServers": {
    "karate": {
      "command": "python3",
      "args": ["karate_mcp_server.py", "."],
      "env": {
        "JAVA_HOME": "/usr/lib/jvm/java-11",
        "MAVEN_OPTS": "-Xmx2g"
      }
    }
  }
}
```

## Testing the Integration

After configuring your MCP client:

1. Restart the client application
2. The Karate tools should appear in the available tools list
3. Try using the `list_karate_features` tool to verify the connection

## Common Issues

### Issue: Server not starting
**Solution**: Verify Python 3 is in your PATH and the script path is absolute

### Issue: Tools not appearing
**Solution**: Check the client logs for connection errors and verify JSON syntax

### Issue: Maven/Java not found
**Solution**: Ensure JAVA_HOME is set and Maven is in PATH, or specify in env variables

## Example Prompts

Once integrated, you can ask your AI assistant:

- "List all available Karate feature files"
- "Run the smoke tests in Karate"
- "Execute the sample-api-test.feature file"
- "Show me the results of the last Karate test run"

## Advanced Configuration

### Using with Docker

```json
{
  "mcpServers": {
    "karate": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "${workspaceFolder}:/workspace",
        "karate-mcp",
        "python3", "/app/karate_mcp_server.py", "/workspace"
      ]
    }
  }
}
```

### Using with Virtual Environment

```json
{
  "mcpServers": {
    "karate": {
      "command": "/path/to/venv/bin/python",
      "args": ["karate_mcp_server.py", "."]
    }
  }
}
```

## Troubleshooting

Enable debug logging by modifying the server script to include verbose output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check the MCP client logs for detailed error messages:
- Claude Desktop: Check Console in Developer Tools
- VS Code: Check Output panel > MCP Servers

## Support

For issues or questions:
1. Check the [KARATE-MCP-README.md](KARATE-MCP-README.md) for detailed documentation
2. Review the test script: `python3 test_karate_mcp.py`
3. Verify tool listing: `python3 karate_mcp_server.py --list-tools`
