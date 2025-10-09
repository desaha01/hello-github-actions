# PowerShell script to set up MCP Test Orchestrator after Python SSL fix
# Save as: setup_after_python_fix.ps1
# Run with: .\setup_after_python_fix.ps1

Write-Host "🚀 MCP Test Orchestrator Setup Script" -ForegroundColor Green
Write-Host "=" * 50

# Check if Python has SSL support
Write-Host "1. Checking Python SSL support..." -ForegroundColor Yellow
try {
    $sslTest = python -c "import ssl; print('SSL available:', ssl.OPENSSL_VERSION)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ SSL is available: $sslTest" -ForegroundColor Green
    } else {
        Write-Host "❌ SSL not available. Please install Python from python.org first!" -ForegroundColor Red
        Write-Host "📖 See SSL_FIX_GUIDE.md for instructions" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Python not found or SSL not available" -ForegroundColor Red
    exit 1
}

# Show current Python info
Write-Host "`n2. Current Python information:" -ForegroundColor Yellow
python --version
python -c "import sys; print('Location:', sys.executable)"

# Remove old virtual environment if it exists
Write-Host "`n3. Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "🗑️  Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item ".venv" -Recurse -Force -ErrorAction SilentlyContinue
}

# Create new virtual environment
Write-Host "📁 Creating new virtual environment..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Try to activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
try {
    & ".\.venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Could not activate virtual environment (PowerShell execution policy)" -ForegroundColor Yellow
    Write-Host "💡 Run as Administrator: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host "📖 Or use: .\.venv\Scripts\python.exe instead of 'python'" -ForegroundColor Cyan
}

# Upgrade pip
Write-Host "`n4. Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Pip upgrade had issues, but continuing..." -ForegroundColor Yellow
}

# Install requirements
Write-Host "`n5. Installing Python packages..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python packages installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install some packages" -ForegroundColor Red
        Write-Host "💡 Try manually: pip install loguru fastmcp mcp openai playwright python-dotenv" -ForegroundColor Cyan
    }
} else {
    Write-Host "📦 Installing core packages manually..." -ForegroundColor Yellow
    pip install loguru fastmcp mcp openai playwright python-dotenv pydantic aiohttp requests
}

# Install Playwright browsers
Write-Host "`n6. Installing Playwright browsers..." -ForegroundColor Yellow
playwright install
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Playwright browsers installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Playwright browsers installation had issues" -ForegroundColor Yellow
}

# Verify installation
Write-Host "`n7. Verifying installation..." -ForegroundColor Yellow
try {
    python -c "import loguru; import fastmcp; import mcp; print('✅ Core packages imported successfully')"
    Write-Host "✅ Package verification successful" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Some packages may not be properly installed" -ForegroundColor Yellow
}

# Test the applications
Write-Host "`n8. Testing applications..." -ForegroundColor Yellow
Write-Host "📋 Testing MCP Client help..." -ForegroundColor Cyan
python mcp_client_caller.py --help
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MCP Client working" -ForegroundColor Green
} else {
    Write-Host "❌ MCP Client has issues" -ForegroundColor Red
}

Write-Host "`n📋 Testing LLM Bridge help..." -ForegroundColor Cyan
python mcpllm_bridge_client_caller.py --help  
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ LLM Bridge working" -ForegroundColor Green
} else {
    Write-Host "❌ LLM Bridge has issues" -ForegroundColor Red
}

# Final instructions
Write-Host "`n" + "=" * 50 -ForegroundColor Green
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Copy .env.example to .env: Copy-Item .env.example .env" -ForegroundColor Cyan
Write-Host "2. Edit .env file with your real JIRA and Azure OpenAI credentials" -ForegroundColor Cyan
Write-Host "3. Run: python mcp_client_caller.py --jira YOUR-TICKET-KEY" -ForegroundColor Cyan
Write-Host "4. Or run: python mcpllm_bridge_client_caller.py" -ForegroundColor Cyan

Write-Host "`n🔧 If activation failed, use:" -ForegroundColor Yellow
Write-Host "   .\.venv\Scripts\python.exe mcp_client_caller.py --help" -ForegroundColor Cyan

Write-Host "`n📖 For troubleshooting, see SSL_FIX_GUIDE.md" -ForegroundColor Yellow