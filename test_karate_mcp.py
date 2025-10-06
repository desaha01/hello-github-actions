#!/usr/bin/env python3
"""
Test script for Karate MCP Server

This script demonstrates how to use the Karate MCP Server tools.
"""

import json
import sys
from karate_mcp_server import KarateMCPServer


def main():
    """Run example tests for the MCP server"""
    
    print("=" * 60)
    print("Karate MCP Server - Test Script")
    print("=" * 60)
    print()
    
    # Initialize the server
    server = KarateMCPServer(".")
    
    # Test 1: List all available tools
    print("1. Listing available tools:")
    print("-" * 40)
    tools = server.list_tools()
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    print()
    
    # Test 2: List all Karate features
    print("2. Listing all Karate features:")
    print("-" * 40)
    features_result = server.list_karate_features()
    if features_result["success"]:
        print(f"   Found {features_result['count']} feature(s):")
        for feature in features_result["features"]:
            print(f"   - {feature['path']}")
            if "scenarios" in feature:
                for scenario in feature["scenarios"]:
                    print(f"     * {scenario}")
    else:
        print(f"   Error: {features_result.get('message', 'Unknown error')}")
    print()
    
    # Test 3: Search for specific features
    print("3. Searching for 'api' features:")
    print("-" * 40)
    search_result = server.list_karate_features(pattern="**/*api*.feature")
    if search_result["success"]:
        print(f"   Found {search_result['count']} matching feature(s):")
        for feature in search_result["features"]:
            print(f"   - {feature['path']}")
    else:
        print(f"   Error: {search_result.get('message', 'Unknown error')}")
    print()
    
    # Test 4: Check test results (will fail if no tests have been run)
    print("4. Getting test results:")
    print("-" * 40)
    results = server.get_test_results()
    if results["success"]:
        print(f"   Total scenarios: {results.get('total_scenarios', 0)}")
        print(f"   Passed: {results.get('passed_scenarios', 0)}")
        print(f"   Failed: {results.get('failed_scenarios', 0)}")
    else:
        print(f"   {results.get('message', 'No results available')}")
    print()
    
    print("=" * 60)
    print("Test script completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
