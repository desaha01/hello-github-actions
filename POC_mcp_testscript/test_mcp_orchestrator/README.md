# MCP Test Orchestrator

A Model Context Protocol (MCP) based automation framework that integrates JIRA workflows with browser automation using Playwright. This project demonstrates how to fetch JIRA stories and automatically generate browser automation scripts based on the story content.

## 🚀 Features

- **JIRA Integration**: Fetch JIRA stories and extract automation instructions
- **Browser Automation**: Automated web testing using Playwright
- **MCP Architecture**: Modular server-client architecture using Model Context Protocol
- **LLM Bridge**: Natural language interface to browser automation via Azure OpenAI
- **Script Generation**: Automatically generate Playwright test scripts from JIRA stories
- **Screenshot Capture**: Take screenshots during automation workflows
- **Interactive Chat**: Conversational interface for browser automation commands
- **Flexible Configuration**: Support for environment variables and command-line arguments

## 📋 Prerequisites

- Python 3.11 or higher
- JIRA account with API access
- Node.js (for Playwright)
- Azure OpenAI account (for LLM Bridge functionality)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd test_mcp_orchestrator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   # or if using uv
   uv sync
   ```

3. **Install Playwright:**
   ```bash
   playwright install
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   JIRA_BASE_URL=https://your-company.atlassian.net
   JIRA_EMAIL=your-email@company.com
   JIRA_API_TOKEN=your-jira-api-token
   JIRA_KEY=DEFAULT-TICKET-KEY
   ```

## 🎯 Usage

### Basic Usage

Run the main script with a JIRA ticket key:

```bash
python mcp_client_caller.py --jira TICKET-123
```

### Command Line Options

- `--jira TICKET_KEY`: Specify the JIRA ticket key to process
- `--debug`: Enable detailed debug information about available tools
- `--verbose`: Enable verbose logging output

### Examples

1. **Run with specific JIRA ticket:**
   ```bash
   python mcp_client_caller.py --jira QAAR-6916
   ```

2. **Run with debug information:**
   ```bash
   python mcp_client_caller.py --jira QAAR-6916 --debug
   ```

3. **Run with verbose logging:**
   ```bash
   python mcp_client_caller.py --jira QAAR-6916 --verbose
   ```

4. **Run with environment variable:**
   ```bash
   export JIRA_KEY=QAAR-6916
   python mcp_client_caller.py
   ```

### MCP-LLM Bridge Usage

The project also includes an LLM bridge that allows natural language interaction with browser automation tools through Azure OpenAI.

#### Prerequisites for LLM Bridge

Add these environment variables to your `.env` file:
```env
AZURE_OPEN_AI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPEN_AI_API_VERSION=2024-02-15-preview
AZURE_OPEN_AI_API_KEY=your-azure-openai-api-key
AZURE_OPEN_AI_DEPLOYMENT_MODEL=your-deployment-name
```

#### Running the LLM Bridge

1. **Interactive Session** (default):
   ```bash
   python mcpllm_bridge_client_caller.py
   ```
   This starts an interactive chat session where you can give natural language commands like:
   - "Navigate to https://www.amazon.com and take a screenshot"
   - "Click on the search button"
   - "Fill the form with test data"

2. **Single Query Mode**:
   ```bash
   python mcpllm_bridge_client_caller.py --single
   ```
   This runs a predefined test query and exits.

#### LLM Bridge Features

- **Natural Language Processing**: Give browser automation commands in plain English
- **Intelligent Tool Selection**: The LLM automatically chooses the right browser automation tools
- **Interactive Chat**: Continuous conversation with context awareness
- **Error Handling**: Graceful handling of automation failures with explanations
- **Debug Mode**: Detailed logging of tool selection and execution

## 🏗️ Project Structure

```
test_mcp_orchestrator/
├── client_bridge/           # MCP client bridge components
│   ├── __init__.py
│   ├── bridge.py           # Main bridge implementation
│   ├── config.py           # Configuration management
│   ├── llm_client.py       # LLM client integration
│   ├── llm_config.py       # LLM configuration
│   └── mcp_client.py       # MCP client implementation
├── server/                 # MCP server components
│   ├── browser_manager.py  # Browser management utilities
│   ├── browser_navigator_server.py  # Main MCP server
│   └── jira_config.py      # JIRA configuration
├── generated_scripts/      # Auto-generated Playwright scripts
├── screenshots/           # Captured screenshots
├── mcp_client_caller.py   # Main execution script
├── mcpllm_bridge_client_caller.py  # LLM bridge caller
├── pyproject.toml         # Project dependencies
├── Dockerfile             # Container configuration
└── README.md              # This file
```

## 🔧 How It Works

1. **JIRA Story Fetching**: The script connects to JIRA using the provided API credentials and fetches the specified story/ticket.

2. **URL Extraction**: Extracts URLs from the JIRA story description using regex patterns.

3. **Browser Automation**: Uses Playwright to:
   - Navigate to extracted URLs
   - Take screenshots
   - Find and interact with page elements
   - Fill forms, click buttons, hover over elements
   - Execute JavaScript

4. **Script Generation**: Automatically generates Playwright test scripts based on the actions performed during the workflow.

5. **Results**: Returns a comprehensive results object containing:
   - Execution status
   - Step-by-step results
   - Generated script content
   - Screenshots taken

### LLM Bridge Workflow

The MCP-LLM Bridge provides an additional interaction mode:

1. **Bridge Initialization**: Connects MCP server to Azure OpenAI LLM
2. **Tool Registration**: Converts MCP tools to OpenAI function format
3. **Natural Language Processing**: User queries processed by the LLM
4. **Intelligent Tool Selection**: LLM chooses appropriate browser automation tools
5. **Action Execution**: Tools executed through MCP protocol
6. **Response Generation**: LLM provides natural language feedback
7. **Context Maintenance**: Conversation history maintained for follow-up commands

## 🔌 MCP Architecture

This project uses the Model Context Protocol (MCP) to create a modular architecture:

- **Server**: `BrowserNavigationServer` provides browser automation tools
- **Client**: `MCPClient` connects to the server and executes tools
- **Bridge**: `MCPLLMBridge` connects MCP tools to Azure OpenAI for natural language interaction
- **LLM Client**: Handles communication with Azure OpenAI and tool execution coordination

Available MCP tools include:
- `fetch_jira_story`: Fetch JIRA ticket information
- `playwright_navigate`: Navigate to URLs
- `playwright_screenshot`: Take screenshots
- `playwright_click`: Click elements
- `playwright_fill`: Fill form fields
- `playwright_hover`: Hover over elements
- `playwright_select`: Select dropdown options
- `playwright_evaluate`: Execute JavaScript
- `extract_selector_by_page_content`: Find selectors based on page content
- `generate_playwright_script`: Generate test scripts

## 📸 Output

The script generates several outputs:

1. **Screenshots**: Saved in the `screenshots/` directory
2. **Playwright Scripts**: Generated TypeScript test files in `generated_scripts/`
3. **Execution Logs**: Detailed logging of the automation workflow
4. **Results JSON**: Structured results containing all execution details

## 🚨 Error Handling

The script includes comprehensive error handling:
- Graceful handling of missing JIRA tickets
- Fallback for URL extraction failures
- Retry mechanisms for browser automation
- Detailed error logging with stack traces

## 🐳 Docker Support

Build and run using Docker:

```bash
# Build the image
docker build -t mcp-test-orchestrator .

# Run the container
docker run -e JIRA_KEY=TICKET-123 mcp-test-orchestrator
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the terms specified in the LICENSE file.

## 🔍 Troubleshooting

### Common Issues

1. **JIRA Authentication Errors**:
   - Verify your JIRA_API_TOKEN is correct
   - Ensure your JIRA_EMAIL has access to the specified tickets

2. **Playwright Errors**:
   - Run `playwright install` to ensure browsers are installed
   - Check that the target website is accessible

3. **Module Import Errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Verify Python version is 3.11 or higher

4. **Azure OpenAI Configuration Errors**:
   - Verify all Azure OpenAI environment variables are set correctly
   - Check that your Azure OpenAI deployment is active and accessible
   - Ensure your API key has the necessary permissions

5. **LLM Bridge Initialization Errors**:
   - Check Azure OpenAI endpoint URL format
   - Verify API version compatibility
   - Ensure deployment model name matches your Azure OpenAI configuration

### Debug Mode

Use the `--debug` flag to get detailed information about:
- Available MCP tools
- JIRA story content
- Browser automation steps
- Generated script content

### Verbose Logging

Use the `--verbose` flag to enable detailed logging for troubleshooting.

## 📧 Support

For issues and questions, please create an issue in the project repository.
