#!/usr/bin/env python3
"""
System requirements verification script for Enhanced MCP Test Orchestrator
Checks all prerequisites and provides setup guidance
"""

import sys
import subprocess
import os
import platform
import importlib
from pathlib import Path
from typing import Tuple, List, Dict, Any

class SystemChecker:
    def __init__(self):
        self.results = []
        self.warnings = []
        self.errors = []
        self.system_info = self.get_system_info()
        
    def get_system_info(self) -> Dict[str, str]:
        """Get basic system information"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
    
    def print_header(self):
        """Print system check header"""
        print("🔍 Enhanced MCP Test Orchestrator - System Requirements Check")
        print("=" * 70)
        print(f"🖥️  OS: {self.system_info['os']} {self.system_info['architecture']}")
        print(f"🐍 Python: {self.system_info['python_version']} ({self.system_info['python_implementation']})")
        print("=" * 70)
        print()
    
    def check_python_version(self) -> Tuple[bool, str, str]:
        """Check Python version requirements"""
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            return False, version_str, "Python 3.11+ required for async features and type hints"
        elif version.major == 3 and version.minor >= 12:
            return True, version_str, "Excellent! Latest Python version"
        else:
            return True, version_str, "Good! Compatible Python version"
    
    def check_ssl_support(self) -> Tuple[bool, str, str]:
        """Check SSL/TLS support in Python"""
        try:
            import ssl
            openssl_version = ssl.OPENSSL_VERSION
            # Test SSL by making a simple connection
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=5)
            return True, openssl_version, "SSL/TLS working correctly"
        except ImportError:
            return False, "Not available", "SSL module not available - Python installation issue"
        except Exception as e:
            return False, "Available but not working", f"SSL connection test failed: {str(e)}"
    
    def check_java_installation(self) -> Tuple[bool, str, str]:
        """Check Java installation and version"""
        try:
            result = subprocess.run(
                ['java', '-version'], 
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Java version is in stderr
                version_line = result.stderr.split('\n')[0]
                # Extract version number
                if 'openjdk' in version_line.lower():
                    return True, version_line.strip(), "OpenJDK detected - perfect for Karate"
                elif 'java' in version_line.lower():
                    return True, version_line.strip(), "Java detected - compatible with Karate"
                else:
                    return True, version_line.strip(), "Java runtime available"
            else:
                return False, "Error running java", result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Timeout", "Java command timed out"
        except FileNotFoundError:
            return False, "Not found", "Java not installed or not in PATH"
        except Exception as e:
            return False, "Error", f"Java check failed: {str(e)}"
    
    def check_java_home(self) -> Tuple[bool, str, str]:
        """Check JAVA_HOME environment variable"""
        java_home = os.getenv('JAVA_HOME')
        if not java_home:
            return False, "Not set", "JAVA_HOME environment variable not set"
        
        java_home_path = Path(java_home)
        if not java_home_path.exists():
            return False, java_home, "JAVA_HOME path does not exist"
        
        java_exe = java_home_path / 'bin' / ('java.exe' if platform.system() == 'Windows' else 'java')
        if java_exe.exists():
            return True, java_home, "JAVA_HOME correctly configured"
        else:
            return False, java_home, "JAVA_HOME set but java executable not found in bin/"
    
    def check_node_installation(self) -> Tuple[bool, str, str]:
        """Check Node.js installation"""
        try:
            result = subprocess.run(
                ['node', '--version'], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                # Extract major version number
                major_version = int(version.replace('v', '').split('.')[0])
                if major_version >= 16:
                    return True, version, "Node.js version compatible with Playwright"
                else:
                    return False, version, "Node.js version too old - need 16+"
            else:
                return False, "Error", result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Timeout", "Node.js command timed out"
        except FileNotFoundError:
            return False, "Not found", "Node.js not installed or not in PATH"
        except Exception as e:
            return False, "Error", f"Node.js check failed: {str(e)}"
    
    def check_npm_installation(self) -> Tuple[bool, str, str]:
        """Check npm installation"""
        try:
            result = subprocess.run(
                ['npm', '--version'], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return True, version, "npm package manager available"
            else:
                return False, "Error", result.stderr.strip()
        except FileNotFoundError:
            return False, "Not found", "npm not installed or not in PATH"
        except Exception as e:
            return False, "Error", f"npm check failed: {str(e)}"
    
    def check_python_packages(self) -> Tuple[bool, str, str]:
        """Check required Python packages"""
        required_packages = [
            'fastmcp', 'playwright', 'aiohttp', 'pydantic', 
            'httpx', 'python-dotenv', 'PyYAML'
        ]
        
        installed = []
        missing = []
        
        for package in required_packages:
            try:
                importlib.import_module(package.replace('-', '_'))
                installed.append(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            return True, f"{len(installed)} packages", "All required Python packages installed"
        elif len(missing) < len(required_packages) / 2:
            return True, f"{len(installed)}/{len(required_packages)}", f"Most packages installed, missing: {', '.join(missing)}"
        else:
            return False, f"{len(installed)}/{len(required_packages)}", f"Many packages missing: {', '.join(missing)}"
    
    def check_karate_jar(self) -> Tuple[bool, str, str]:
        """Check Karate JAR file availability"""
        # Check environment variable
        jar_path_env = os.getenv('KARATE_JAR_PATH')
        
        # Possible locations
        possible_paths = [
            jar_path_env,
            './tools/karate.jar',
            './karate.jar',
            '../tools/karate.jar'
        ]
        
        for path_str in possible_paths:
            if not path_str:
                continue
            path = Path(path_str)
            if path.exists() and path.is_file():
                # Try to get version info
                try:
                    result = subprocess.run(
                        ['java', '-jar', str(path), '--version'],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        return True, str(path), "Karate JAR found and working"
                    else:
                        return True, str(path), "Karate JAR found but version check failed"
                except:
                    return True, str(path), "Karate JAR found but not tested"
        
        return False, "Not found", "Karate JAR not found in expected locations"
    
    def check_gatling_installation(self) -> Tuple[bool, str, str]:
        """Check Gatling installation"""
        gatling_home = os.getenv('GATLING_HOME')
        
        if not gatling_home:
            # Check common locations
            possible_paths = [
                './tools/gatling/gatling-bundle',
                './gatling',
                '../tools/gatling'
            ]
            for path_str in possible_paths:
                path = Path(path_str)
                if path.exists() and (path / 'bin').exists():
                    gatling_home = str(path)
                    break
        
        if gatling_home:
            gatling_path = Path(gatling_home)
            if gatling_path.exists():
                bin_dir = gatling_path / 'bin'
                if bin_dir.exists():
                    return True, gatling_home, "Gatling installation found"
                else:
                    return False, gatling_home, "Gatling path exists but bin/ directory missing"
            else:
                return False, gatling_home, "GATLING_HOME path does not exist"
        else:
            return False, "Not set", "Gatling not found - needed for performance testing"
    
    def check_environment_file(self) -> Tuple[bool, str, str]:
        """Check environment configuration file"""
        env_file = Path('.env')
        if env_file.exists():
            # Check if it has required sections
            content = env_file.read_text()
            required_sections = ['JIRA_', 'AZURE_OPENAI_', 'KARATE_']
            found_sections = [section for section in required_sections 
                            if any(line.startswith(section) for line in content.split('\n'))]
            
            if len(found_sections) == len(required_sections):
                return True, str(env_file), "Environment file complete"
            elif found_sections:
                return True, str(env_file), f"Environment file partial ({len(found_sections)}/{len(required_sections)} sections)"
            else:
                return True, str(env_file), "Environment file exists but appears empty"
        else:
            return False, "Not found", "Environment file (.env) not found - copy from template"
    
    def check_directories(self) -> Tuple[bool, str, str]:
        """Check required directory structure"""
        required_dirs = [
            'server', 'client_bridge', 'prompts',
            'screenshots', 'karate_features', 'karate_results',
            'performance_results', 'unified_test_results'
        ]
        
        existing_dirs = []
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                existing_dirs.append(dir_name)
        
        if len(existing_dirs) == len(required_dirs):
            return True, f"{len(existing_dirs)} directories", "All required directories exist"
        elif len(existing_dirs) > len(required_dirs) / 2:
            return True, f"{len(existing_dirs)}/{len(required_dirs)}", "Most directories exist"
        else:
            return False, f"{len(existing_dirs)}/{len(required_dirs)}", "Many required directories missing"
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all system checks"""
        checks = [
            ("Python Version", self.check_python_version),
            ("SSL Support", self.check_ssl_support),
            ("Java Installation", self.check_java_installation),
            ("JAVA_HOME", self.check_java_home),
            ("Node.js", self.check_node_installation),
            ("npm", self.check_npm_installation),
            ("Python Packages", self.check_python_packages),
            ("Karate JAR", self.check_karate_jar),
            ("Gatling", self.check_gatling_installation),
            ("Environment File", self.check_environment_file),
            ("Directories", self.check_directories)
        ]
        
        results = {}
        passed = 0
        total = len(checks)
        
        for check_name, check_func in checks:
            try:
                success, value, message = check_func()
                status = "✅" if success else "❌"
                print(f"{status} {check_name:20} {value:30} {message}")
                
                results[check_name] = {
                    "success": success,
                    "value": value,
                    "message": message
                }
                
                if success:
                    passed += 1
                else:
                    self.errors.append(f"{check_name}: {message}")
                    
            except Exception as e:
                print(f"❌ {check_name:20} {'ERROR':30} Check failed: {str(e)}")
                results[check_name] = {
                    "success": False,
                    "value": "ERROR",
                    "message": f"Check failed: {str(e)}"
                }
                self.errors.append(f"{check_name}: Check failed: {str(e)}")
        
        results["summary"] = {
            "passed": passed,
            "total": total,
            "percentage": int((passed / total) * 100)
        }
        
        return results
    
    def print_recommendations(self, results: Dict[str, Any]):
        """Print setup recommendations based on check results"""
        print("\n" + "="*70)
        print("🎯 SETUP RECOMMENDATIONS")
        print("="*70)
        
        summary = results["summary"]
        
        if summary["percentage"] >= 90:
            print("🎉 Excellent! Your system is ready for Enhanced MCP Test Orchestrator!")
            print("   You can run all features including:")
            print("   - Web automation with Playwright")
            print("   - API testing with Karate DSL")
            print("   - Performance testing with Gatling")
            print("   - JIRA integration")
            
        elif summary["percentage"] >= 70:
            print("🟡 Good! Most requirements are met. Address these items:")
            for error in self.errors[:3]:  # Show top 3 issues
                print(f"   • {error}")
                
        else:
            print("🔴 Several requirements need attention:")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n📚 Next Steps:")
        
        # Specific recommendations
        if not results.get("Java Installation", {}).get("success"):
            print("   1. Install Java 11+: https://adoptium.net/temurin/releases/")
            
        if not results.get("Karate JAR", {}).get("success"):
            print("   2. Download Karate JAR: https://github.com/karatelabs/karate/releases/latest")
            
        if not results.get("Python Packages", {}).get("success"):
            print("   3. Install Python packages: pip install -r requirements.txt")
            
        if not results.get("Environment File", {}).get("success"):
            print("   4. Create .env file from SETUP_INSTALLATION_GUIDE.md template")
            
        print(f"\n   📖 Full setup guide: SETUP_INSTALLATION_GUIDE.md")
        print(f"   🚀 After setup, run: python demo_runner.py --demo api_basic")

def main():
    checker = SystemChecker()
    checker.print_header()
    
    results = checker.run_all_checks()
    
    print(f"\n📊 SYSTEM CHECK SUMMARY")
    print(f"   Passed: {results['summary']['passed']}/{results['summary']['total']} ({results['summary']['percentage']}%)")
    
    checker.print_recommendations(results)
    
    # Exit with appropriate code
    if results['summary']['percentage'] >= 70:
        print("\n✅ System check completed successfully!")
        return 0
    else:
        print("\n⚠️  System check completed with issues. Please address requirements above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())