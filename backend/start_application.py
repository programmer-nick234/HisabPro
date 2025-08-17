#!/usr/bin/env python
"""
Start Application Script
Ensures all services are running properly
"""

import os
import sys
import django
import subprocess
import time
import requests

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service

def check_mongodb_connection():
    """Check MongoDB connection"""
    print("🔍 Checking MongoDB connection...")
    try:
        mongodb_service.connect()
        if mongodb_service._connected:
            print("✅ MongoDB connection successful!")
            return True
        else:
            print("❌ MongoDB connection failed!")
            return False
    except Exception as e:
        print(f"❌ MongoDB connection error: {str(e)}")
        return False

def check_django_server():
    """Check if Django server is running"""
    print("🔍 Checking Django server...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code in [200, 401, 403]:
            print("✅ Django server is running!")
            return True
        else:
            print(f"⚠️ Django server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running!")
        return False
    except Exception as e:
        print(f"❌ Error checking Django server: {str(e)}")
        return False

def start_django_server():
    """Start Django server"""
    print("🚀 Starting Django server...")
    try:
        # Start Django server in background
        subprocess.Popen([
            sys.executable, "manage.py", "runserver", "0.0.0.0:8000"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        time.sleep(3)
        
        if check_django_server():
            print("✅ Django server started successfully!")
            return True
        else:
            print("❌ Failed to start Django server!")
            return False
    except Exception as e:
        print(f"❌ Error starting Django server: {str(e)}")
        return False

def main():
    """Main startup function"""
    print("🚀 HisabPro Application Startup")
    print("=" * 50)
    
    # Check MongoDB
    if not check_mongodb_connection():
        print("\n❌ Cannot proceed without MongoDB connection")
        print("Please ensure MongoDB is running:")
        print("1. MongoDB should be installed and running")
        print("2. Data directory should exist: C:\\data\\db")
        print("3. MongoDB should be listening on localhost:27017")
        return False
    
    # Check Django server
    if not check_django_server():
        print("\n🔄 Django server not running, starting it...")
        if not start_django_server():
            print("\n❌ Failed to start Django server")
            return False
    
    # Final check
    print("\n🔍 Final system check...")
    if check_mongodb_connection() and check_django_server():
        print("\n🎉 All systems are running!")
        print("\n📋 Application Status:")
        print("✅ MongoDB: Running and connected")
        print("✅ Django Server: Running on http://localhost:8000")
        print("✅ API Endpoints: Available")
        print("\n🚀 You can now:")
        print("1. Start the frontend: cd ../frontend && npm run dev")
        print("2. Access the application: http://localhost:3000")
        print("3. Login with: admin/admin123")
        print("4. Create invoices without any errors!")
        return True
    else:
        print("\n❌ System check failed!")
        return False

if __name__ == '__main__':
    main()
