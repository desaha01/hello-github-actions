"""
Karate MCP Server - Advanced API Testing, Performance Testing, and Mock Server
Integrates Karate DSL capabilities with the MCP Test Orchestrator framework
"""
import json
import sys
import subprocess
import os
import yaml
from datetime import datetime
from pathlib import Path
from typing import Literal, List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the Python path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
from server.jira_config import get_jira_config


class KarateTestServer(FastMCP):
    """
    Karate MCP Server providing comprehensive API testing, performance testing,
    and mock server capabilities through Karate DSL integration.
    """
    
    def __init__(self, server_name="karate-test-server"):
        super().__init__(server_name)
        self.mcp = self
        self.karate_version = "1.4.1"  # Latest stable version
        self.test_results_dir = parent_dir / "karate_results"
        self.test_features_dir = parent_dir / "karate_features"
        self.mock_servers_dir = parent_dir / "karate_mocks"
        self.performance_results_dir = parent_dir / "performance_results"
        
        # Ensure directories exist
        self._setup_directories()
        
        # Get JIRA configuration
        self.jira_config = get_jira_config()
        
        # Register resources and prompts
        self.register_resources()
        self.register_prompts()
        
        print("Karate Test Server initialized")
        print(f"Features directory: {self.test_features_dir}")
        print(f"Results directory: {self.test_results_dir}")
        print(f"Mock servers directory: {self.mock_servers_dir}")
        
        self._register_karate_tools()
    
    def _setup_directories(self):
        """Create necessary directories for Karate operations."""
        dirs_to_create = [
            self.test_results_dir,
            self.test_features_dir,
            self.mock_servers_dir,
            self.performance_results_dir,
            self.test_features_dir / "api",
            self.test_features_dir / "performance", 
            self.test_features_dir / "integration",
            self.mock_servers_dir / "responses"
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _register_karate_tools(self):
        """Register all Karate-related tools with the MCP server."""
        
        @self.mcp.tool()
        async def karate_generate_api_test(
            api_name: str,
            base_url: str,
            endpoints: List[Dict[str, Any]],
            auth_type: Literal["none", "basic", "bearer", "oauth2", "apikey"] = "none",
            auth_config: Dict[str, str] = None
        ):
            """
            Generate comprehensive API test suite using Karate DSL.
            
            Args:
                api_name: Name of the API being tested
                base_url: Base URL of the API
                endpoints: List of endpoint configurations with method, path, expected status, etc.
                auth_type: Type of authentication required
                auth_config: Authentication configuration details
            """
            try:
                feature_content = self._generate_karate_feature(
                    api_name, base_url, endpoints, auth_type, auth_config
                )
                
                feature_file = self.test_features_dir / "api" / f"{api_name.lower().replace(' ', '_')}.feature"
                
                with open(feature_file, 'w') as f:
                    f.write(feature_content)
                
                return {
                    "status": "success",
                    "feature_file": str(feature_file),
                    "endpoints_count": len(endpoints),
                    "auth_type": auth_type,
                    "preview": feature_content[:500] + "..." if len(feature_content) > 500 else feature_content
                }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.mcp.tool()
        async def karate_run_api_tests(
            feature_path: str = None,
            tags: List[str] = None,
            parallel: int = 1,
            environment: str = "test",
            generate_report: bool = True
        ):
            """
            Execute Karate API tests with comprehensive reporting.
            
            Args:
                feature_path: Specific feature file to run (optional, runs all if not specified)
                tags: Karate tags to filter tests
                parallel: Number of parallel threads
                environment: Environment configuration to use
                generate_report: Whether to generate HTML report
            """
            try:
                cmd = self._build_karate_run_command(
                    feature_path, tags, parallel, environment, generate_report
                )
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.test_features_dir)
                
                # Parse results
                results = self._parse_karate_results()
                
                return {
                    "status": "completed",
                    "exit_code": result.returncode,
                    "results": results,
                    "report_path": str(self.test_results_dir / "karate-reports" / "karate-summary.html") if generate_report else None,
                    "stdout": result.stdout,
                    "stderr": result.stderr if result.returncode != 0 else None
                }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.mcp.tool()
        async def karate_performance_test(
            api_name: str,
            target_url: str,
            ramp_up_duration: int = 30,
            hold_duration: int = 60,
            ramp_down_duration: int = 30,
            target_rps: int = 10,
            scenario_name: str = "load_test"
        ):
            """
            Create and execute performance tests using Karate Gatling integration.
            
            Args:
                api_name: Name of the API for the performance test
                target_url: Target URL for load testing
                ramp_up_duration: Ramp up time in seconds
                hold_duration: Hold time at target load in seconds  
                ramp_down_duration: Ramp down time in seconds
                target_rps: Target requests per second
                scenario_name: Name of the performance scenario
            """
            try:
                # Generate Gatling simulation
                simulation_content = self._generate_gatling_simulation(
                    api_name, target_url, ramp_up_duration, hold_duration, 
                    ramp_down_duration, target_rps, scenario_name
                )
                
                simulation_file = self.performance_results_dir / f"{scenario_name}_simulation.scala"
                
                with open(simulation_file, 'w') as f:
                    f.write(simulation_content)
                
                # Run performance test (would need Gatling setup)
                return {
                    "status": "simulation_created",
                    "simulation_file": str(simulation_file),
                    "config": {
                        "ramp_up": ramp_up_duration,
                        "hold": hold_duration,
                        "ramp_down": ramp_down_duration,
                        "target_rps": target_rps
                    },
                    "next_steps": "Run with Gatling: gatling:test -Dgatling.simulationClass=YourSimulation"
                }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.mcp.tool()
        async def karate_mock_server(
            mock_name: str,
            port: int = 8080,
            mock_responses: List[Dict[str, Any]] = None,
            start_server: bool = True
        ):
            """
            Create and optionally start a Karate mock server.
            
            Args:
                mock_name: Name of the mock server
                port: Port number for the mock server
                mock_responses: List of mock response configurations
                start_server: Whether to start the server immediately
            """
            try:
                mock_feature = self._generate_mock_feature(mock_name, mock_responses)
                
                mock_file = self.mock_servers_dir / f"{mock_name.lower()}_mock.feature"
                
                with open(mock_file, 'w') as f:
                    f.write(mock_feature)
                
                if start_server:
                    # Start mock server (would need proper Karate mock server setup)
                    return {
                        "status": "server_starting",
                        "mock_file": str(mock_file),
                        "port": port,
                        "endpoints": len(mock_responses or []),
                        "url": f"http://localhost:{port}",
                        "command": f"java -jar karate.jar -m {mock_file} -p {port}"
                    }
                else:
                    return {
                        "status": "mock_created",
                        "mock_file": str(mock_file),
                        "port": port,
                        "endpoints": len(mock_responses or [])
                    }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.mcp.tool()
        async def karate_data_driven_test(
            feature_name: str,
            base_scenario: Dict[str, Any],
            test_data: List[Dict[str, Any]],
            data_source_type: Literal["json", "csv", "yaml"] = "json"
        ):
            """
            Generate data-driven tests with multiple test data sets.
            
            Args:
                feature_name: Name of the feature file
                base_scenario: Base scenario template
                test_data: Array of test data objects
                data_source_type: Format for test data file
            """
            try:
                # Create data file
                data_file = self.test_features_dir / f"{feature_name}_data.{data_source_type}"
                
                if data_source_type == "json":
                    with open(data_file, 'w') as f:
                        json.dump(test_data, f, indent=2)
                elif data_source_type == "yaml":
                    with open(data_file, 'w') as f:
                        yaml.dump(test_data, f, default_flow_style=False)
                elif data_source_type == "csv":
                    import csv
                    with open(data_file, 'w', newline='') as f:
                        if test_data:
                            writer = csv.DictWriter(f, fieldnames=test_data[0].keys())
                            writer.writeheader()
                            writer.writerows(test_data)
                
                # Generate feature with data-driven scenario
                feature_content = self._generate_data_driven_feature(
                    feature_name, base_scenario, str(data_file), data_source_type
                )
                
                feature_file = self.test_features_dir / f"{feature_name}.feature"
                
                with open(feature_file, 'w') as f:
                    f.write(feature_content)
                
                return {
                    "status": "success",
                    "feature_file": str(feature_file),
                    "data_file": str(data_file),
                    "test_cases": len(test_data),
                    "data_format": data_source_type
                }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.mcp.tool()
        async def karate_generate_from_jira(
            jira_key: str,
            test_type: Literal["api", "integration", "performance"] = "api",
            auto_parse: bool = True
        ):
            """
            Generate Karate tests from JIRA ticket specifications.
            
            Args:
                jira_key: JIRA ticket key
                test_type: Type of tests to generate
                auto_parse: Whether to auto-parse API specs from ticket
            """
            try:
                # Fetch JIRA ticket (reuse existing JIRA integration)
                import requests
                from requests.auth import HTTPBasicAuth
                
                jira_url = f"{self.jira_config.base_url}/rest/api/2/issue/{jira_key}"
                auth = HTTPBasicAuth(self.jira_config.email, self.jira_config.api_token)
                
                response = requests.get(jira_url, auth=auth)
                
                if response.status_code != 200:
                    return {"status": "error", "message": f"Failed to fetch JIRA ticket: {response.status_code}"}
                
                issue_data = response.json()
                
                # Parse ticket content for API specifications
                description = issue_data['fields']['description'] or ""
                summary = issue_data['fields']['summary'] or ""
                
                # Generate tests based on parsed content
                test_specs = self._parse_jira_for_api_specs(description, summary)
                
                if test_specs:
                    feature_content = self._generate_karate_from_specs(jira_key, test_specs, test_type)
                    
                    feature_file = self.test_features_dir / test_type / f"{jira_key.lower()}_tests.feature"
                    
                    with open(feature_file, 'w') as f:
                        f.write(feature_content)
                    
                    return {
                        "status": "success",
                        "jira_key": jira_key,
                        "feature_file": str(feature_file),
                        "test_type": test_type,
                        "specs_found": len(test_specs),
                        "preview": feature_content[:300] + "..."
                    }
                else:
                    return {
                        "status": "no_specs_found",
                        "jira_key": jira_key,
                        "message": "No API specifications found in JIRA ticket"
                    }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        @self.mcp.tool()
        async def karate_report_analysis(
            results_path: str = None,
            compare_with_baseline: bool = False,
            generate_trends: bool = True
        ):
            """
            Analyze Karate test results and generate comprehensive reports.
            
            Args:
                results_path: Path to specific results (optional)
                compare_with_baseline: Whether to compare with baseline results
                generate_trends: Whether to generate trend analysis
            """
            try:
                if not results_path:
                    results_path = str(self.test_results_dir)
                
                analysis = self._analyze_karate_results(
                    results_path, compare_with_baseline, generate_trends
                )
                
                # Generate analysis report
                report_file = self.test_results_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(report_file, 'w') as f:
                    json.dump(analysis, f, indent=2, default=str)
                
                return {
                    "status": "analysis_complete",
                    "report_file": str(report_file),
                    "summary": analysis.get("summary", {}),
                    "trends": analysis.get("trends", {}) if generate_trends else None
                }
                
            except Exception as e:
                return {"status": "error", "message": str(e)}
    
    def _generate_karate_feature(self, api_name: str, base_url: str, endpoints: List[Dict], auth_type: str, auth_config: Dict) -> str:
        """Generate Karate feature file content."""
        feature_lines = [
            f"Feature: {api_name} API Testing",
            f"  Comprehensive API tests for {api_name}",
            "",
            "Background:",
            f"  * url '{base_url}'",
        ]
        
        # Add authentication setup
        if auth_type == "bearer" and auth_config:
            feature_lines.extend([
                f"  * def token = '{auth_config.get('token', 'YOUR_TOKEN')}'",
                "  * header Authorization = 'Bearer ' + token"
            ])
        elif auth_type == "basic" and auth_config:
            feature_lines.extend([
                f"  * def credentials = '{auth_config.get('username', 'user')}:{auth_config.get('password', 'pass')}'",
                "  * header Authorization = 'Basic ' + java.util.Base64.encoder.encodeToString(credentials.bytes)"
            ])
        elif auth_type == "apikey" and auth_config:
            key_header = auth_config.get('header', 'X-API-Key')
            feature_lines.extend([
                f"  * header {key_header} = '{auth_config.get('key', 'YOUR_API_KEY')}'"
            ])
        
        feature_lines.append("")
        
        # Generate scenarios for each endpoint
        for i, endpoint in enumerate(endpoints, 1):
            method = endpoint.get('method', 'GET').upper()
            path = endpoint.get('path', '/')
            expected_status = endpoint.get('status', 200)
            scenario_name = endpoint.get('name', f"{method} {path}")
            
            feature_lines.extend([
                f"Scenario: {scenario_name}",
                f"  Given path '{path}'"
            ])
            
            # Add request body if provided
            if 'body' in endpoint:
                feature_lines.append(f"  And request {json.dumps(endpoint['body'])}")
            
            # Add query parameters if provided
            if 'params' in endpoint:
                for key, value in endpoint['params'].items():
                    feature_lines.append(f"  And param {key} = '{value}'")
            
            feature_lines.extend([
                f"  When method {method}",
                f"  Then status {expected_status}"
            ])
            
            # Add response validations if provided
            if 'validate' in endpoint:
                for validation in endpoint['validate']:
                    feature_lines.append(f"  And match {validation}")
            
            feature_lines.append("")
        
        return "\n".join(feature_lines)
    
    def _generate_gatling_simulation(self, api_name: str, target_url: str, ramp_up: int, 
                                   hold: int, ramp_down: int, target_rps: int, scenario_name: str) -> str:
        """Generate Gatling simulation for performance testing."""
        simulation = f"""
package simulations

import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class {scenario_name.capitalize()}Simulation extends Simulation {{

  val httpProtocol = http
    .baseUrl("{target_url}")
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  val {scenario_name} = scenario("{api_name} Performance Test")
    .exec(http("API Request")
      .get("/")
      .check(status.is(200)))

  setUp(
    {scenario_name}.inject(
      rampUsersPerSec(0) to {target_rps} during {ramp_up}.seconds,
      constantUsersPerSec({target_rps}) during {hold}.seconds,
      rampUsersPerSec({target_rps}) to 0 during {ramp_down}.seconds
    )
  ).protocols(httpProtocol)
   .assertions(
     global.responseTime.max.lt(5000),
     global.responseTime.mean.lt(1000),
     global.successfulRequests.percent.gt(95)
   )
}}
"""
        return simulation.strip()
    
    def _generate_mock_feature(self, mock_name: str, mock_responses: List[Dict]) -> str:
        """Generate Karate mock server feature."""
        feature_lines = [
            f"Feature: {mock_name} Mock Server",
            "",
            "Background:",
            "  * def responseDelay = 100"
        ]
        
        if mock_responses:
            for i, response in enumerate(mock_responses):
                path = response.get('path', f'/mock/{i}')
                method = response.get('method', 'GET').upper()
                status_code = response.get('status', 200)
                response_body = response.get('body', {})
                
                feature_lines.extend([
                    "",
                    f"Scenario: pathMatches('{path}') && methodIs('{method}')",
                    f"  * def responseStatus = {status_code}",
                    f"  * def response = {json.dumps(response_body)}",
                    "  * karate.proceed('classpath:mock-responses.js')"
                ])
        
        return "\n".join(feature_lines)
    
    def _generate_data_driven_feature(self, feature_name: str, base_scenario: Dict, 
                                    data_file: str, data_format: str) -> str:
        """Generate data-driven test feature."""
        feature_lines = [
            f"Feature: {feature_name} Data-Driven Tests",
            "",
            "Background:",
            "  * url 'https://api.example.com'",
            "",
            f"Scenario Outline: {base_scenario.get('name', 'Data-driven test')}",
            "  Given path '<endpoint>'",
            "  And request { id: '<id>', name: '<name>' }",
            "  When method POST",
            "  Then status <expectedStatus>",
            "  And match response.id == '<id>'",
            "",
            "Examples:",
            f"  | read('file:{Path(data_file).name}') |"
        ]
        
        return "\n".join(feature_lines)
    
    def _parse_jira_for_api_specs(self, description: str, summary: str) -> List[Dict]:
        """Parse JIRA ticket content for API specifications."""
        # Simplified parser - would be more sophisticated in practice
        specs = []
        
        # Look for common API patterns
        import re
        
        # Find URLs/endpoints
        url_pattern = r'(GET|POST|PUT|DELETE|PATCH)\s+(\/\S+)'
        matches = re.findall(url_pattern, description, re.IGNORECASE)
        
        for method, path in matches:
            specs.append({
                'method': method.upper(),
                'path': path,
                'status': 200,
                'name': f"{method.upper()} {path}"
            })
        
        return specs
    
    def _generate_karate_from_specs(self, jira_key: str, specs: List[Dict], test_type: str) -> str:
        """Generate Karate feature from parsed JIRA specs."""
        return self._generate_karate_feature(
            f"JIRA {jira_key} API Tests",
            "https://api.example.com",  # Would be parsed from JIRA
            specs,
            "none",
            None
        )
    
    def _build_karate_run_command(self, feature_path: str, tags: List[str], 
                                parallel: int, environment: str, generate_report: bool) -> List[str]:
        """Build command to run Karate tests."""
        cmd = ["java", "-jar", "karate.jar"]
        
        if feature_path:
            cmd.append(feature_path)
        else:
            cmd.extend([str(self.test_features_dir)])
        
        if tags:
            cmd.extend(["--tags", ",".join(tags)])
        
        if parallel > 1:
            cmd.extend(["--threads", str(parallel)])
        
        cmd.extend(["--env", environment])
        
        if generate_report:
            cmd.extend(["--output", str(self.test_results_dir)])
        
        return cmd
    
    def _parse_karate_results(self) -> Dict:
        """Parse Karate test results."""
        # Would parse actual Karate JSON results
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0,
            "features": []
        }
    
    def _analyze_karate_results(self, results_path: str, compare_baseline: bool, 
                              generate_trends: bool) -> Dict:
        """Analyze Karate test results."""
        return {
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            },
            "trends": {} if generate_trends else None,
            "baseline_comparison": {} if compare_baseline else None
        }


# Add Karate-specific configuration
def get_karate_config():
    """Get Karate-specific configuration."""
    return {
        "karate_jar_path": os.getenv("KARATE_JAR_PATH", "karate.jar"),
        "java_home": os.getenv("JAVA_HOME", ""),
        "gatling_home": os.getenv("GATLING_HOME", ""),
        "default_timeout": int(os.getenv("KARATE_TIMEOUT", "30000")),
        "default_retry_count": int(os.getenv("KARATE_RETRY", "0"))
    }