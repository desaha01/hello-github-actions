"""
Enhanced MCP Client Caller with Karate Integration
Supports both Playwright web automation and Karate API testing
"""
import asyncio
import json
import re
import os
import sys
import argparse
from pathlib import Path
from loguru import logger

# Configure logger
def setup_logger(verbose=False):
    """Configure the logger with appropriate verbosity level."""
    logger.remove()
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

# Import the unified orchestrator
try:
    from server.unified_test_orchestrator import UnifiedTestOrchestrator
    from client_bridge.mcp_client import MCPClient
    UNIFIED_MODE = True
except ImportError:
    # Fallback to original browser server
    from server.browser_navigator_server import BrowserNavigationServer
    from client_bridge.mcp_client import MCPClient
    UNIFIED_MODE = False
    logger.warning("Unified orchestrator not available, using browser-only mode")


async def execute_comprehensive_testing(
    jira_key: str, 
    test_types: list = None,
    debug: bool = False, 
    verbose: bool = False
):
    """
    Execute comprehensive testing workflow including web, API, and integration tests.

    Args:
        jira_key: The JIRA ticket key (e.g., "TEST-1234")
        test_types: List of test types to include ['web', 'api', 'performance', 'integration']
        debug: Whether to output detailed information about available tools
        verbose: Whether to show all log messages

    Returns:
        A dictionary containing the results of the comprehensive testing execution
    """
    # Configure logger based on verbosity setting
    setup_logger(verbose)

    if test_types is None:
        test_types = ['web', 'api', 'integration']

    # Create unified orchestrator or fallback server
    if UNIFIED_MODE:
        server = UnifiedTestOrchestrator()
        server_type = "Unified Test Orchestrator (Web + API + Integration)"
    else:
        server = BrowserNavigationServer()
        server_type = "Browser Navigation Server (Web Only)"

    # Create an MCP client that connects to the server
    mcp_client = MCPClient(server)

    results = {
        "jira_key": jira_key,
        "test_types": test_types,
        "server_type": server_type,
        "status": "started",
        "steps": []
    }

    try:
        logger.info(f"🚀 Starting comprehensive testing for JIRA ticket {jira_key}")
        logger.info(f"📋 Test types: {', '.join(test_types)}")
        logger.info(f"🔧 Server: {server_type}")
        logger.info("=" * 70)

        # Connect to MCP server
        logger.info("Connecting to MCP server...")
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
                logger.info(f"  {i+1}. {tool.name}: {tool.description}")

        if UNIFIED_MODE:
            # Use unified orchestrator capabilities
            await execute_unified_workflow(mcp_client, jira_key, test_types, results, debug, verbose)
        else:
            # Fallback to web-only workflow
            await execute_web_only_workflow(mcp_client, jira_key, results, debug, verbose)

        results["status"] = "completed"
        logger.info("🎉 Comprehensive testing workflow completed successfully!")

        return results

    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        return results


async def execute_unified_workflow(mcp_client, jira_key, test_types, results, debug, verbose):
    """Execute workflow using unified orchestrator."""
    
    logger.info("🔄 Generating comprehensive test suite from JIRA ticket...")
    
    # Generate comprehensive tests from JIRA
    generation_result = await mcp_client.call_tool(
        "generate_tests_from_jira_comprehensive",
        {
            "jira_key": jira_key,
            "include_web_tests": "web" in test_types,
            "include_api_tests": "api" in test_types,
            "include_performance_tests": "performance" in test_types,
            "auto_detect_test_types": True
        }
    )
    
    results["steps"].append({"step": "generate_comprehensive_tests", "status": "success", "result": generation_result})
    
    if debug:
        logger.info(f"📊 Test Generation Results:")
        if hasattr(generation_result, 'content') and generation_result.content:
            content = generation_result.content[0].text if generation_result.content else str(generation_result)
            logger.info(f"   {content}")

    # Create full-stack test suite
    logger.info("📦 Creating full-stack test suite...")
    
    suite_result = await mcp_client.call_tool(
        "create_full_stack_test_suite",
        {
            "suite_name": f"jira_{jira_key.lower()}_comprehensive",
            "jira_key": jira_key,
            "web_scenarios": [
                {
                    "name": "User Journey Test",
                    "steps": ["navigate", "login", "perform_actions", "logout"]
                }
            ] if "web" in test_types else [],
            "api_scenarios": [
                {
                    "name": "API Functionality Test",
                    "endpoints": [
                        {"method": "GET", "path": "/api/health", "status": 200},
                        {"method": "POST", "path": "/api/users", "status": 201}
                    ]
                }
            ] if "api" in test_types else [],
            "integration_flows": [
                {
                    "name": "End-to-End User Flow",
                    "description": "Complete user journey with API validation"
                }
            ] if "integration" in test_types else []
        }
    )
    
    results["steps"].append({"step": "create_test_suite", "status": "success", "result": suite_result})

    # Execute the test suite
    logger.info("🧪 Executing comprehensive test suite...")
    
    execution_result = await mcp_client.call_tool(
        "execute_full_stack_test_suite",
        {
            "suite_name": f"jira_{jira_key.lower()}_comprehensive",
            "run_web_tests": "web" in test_types,
            "run_api_tests": "api" in test_types,
            "run_integration_tests": "integration" in test_types,
            "parallel_execution": len(test_types) > 1,
            "generate_unified_report": True
        }
    )
    
    results["steps"].append({"step": "execute_test_suite", "status": "success", "result": execution_result})

    # Display results
    if hasattr(execution_result, 'content') and execution_result.content:
        content = execution_result.content[0].text if execution_result.content else str(execution_result)
        logger.info("📊 Execution Results:")
        logger.info(f"   {content}")

    # Run smoke tests if requested
    if verbose:
        logger.info("💨 Running smoke test suite...")
        
        smoke_result = await mcp_client.call_tool(
            "run_smoke_test_suite",
            {
                "target_environment": "test",
                "include_critical_apis": "api" in test_types,
                "include_critical_web_flows": "web" in test_types,
                "parallel_execution": True
            }
        )
        
        results["steps"].append({"step": "smoke_tests", "status": "success", "result": smoke_result})


async def execute_web_only_workflow(mcp_client, jira_key, results, debug, verbose):
    """Execute fallback web-only workflow."""
    
    logger.info("🌐 Executing web automation workflow...")
    
    # Fetch JIRA story
    jira_result = await mcp_client.call_tool(
        "fetch_jira_story", {"jira_key": jira_key}
    )
    results["steps"].append({"step": "fetch_jira_story", "status": "success"})

    # Extract text content from JIRA result
    jira_text = ""
    if hasattr(jira_result, 'content') and jira_result.content:
        jira_text = jira_result.content[0].text if jira_result.content else ""

    if debug:
        logger.info(f"📋 JIRA Story Content Preview:")
        logger.info(f"   {jira_text[:300]}..." if len(jira_text) > 300 else jira_text)

    # Execute web automation steps
    automation_steps = [
        ("playwright_navigate", {"url": "https://example.com"}),
        ("playwright_screenshot", {"name": f"{jira_key}_before"}),
        ("playwright_click", {"selector": "button[data-testid='action']"}),
        ("playwright_screenshot", {"name": f"{jira_key}_after"}),
    ]

    logger.info("🤖 Executing web automation steps...")
    
    for i, (tool_name, args) in enumerate(automation_steps, 1):
        logger.info(f"   Step {i}: {tool_name}")
        result = await mcp_client.call_tool(tool_name, args)
        results["steps"].append({"step": tool_name, "status": "success", "args": args})

        if debug and hasattr(result, 'content'):
            content = result.content[0].text if result.content else str(result)
            logger.info(f"      Result: {content}")


async def main():
    """Main function with enhanced argument parsing."""
    parser = argparse.ArgumentParser(
        description="Enhanced MCP Test Orchestrator - Web + API + Integration Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all test types for a JIRA ticket
  python enhanced_mcp_client_caller.py --jira TEST-1234

  # Run only web and API tests
  python enhanced_mcp_client_caller.py --jira TEST-1234 --types web api

  # Run with debug and verbose output
  python enhanced_mcp_client_caller.py --jira TEST-1234 --debug --verbose

  # Run performance testing
  python enhanced_mcp_client_caller.py --jira TEST-1234 --types api performance

Available Test Types:
  web         - Web automation using Playwright
  api         - API testing using Karate DSL
  performance - Performance testing with Gatling integration  
  integration - End-to-end integration testing
        """
    )
    
    parser.add_argument(
        "--jira", 
        type=str, 
        default="DEMO-123", 
        help="JIRA ticket key (e.g., TEST-1234)"
    )
    
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["web", "api", "performance", "integration"],
        default=["web", "api", "integration"],
        help="Types of tests to run (default: web api integration)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Show debug information about available tools"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Show all log messages and detailed output"
    )

    args = parser.parse_args()

    print("🚀 Enhanced MCP Test Orchestrator")
    print("=" * 50)
    print(f"📋 JIRA Ticket: {args.jira}")
    print(f"🧪 Test Types: {', '.join(args.types)}")
    print(f"🔧 Mode: {'Unified (Web+API+Integration)' if UNIFIED_MODE else 'Web-Only (Fallback)'}")
    print("=" * 50)

    # Execute comprehensive testing
    results = await execute_comprehensive_testing(
        args.jira, args.types, args.debug, args.verbose
    )

    # Display final summary
    print("\n" + "=" * 50)
    print("📊 Final Results Summary")
    print("=" * 50)
    print(f"JIRA Ticket: {results['jira_key']}")
    print(f"Status: {results['status']}")
    print(f"Test Types: {', '.join(results['test_types'])}")
    print(f"Steps Completed: {len(results['steps'])}")
    
    if results['status'] == 'completed':
        print("✅ All testing workflows completed successfully!")
        return 0
    else:
        print(f"❌ Testing failed: {results.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))