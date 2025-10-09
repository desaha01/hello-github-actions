"""
Quick SSL verification script - Run this AFTER repairing Python
"""
import sys

def test_ssl_after_repair():
    print("🔧 Testing Python 3.12.10 after repair...")
    print("=" * 50)
    
    try:
        import ssl
        print("✅ SSL import: SUCCESS!")
        print(f"📋 OpenSSL Version: {ssl.OPENSSL_VERSION}")
        
        # Test HTTPS connection
        import urllib.request
        response = urllib.request.urlopen('https://httpbin.org/get', timeout=10)
        print(f"✅ HTTPS connection: SUCCESS! (Status: {response.getcode()})")
        
        print(f"\n🎉 SSL IS FIXED! You can now:")
        print("   pip install -r requirements.txt")
        print("   python mcp_client_caller.py --help")
        print("   python mcpllm_bridge_client_caller.py --help")
        
        return True
        
    except Exception as e:
        print(f"❌ SSL still not working: {e}")
        print(f"\n💡 If repair didn't work, try:")
        print("1. Download Python 3.12.10 from python.org and reinstall")
        print("2. Or use conda: conda install python=3.12 openssl")
        return False

if __name__ == "__main__":
    test_ssl_after_repair()