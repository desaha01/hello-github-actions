#!/usr/bin/env python3
"""
MCP Server for Karate Testing Framework

This server provides tools to interact with Karate tests through the Model Context Protocol.
It allows running Karate tests, listing feature files, and retrieving test results.
"""

import json
import subprocess
import os
import glob
from pathlib import Path
from typing import Any, Dict, List, Optional


class KarateMCPServer:
    """MCP Server for Karate testing framework"""
    
    def __init__(self, base_path: str = "."):
        """
        Initialize the Karate MCP Server
        
        Args:
            base_path: Base directory path for Karate tests
        """
        self.base_path = Path(base_path).resolve()
        self.features_dir = self.base_path / "karate-tests" / "features"
        self.results_dir = self.base_path / "karate-tests" / "target"
        
    def list_tools(self) -> List[Dict[str, Any]]:
        """Return list of available MCP tools"""
        return [
            {
                "name": "run_karate_test",
                "description": "Run a Karate feature file or specific scenario",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "feature_path": {
                            "type": "string",
                            "description": "Path to the Karate feature file (relative to features directory)"
                        },
                        "tags": {
                            "type": "string",
                            "description": "Optional tags to filter scenarios (e.g., '@smoke')"
                        }
                    },
                    "required": ["feature_path"]
                }
            },
            {
                "name": "list_karate_features",
                "description": "List all available Karate feature files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Optional glob pattern to filter feature files (e.g., '**/user*.feature')"
                        }
                    }
                }
            },
            {
                "name": "get_test_results",
                "description": "Get the results of the last Karate test run",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "Whether to include detailed scenario results"
                        }
                    }
                }
            }
        ]
    
    def run_karate_test(self, feature_path: str, tags: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a Karate test
        
        Args:
            feature_path: Path to the feature file
            tags: Optional tags to filter scenarios
            
        Returns:
            Dictionary containing test results
        """
        try:
            # Construct the command to run Karate tests
            cmd = ["mvn", "test"]
            
            # Add feature path if specified
            if feature_path:
                cmd.append(f"-Dkarate.options=classpath:features/{feature_path}")
            
            # Add tags if specified
            if tags:
                cmd.append(f"-Dkarate.options=--tags {tags}")
            
            # Run the command
            result = subprocess.run(
                cmd,
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "message": "Test execution completed" if result.returncode == 0 else "Test execution failed"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Test execution timed out after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error running test: {str(e)}"
            }
    
    def list_karate_features(self, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List all Karate feature files
        
        Args:
            pattern: Optional glob pattern to filter files
            
        Returns:
            Dictionary containing list of feature files
        """
        try:
            if not self.features_dir.exists():
                return {
                    "success": False,
                    "message": f"Features directory not found: {self.features_dir}",
                    "features": []
                }
            
            # Use pattern if provided, otherwise find all .feature files
            search_pattern = pattern if pattern else "**/*.feature"
            feature_files = []
            
            for feature_path in self.features_dir.glob(search_pattern):
                if feature_path.is_file():
                    relative_path = feature_path.relative_to(self.features_dir)
                    
                    # Try to extract feature name and scenarios
                    feature_info = {
                        "path": str(relative_path),
                        "full_path": str(feature_path),
                        "name": feature_path.stem
                    }
                    
                    # Read feature file to extract scenarios
                    try:
                        with open(feature_path, 'r') as f:
                            content = f.read()
                            scenarios = []
                            for line in content.split('\n'):
                                line = line.strip()
                                if line.startswith('Scenario:'):
                                    scenarios.append(line.replace('Scenario:', '').strip())
                            feature_info["scenarios"] = scenarios
                    except Exception:
                        pass
                    
                    feature_files.append(feature_info)
            
            return {
                "success": True,
                "count": len(feature_files),
                "features": feature_files
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing features: {str(e)}",
                "features": []
            }
    
    def get_test_results(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Get results from the last test run
        
        Args:
            detailed: Whether to include detailed results
            
        Returns:
            Dictionary containing test results
        """
        try:
            # Look for Karate JSON results
            results_pattern = str(self.results_dir / "karate-reports" / "*.json")
            result_files = glob.glob(results_pattern)
            
            if not result_files:
                return {
                    "success": False,
                    "message": "No test results found. Run tests first."
                }
            
            # Read the most recent result file
            latest_result = max(result_files, key=os.path.getctime)
            
            with open(latest_result, 'r') as f:
                results = json.load(f)
            
            # Extract summary information
            summary = {
                "success": True,
                "total_scenarios": 0,
                "passed_scenarios": 0,
                "failed_scenarios": 0,
                "duration": 0
            }
            
            if isinstance(results, list):
                for feature in results:
                    for scenario in feature.get('elements', []):
                        summary["total_scenarios"] += 1
                        if scenario.get('status') == 'passed':
                            summary["passed_scenarios"] += 1
                        else:
                            summary["failed_scenarios"] += 1
            
            if detailed:
                summary["detailed_results"] = results
            
            return summary
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error reading test results: {str(e)}"
            }
    
    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a tool call from MCP client
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Result of the tool execution
        """
        if tool_name == "run_karate_test":
            return self.run_karate_test(
                arguments.get("feature_path"),
                arguments.get("tags")
            )
        elif tool_name == "list_karate_features":
            return self.list_karate_features(
                arguments.get("pattern")
            )
        elif tool_name == "get_test_results":
            return self.get_test_results(
                arguments.get("detailed", False)
            )
        else:
            return {
                "success": False,
                "message": f"Unknown tool: {tool_name}"
            }
    
    def start_server(self):
        """Start the MCP server (stdio-based)"""
        print("Karate MCP Server started", file=sys.stderr)
        print("Available tools:", file=sys.stderr)
        for tool in self.list_tools():
            print(f"  - {tool['name']}: {tool['description']}", file=sys.stderr)
        
        # In a real MCP server, this would implement the MCP protocol
        # For now, this is a basic implementation
        while True:
            try:
                line = input()
                if not line:
                    continue
                
                request = json.loads(line)
                
                if request.get("method") == "tools/list":
                    response = {
                        "tools": self.list_tools()
                    }
                elif request.get("method") == "tools/call":
                    params = request.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    response = self.handle_tool_call(tool_name, arguments)
                else:
                    response = {
                        "error": "Unknown method"
                    }
                
                print(json.dumps(response))
                
            except EOFError:
                break
            except Exception as e:
                print(json.dumps({"error": str(e)}))


def main():
    """Main entry point"""
    import sys
    
    # Get base path from arguments or use current directory
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    server = KarateMCPServer(base_path)
    
    # If running with --list-tools, just print tools and exit
    if "--list-tools" in sys.argv:
        print(json.dumps(server.list_tools(), indent=2))
        return
    
    # Start the server
    server.start_server()


if __name__ == "__main__":
    main()
