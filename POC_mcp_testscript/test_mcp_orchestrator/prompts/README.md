# Prompts Organization

This document explains how the prompts are organized in the MCP LLM Bridge project.

## Structure

```
prompts/
├── __init__.py
├── system_prompts.py      # Core system prompts for the LLM
└── automation_prompts.py  # User automation prompts for specific tasks
```

## Files Description

### `system_prompts.py`
Contains the main system prompt that defines the LLM's behavior and capabilities:
- `get_browser_automation_system_prompt()`: The core system prompt for browser automation
- `get_action_tracking_prompt()`: Instructions for tracking automation actions

### `automation_prompts.py`
Contains user-facing prompts for specific automation tasks:
- `create_jira_automation_prompt(jira_key)`: Prompt for JIRA ticket automation
- `create_demo_automation_prompt()`: Prompt for demo browser automation
- `create_automation_prompt(jira_key=None)`: Main entry point that routes to specific prompts

## Usage in Main Script

The main script `mcpllm_bridge_client_caller.py` imports and uses these prompts:

```python
from prompts.system_prompts import get_browser_automation_system_prompt
from prompts.automation_prompts import create_automation_prompt

# System prompt for LLM configuration
system_prompt = get_browser_automation_system_prompt()

# User automation prompt for specific tasks
test_query = create_automation_prompt(jira_key if jira_key else None)
```

## Benefits

1. **Separation of Concerns**: Prompts are separated from business logic
2. **Maintainability**: Easy to modify prompts without touching main code
3. **Reusability**: Prompts can be imported and used in other modules
4. **Organization**: Clear structure for different types of prompts
5. **Version Control**: Prompt changes can be tracked separately

## Key Features

- **MCP Tool Focus**: All prompts emphasize using MCP tools rather than generating code manually
- **Action Tracking**: Clear instructions for tracking automation actions
- **Script Generation**: Mandatory use of `generate_playwright_script` MCP tool
- **Error Prevention**: Explicit rules to prevent manual code generation
