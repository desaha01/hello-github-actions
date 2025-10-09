"""
Python 3.12 SSL Diagnostic and Fix Tool
Diagnoses SSL issues and attempts repairs for existing Python 3.12 installation
"""
import os
import sys
import subprocess
from pathlib import Path

def diagnose_python_installation():
    """Diagnose the current Python installation for SSL issues."""
    print("🔍 Diagnosing Python 3.12.10 SSL Installation...")
    print("=" * 60)
    
    python_path = Path(sys.executable).parent
    print(f"📁 Python Location: {python_path}")
    print(f"🐍 Python Version: {sys.version}")
    
    # Check for required DLL files
    dlls_to_check = [
        "libcrypto-3.dll",
        "libssl-3.dll", 
        "libcrypto-3-x64.dll",
        "libssl-3-x64.dll"
    ]
    
    print(f"\n🔍 Checking for OpenSSL DLL files in main directory:")
    missing_dlls = []
    
    for dll in dlls_to_check:
        dll_path = python_path / dll
        if dll_path.exists():
            size = dll_path.stat().st_size
            print(f"   ✅ {dll} - Found ({size:,} bytes)")
        else:
            print(f"   ❌ {dll} - Missing")
            missing_dlls.append(dll)
    
    # Check DLLs directory
    dlls_dir = python_path / "DLLs"
    print(f"\n📁 Checking DLLs directory: {dlls_dir}")
    if dlls_dir.exists():
        dll_files = list(dlls_dir.glob("*.dll"))
        pyd_files = list(dlls_dir.glob("*.pyd"))
        print(f"   Found {len(dll_files)} DLL files and {len(pyd_files)} PYD files")
        
        # Look specifically for SSL-related files
        ssl_files = []
        for file in dlls_dir.iterdir():
            if any(keyword in file.name.lower() for keyword in ['ssl', 'crypto', 'openssl']):
                size = file.stat().st_size if file.is_file() else 0
                ssl_files.append(f"   🔍 {file.name} ({size:,} bytes)")
        
        if ssl_files:
            print("   SSL-related files found:")
            for file_info in ssl_files:
                print(file_info)
        else:
            print("   ❌ No SSL-related files found in DLLs directory")
    else:
        print("   ❌ DLLs directory not found!")
    
    return missing_dlls, python_path, dlls_dir

def try_ssl_import():
    """Try to import SSL and see what happens."""
    print(f"\n🧪 Testing SSL Import:")
    try:
        import ssl
        print(f"   ✅ SSL imported successfully!")
        print(f"   📋 OpenSSL Version: {ssl.OPENSSL_VERSION}")
        print(f"   🔐 SSL Context: {ssl.create_default_context()}")
        return True
    except ImportError as e:
        print(f"   ❌ SSL import failed: {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  SSL import error: {e}")
        return False

def test_https_connection():
    """Test if HTTPS connections work."""
    print(f"\n🌐 Testing HTTPS Connection:")
    try:
        import urllib.request
        response = urllib.request.urlopen('https://httpbin.org/get', timeout=5)
        print(f"   ✅ HTTPS connection works! Status: {response.getcode()}")
        return True
    except Exception as e:
        print(f"   ❌ HTTPS connection failed: {e}")
        return False

def try_pip_with_trusted_hosts():
    """Try to install packages using trusted hosts to bypass SSL."""
    print(f"\n📦 Attempting package installation with SSL bypass...")
    
    test_package = "python-dotenv"
    cmd = [
        sys.executable, "-m", "pip", "install", 
        test_package,
        "--trusted-host", "pypi.org",
        "--trusted-host", "pypi.python.org", 
        "--trusted-host", "files.pythonhosted.org",
        "--upgrade"
    ]
    
    try:
        print(f"   🔄 Installing {test_package} with trusted hosts...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"   ✅ {test_package} installed successfully!")
            print("   🎉 SSL bypass method works!")
            return True
        else:
            print(f"   ❌ Installation failed:")
            print(f"   {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Installation timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error during installation: {e}")
        return False

def suggest_fixes(missing_dlls, python_path):
    """Suggest fixes based on what's missing."""
    print(f"\n💡 Suggested Fixes for Python 3.12.10:")
    print("=" * 50)
    
    print("🔧 Method 1: Repair Python Installation (RECOMMENDED)")
    print("   1. Press Win+R, type 'appwiz.cpl', press Enter")
    print("   2. Find 'Python 3.12.10 (64-bit)' in the list")
    print("   3. Click on it and select 'Change'")
    print("   4. Click 'Modify' then 'Repair'")
    print("   5. Wait for repair to complete")
    
    print(f"\n🔧 Method 2: Reinstall Python 3.12")
    print("   1. Go to https://www.python.org/ftp/python/3.12.10/")
    print("   2. Download 'python-3.12.10-amd64.exe'")
    print("   3. Run installer and choose 'Repair' option")
    
    print(f"\n🔧 Method 3: Manual OpenSSL Installation")
    print("   1. Download OpenSSL from https://slproweb.com/products/Win32OpenSSL.html")
    print("   2. Install 'Win64 OpenSSL v3.0.x'")
    print("   3. Copy DLLs to Python directory")
    
    print(f"\n🔧 Method 4: Use Conda/Miniconda")
    print("   1. Install Miniconda")
    print("   2. conda create -n mcp python=3.12")
    print("   3. conda activate mcp")
    print("   4. conda install openssl")

def provide_workaround():
    """Provide immediate workaround for package installation."""
    print(f"\n🚀 IMMEDIATE WORKAROUND:")
    print("=" * 40)
    print("If SSL repair doesn't work immediately, you can still install packages:")
    print()
    print("# Install packages with SSL bypass:")
    print("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org python-dotenv")
    print("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org loguru")
    print("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fastmcp")
    print()
    print("# Or install all at once:")
    print("pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt")

def main():
    """Main diagnostic function."""
    print("🐍 Python 3.12.10 SSL Diagnostic and Fix Tool")
    print("=" * 60)
    
    # Run diagnostics
    missing_dlls, python_path, dlls_dir = diagnose_python_installation()
    ssl_works = try_ssl_import()
    https_works = test_https_connection()
    
    if not ssl_works:
        print(f"\n❌ SSL is not working properly")
        
        # Try the trusted hosts method
        bypass_works = try_pip_with_trusted_hosts()
        
        if bypass_works:
            print(f"\n🎉 Good news! Package installation works with SSL bypass")
            provide_workaround()
        else:
            suggest_fixes(missing_dlls, python_path)
    else:
        print(f"\n🎉 SSL is working perfectly!")
        print("   You can now install packages normally:")
        print("   pip install -r requirements.txt")
    
    print(f"\n📍 Your Python Details:")
    print(f"   Executable: {sys.executable}")
    print(f"   Version: {sys.version}")
    print(f"   Location: {python_path}")

if __name__ == "__main__":
    main()