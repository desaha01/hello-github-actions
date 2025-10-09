# Setup and Installation Guide

## 🚀 **Complete Setup Guide for Enhanced MCP Test Orchestrator**

This guide will help you set up the enhanced MCP Test Orchestrator with full Karate DSL integration for comprehensive testing capabilities.

---

## 📋 **Prerequisites and System Requirements**

### **System Requirements**
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.11+ (recommended: 3.12)
- **Java**: JDK 11+ (required for Karate DSL)
- **Node.js**: 16+ (required for Playwright)
- **Memory**: Minimum 4GB RAM (8GB+ recommended for performance testing)
- **Disk Space**: 2GB free space for tools and test results

### **Network Requirements**
- Internet access for downloading dependencies
- Corporate firewall exceptions (if applicable):
  - Maven Central Repository: `repo1.maven.org`
  - GitHub Releases: `github.com`
  - NPM Registry: `registry.npmjs.org`

---

## 🔧 **Step 1: Python Environment Setup**

### **1.1 Verify Python Installation**
```bash
# Check Python version (must be 3.11+)
python --version

# Check if pip is working
pip --version

# Check SSL support (critical for package installation)
python -c "import ssl; print('SSL support:', ssl.OPENSSL_VERSION)"
```

### **1.2 Fix SSL Issues (If Encountered)**
If you see SSL errors when installing packages:

#### **Windows - SSL Fix**
```powershell
# Method 1: Reinstall Python with SSL support
# Download latest Python from python.org and reinstall

# Method 2: Manual OpenSSL DLL repair
# Download OpenSSL DLLs and place in Python/DLLs folder
# Required files: libcrypto-3-x64.dll, libssl-3-x64.dll

# Method 3: Use conda instead of pip
# Download Miniconda and create environment
conda create -n mcp_test python=3.12
conda activate mcp_test
```

#### **macOS - SSL Fix**
```bash
# Update certificates
/Applications/Python\ 3.12/Install\ Certificates.command

# Or install via Homebrew
brew install python@3.12
```

#### **Linux - SSL Fix**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-dev libssl-dev

# CentOS/RHEL
sudo yum install python3-pip python3-devel openssl-devel
```

### **1.3 Create Virtual Environment**
```bash
# Create dedicated environment
python -m venv mcp_test_env

# Activate environment
# Windows:
mcp_test_env\Scripts\activate
# macOS/Linux:
source mcp_test_env/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

---

## ☕ **Step 2: Java Setup for Karate DSL**

### **2.1 Install Java Development Kit (JDK)**

#### **Windows**
```powershell
# Option 1: Download from Oracle or OpenJDK
# https://adoptium.net/temurin/releases/

# Option 2: Use Chocolatey (if available)
choco install openjdk11

# Option 3: Use scoop (if available)
scoop install openjdk11
```

#### **macOS**
```bash
# Option 1: Use Homebrew
brew install openjdk@11

# Option 2: Use SDKMAN
curl -s "https://get.sdkman.io" | bash
sdk install java 11.0.19-tem
```

#### **Linux**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# CentOS/RHEL
sudo yum install java-11-openjdk-devel

# Verify installation
java -version
javac -version
```

### **2.2 Set JAVA_HOME Environment Variable**

#### **Windows**
```powershell
# Find Java installation path
where java

# Set JAVA_HOME (replace path with your Java installation)
setx JAVA_HOME "C:\Program Files\OpenJDK\openjdk-11.0.19"
setx PATH "%PATH%;%JAVA_HOME%\bin"

# Restart terminal and verify
echo $env:JAVA_HOME
java -version
```

#### **macOS/Linux**
```bash
# Add to ~/.bashrc or ~/.zshrc
export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"  # Linux
export JAVA_HOME="/opt/homebrew/opt/openjdk@11"        # macOS Homebrew
export PATH="$JAVA_HOME/bin:$PATH"

# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Verify
echo $JAVA_HOME
java -version
```

---

## 🎭 **Step 3: Karate DSL Setup**

### **3.1 Download Karate JAR**
```bash
# Create tools directory
mkdir -p ./tools
cd ./tools

# Download latest Karate standalone JAR
# Method 1: Direct download
curl -L -o karate.jar https://github.com/karatelabs/karate/releases/latest/download/karate.jar

# Method 2: Using wget
wget -O karate.jar https://github.com/karatelabs/karate/releases/latest/download/karate.jar

# Method 3: Manual download
# Visit: https://github.com/karatelabs/karate/releases/latest
# Download karate.jar to ./tools/ directory
```

### **3.2 Verify Karate Installation**
```bash
# Test Karate JAR
java -jar ./tools/karate.jar --version

# Expected output: Karate version information
```

### **3.3 Set Karate Environment Variables**
```bash
# Add to environment variables
export KARATE_JAR_PATH="$(pwd)/tools/karate.jar"

# Windows PowerShell:
$env:KARATE_JAR_PATH = "$(Get-Location)\tools\karate.jar"
```

---

## ⚡ **Step 4: Gatling Setup (for Performance Testing)**

### **4.1 Download Gatling**
```bash
# Create gatling directory
mkdir -p ./tools/gatling
cd ./tools/gatling

# Download Gatling (choose appropriate version for your OS)
# Linux/macOS:
curl -L -o gatling.zip https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/3.9.5/gatling-charts-highcharts-bundle-3.9.5-bundle.zip

# Windows:
# Download from: https://gatling.io/open-source/
# Extract to ./tools/gatling/
```

### **4.2 Extract and Setup Gatling**
```bash
# Extract Gatling
unzip gatling.zip
mv gatling-charts-highcharts-bundle-* gatling-bundle

# Set permissions (Linux/macOS)
chmod +x gatling-bundle/bin/gatling.sh

# Set environment variable
export GATLING_HOME="$(pwd)/gatling-bundle"

# Windows PowerShell:
$env:GATLING_HOME = "$(Get-Location)\gatling-bundle"
```

---

## 🌐 **Step 5: Node.js and Playwright Setup**

### **5.1 Install Node.js**
```bash
# Verify Node.js installation
node --version
npm --version

# If not installed, download from: https://nodejs.org/
# Or use package managers:

# Windows (chocolatey):
choco install nodejs

# macOS (homebrew):
brew install node

# Linux (apt):
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### **5.2 Install Playwright**
```bash
# Install Playwright globally (optional, for CLI)
npm install -g playwright

# Install Playwright browsers
npx playwright install

# Verify installation
npx playwright --version
```

---

## 🐍 **Step 6: Python Dependencies Installation**

### **6.1 Install Required Python Packages**
```bash
# Make sure virtual environment is activated
# Navigate to project root directory

# Install from requirements.txt (if exists)
pip install -r requirements.txt

# Or install packages individually:
pip install fastmcp
pip install playwright
pip install python-dotenv
pip install aiohttp
pip install pydantic
pip install httpx
pip install PyYAML
pip install jira
pip install openai
```

### **6.2 Install Development Dependencies**
```bash
# Optional development tools
pip install pytest
pip install black  # Code formatter
pip install flake8  # Linting
pip install mypy    # Type checking
```

---

## 📁 **Step 7: Project Structure Setup**

### **7.1 Create Required Directories**
```bash
# Create all necessary directories
mkdir -p karate_features/{api,performance,integration}
mkdir -p karate_results
mkdir -p karate_mocks
mkdir -p performance_results
mkdir -p unified_test_results
mkdir -p test_suites/{api_only,web_only,end_to_end}
mkdir -p integration_tests/api_web_flows
mkdir -p screenshots
mkdir -p web_results
mkdir -p demo_results
mkdir -p tools
```

### **7.2 Create Environment Configuration**
Create `.env` file:
```env
# JIRA Configuration
JIRA_SERVER=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Karate Configuration
KARATE_JAR_PATH=./tools/karate.jar
KARATE_TIMEOUT=30000
KARATE_RETRY=0

# Gatling Configuration
GATLING_HOME=./tools/gatling/gatling-bundle

# Test Environment URLs
TEST_BASE_URL=https://test-api.example.com
STAGING_BASE_URL=https://staging-api.example.com
PROD_BASE_URL=https://api.example.com

# Browser Configuration
HEADLESS=true
BROWSER_TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true

# Performance Testing Defaults
DEFAULT_RPS=25
DEFAULT_DURATION=60
DEFAULT_RAMP_UP=15
```

---

## 🧪 **Step 8: Installation Verification**

### **8.1 Run System Check Script**
Create and run `system_check.py`:
```python
#!/usr/bin/env python3
"""System requirements verification script"""

import sys
import subprocess
import os
from pathlib import Path

def check_python():
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ required")
        return False
    return True

def check_java():
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"✅ Java: {version_line}")
            return True
    except:
        pass
    print("❌ Java not found - required for Karate DSL")
    return False

def check_node():
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js: {result.stdout.strip()}")
            return True
    except:
        pass
    print("❌ Node.js not found - required for Playwright")
    return False

def check_karate_jar():
    jar_path = os.getenv('KARATE_JAR_PATH', './tools/karate.jar')
    if Path(jar_path).exists():
        print(f"✅ Karate JAR found: {jar_path}")
        return True
    print(f"❌ Karate JAR not found: {jar_path}")
    return False

def check_environment():
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Environment file (.env) found")
        return True
    print("⚠️  Environment file (.env) not found - create from template")
    return False

if __name__ == "__main__":
    print("🔍 Enhanced MCP Test Orchestrator - System Check")
    print("="*50)
    
    checks = [
        check_python(),
        check_java(), 
        check_node(),
        check_karate_jar(),
        check_environment()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n📊 System Check Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All requirements met! Ready to run Enhanced MCP Test Orchestrator")
    else:
        print("⚠️  Some requirements missing. Please review setup steps above.")
```

### **8.2 Run Quick Demo Test**
```bash
# Run the system check
python system_check.py

# If all checks pass, run a quick demo
python demo_runner.py --demo api_basic

# Expected output: Successful API testing demo
```

---

## 🔧 **Step 9: Troubleshooting Common Issues**

### **9.1 SSL Certificate Issues**
```bash
# Problem: SSL certificate verification failed
# Solution 1: Update certificates
python -m pip install --upgrade certifi

# Solution 2: Bypass SSL (temporary, not recommended for production)
pip install --trusted-host pypi.org --trusted-host pypi.python.org package_name

# Solution 3: Corporate proxy/firewall
pip install --proxy http://proxy.company.com:8080 package_name
```

### **9.2 Java PATH Issues**
```bash
# Problem: Java not found in PATH
# Solution: Add Java to PATH
export PATH="$JAVA_HOME/bin:$PATH"

# Verify
which java
java -version
```

### **9.3 Karate JAR Download Issues**
```bash
# Problem: Cannot download Karate JAR
# Solution 1: Manual download
# Go to: https://github.com/karatelabs/karate/releases/latest
# Download karate.jar manually

# Solution 2: Use Maven (if available)
mvn dependency:get -Dartifact=com.intuit.karate:karate-junit5:1.4.1:jar:all -Ddest=./tools/karate.jar
```

### **9.4 Port Conflicts**
```bash
# Problem: Port 8080 already in use
# Solution: Change default ports in .env file
MOCK_SERVER_PORT=8081
KARATE_MOCK_PORT=8082
```

### **9.5 Permission Issues**
```bash
# Problem: Permission denied on scripts
# Solution: Set execute permissions (Linux/macOS)
chmod +x demo_runner.py
chmod +x enhanced_mcp_client_caller.py

# Windows: Run as Administrator if needed
```

---

## 📚 **Step 10: Next Steps and Usage**

### **10.1 Quick Start Commands**
```bash
# Run comprehensive demo
python demo_runner.py --demo all

# Test with real JIRA ticket (configure .env first)
python enhanced_mcp_client_caller.py --jira YOUR-TICKET-123

# Run specific test types
python enhanced_mcp_client_caller.py --jira YOUR-TICKET-123 --types api performance

# Interactive demo with verbose output
python demo_runner.py --demo integration_full --verbose
```

### **10.2 Configuration Files to Review**
- `.env` - Environment variables and API keys
- `pyproject.toml` - Python project configuration
- `karate_features/` - Generated Karate test files
- `unified_test_results/` - Test execution reports

### **10.3 Documentation References**
- `KARATE_ENHANCEMENT_GUIDE.md` - Comprehensive feature guide
- `DEMO_SCRIPTS.md` - Demo usage examples
- `README.md` - Project overview and basic usage

---

## 🎉 **Installation Complete!**

Your Enhanced MCP Test Orchestrator is now ready for:
- 🔧 **API Testing** with Karate DSL
- 🌐 **Web Automation** with Playwright  
- ⚡ **Performance Testing** with Gatling
- 🔄 **Integration Testing** with unified workflows
- 📋 **JIRA-Driven Testing** with intelligent test generation
- 🎭 **Service Virtualization** with mock servers

**Next:** Run `python demo_runner.py --demo all` to see all capabilities in action! 🚀