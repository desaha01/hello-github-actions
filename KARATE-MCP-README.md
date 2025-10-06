# Karate MCP Server

This is a Model Context Protocol (MCP) server for the Karate testing framework. It provides tools to interact with Karate tests through the MCP protocol, enabling AI assistants and other tools to run and manage Karate API tests.

## Overview

The Karate MCP Server exposes three main tools:

1. **run_karate_test**: Run a Karate feature file or specific scenarios with optional tag filtering
2. **list_karate_features**: List all available Karate feature files with their scenarios
3. **get_test_results**: Retrieve results from the last test run

## Prerequisites

- Python 3.7 or higher
- Java 8 or higher (required by Karate)
- Maven (for running Karate tests)
- Karate framework project setup

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements-karate-mcp.txt
```

2. Ensure Java and Maven are installed:
```bash
java -version
mvn -version
```

## Usage

### Running the MCP Server

Start the server in your Karate project directory:

```bash
python karate_mcp_server.py /path/to/karate/project
```

Or from the current directory:

```bash
python karate_mcp_server.py
```

### Listing Available Tools

To see all available tools:

```bash
python karate_mcp_server.py --list-tools
```

## Project Structure

The server expects the following directory structure:

```
project-root/
├── karate-tests/
│   ├── features/
│   │   ├── examples/
│   │   │   └── sample-api-test.feature
│   │   └── ... (other feature files)
│   └── target/
│       └── karate-reports/
│           └── ... (test results)
├── pom.xml (Maven project file)
└── karate_mcp_server.py
```

## Tools Documentation

### 1. run_karate_test

Runs a Karate test feature file.

**Parameters:**
- `feature_path` (required): Path to the feature file relative to the features directory
- `tags` (optional): Tags to filter scenarios (e.g., "@smoke")

**Example:**
```json
{
  "name": "run_karate_test",
  "arguments": {
    "feature_path": "examples/sample-api-test.feature",
    "tags": "@smoke"
  }
}
```

### 2. list_karate_features

Lists all available Karate feature files.

**Parameters:**
- `pattern` (optional): Glob pattern to filter feature files (e.g., "**/user*.feature")

**Example:**
```json
{
  "name": "list_karate_features",
  "arguments": {
    "pattern": "**/*api*.feature"
  }
}
```

### 3. get_test_results

Retrieves results from the last test run.

**Parameters:**
- `detailed` (optional): Whether to include detailed scenario results (default: false)

**Example:**
```json
{
  "name": "get_test_results",
  "arguments": {
    "detailed": true
  }
}
```

## Example Karate Feature File

A sample feature file is included at `karate-tests/features/examples/sample-api-test.feature`:

```gherkin
Feature: Sample API Test
  Background:
    * url 'https://jsonplaceholder.typicode.com'

  @smoke
  Scenario: Get all users
    Given path 'users'
    When method GET
    Then status 200
    And match response == '#array'
```

## Integration with MCP Clients

This server implements the MCP protocol and can be used with any MCP-compatible client. The server communicates via standard input/output using JSON messages.

### Example MCP Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "karate": {
      "command": "python",
      "args": ["/path/to/karate_mcp_server.py", "/path/to/project"],
      "env": {}
    }
  }
}
```

## Development

The server is built using Python's standard library and requires minimal dependencies. The main components are:

- **KarateMCPServer**: Main server class that handles tool execution
- **list_tools()**: Returns available MCP tools
- **handle_tool_call()**: Dispatches tool calls to appropriate handlers
- **start_server()**: Starts the MCP server loop

## Limitations

- The server currently uses Maven to run Karate tests
- Test execution timeout is set to 5 minutes
- Results are read from JSON files in the target directory

## Contributing

This is a basic implementation that can be extended with:
- Support for Gradle-based Karate projects
- Real-time test progress updates
- Enhanced error reporting
- Support for parallel test execution
- Integration with CI/CD pipelines

## License

This project is licensed under the MIT License - see the LICENSE file for details.
