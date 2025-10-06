#!/usr/bin/env python3
"""
Example: Using Karate MCP Server Programmatically

This script demonstrates how to use the Karate MCP Server tools
directly from Python code.
"""

import json
from karate_mcp_server import KarateMCPServer


def example_list_features():
    """Example 1: List all Karate feature files"""
    print("\n" + "="*60)
    print("Example 1: Listing All Feature Files")
    print("="*60)
    
    server = KarateMCPServer(".")
    result = server.list_karate_features()
    
    print(f"\nFound {result['count']} feature file(s):\n")
    for feature in result['features']:
        print(f"📄 {feature['path']}")
        if 'scenarios' in feature:
            print(f"   Scenarios: {len(feature['scenarios'])}")
            for scenario in feature['scenarios']:
                print(f"   • {scenario}")
        print()


def example_search_features():
    """Example 2: Search for specific feature files"""
    print("\n" + "="*60)
    print("Example 2: Searching for API Test Features")
    print("="*60)
    
    server = KarateMCPServer(".")
    result = server.list_karate_features(pattern="**/*api*.feature")
    
    print(f"\nFound {result['count']} matching feature file(s):\n")
    for feature in result['features']:
        print(f"📄 {feature['name']}")
        print(f"   Path: {feature['path']}")


def example_run_test():
    """Example 3: Run a Karate test (requires Maven and Java)"""
    print("\n" + "="*60)
    print("Example 3: Running a Karate Test")
    print("="*60)
    print("\n⚠️  This example requires Maven and Java to be installed.")
    print("Skipping actual test execution in this demo.\n")
    
    # Uncomment below to actually run tests:
    # server = KarateMCPServer(".")
    # result = server.run_karate_test(
    #     feature_path="examples/sample-api-test.feature",
    #     tags="@smoke"
    # )
    # print(f"Test result: {result}")


def example_tool_metadata():
    """Example 4: Get tool metadata"""
    print("\n" + "="*60)
    print("Example 4: Getting Tool Metadata")
    print("="*60)
    
    server = KarateMCPServer(".")
    tools = server.list_tools()
    
    print(f"\nAvailable tools: {len(tools)}\n")
    for tool in tools:
        print(f"🔧 {tool['name']}")
        print(f"   Description: {tool['description']}")
        print(f"   Required params: {tool['inputSchema'].get('required', [])}")
        print()


def example_handle_tool_call():
    """Example 5: Handle a tool call (MCP protocol style)"""
    print("\n" + "="*60)
    print("Example 5: Handling Tool Call (MCP Protocol Style)")
    print("="*60)
    
    server = KarateMCPServer(".")
    
    # Simulate an MCP tool call
    tool_call = {
        "name": "list_karate_features",
        "arguments": {
            "pattern": "**/*.feature"
        }
    }
    
    print(f"\nTool call: {json.dumps(tool_call, indent=2)}")
    print("\nExecuting...\n")
    
    result = server.handle_tool_call(
        tool_call['name'],
        tool_call['arguments']
    )
    
    print(f"Result: {json.dumps(result, indent=2)}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Karate MCP Server - Programmatic Usage Examples")
    print("="*60)
    
    # Run all examples
    example_list_features()
    example_search_features()
    example_run_test()
    example_tool_metadata()
    example_handle_tool_call()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)
    print("\nNext steps:")
    print("  • Review the code in this file to understand the API")
    print("  • Check KARATE-MCP-README.md for detailed documentation")
    print("  • See MCP-CLIENT-INTEGRATION.md for client integration examples")
    print()


if __name__ == "__main__":
    main()
