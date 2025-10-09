# Installation and Setup Instructions

## Prerequisites
- Python 3.11 or higher
- Node.js (for Playwright)

## Setup Steps

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers:**
   ```bash
   playwright install
   ```

3. **Setup Environment Variables:**
   - Copy `.env.example` to `.env`
   - Fill in your actual configuration values:
     - JIRA credentials (base URL, email, API token)
     - Azure OpenAI credentials (if using LLM bridge)
     - Default JIRA ticket key

4. **Verify Installation:**
   ```bash
   python mcp_client_caller.py --help
   ```

## Running the Application

### Basic JIRA Automation:
```bash
python mcp_client_caller.py --jira YOUR-TICKET-KEY
```

### Interactive LLM Bridge Mode:
```bash
python mcpllm_bridge_client_caller.py
```

### With Debug Information:
```bash
python mcp_client_caller.py --jira YOUR-TICKET-KEY --debug --verbose
```

## Troubleshooting

1. **Import Errors:** Make sure all dependencies are installed
2. **JIRA Connection Issues:** Verify your JIRA credentials in `.env`
3. **Browser Issues:** Ensure Playwright browsers are installed
4. **LLM Issues:** Check Azure OpenAI configuration in `.env`