# SSL Fix Guide for Python Installation

## Problem Diagnosed ❌
Your current Python 3.12.10 installation is missing SSL support:
- Location: C:\Users\DesaHa01\AppData\Local\Programs\Python\Python312\
- Issue: `ImportError: DLL load failed while importing _ssl`
- Impact: Cannot install packages from PyPI (HTTPS connections fail)

## Solution: Install Official Python from python.org ✅

### Step 1: Download Python from python.org
1. Go to https://www.python.org/downloads/windows/
2. Download "Windows installer (64-bit)" for Python 3.11 or 3.12
3. Choose the latest stable version (recommended: Python 3.11.x for compatibility)

### Step 2: Install Python with SSL Support
1. Run the downloaded installer
2. ⚠️ **IMPORTANT**: Check "Add python.exe to PATH" 
3. Click "Customize installation"
4. Ensure these options are checked:
   - ✅ pip
   - ✅ tcl/tk and IDLE
   - ✅ Python test suite
   - ✅ py launcher
   - ✅ for all users (requires admin)

5. In Advanced Options:
   - ✅ Install for all users
   - ✅ Associate files with Python
   - ✅ Create shortcuts for installed applications
   - ✅ Add Python to environment variables
   - ✅ Precompile standard library

6. Choose installation directory (default is fine)
7. Click "Install"

### Step 3: Verify New Installation
Open a NEW PowerShell window and run:
```powershell
python --version
python -c "import ssl; print('SSL available:', ssl.OPENSSL_VERSION)"
where python
```

### Step 4: Create New Virtual Environment
```powershell
cd "C:\Users\DesaHa01\OneDrive - Reed Elsevier Group ICO Reed Elsevier Inc\Desktop\Python_Test\POC_mcp_testscript\POC_mcp_testscript\test_mcp_orchestrator"

# Remove old broken virtual environment
Remove-Item .venv -Recurse -Force

# Create new virtual environment with SSL-enabled Python
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies
```powershell
# With virtual environment activated:
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install
```

### Step 6: Test Your Application
```powershell
# Test the original scripts:
python mcp_client_caller.py --help
python mcpllm_bridge_client_caller.py --help

# Run with JIRA ticket:
python mcp_client_caller.py --jira TEST-1234 --debug
```

## Alternative: Quick Fix for Current Installation

If you prefer to fix the current installation:

### Option A: Repair Current Installation
1. Go to "Add or Remove Programs" in Windows
2. Find "Python 3.12.10" 
3. Click "Modify"
4. Choose "Repair" installation
5. This may restore missing SSL libraries

### Option B: Install Missing SSL Libraries
```powershell
# Try installing OpenSSL manually
# Download from: https://slproweb.com/products/Win32OpenSSL.html
# Install "Win64 OpenSSL v3.0.x" version
```

## Troubleshooting

### If PowerShell execution policy prevents virtual environment activation:
```powershell
# Run as Administrator and execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If PATH is not updated after Python installation:
1. Restart PowerShell/VS Code completely
2. Or manually add Python to PATH:
   - Windows Key + R → "sysdm.cpl" → Advanced → Environment Variables
   - Add Python installation directory to PATH

### Verify SSL after fixes:
```powershell
python -c "import ssl, urllib.request; print('SSL Test:', urllib.request.urlopen('https://pypi.org').getcode() == 200)"
```

## Expected Result After Fix ✅
```powershell
PS> python --version
Python 3.11.x (or 3.12.x)

PS> python -c "import ssl; print('SSL available:', ssl.OPENSSL_VERSION)"
SSL available: OpenSSL 3.0.x

PS> pip install loguru
Collecting loguru...
Successfully installed loguru-x.x.x
```

Your MCP Test Orchestrator will then work perfectly! 🚀