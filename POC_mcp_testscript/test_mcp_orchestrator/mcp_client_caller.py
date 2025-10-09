import asyncio
import json
import re
import os
import sys
import argparse
from pathlib import Path
from loguru import logger

# Configure logger to only show warnings and errors by default
# Set up a function to configure logging levels


def setup_logger(verbose=False):
    """Configure the logger with appropriate verbosity level."""
    logger.remove()  # Remove existing handlers
    if verbose:
        logger.add(sys.stderr, level="INFO")
    else:
        log_level = "DEBUG" if os.getenv("DEBUG", "0") == "1" else "WARNING"
        logger.add(sys.stderr, level=log_level)


# Set default logging level
setup_logger(False)

# Add the current directory to sys.path so Python can find the modules
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Now we can import the modules from the parent directory
# noqa: E402 (imports not at top of file)
from server.browser_navigator_server import BrowserNavigationServer
from client_bridge.mcp_client import MCPClient


async def execute_jira(jira_key, debug=False, verbose=False):
    """
    Execute a workflow that fetches a JIRA story and uses browser automation
    tools based on the story.

    Args:
        jira_key: The JIRA ticket key (e.g., "TEST-1234")
        debug: Whether to output detailed information about available tools
        verbose: Whether to show all log messages regardless of global setting

    Returns:
        A dictionary containing the results of the JIRA workflow execution
    """
    # Configure logger based on verbosity setting
    setup_logger(verbose)

    # Create an MCP server instance
    server = BrowserNavigationServer()

    # Create an MCP client that connects to the server
    mcp_client = MCPClient(server)

    results = {"jira_key": jira_key, "status": "started", "steps": []}

    try:
        logger.info(f"Connecting to MCP server for JIRA ticket {jira_key}...")
        await mcp_client.connect()
        results["steps"].append({"step": "connect", "status": "success"})

        # Get available tools
        logger.info("Fetching available tools...")
        tools = await mcp_client.get_available_tools()
        results["steps"].append(
            {"step": "get_tools", "status": "success", "count": len(tools)}
        )

        if debug:
            logger.info(f"Found {len(tools)} available tools:")
            for i, tool in enumerate(tools):
                logger.info(f"{i+1}. {tool.name}: {tool.description}")
                if hasattr(tool, "inputSchema"):
                    logger.info(f"   Schema: {tool.inputSchema}")

        # Step 3: Fetch the JIRA story using the fetch_jira_story tool
        logger.info(f"Fetching JIRA story for {jira_key}...")
        jira_result = await mcp_client.call_tool(
            "fetch_jira_story", {"jira_key": jira_key}
        )
        results["steps"].append({"step": "fetch_jira_story", "status": "success"})

        if debug:
            logger.info(f"JIRA Story: {jira_result}")

        # Extract text content from JIRA result
        # Format: content=[TextContent(type='text', text='content here', ...)]
        jira_text = ""
        jira_json = {"story": jira_key, "steps": []}  # Initialize with default

        try:
            # Using regex to extract text between text='...' pattern
            pattern = r"text=['\"]([^'\"]+)['\"]"
            text_pattern = re.search(pattern, str(jira_result))
            if text_pattern:
                jira_text = text_pattern.group(1)

                # Convert the raw text to structured JSON
                steps = []

                # Split by both \r\n and \\r\\n patterns
                raw_lines = jira_text.replace("\\r\\n", "\n").split("\n")

                for line in raw_lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Remove leading '# ' if present
                    if line.startswith("# "):
                        line = line[2:].strip()
                    elif line.startswith("#"):
                        line = line[1:].strip()

                    # Clean up special characters
                    line = line.replace("\\xa0", " ").strip()

                    # Remove brackets from URLs but keep the URL
                    if line.startswith("Navigate to [") and line.endswith("]"):
                        line = line.replace("Navigate to [", "Navigate to ").rstrip("]")

                    # Add non-empty lines as steps
                    if line:
                        steps.append({"instruction": line})

                # Create a formatted JSON structure
                jira_json = {"story": jira_key, "steps": steps}

                # Store both the raw text and structured JSON in results
                results["jira_description"] = jira_text
                results["jira_json"] = jira_json

                if debug:
                    logger.info(f"Extracted JIRA text: {jira_text}")
                    json_str = json.dumps(jira_json, indent=2)
                    logger.info(f"Formatted JIRA JSON: {json_str}")
        except Exception as e:
            logger.error(f"Error parsing JIRA result: {e}")
            results["jira_description"] = str(jira_result)
            jira_text = str(jira_result)

        # Check if the JIRA description contains a URL to navigate to
        url = None
        try:
            # Look for URLs in the extracted text
            url_match = re.search(r"https?://[^\s]+", jira_text)
            if url_match:
                url = url_match.group(0)
                # Remove any trailing characters that aren't part of the URL
                if url.endswith("\\"):
                    url = url[:-1]
                # Check for common end-of-url markers
                for char in ['"', "'", ")", "]", "}", ",", ";"]:
                    if char in url:
                        url = url.split(char)[0]
        except Exception as e:
            logger.warning(f"Error extracting URL: {e}")

        # If we found a URL, navigate to it
        if url:
            logger.info(f"Navigating to URL: {url}")
            navigate_result = await mcp_client.call_tool(
                "playwright_navigate", {"url": url}
            )
            results["steps"].append(
                {"step": "playwright_navigate", "status": "success", "url": url}
            )

            if debug:
                logger.info(f"Navigation result: {navigate_result}")

            # Take a screenshot
            screenshot_name = f"{jira_key}_screenshot"
            screenshot_result = await mcp_client.call_tool(
                "playwright_screenshot", {"name": screenshot_name}
            )
            results["steps"].append(
                {
                    "step": "playwright_screenshot",
                    "status": "success",
                    "name": screenshot_name,
                }
            )

            if debug:
                logger.info(f"Screenshot saved as {screenshot_name}.png")

            # Execute the actual JIRA instructions instead of hardcoded ones
            await execute_jira_instructions(mcp_client, results, jira_json, debug)
        else:
            logger.warning(f"No URL found in JIRA description for {jira_key}")
            results["steps"].append(
                {
                    "step": "url_extraction",
                    "status": "failure",
                    "message": "No URL found in JIRA description",
                }
            )

        # Generate Playwright script from the actions performed
        try:
            logger.info(f"Generating Playwright script for {jira_key}...")

            # Collect all the actions performed during the test
            actions = []

            # Add a navigate action if URL was found
            if url:
                actions.append({"type": "navigate", "url": url})

                # Add actions based on the steps we performed
                for step in results["steps"]:
                    # Handle click actions
                    if step["step"] == "playwright_click" and "selector" in step:
                        actions.append({"type": "click", "selector": step["selector"]})
                    # Handle fill actions
                    elif (
                        step["step"] == "playwright_fill"
                        and "selector" in step
                        and "value" in step
                    ):
                        actions.append(
                            {
                                "type": "fill",
                                "selector": step["selector"],
                                "value": step.get("value", "test_value"),
                            }
                        )
                    # Handle hover actions (convert to click for script)
                    elif step["step"] == "playwright_hover" and "selector" in step:
                        # Convert hover to click for script compatibility
                        actions.append({"type": "click", "selector": step["selector"]})
                    # Handle select actions
                    elif (
                        step["step"] == "playwright_select"
                        and "selector" in step
                        and "value" in step
                    ):
                        actions.append(
                            {
                                "type": "select",
                                "selector": step["selector"],
                                "value": step.get("value", "option1"),
                            }
                        )

                # Add a final screenshot action
                screenshot_name = f"{jira_key}_final"
                actions.append({"type": "screenshot", "name": screenshot_name})

                # Call the generate_playwright_script tool
                desc = f"Automated test for JIRA {jira_key}"
                script_params = {
                    "script_name": f"{jira_key}_test_script",
                    "url": url,
                    "actions": actions,
                    "description": desc,
                    "headless": False,
                }

                script_result = await mcp_client.call_tool(
                    "generate_playwright_script", script_params
                )

                results["steps"].append(
                    {
                        "step": "generate_playwright_script",
                        "status": "success",
                        "script_name": script_params["script_name"],
                    }
                )

                if debug:
                    result_preview = str(script_result)[:60]
                    logger.info(f"Script generation result: {result_preview}...")

                # Store the script generation result
                results["playwright_script"] = str(script_result)
            else:
                logger.warning(
                    f"Skipping script generation - no URL found for {jira_key}"
                )
        except Exception as e:
            logger.error(f"Error generating Playwright script: {e}")
            results["steps"].append(
                {
                    "step": "generate_playwright_script",
                    "status": "error",
                    "error": str(e),
                }
            )

        # Mark the overall workflow as completed successfully
        results["status"] = "completed"
        return results

    except Exception as e:
        logger.error(f"Error executing JIRA workflow: {e}", exc_info=True)
        results["status"] = "error"
        results["error"] = str(e)
        return results


async def execute_jira_instructions(mcp_client, results, jira_json, debug=False):
    """
    Parse and execute the actual JIRA instructions dynamically.

    Args:
        mcp_client: The MCP client instance
        results: The results dictionary to append steps to
        jira_json: The parsed JIRA JSON containing structured steps
        debug: Whether to output debug information
    """
    # Get the steps from the parsed JSON
    if isinstance(jira_json, dict) and "steps" in jira_json:
        instructions = [step["instruction"] for step in jira_json["steps"]]
    else:
        # Fallback to old parsing method if JSON format is different
        instructions = str(jira_json).replace("\\r\\n", "\n").split("\n")

    for i, instruction in enumerate(instructions):
        instruction = instruction.strip()
        if not instruction:
            continue

        logger.info(f"Executing instruction {i+1}: {instruction}")

        try:
            # Parse different types of instructions
            if (
                "take a screenshot" in instruction.lower()
                or "take the screenshot" in instruction.lower()
            ):
                # Take screenshot
                screenshot_name = f"step_{i+1}_screenshot"
                await mcp_client.call_tool(
                    "playwright_screenshot", {"name": screenshot_name}
                )
                results["steps"].append(
                    {
                        "step": "playwright_screenshot",
                        "status": "success",
                        "name": screenshot_name,
                        "instruction": instruction,
                    }
                )
                if debug:
                    logger.info(f"Screenshot taken: {screenshot_name}.png")

            elif "click" in instruction.lower():
                # Extract what to click on
                click_target = extract_click_target(instruction)
                if click_target:
                    # Use MCP tool to find the element
                    selector_query = f"find the {click_target}"
                    params = {"user_message": selector_query}
                    selector_result = await mcp_client.call_tool(
                        "extract_selector_by_page_content", params
                    )

                    # Extract selector from result
                    selector_text = extract_selector_from_result(selector_result)

                    if selector_text and not selector_text.startswith("Error"):
                        await mcp_client.call_tool(
                            "playwright_click", {"selector": selector_text}
                        )
                        results["steps"].append(
                            {
                                "step": "playwright_click",
                                "status": "success",
                                "selector": selector_text,
                                "instruction": instruction,
                                "target": click_target,
                            }
                        )
                        if debug:
                            logger.info(f"Clicked on: {click_target}")
                    else:
                        logger.warning(
                            f"Could not find element to click: {click_target}"
                        )
                        results["steps"].append(
                            {
                                "step": "playwright_click",
                                "status": "failed",
                                "instruction": instruction,
                                "target": click_target,
                                "error": "Element not found",
                            }
                        )

            elif "check for" in instruction.lower():
                # This is a verification step - take screenshot and log
                verification_target = extract_verification_target(instruction)
                logger.info(f"Checking for: {verification_target}")

                # Take a screenshot for verification
                screenshot_name = f"verification_step_{i+1}"
                await mcp_client.call_tool(
                    "playwright_screenshot", {"name": screenshot_name}
                )
                results["steps"].append(
                    {
                        "step": "verification_screenshot",
                        "status": "success",
                        "name": screenshot_name,
                        "instruction": instruction,
                        "verification_target": verification_target,
                    }
                )
                if debug:
                    logger.info(f"Verification screenshot: {screenshot_name}.png")

            elif "navigate to" in instruction.lower():
                # Navigation instruction - extract URL and navigate
                url_match = re.search(r"https?://[^\s\]]+", instruction)
                if url_match:
                    nav_url = url_match.group(0)
                    logger.info(f"Navigating to: {nav_url}")
                    await mcp_client.call_tool("playwright_navigate", {"url": nav_url})
                    results["steps"].append(
                        {
                            "step": "playwright_navigate",
                            "status": "success",
                            "url": nav_url,
                            "instruction": instruction,
                        }
                    )
                    if debug:
                        logger.info(f"Navigated to: {nav_url}")

        except Exception as e:
            logger.error(f"Error executing instruction '{instruction}': {e}")
            results["steps"].append(
                {
                    "step": "instruction_execution",
                    "status": "error",
                    "instruction": instruction,
                    "error": str(e),
                }
            )


def extract_click_target(instruction):
    """Extract what element to click from the instruction text."""
    instruction_lower = instruction.lower()

    # Common patterns for click instructions
    if "sign in" in instruction_lower:
        return "sign in button"
    elif "microsoft account" in instruction_lower:
        return "Microsoft Account button"
    elif "login" in instruction_lower:
        return "login button"
    elif "submit" in instruction_lower:
        return "submit button"
    elif "click on" in instruction_lower:
        # Extract text after "click on"
        parts = instruction_lower.split("click on")
        if len(parts) > 1:
            return parts[1].strip()

    # Default extraction - try to find button-like words
    button_words = ["button", "link", "tab", "menu"]
    for word in instruction.split():
        for button_word in button_words:
            if button_word in word.lower():
                return word

    return None


def extract_verification_target(instruction):
    """Extract what to verify from the instruction text."""
    instruction_lower = instruction.lower()

    if "check for" in instruction_lower:
        parts = instruction_lower.split("check for")
        if len(parts) > 1:
            target = parts[1].strip()
            # Clean up common suffixes
            for suffix in [" and then", " then"]:
                if suffix in target:
                    target = target.split(suffix)[0]
            return target

    return instruction


def extract_selector_from_result(selector_result):
    """Extract the actual selector from MCP tool result."""
    try:
        # Check if structuredContent with result key exists
        has_content = hasattr(selector_result, "structuredContent")
        has_result = False
        if has_content and selector_result.structuredContent:
            has_result = "result" in selector_result.structuredContent

        # Extract selector text
        if has_content and has_result:
            return selector_result.structuredContent["result"]
        else:
            # Try to extract from TextContent using regex pattern
            result_str = str(selector_result)
            pattern = r"text=['\"]([^'\"]+)['\"]"
            text_pattern = re.search(pattern, result_str)
            if text_pattern:
                return text_pattern.group(1)
    except Exception as e:
        logger.warning(f"Could not extract selector: {e}")

    return None


if __name__ == "__main__":
    try:
        # Set up command line arguments
        parser = argparse.ArgumentParser(description="Execute JIRA automation workflow")
        parser.add_argument(
            "--jira",
            dest="jira_key",
            help="JIRA ticket key",
            default=os.getenv("JIRA_KEY", ""),
        )
        parser.add_argument(
            "--debug", action="store_true", help="Enable debug information"
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose logging"
        )
        args = parser.parse_args()

        # Run with command line arguments
        asyncio.run(
            execute_jira(jira_key=args.jira_key, debug=args.debug, verbose=args.verbose)
        )
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
