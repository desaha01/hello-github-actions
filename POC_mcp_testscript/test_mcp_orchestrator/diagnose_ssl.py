"""
Quick SSL diagnostic and potential fix script
Run this to try fixing the current Python installation
"""
import sys
import os
from pathlib import Path

def diagnose_ssl_issue():
    print("🔍 Diagnosing Python SSL Issue")
    print("=" * 40)
    
    # Check Python version and location
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Python Path: {sys.path[0]}")
    
    # Check if SSL module files exist
    python_dir = Path(sys.executable).parent
    dll_dir = python_dir / "DLLs"
    
    print(f"\nPython Installation: {python_dir}")
    print(f"DLLs Directory: {dll_dir}")
    
    ssl_files = [
        "_ssl.pyd",
        "libcrypto-3.dll", 
        "libssl-3.dll",
        "libcrypto-1_1.dll",
        "libssl-1_1.dll"
    ]
    
    print(f"\nSSL Files Check:")
    for file in ssl_files:
        file_path = dll_dir / file
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        print(f"  {file:<20} {'✅' if exists else '❌'} {size:>10} bytes")
    
    # Try importing SSL step by step
    print(f"\nSSL Import Test:")
    try:
        import _ssl
        print("  _ssl import: ✅")
    except Exception as e:
        print(f"  _ssl import: ❌ {e}")
    
    try:
        import ssl
        print(f"  ssl import: ✅")
        print(f"  SSL Version: {ssl.OPENSSL_VERSION}")
    except Exception as e:
        print(f"  ssl import: ❌ {e}")
    
    # Check environment variables
    print(f"\nEnvironment Variables:")
    ssl_env_vars = ['SSL_CERT_FILE', 'SSL_CERT_DIR', 'REQUESTS_CA_BUNDLE', 'CURL_CA_BUNDLE']
    for var in ssl_env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"  {var:<20} = {value}")
    
    # Test HTTPS connection
    print(f"\nHTTPS Connection Test:")
    try:
        import urllib.request
        response = urllib.request.urlopen('https://httpbin.org/get', timeout=10)
        print(f"  HTTPS test: ✅ Status {response.getcode()}")
    except Exception as e:
        print(f"  HTTPS test: ❌ {e}")

def suggest_fixes():
    print(f"\n💡 Suggested Fixes:")
    print("=" * 40)
    
    print("1. IMMEDIATE FIX - Install Python from python.org:")
    print("   • Go to https://www.python.org/downloads/windows/")
    print("   • Download 'Windows installer (64-bit)' for Python 3.11.x")
    print("   • Run installer with 'Add to PATH' checked")
    print("   • This includes proper SSL/TLS support")
    
    print(f"\n2. ALTERNATIVE - Try to repair current installation:")
    print("   • Go to 'Add or Remove Programs'")
    print("   • Find 'Python 3.12.10'")
    print("   • Click 'Modify' → 'Repair'")
    
    print(f"\n3. MANUAL SSL FIX - Download OpenSSL libraries:")
    print("   • Download from https://slproweb.com/products/Win32OpenSSL.html")
    print("   • Install 'Win64 OpenSSL v3.0.x'")
    print("   • Copy DLL files to Python DLLs directory")
    
    print(f"\n4. WORKAROUND - Use conda/miniconda:")
    print("   • Download Miniconda from https://docs.conda.io/en/latest/miniconda.html")
    print("   • conda create -n mcp python=3.11")
    print("   • conda activate mcp")
    print("   • pip install -r requirements.txt")

if __name__ == "__main__":
    try:
        diagnose_ssl_issue()
        suggest_fixes()
        
        print(f"\n🚀 RECOMMENDED ACTION:")
        print("Install fresh Python from python.org - it's the fastest solution!")
        print("Then run: .\\setup_after_python_fix.ps1")
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        print("This confirms the SSL issue - please install Python from python.org")