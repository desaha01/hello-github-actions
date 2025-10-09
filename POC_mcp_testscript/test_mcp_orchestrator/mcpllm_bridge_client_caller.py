import asyncio
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
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

# Add the parent directory to sys.path so Python can find the modules
parent_dir = Path(__file__).parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import necessary components after setting up path
# noqa: E402 (imports not at top of file)
from server.browser_navigator_server import BrowserNavigationServer
from client_bridge.config import BridgeConfig, LLMConfig
from client_bridge.bridge import MCPLLMBridge
from prompts.system_prompts import get_browser_automation_system_prompt
from prompts.automation_prompts import create_automation_prompt


async def setup_bridge(debug=False, verbose=False):
    """
    Set up a bridge configuration between MCP server and an LLM agent.

    Args:
        debug: Whether to output detailed information about available tools
        verbose: Whether to show all log messages regardless of global setting

    Returns:
        A configured MCPLLMBridge instance if successful, None otherwise
    """
    # Configure logger based on verbosity setting
    setup_logger(verbose)

    # Load environment variables from .env file if present
    load_dotenv()

    # Create an MCP server instance (BrowserNavigationServer)
    server = BrowserNavigationServer()

    # Get required LLM configuration variables from environment
    azure_endpoint = os.getenv("AZURE_OPEN_AI_ENDPOINT", "")
    api_version = os.getenv("AZURE_OPEN_AI_API_VERSION", "")
    api_key = os.getenv("AZURE_OPEN_AI_API_KEY", "")
    deploy_name = os.getenv("AZURE_OPEN_AI_DEPLOYMENT_MODEL", "")

    if not all([azure_endpoint, api_version, api_key, deploy_name]):
        logger.error(
            "Missing required Azure OpenAI configuration. "
            "Please check environment variables."
        )
        return None

    # Set up LLM configuration with Azure OpenAI settings
    llm_config = LLMConfig(
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        api_key=api_key,
        deploy_name=deploy_name,
    )

    # Create system prompt for the LLM
    system_prompt = get_browser_automation_system_prompt()

    # Create bridge configuration
    bridge_config = BridgeConfig(
        mcp=server, llm_config=llm_config, system_prompt=system_prompt
    )

    # Create bridge instance
    bridge = MCPLLMBridge(bridge_config)

    try:
        # Initialize the bridge
        logger.info("Initializing MCP-LLM bridge...")
        success = await bridge.initialize()

        if not success:
            logger.error("Bridge initialization failed")
            return None

        logger.info("Bridge initialized successfully!")

        # List available tools if debug is True
        if debug:
            logger.info(f"Available tools ({len(bridge.available_tools)}):")
            for i, tool in enumerate(bridge.available_tools):
                logger.info(f"{i+1}. {tool.name}: {tool.description}")
                if hasattr(tool, "inputSchema"):
                    logger.info(f"   Schema: {tool.inputSchema}")

        return bridge

    except Exception as e:
        logger.error(f"Error setting up bridge: {e}", exc_info=True)
        return None


async def process_user_request(bridge, user_query, debug=False):
    """
    Process a user query through the MCP-LLM bridge.

    Args:
        bridge: The configured MCPLLMBridge instance
        user_query: The user's query string
        debug: Whether to output debug information

    Returns:
        The LLM's response string
    """
    if not bridge:
        return "Bridge is not properly initialized. Cannot process request."

    try:
        if debug:
            logger.info(f"Processing user query: {user_query}")

        # Send the query through the bridge
        response = await bridge.process_message(user_query)

        if debug:
            logger.info("Response received from LLM")
        return response

    except Exception as e:
        logger.error(f"Error processing user request: {e}", exc_info=True)
        return f"Error processing your request: {str(e)}"


async def interactive_session(bridge, debug=False):
    """
    Run an interactive session with the user and the MCP-LLM bridge.

    Args:
        bridge: The configured MCPLLMBridge instance
        debug: Whether to output debug information
    """
    if not bridge:
        logger.error("Bridge not initialized")
        return

    print("\n=== MCP-LLM Bridge Interactive Session ===")
    print("Type 'exit' or 'quit' to end the session")
    print("\nExample commands:")
    print("- 'Help me automate JIRA ticket QAAR-6916'")
    print("- 'Navigate to amazon.com and generate a test script'")
    print("- 'Fetch JIRA story ABC-123 and automate the steps'")
    print("- 'Generate a Playwright script for login automation'")
    print("=" * 50)

    while True:
        # Get user input
        user_query = input("\nYou: ")

        # Exit condition
        if user_query.lower() in ["exit", "quit", "q"]:
            print("Ending session. Goodbye!")
            break

        # Process the query
        print("\nProcessing your request...")
        response = await process_user_request(bridge, user_query, debug)

        # Print the response
        print(f"\nAI: {response}")


async def main(jira_key="", debug=False, verbose=False, single_query=False):
    """
    Main function to set up the bridge and process queries.

    Args:
        jira_key: The JIRA ticket key (optional, for future integration)
        debug: Whether to output detailed information about available tools
        verbose: Whether to show all log messages regardless of global setting
        single_query: Whether to run a single test query instead of interactive mode
    """
    # Configure logger based on verbosity setting
    setup_logger(verbose)

    # Setup the bridge between MCP server and LLM agent
    bridge = await setup_bridge(debug=debug, verbose=verbose)

    if not bridge:
        logger.error("Failed to set up the MCP-LLM bridge")
        return

    # Process based on mode
    if single_query:
        # Create comprehensive prompt for automation and script generation
        test_query = create_automation_prompt(jira_key if jira_key else None)

        response = await process_user_request(bridge, test_query, debug)

        # Output the response
        logger.info(f"LLM Response: {response}")
    else:
        # Run interactive session
        await interactive_session(bridge, debug)


if __name__ == "__main__":
    try:
        # Set up command line arguments
        parser = argparse.ArgumentParser(
            description="Execute MCP-LLM bridge workflow"
        )
        parser.add_argument(
            "--jira",
            dest="jira_key",
            help="JIRA ticket key (optional)",
            default=os.getenv("JIRA_KEY", ""),
        )
        parser.add_argument(
            "--debug", action="store_true", help="Enable debug information"
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose logging"
        )
        parser.add_argument(
            "--single",
            action="store_true",
            help="Run single test query instead of interactive mode",
        )
        args = parser.parse_args()

        # Run with command line arguments
        asyncio.run(
            main(
                jira_key=args.jira_key,
                debug=args.debug,
                verbose=args.verbose,
                single_query=args.single,
            )
        )
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
