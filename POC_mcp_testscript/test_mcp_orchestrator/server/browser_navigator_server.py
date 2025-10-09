import base64
import json
import sys
import requests
from datetime import datetime
from pathlib import Path
from typing import Literal, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the Python path so we can import client_bridge
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from server.jira_config import get_jira_config
from client_bridge.llm_client import LLMClient, LLMResponse
from client_bridge.llm_config import get_default_llm_config
from server.browser_manager import BrowserManager


class BrowserNavigationServer(FastMCP):
    def __init__(self, server_name="browser-navigator-server"):
        super().__init__(server_name)
        self.mcp = self
        self.browser_manager = BrowserManager()
        self.llm_config = get_default_llm_config()
        self.llm_client = LLMClient(self.llm_config)
        self.screenshots = dict()
        # self.register_tools()
        self.register_resources()
        self.register_prompts()

        # Get Jira configuration directly
        self.jira_config = get_jira_config()

        # Register the available tools with the LLM client
        # self._register_tools_with_llm_client()

        # Print startup information
        print("Browser Navigation Server initialized")
        print(f"Screenshots will be saved to: {parent_dir / 'screenshots'}")
        print("Browser will be visible (headless=False)")
        # print("Jira configuration loaded from environment variables")

        @self.mcp.tool()
        async def playwright_navigate(
            url: str, timeout=30000, wait_until: Literal["load", "networkidle"] = "load"
        ):
            """Navigate to a URL."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")
                await page.goto(url, timeout=timeout, wait_until=wait_until)
                return f"Navigated to {url} with {wait_until} wait"
            except Exception as e:
                raise ValueError(f"Navigation failed: {e}")

        @self.mcp.tool()
        async def playwright_screenshot(
            name: str, selector: str = None, width: int = 800, height: int = 600
        ):
            """Take a screenshot of the current page or a specific element."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")

                screenshot_options = {
                    "type": "png",
                    "full_page": True,
                }

                if selector:
                    # Screenshot of a specific element
                    element = await page.query_selector(selector)
                    if element:
                        screenshot = await element.screenshot(type="png")
                    else:
                        return f"Element not found: {selector}"
                else:
                    # Screenshot of the full page
                    screenshot = await page.screenshot(**screenshot_options)

                # Create screenshots directory if it doesn't exist
                screenshots_dir = parent_dir / "screenshots"
                screenshots_dir.mkdir(exist_ok=True)

                # Save screenshot to local file
                filename = f"{name}.png"
                filepath = screenshots_dir / filename

                with open(filepath, "wb") as f:
                    f.write(screenshot)

                # Convert the screenshot to a base64 string for response
                screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
                self.screenshots[name] = screenshot_base64

                return [
                    TextContent(
                        type="text", text=f"Screenshot '{name}' saved to {filepath}"
                    ),
                    ImageContent(
                        type="image", data=screenshot_base64, mimeType="image/png"
                    ),
                ]
            except Exception as e:
                raise ValueError(f"Screenshot failed: {e}")

        @self.mcp.tool()
        async def playwright_click(selector: str):
            """Click an element on the page."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")
                await page.click(selector)
                return f"Clicked on {selector}"
            except Exception as e:
                raise ValueError(f"Failed to click: {e}")

        @self.mcp.tool()
        async def playwright_fill(selector: str, value: str):
            """Fill out an input field."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")
                await page.wait_for_selector(selector)
                await page.fill(selector, value)
                return f"Filled {selector} with {value}"
            except Exception as e:
                raise ValueError(f"Failed to fill: {e}")

        @self.mcp.tool()
        async def playwright_select(selector: str, value: str):
            """Select an element on the page with a Select tag."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")
                await page.wait_for_selector(selector)
                await page.select_option(selector, value)
                return f"Selected {value} in {selector}"
            except Exception as e:
                raise ValueError(f"Failed to select: {e}")

        @self.mcp.tool()
        async def playwright_hover(selector: str):
            """Hover over an element on the page."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")
                await page.wait_for_selector(selector)
                await page.hover(selector)
                return f"Hovered over {selector}"
            except Exception as e:
                raise ValueError(f"Failed to hover: {e}")

        @self.mcp.tool()
        async def playwright_evaluate(script: str):
            """Execute JavaScript in the browser console."""
            try:
                page = await self.browser_manager.ensure_browser()
                if page is None:
                    raise ValueError("Failed to initialize browser")
                script_result = await page.evaluate(
                    """
                (script) => {
                    const logs = [];
                    const originalConsole = { ...console };

                    ['log', 'info', 'warn', 'error'].forEach(method => {
                        console[method] = (...args) => {
                            logs.push(`[${method}] ${args.join(' ')}`);
                            originalConsole[method](...args);
                        };
                    });

                    try {
                        const result = eval(script);
                        Object.assign(console, originalConsole);
                        return { result, logs };
                    } catch (error) {
                        Object.assign(console, originalConsole);
                        throw error;
                    }
                }
                """,
                    script,
                )
                # Parentheses allow grouping of multiple expressions in one line,
                # often used for long strings, tuples, or function arguments
                # that span multiple lines.
                return_string = (
                    "Execution result:\n"
                    + json.dumps(script_result["result"], indent=2)
                    + "\n\n"
                    + "Console output:\n"
                    + "\n".join(script_result["logs"])
                )
                return return_string
            except Exception as e:
                raise ValueError(f"Script execution failed: {e}")

        @self.mcp.tool()
        async def extract_selector_by_page_content(user_message: str) -> str:
            """Try to find a css selector by current page content."""
            # Ensure the browser page is available
            page = await self.browser_manager.ensure_browser()
            if page is None:
                raise ValueError("Failed to initialize browser")

            # Get the HTML content of the page
            html_content = await page.content()

            # Prepare the prompt for the LLM
            prompt = (
                "Given the following HTML content of a web page:\n\n"
                f"{html_content}\n\n"
                f"User request: '{user_message}'\n\n"
                "Provide the CSS selector that best matches the user's request. Return only the CSS selector."
            )

            # Use the LLM client to generate the selector
            llm_response: LLMResponse = await self.llm_client.invoke_with_prompt(prompt)
            selector: str = llm_response.content

            # Return the selector
            return selector.strip()

        @self.mcp.tool()
        async def fetch_jira_story(jira_key: str) -> str:
            """Fetch Jira story description by ticket key."""
            try:
                # Get configuration
                base_url = self.jira_config["base_url"]
                jira_email = self.jira_config["email"]
                api_token = self.jira_config["api_token"]

                if not all([base_url, jira_email, api_token]):
                    missing_vars = []
                    if not base_url:
                        missing_vars.append("JIRA_BASE_URL")
                    if not jira_email:
                        missing_vars.append("JIRA_EMAIL")
                    if not api_token:
                        missing_vars.append("JIRA_API_TOKEN")

                    return f"❌ Missing environment variables: {', '.join(missing_vars)}\nMake sure these are set in your .env file."

                # Construct URL
                url = f"{base_url}/rest/api/2/issue/{jira_key}"

                # Set up headers
                headers = {
                    "Authorization": f"Bearer {api_token}",
                    "Accept": "application/json",
                }

                # Make the request
                response = requests.get(url, headers=headers, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    # Extract only the description
                    description = data.get("fields", {}).get(
                        "description", "No description available"
                    )

                    return description

                elif response.status_code == 401:
                    return (
                        f"❌ Authentication failed. Please check your JIRA_API_TOKEN."
                    )
                elif response.status_code == 404:
                    return f"❌ Jira ticket {jira_key} not found."
                else:
                    return f"❌ Failed to fetch Jira story. Status: {response.status_code}, Response: {response.text}"

            except requests.exceptions.Timeout:
                return f"❌ Request timed out while fetching {jira_key}"
            except requests.exceptions.ConnectionError:
                return (
                    f"❌ Connection error. Please check your JIRA_BASE_URL: {base_url}"
                )
            except Exception as e:
                return f"❌ Error fetching Jira story {jira_key}: {str(e)}"

        @self.mcp.tool()
        async def generate_playwright_script(
            script_name: str,
            url: str,
            actions: List[dict] = [],
            description: str = "",
            headless: bool = False,
        ) -> str:
            """Generate a Playwright test script in TypeScript.

            Args:
                script_name: Name for the script file (without extension)
                url: The URL to navigate to in the test
                actions: List of actions to perform (click, fill, etc)
                description: Description of what the test does
                headless: Whether to run browser in headless mode

            Returns:
                Path to the generated script file
            """
            try:
                # Ensure the generated_scripts directory exists
                scripts_dir = parent_dir / "generated_scripts"
                scripts_dir.mkdir(exist_ok=True)

                # Sanitize script name (remove spaces, special chars)
                script_name = "".join(c if c.isalnum() else "_" for c in script_name)

                # Create the full file path
                script_path = scripts_dir / f"{script_name}.spec.ts"

                # Default actions if none provided
                if not actions:
                    actions = [
                        {"type": "navigate", "url": url},
                        {"type": "screenshot", "name": "page_loaded"},
                    ]

                # Generate the TypeScript code
                current_date = datetime.now().strftime("%Y-%m-%d")

                typescript_code = f"""
// {script_name}.ts
// Generated on: {current_date}
// Description: {description}

import {{ test, expect }} from '@playwright/test';

test('{script_name}', async ({{ page }}) => {{
  // Test configuration
  const headless = {str(headless).lower()};

  console.log('Starting test: {script_name}');

  try {{
"""

                # Add actions to the script
                indent = "    "  # Base indentation level

                # Process each action and add to the script
                for i, action in enumerate(actions):
                    action_type = action.get("type", "").lower()

                    # Navigate action
                    if action_type == "navigate":
                        action_url = action.get("url", url)
                        typescript_code += (
                            f"{indent}// Navigate to URL\n"
                            f"{indent}console.log('Navigating to {action_url}');\n"
                            f"{indent}await page.goto('{action_url}', {{ waitUntil: 'networkidle' }});\n"
                            f"{indent}console.log('Navigation complete');\n\n"
                        )

                    # Click action
                    elif action_type == "click":
                        selector = action.get("selector", "")
                        typescript_code += (
                            f"{indent}// Click element\n"
                            f"{indent}console.log('Clicking on {selector}');\n"
                            f"{indent}await page.waitForSelector('{selector}', {{ state: 'visible' }});\n"
                            f"{indent}await page.click('{selector}');\n\n"
                        )

                    # Fill form field action
                    elif action_type == "fill":
                        selector = action.get("selector", "")
                        value = action.get("value", "")
                        typescript_code += (
                            f"{indent}// Fill form field\n"
                            f"{indent}console.log('Filling {selector} with value');\n"
                            f"{indent}await page.waitForSelector('{selector}', {{ state: 'visible' }});\n"
                            f"{indent}await page.fill('{selector}', '{value}');\n\n"
                        )

                    # Screenshot action
                    elif action_type == "screenshot":
                        name = action.get("name", f"screenshot_{i}")
                        typescript_code += (
                            f"{indent}// Take screenshot\n"
                            f"{indent}console.log('Taking screenshot: {name}');\n"
                            f"{indent}await page.screenshot({{ path: './screenshots/{name}.png', fullPage: true }});\n\n"
                        )

                    # Select dropdown option action
                    elif action_type == "select":
                        selector = action.get("selector", "")
                        value = action.get("value", "")
                        select_log = f"Selecting {value} from {selector}"
                        # Break up long lines for select options
                        comment = f"{indent}// Select dropdown option"
                        log_line = f"{indent}console.log('{select_log}');"
                        typescript_code += f"{comment}\n{log_line}\n"
                        typescript_code += (
                            f"{indent}await page.selectOption('{selector}', "
                            f"'{value}');\n\n"
                        )

                    # Wait timeout action
                    elif action_type == "wait":
                        timeout = action.get("timeout", 1000)
                        wait_log = f"Waiting for {timeout}ms"
                        comment = f"{indent}// Wait for specified timeout"
                        log_line = f"{indent}console.log('{wait_log}');"
                        timeout_cmd = f"await page.waitForTimeout({timeout});"
                        timeout_line = f"{indent}{timeout_cmd}"
                        typescript_code += f"{comment}\n"
                        typescript_code += f"{log_line}\n"
                        typescript_code += f"{timeout_line}\n\n"

                    # Expect assertion action
                    elif action_type == "expect":
                        selector = action.get("selector", "")
                        assertion = action.get("assertion", "toBeVisible")
                        expect_log = f"Expecting {selector} to {assertion}"
                        typescript_code += f"{indent}// Assert element state\n"
                        log_cmd = f"console.log('{expect_log}');"
                        typescript_code += f"{indent}{log_cmd}\n"
                        typescript_code += (
                            f"{indent}await expect(page.locator('{selector}'))"
                            f".{assertion}();\n\n"
                        )

                # Add closing parts of the test
                failure_ss = f"./screenshots/{script_name}_failure.png"
                completed_msg = f"Test completed successfully: {script_name}"
                typescript_code += (
                    f"  }} catch (error) {{\n"
                    f"    console.error(`Test failed: ${{error}}`);\n"
                    f"    // Take screenshot on failure\n"
                    f"    await page.screenshot({{\n"
                    f"      path: '{failure_ss}',\n"
                    f"      fullPage: true\n"
                    f"    }});\n"
                    f"    throw error;\n"
                    f"  }}\n"
                    f"  \n"
                    f"  console.log('{completed_msg}');\n"
                    f"}});\n"
                )

                # Create the playwright.config.ts file if it doesn't exist
                config_path = scripts_dir / "playwright.config.ts"
                if not config_path.exists():
                    config_code = """
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  outputDir: 'test-results/',
});
"""
                    with open(config_path, "w") as config_file:
                        config_file.write(config_code)

                # Create a README file with instructions if it doesn't exist
                readme_path = scripts_dir / "README.md"
                if not readme_path.exists():
                    readme_content = """# Generated Playwright Test Scripts

This directory contains automatically generated Playwright test scripts.

## Running Tests

To run the tests:

1. Make sure you have Playwright installed:
   ```
   npm install -g @playwright/test
   ```

2. Install browsers:
   ```
   npx playwright install
   ```

3. Run a specific test:
   ```
   npx playwright test script-name.ts
   ```

4. Run all tests:
   ```
   npx playwright test
   ```

## Generating Package Files

If you don't have a `package.json` file yet, create one with:

```
npm init -y
npm install -D @playwright/test
```

## Test Structure

Each test follows a similar pattern:
- Navigate to the target URL
- Perform a series of actions (clicks, form filling, etc.)
- Take screenshots at key points
- Include assertions to verify the expected state
"""
                    with open(readme_path, "w") as readme_file:
                        readme_file.write(readme_content)

                # Create the test script file
                with open(script_path, "w") as script_file:
                    script_file.write(typescript_code)

                # Generate package.json if it doesn't exist
                package_path = scripts_dir / "package.json"
                if not package_path.exists():
                    package_json = """{
  "name": "generated-playwright-tests",
  "version": "1.0.0",
  "description": "Auto-generated Playwright tests",
  "main": "index.js",
  "scripts": {
    "test": "playwright test"
  },
  "keywords": [
    "playwright",
    "testing",
    "automation"
  ],
  "devDependencies": {
    "@playwright/test": "^1.40.0"
  }
}
"""
                    with open(package_path, "w") as package_file:
                        package_file.write(package_json)

                success_msg = "✅ Generated Playwright TypeScript test script:"
                return f"{success_msg} {script_path}"

            except Exception as e:
                return f"❌ Error generating Playwright script: {str(e)}"

    def register_resources(self):
        @self.mcp.resource("console://logs")
        async def get_console_logs() -> TextContent:
            """Return browser console logs."""
            return TextContent(
                type="text", text="\n".join(self.browser_manager.console_logs)
            )

        @self.mcp.resource("screenshot://{name}")
        async def get_screenshot(name: str) -> str:
            """Get a screenshot by name"""
            screenshot_base64 = self.screenshots.get(name)
            if screenshot_base64:
                return screenshot_base64
            else:
                raise ValueError(f"Screenshot {name} not found")

    def register_prompts(self):
        """Register prompt handlers for the server."""
        @self.mcp.prompt()
        async def hello_world(code: str) -> str:
            return f"Hello world:\n\n{code}"


def create_app():
    """Create and return the BrowserNavigationServer instance"""
    return BrowserNavigationServer()


# Only create app when explicitly requested
app = None

if __name__ == "__main__":
    import asyncio

    async def main():
        # Start the server
        server = BrowserNavigationServer()
        print("Browser Navigation Server started!")

        # Initialize browser upfront to ensure it's ready
        try:
            print("Pre-initializing browser to ensure it's ready for tests...")
            page = await server.browser_manager.ensure_browser()
            if page:
                print("✅ Browser initialized successfully!")
                await page.goto("about:blank")
                print("✅ Browser navigation test successful")
                # Take a test screenshot
                screenshots_dir = parent_dir / "screenshots"
                screenshots_dir.mkdir(exist_ok=True)
                test_screenshot = await page.screenshot(type="png")
                test_path = screenshots_dir / "server_start_test.png"
                with open(test_path, "wb") as f:
                    f.write(test_screenshot)
                print(f"✅ Test screenshot saved to: {test_path}")
            else:
                print("❌ Failed to initialize browser - check Playwright installation")
        except Exception as e:
            print(f"❌ Error during browser initialization: {str(e)}")

        print("Server is ready to accept MCP connections...")

        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")

    asyncio.run(main())
