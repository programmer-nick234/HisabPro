#!/usr/bin/env python
"""
Diagnose Python Errors Script
"""

import os
import sys
import django

def check_python_version():
    """Check Python version"""
    print("🐍 Python Version Check:")
    print(f"   Python Version: {sys.version}")
    print(f"   Python Path: {sys.executable}")
    print()

def check_django_setup():
    """Check Django setup"""
    print("🔧 Django Setup Check:")
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
        django.setup()
        print("   ✅ Django setup successful")
        
        # Check settings
        from django.conf import settings
        print(f"   ✅ DEBUG: {settings.DEBUG}")
        print(f"   ✅ INSTALLED_APPS: {len(settings.INSTALLED_APPS)} apps")
        
    except Exception as e:
        print(f"   ❌ Django setup failed: {str(e)}")
    print()

def check_mongodb_connection():
    """Check MongoDB connection"""
    print("🗄️ MongoDB Connection Check:")
    try:
        from lib.mongodb import mongodb_service
        mongodb_service.connect()
        if mongodb_service._connected:
            print("   ✅ MongoDB connection successful")
        else:
            print("   ❌ MongoDB connection failed")
    except Exception as e:
        print(f"   ❌ MongoDB connection error: {str(e)}")
    print()

def check_imports():
    """Check all imports"""
    print("📦 Import Check:")
    
    imports_to_test = [
        ("invoices.mongodb_models", "MongoDBInvoice"),
        ("invoices.mongodb_serializers", "MongoDBInvoiceSerializer"),
        ("invoices.mongodb_views_v2", "MongoDBInvoiceListCreateView"),
        ("lib.mongodb", "mongodb_service"),
    ]
    
    for module, class_name in imports_to_test:
        try:
            module_obj = __import__(module, fromlist=[class_name])
            class_obj = getattr(module_obj, class_name)
            print(f"   ✅ {module}.{class_name}")
        except Exception as e:
            print(f"   ❌ {module}.{class_name}: {str(e)}")
    print()

def check_api_endpoints():
    """Check API endpoints"""
    print("🌐 API Endpoints Check:")
    try:
        import requests
        
        base_url = "http://localhost:8000"
        endpoints = [
            "/",
            "/api/auth/login/",
            "/api/mongodb/invoices/",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code in [200, 401, 403, 404]:
                    print(f"   ✅ {endpoint} - Status: {response.status_code}")
                else:
                    print(f"   ⚠️ {endpoint} - Status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"   ❌ {endpoint} - Server not running")
            except Exception as e:
                print(f"   ❌ {endpoint} - Error: {str(e)}")
                
    except ImportError:
        print("   ❌ requests module not available")
    print()

def main():
    """Main diagnostic function"""
    print("🔍 HisabPro Error Diagnosis")
    print("=" * 50)
    
    check_python_version()
    check_django_setup()
    check_mongodb_connection()
    check_imports()
    check_api_endpoints()
    
    print("🎯 Diagnosis Complete!")
    print("\n💡 If you're seeing errors in your IDE:")
    print("   1. Make sure your IDE is using the correct Python interpreter (venv)")
    print("   2. Set DJANGO_SETTINGS_MODULE=hisabpro.settings in your IDE")
    print("   3. Restart your IDE after activating the virtual environment")
    print("   4. Check that all dependencies are installed: pip install -r requirements.txt")

if __name__ == '__main__':
    main()
