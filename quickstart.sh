#!/bin/bash
# Quick start script for Karate MCP Server

echo "============================================"
echo "Karate MCP Server - Quick Start"
echo "============================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is not installed!"; exit 1; }
echo "✓ Python 3 is installed"
echo ""

# Check Java version
echo "Checking Java version..."
java -version 2>&1 | grep -q "version" && echo "✓ Java is installed" || { echo "⚠ Java is not installed. Required for running Karate tests."; }
echo ""

# Check Maven
echo "Checking Maven..."
mvn -version 2>&1 | grep -q "Apache Maven" && echo "✓ Maven is installed" || { echo "⚠ Maven is not installed. Required for running Karate tests."; }
echo ""

# Install Python dependencies (if any)
echo "Installing Python dependencies..."
if [ -f "requirements-karate-mcp.txt" ]; then
    pip3 install -r requirements-karate-mcp.txt 2>/dev/null || true
    echo "✓ Dependencies checked"
else
    echo "⚠ requirements-karate-mcp.txt not found"
fi
echo ""

# Make scripts executable
echo "Making scripts executable..."
chmod +x karate_mcp_server.py test_karate_mcp.py 2>/dev/null || true
echo "✓ Scripts are executable"
echo ""

# Run test script
echo "Running MCP server test..."
echo "============================================"
python3 test_karate_mcp.py
echo "============================================"
echo ""

echo "Quick start complete!"
echo ""
echo "Next steps:"
echo "  1. Review KARATE-MCP-README.md for detailed documentation"
echo "  2. Start the server: python3 karate_mcp_server.py"
echo "  3. List available tools: python3 karate_mcp_server.py --list-tools"
echo "  4. Add your Karate feature files to: karate-tests/features/"
echo ""
echo "For Maven/Java setup, see karate-tests/pom.xml"
echo "============================================"
