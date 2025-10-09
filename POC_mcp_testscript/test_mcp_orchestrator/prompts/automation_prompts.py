"""
User automation prompts for JIRA ticket processing and demo automation.
"""


def create_jira_automation_prompt(jira_key):
    """
    Create a comprehensive prompt for JIRA automation and script generation.

    Args:
        jira_key: The JIRA ticket key

    Returns:
        str: A detailed prompt string for the LLM
    """
    return f"""
AUTOMATE JIRA TICKET {jira_key} - USE MCP TOOLS ONLY:

STEP 1 - FETCH JIRA:
Call: fetch_jira_story(jira_key="{jira_key}")

STEP 2 - EXECUTE AUTOMATION USING MCP TOOLS:
Use ONLY these MCP tools for automation:
- playwright_navigate(url="actual_url")
- playwright_click(selector="actual_selector")
- playwright_screenshot(name="descriptive_name")
- playwright_fill(selector="input", value="text")

Track each action in this format:
Action 1: playwright_navigate -> {{"type": "navigate", "url": "ACTUAL_URL"}}
Action 2: playwright_click -> {{"type": "click", "selector": "ACTUAL_SELECTOR"}}
Action 3: playwright_screenshot -> {{"type": "screenshot", "name": "name"}}

STEP 3 - MANDATORY MCP TOOL USAGE:
You MUST call the generate_playwright_script MCP tool:

generate_playwright_script(
    script_name="{jira_key}",
    url="main_url_from_jira",
    actions=[complete_array_of_all_actions],
    description="QA automation for {jira_key}",
    headless=false
)

🚫 DO NOT WRITE TYPESCRIPT CODE
🚫 DO NOT GENERATE CODE MANUALLY
✅ USE generate_playwright_script MCP TOOL
✅ PASS ALL ACTIONS TO THE TOOL

The MCP tool will generate the .spec.ts file for you.
"""


def create_demo_automation_prompt():
    """
    Create a demo automation prompt for testing purposes.

    Returns:
        str: A demo automation prompt
    """
    return """
BROWSER AUTOMATION DEMO - USE MCP TOOLS ONLY:

STEP 1: playwright_navigate(url="https://www.amazon.com")
Track: {"type": "navigate", "url": "https://www.amazon.com"}

STEP 2: playwright_screenshot(name="amazon_homepage")
Track: {"type": "screenshot", "name": "amazon_homepage"}

STEP 3: MANDATORY MCP TOOL USAGE
Call generate_playwright_script MCP tool:

generate_playwright_script(
    script_name="amazon_demo_script",
    url="https://www.amazon.com",
    actions=[
        {"type": "navigate", "url": "https://www.amazon.com"},
        {"type": "screenshot", "name": "amazon_homepage"}
    ],
    description="Demo browser automation script",
    headless=false
)

🚫 DO NOT WRITE CODE MANUALLY
✅ USE THE MCP TOOL ONLY
"""


def create_automation_prompt(jira_key=None):
    """
    Create a comprehensive prompt for automation and script generation.

    Args:
        jira_key: The JIRA ticket key (optional)

    Returns:
        str: A detailed prompt string for the LLM
    """
    if jira_key:
        return create_jira_automation_prompt(jira_key)
    else:
        return create_demo_automation_prompt()
