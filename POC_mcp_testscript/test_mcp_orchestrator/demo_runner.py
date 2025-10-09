#!/usr/bin/env python3
"""
Enhanced MCP Test Orchestrator Demo Runner
Runs interactive demos showcasing all capabilities
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
from datetime import datetime

# Demo data and configurations
DEMO_CONFIGS = {
    "api_basic": {
        "name": "Basic API Testing with Karate",
        "description": "Tests JSONPlaceholder API with GET, POST, PUT, DELETE operations",
        "config": {
            "api_name": "JSONPlaceholder Demo API",
            "base_url": "https://jsonplaceholder.typicode.com",
            "endpoints": [
                {"method": "GET", "path": "/posts", "status": 200},
                {"method": "GET", "path": "/posts/1", "status": 200},
                {"method": "POST", "path": "/posts", "status": 201, 
                 "body": {"title": "Demo Post", "body": "Demo content", "userId": 1}},
                {"method": "PUT", "path": "/posts/1", "status": 200,
                 "body": {"id": 1, "title": "Updated Post", "body": "Updated content", "userId": 1}},
                {"method": "DELETE", "path": "/posts/1", "status": 200}
            ]
        }
    },
    
    "web_basic": {
        "name": "Basic Web Automation with Playwright",
        "description": "Automates interactions with DemoQA practice website",
        "config": {
            "base_url": "https://demoqa.com",
            "test_actions": [
                {"action": "navigate", "url": "https://demoqa.com"},
                {"action": "click", "selector": "text=Elements"},
                {"action": "click", "selector": "text=Text Box"},
                {"action": "fill", "selector": "#userName", "value": "Demo User"},
                {"action": "fill", "selector": "#userEmail", "value": "demo@example.com"},
                {"action": "click", "selector": "#submit"},
                {"action": "screenshot", "name": "demo_elements_result"}
            ]
        }
    },
    
    "performance_basic": {
        "name": "Basic Performance Testing with Gatling",
        "description": "Load tests JSONPlaceholder API with configurable RPS",
        "config": {
            "api_name": "JSONPlaceholder Load Test",
            "target_url": "https://jsonplaceholder.typicode.com",
            "ramp_up_duration": 15,
            "hold_duration": 60,
            "ramp_down_duration": 15,
            "target_rps": 25,
            "scenario_name": "demo_load_test"
        }
    },
    
    "mock_server": {
        "name": "Mock Server Creation and Testing",
        "description": "Creates a mock API server and runs tests against it",
        "config": {
            "mock_name": "demo_user_api",
            "port": 8080,
            "mock_responses": [
                {
                    "path": "/users",
                    "method": "GET",
                    "status": 200,
                    "body": {"users": [{"id": 1, "name": "Demo User", "email": "demo@example.com"}]}
                },
                {
                    "path": "/users",
                    "method": "POST",
                    "status": 201,
                    "body": {"id": 2, "name": "New User", "email": "new@example.com", "created": True}
                },
                {
                    "path": "/users/1",
                    "method": "PUT",
                    "status": 200,
                    "body": {"id": 1, "name": "Updated User", "email": "updated@example.com"}
                },
                {
                    "path": "/users/1",
                    "method": "DELETE",
                    "status": 204,
                    "body": {}
                }
            ]
        }
    },
    
    "integration_full": {
        "name": "Full-Stack Integration Testing",
        "description": "Combines API, web, and integration testing in a unified flow",
        "config": {
            "flow_name": "demo_integration_flow",
            "api_setup_steps": [
                {"endpoint": "/posts", "method": "GET", "validate": "response.length > 0"}
            ],
            "web_automation_steps": [
                {"action": "navigate", "url": "https://demoqa.com"},
                {"action": "click", "selector": "text=Elements"},
                {"action": "verify", "selector": "text=Text Box"}
            ],
            "api_validation_steps": [
                {"endpoint": "/posts/1", "method": "GET", "validate": "response.id == 1"}
            ]
        }
    },
    
    "jira_simulation": {
        "name": "JIRA-Driven Test Generation (Simulated)",
        "description": "Simulates JIRA ticket analysis and comprehensive test generation",
        "config": {
            "jira_key": "DEMO-1234",
            "ticket_summary": "Implement User Registration Feature",
            "ticket_description": "Create user registration with email validation, password strength check, and confirmation email",
            "components": ["Frontend UI", "REST API", "Database", "Email Service"],
            "acceptance_criteria": [
                "User can enter email and password",
                "Password meets strength requirements",
                "Email validation works correctly", 
                "Confirmation email is sent",
                "User account is created in database"
            ]
        }
    }
}

class DemoRunner:
    def __init__(self, verbose: bool = False, debug: bool = False):
        self.verbose = verbose
        self.debug = debug
        self.demo_results_dir = Path("./demo_results")
        self.demo_results_dir.mkdir(exist_ok=True)
        
    def print_banner(self, title: str, description: str):
        """Print a formatted banner for demo start"""
        print("\n" + "="*70)
        print(f"🚀 Enhanced MCP Test Orchestrator - {title}")
        print("="*70)
        print(f"📋 {description}")
        print(f"🔧 Mode: Demo Simulation")
        print("="*70)
        
    def print_success(self, message: str):
        """Print success message with checkmark"""
        print(f"✅ {message}")
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"📊 {message}")
        
    def print_error(self, message: str):
        """Print error message with X mark"""
        print(f"❌ {message}")
        
    async def simulate_api_test_demo(self) -> Dict[str, Any]:
        """Simulate API testing demo"""
        config = DEMO_CONFIGS["api_basic"]["config"]
        
        self.print_banner(
            DEMO_CONFIGS["api_basic"]["name"],
            DEMO_CONFIGS["api_basic"]["description"]
        )
        
        # Simulate generating Karate feature file
        await asyncio.sleep(1)
        self.print_success(f"Generated API test: demo_jsonplaceholder.feature")
        
        if self.verbose:
            print("\n📝 Generated Feature File Content:")
            print("""
Feature: JSONPlaceholder Demo API Tests
  
  Background:
    * url 'https://jsonplaceholder.typicode.com'
    
  Scenario: Get all posts
    Given path '/posts'
    When method get
    Then status 200
    And match response == '#array'
    
  Scenario: Create new post
    Given path '/posts'
    And request { title: 'Demo Post', body: 'Demo content', userId: 1 }
    When method post
    Then status 201
    And match response.title == 'Demo Post'
            """)
        
        # Simulate test execution
        await asyncio.sleep(2)
        self.print_success("Test Results: 5 scenarios passed, 0 failed")
        self.print_info("Average response time: 245ms")
        self.print_info("Report: ./karate_results/demo_jsonplaceholder_report.html")
        
        return {
            "status": "success",
            "scenarios_run": 5,
            "scenarios_passed": 5,
            "scenarios_failed": 0,
            "avg_response_time": 245,
            "report_path": "./karate_results/demo_jsonplaceholder_report.html"
        }
    
    async def simulate_web_test_demo(self) -> Dict[str, Any]:
        """Simulate web automation demo"""
        config = DEMO_CONFIGS["web_basic"]["config"]
        
        self.print_banner(
            DEMO_CONFIGS["web_basic"]["name"],
            DEMO_CONFIGS["web_basic"]["description"]
        )
        
        # Simulate web automation steps
        for i, action in enumerate(config["test_actions"]):
            await asyncio.sleep(0.5)
            if action["action"] == "navigate":
                self.print_success(f"Navigated to {action['url']}")
            elif action["action"] == "click":
                self.print_success(f"Clicked on '{action['selector']}'")
            elif action["action"] == "fill":
                self.print_success(f"Filled '{action['selector']}' with '{action['value']}'")
            elif action["action"] == "screenshot":
                self.print_success(f"Screenshot saved: ./screenshots/{action['name']}.png")
        
        self.print_info("Report: ./web_results/demo_web_report.html")
        
        return {
            "status": "success",
            "actions_completed": len(config["test_actions"]),
            "screenshots_taken": 1,
            "report_path": "./web_results/demo_web_report.html"
        }
    
    async def simulate_performance_test_demo(self) -> Dict[str, Any]:
        """Simulate performance testing demo"""
        config = DEMO_CONFIGS["performance_basic"]["config"]
        
        self.print_banner(
            DEMO_CONFIGS["performance_basic"]["name"],
            DEMO_CONFIGS["performance_basic"]["description"]
        )
        
        # Show configuration
        print(f"\n🔥 Load Test Configuration:")
        print(f"   - Duration: {config['hold_duration']} seconds")
        print(f"   - Target RPS: {config['target_rps']} requests/second")
        print(f"   - Total Requests: ~{config['target_rps'] * config['hold_duration']}")
        
        # Simulate load test execution
        await asyncio.sleep(3)
        
        # Show results
        print(f"\n⚡ Performance Results:")
        print(f"   - Average Response Time: 187ms")
        print(f"   - 95th Percentile: 245ms")
        print(f"   - Max Response Time: 312ms")
        print(f"   - Success Rate: 100%")
        print(f"   - Total Requests: {config['target_rps'] * config['hold_duration'] - 13}")
        
        self.print_info("Performance Report: ./performance_results/demo_load_test.html")
        
        return {
            "status": "success",
            "total_requests": config['target_rps'] * config['hold_duration'] - 13,
            "avg_response_time": 187,
            "success_rate": 100,
            "report_path": "./performance_results/demo_load_test.html"
        }
    
    async def simulate_mock_server_demo(self) -> Dict[str, Any]:
        """Simulate mock server demo"""
        config = DEMO_CONFIGS["mock_server"]["config"]
        
        self.print_banner(
            DEMO_CONFIGS["mock_server"]["name"],
            DEMO_CONFIGS["mock_server"]["description"]
        )
        
        # Simulate mock server creation
        await asyncio.sleep(1)
        print(f"\n🎭 Mock Server Started:")
        print(f"   - Port: {config['port']}")
        print(f"   - Endpoints: {len(config['mock_responses'])} configured")
        print(f"   - Status: Running")
        
        # Simulate testing mock endpoints
        await asyncio.sleep(1)
        print(f"\n✅ Mock Test Results:")
        for response in config['mock_responses']:
            method = response['method']
            path = response['path']
            status = response['status']
            status_text = {200: "OK", 201: "Created", 204: "No Content"}[status]
            print(f"   - {method} {path}: {status} {status_text} ✅")
        
        self.print_info("Mock Interaction Log: ./karate_mocks/user_api_mock_log.json")
        
        return {
            "status": "success",
            "endpoints_tested": len(config['mock_responses']),
            "all_tests_passed": True,
            "mock_port": config['port']
        }
    
    async def simulate_integration_demo(self) -> Dict[str, Any]:
        """Simulate full integration testing demo"""
        config = DEMO_CONFIGS["integration_full"]["config"]
        
        self.print_banner(
            DEMO_CONFIGS["integration_full"]["name"],
            DEMO_CONFIGS["integration_full"]["description"]
        )
        
        # Simulate starting mock server
        await asyncio.sleep(1)
        self.print_success("Started mock server on port 8080")
        
        # Simulate API tests
        await asyncio.sleep(1.5)
        self.print_success("API Tests: 8 scenarios passed")
        
        # Simulate web tests
        await asyncio.sleep(1.5)
        self.print_success("Web Tests: 6 scenarios passed")
        
        # Simulate integration flow
        await asyncio.sleep(1)
        self.print_success("Integration Flow: End-to-end success")
        
        self.print_info("Performance: All endpoints < 200ms")
        self.print_info("Unified Report: ./unified_test_results/integration_demo_report.html")
        
        return {
            "status": "success",
            "api_scenarios": 8,
            "web_scenarios": 6,
            "integration_flows": 1,
            "overall_success": True
        }
    
    async def simulate_jira_demo(self) -> Dict[str, Any]:
        """Simulate JIRA-driven test generation"""
        config = DEMO_CONFIGS["jira_simulation"]["config"]
        
        self.print_banner(
            DEMO_CONFIGS["jira_simulation"]["name"],
            DEMO_CONFIGS["jira_simulation"]["description"]
        )
        
        # Show JIRA analysis
        print(f"\n📝 JIRA Analysis:")
        print(f"   - Feature: {config['ticket_summary']}")
        print(f"   - Components: {', '.join(config['components'])}")
        print(f"   - Test Types: Web automation, API testing, Integration")
        
        # Simulate test generation
        await asyncio.sleep(2)
        print(f"\n🧪 Generated Test Suite:")
        self.print_success("Web Tests: user_registration_ui.spec.ts")
        self.print_success("API Tests: user_registration_api.feature") 
        self.print_success("Integration: end_to_end_registration.feature")
        
        # Simulate execution results
        await asyncio.sleep(2)
        print(f"\n📊 Execution Results:")
        print(f"   - Web Tests: 8/8 passed")
        print(f"   - API Tests: 12/12 scenarios passed")
        print(f"   - Integration: 3/3 flows passed")
        
        self.print_info(f"Comprehensive Report: ./unified_test_results/jira_demo_1234_report.html")
        
        return {
            "status": "success",
            "jira_key": config['jira_key'],
            "web_tests": 8,
            "api_scenarios": 12,
            "integration_flows": 3,
            "all_passed": True
        }
    
    async def run_demo(self, demo_type: str) -> Dict[str, Any]:
        """Run a specific demo"""
        if demo_type not in DEMO_CONFIGS:
            self.print_error(f"Unknown demo type: {demo_type}")
            return {"status": "error", "message": f"Unknown demo type: {demo_type}"}
        
        try:
            if demo_type == "api_basic":
                return await self.simulate_api_test_demo()
            elif demo_type == "web_basic":
                return await self.simulate_web_test_demo()
            elif demo_type == "performance_basic":
                return await self.simulate_performance_test_demo()
            elif demo_type == "mock_server":
                return await self.simulate_mock_server_demo()
            elif demo_type == "integration_full":
                return await self.simulate_integration_demo()
            elif demo_type == "jira_simulation":
                return await self.simulate_jira_demo()
            else:
                self.print_error(f"Demo implementation not found: {demo_type}")
                return {"status": "error", "message": f"Demo implementation not found: {demo_type}"}
                
        except Exception as e:
            self.print_error(f"Demo failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def save_demo_results(self, demo_type: str, results: Dict[str, Any]):
        """Save demo results to file"""
        demo_dir = self.demo_results_dir / demo_type
        demo_dir.mkdir(exist_ok=True)
        
        results_file = demo_dir / "demo_results.json"
        results["timestamp"] = datetime.now().isoformat()
        results["demo_type"] = demo_type
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Demo results saved to: {results_file}")

async def main():
    parser = argparse.ArgumentParser(description="Enhanced MCP Test Orchestrator Demo Runner")
    parser.add_argument("--demo", choices=list(DEMO_CONFIGS.keys()) + ["all"], 
                       help="Demo to run", required=True)
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--debug", "-d", action="store_true", help="Debug output") 
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    runner = DemoRunner(verbose=args.verbose, debug=args.debug)
    
    if args.demo == "all":
        print("🚀 Running All Demos...")
        for demo_type in DEMO_CONFIGS.keys():
            results = await runner.run_demo(demo_type)
            runner.save_demo_results(demo_type, results)
            print("\nDemo completed successfully! ✨\n")
            await asyncio.sleep(1)  # Brief pause between demos
    else:
        results = await runner.run_demo(args.demo)
        runner.save_demo_results(args.demo, results)
        print("\nDemo completed successfully! ✨")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)