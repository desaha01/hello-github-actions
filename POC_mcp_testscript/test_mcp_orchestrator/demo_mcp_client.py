"""
Standalone demo version of mcp_client_caller.py
This version works without external dependencies to demonstrate functionality.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Mock logger
class MockLogger:
    def __init__(self):
        pass
    
    def remove(self):
        pass
    
    def add(self, *args, **kwargs):
        pass
    
    def info(self, msg):
        print(f"ℹ️  INFO: {msg}")
    
    def error(self, msg, **kwargs):
        print(f"❌ ERROR: {msg}")
    
    def debug(self, msg):
        print(f"🔍 DEBUG: {msg}")

logger = MockLogger()

def setup_logger(verbose=False):
    """Configure the logger with appropriate verbosity level."""
    logger.remove()
    if verbose:
        logger.add(sys.stderr, level="INFO")
    else:
        log_level = "DEBUG" if os.getenv("DEBUG", "0") == "1" else "WARNING"
        logger.add(sys.stderr, level=log_level)

# Mock classes
class MockTool:
    def __init__(self, name, description, schema=None):
        self.name = name
        self.description = description
        self.inputSchema = schema or {"type": "object", "properties": {}, "required": []}

class MockBrowserNavigationServer:
    def __init__(self):
        pass

class MockMCPClient:
    def __init__(self, server):
        self.server = server
        self.tools = [
            MockTool("playwright_navigate", "Navigate to a URL"),
            MockTool("playwright_screenshot", "Take screenshot of page or element"),
            MockTool("playwright_click", "Click on element"),
            MockTool("playwright_type", "Type text into element"),
            MockTool("fetch_jira_story", "Fetch JIRA story content"),
            MockTool("generate_playwright_script", "Generate Playwright test script"),
            MockTool("chat_with_llm", "Chat with LLM for automation guidance"),
            MockTool("save_file", "Save generated content to file")
        ]
    
    async def connect(self):
        logger.info("Connected to MCP server successfully")
    
    async def get_available_tools(self):
        logger.debug(f"Received tools from MCP server")
        return self.tools
    
    async def call_tool(self, tool_name, arguments):
        logger.debug(f"Tool '{tool_name}' called with arguments: {arguments}")
        
        if tool_name == "fetch_jira_story":
            jira_key = arguments.get("jira_key", "UNKNOWN")
            # Mock JIRA content
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"""
JIRA Story: {jira_key}
Title: Automate User Login Flow
Description: Create automated tests for the user login functionality

Steps to automate:
1. Navigate to https://example.com/login
2. Enter username: testuser@example.com  
3. Enter password: testpassword123
4. Click the "Sign In" button
5. Verify successful login by checking for welcome message
6. Take screenshot of logged-in state

Acceptance Criteria:
- Test should run in Chrome browser
- Should handle login failures gracefully
- Must capture screenshots at key steps
- Generate reusable Playwright test script
                        """
                    }
                ]
            }
        
        elif tool_name == "playwright_navigate":
            url = arguments.get("url", "unknown")
            return f"✅ Navigated to {url}"
        
        elif tool_name == "playwright_screenshot":
            name = arguments.get("name", "screenshot")
            return f"📸 Screenshot saved as {name}.png"
        
        elif tool_name == "playwright_click":
            selector = arguments.get("selector", "button")
            return f"👆 Clicked on element: {selector}"
        
        elif tool_name == "generate_playwright_script":
            return {
                "script_path": "generated_scripts/login_automation.spec.ts",
                "content": """// Generated Playwright Test Script
import { test, expect } from '@playwright/test';

test('User Login Automation', async ({ page }) => {
  // Navigate to login page
  await page.goto('https://example.com/login');
  
  // Fill login form
  await page.fill('[data-testid="username"]', 'testuser@example.com');
  await page.fill('[data-testid="password"]', 'testpassword123');
  
  // Click sign in button
  await page.click('[data-testid="sign-in-button"]');
  
  // Verify successful login
  await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  
  // Take screenshot
  await page.screenshot({ path: 'login-success.png', fullPage: true });
});"""
            }
        
        else:
            return f"✅ Tool '{tool_name}' executed successfully"

async def execute_jira(jira_key, debug=False, verbose=False):
    """Execute a workflow that fetches a JIRA story and uses browser automation."""
    setup_logger(verbose)
    
    # Create mock instances
    server = MockBrowserNavigationServer()
    mcp_client = MockMCPClient(server)
    
    results = {"jira_key": jira_key, "status": "started", "steps": []}
    
    try:
        print(f"🎯 Starting JIRA automation workflow for ticket: {jira_key}")
        print("=" * 60)
        
        logger.info(f"Connecting to MCP server for JIRA ticket {jira_key}...")
        await mcp_client.connect()
        results["steps"].append({"step": "connect", "status": "success"})
        
        logger.info("Fetching available tools...")
        tools = await mcp_client.get_available_tools()
        results["steps"].append({"step": "get_tools", "status": "success", "count": len(tools)})
        
        if debug:
            logger.info(f"Found {len(tools)} available tools:")
            for i, tool in enumerate(tools):
                logger.info(f"{i+1}. {tool.name}: {tool.description}")
        
        logger.info(f"Fetching JIRA story for {jira_key}...")
        jira_result = await mcp_client.call_tool("fetch_jira_story", {"jira_key": jira_key})
        results["steps"].append({"step": "fetch_jira_story", "status": "success"})
        
        if debug:
            logger.info(f"JIRA Story content received")
        
        # Extract and parse JIRA content
        jira_text = jira_result["content"][0]["text"]
        print(f"📋 JIRA Story Content:")
        print("-" * 40)
        print(jira_text)
        print("-" * 40)
        
        # Execute automation steps
        automation_steps = [
            ("playwright_navigate", {"url": "https://example.com/login"}),
            ("playwright_screenshot", {"name": "before_login"}),
            ("playwright_click", {"selector": "[data-testid='username']"}),
            ("playwright_type", {"selector": "[data-testid='username']", "text": "testuser@example.com"}),
            ("playwright_type", {"selector": "[data-testid='password']", "text": "testpassword123"}),
            ("playwright_click", {"selector": "[data-testid='sign-in-button']"}),
            ("playwright_screenshot", {"name": "after_login"}),
            ("generate_playwright_script", {"test_name": "login_automation", "steps": "login_flow"})
        ]
        
        print(f"\n🤖 Executing {len(automation_steps)} automation steps:")
        print("-" * 50)
        
        for i, (tool_name, args) in enumerate(automation_steps, 1):
            print(f"Step {i}: {tool_name}")
            result = await mcp_client.call_tool(tool_name, args)
            if isinstance(result, dict) and "script_path" in result:
                print(f"   📝 Generated script: {result['script_path']}")
                if verbose:
                    print(f"   📄 Script content preview:")
                    print("   " + "\n   ".join(result["content"].split("\n")[:10]) + "...")
            else:
                print(f"   {result}")
            results["steps"].append({"step": tool_name, "status": "success"})
        
        results["status"] = "completed"
        results["total_steps"] = len(automation_steps)
        results["execution_time"] = "23.4 seconds"
        
        print("\n" + "=" * 60)
        print("✅ Workflow completed successfully!")
        print(f"📊 Summary:")
        print(f"   • JIRA Key: {jira_key}")
        print(f"   • Steps Executed: {results['total_steps']}")
        print(f"   • Status: {results['status']}")
        print(f"   • Execution Time: {results['execution_time']}")
        print(f"   • Screenshots: 2 (before_login.png, after_login.png)")
        print(f"   • Generated Script: login_automation.spec.ts")
        
        return results
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="MCP Client Caller - JIRA and Browser Automation Demo")
    parser.add_argument("--jira", type=str, default="DEMO-123", help="JIRA ticket key (e.g., TEST-1234)")
    parser.add_argument("--debug", action="store_true", help="Show debug information about available tools")
    parser.add_argument("--verbose", action="store_true", help="Show all log messages")
    
    args = parser.parse_args()
    
    print("🚀 MCP Client Caller Demo (Standalone Version)")
    print("⚠️  Note: This is a demo version that works without external dependencies")
    print()
    
    import asyncio
    results = asyncio.run(execute_jira(args.jira, args.debug, args.verbose))
    
    if results["status"] == "completed":
        print(f"\n🎉 Demo completed successfully!")
        return 0
    else:
        print(f"\n❌ Demo failed: {results.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())