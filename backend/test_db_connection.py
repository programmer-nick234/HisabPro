#!/usr/bin/env python3
"""
Database Connection Test Script for Railway Deployment
This script tests the MongoDB connection and basic functionality.
"""

import os
import sys
from decouple import config
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_mongodb_connection():
    """Test MongoDB connection and basic operations."""
    print("🔍 Testing MongoDB Connection...")
    
    try:
        # Get MongoDB URI from environment
        mongodb_uri = config('MONGODB_URI', default='')
        database_name = config('MONGODB_DATABASE', default='hisabpro')
        
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in environment variables")
            return False
        
        print(f"📡 Connecting to MongoDB: {mongodb_uri.split('@')[1] if '@' in mongodb_uri else 'local'}")
        
        # Create client with timeout
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client[database_name]
        print(f"✅ Database '{database_name}' accessible")
        
        # Test basic operations
        test_collection = db['test_connection']
        
        # Insert test document
        test_doc = {'test': True, 'message': 'Connection test successful'}
        result = test_collection.insert_one(test_doc)
        print(f"✅ Insert operation successful: {result.inserted_id}")
        
        # Find test document
        found_doc = test_collection.find_one({'test': True})
        if found_doc:
            print("✅ Find operation successful")
        
        # Delete test document
        delete_result = test_collection.delete_one({'test': True})
        print(f"✅ Delete operation successful: {delete_result.deleted_count} document(s) deleted")
        
        # Close connection
        client.close()
        print("✅ MongoDB connection test completed successfully!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB server selection timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("\n🔍 Testing Environment Variables...")
    
    required_vars = [
        'SECRET_KEY',
        'MONGODB_URI',
        'MONGODB_DATABASE',
        'RAZORPAY_KEY_ID',
        'RAZORPAY_KEY_SECRET',
    ]
    
    optional_vars = [
        'REDIS_URL',
        'EMAIL_HOST',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        value = config(var, default='')
        if not value:
            missing_required.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)} (length: {len(value)})")
    
    for var in optional_vars:
        value = config(var, default='')
        if not value:
            missing_optional.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)} (length: {len(value)})")
    
    if missing_required:
        print(f"❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {', '.join(missing_optional)}")
    
    print("✅ Environment variables test completed!")
    return True

def test_django_settings():
    """Test Django settings import and basic configuration."""
    print("\n🔍 Testing Django Settings...")
    
    try:
        import django
        from django.conf import settings
        
        # Configure Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
        django.setup()
        
        # Test basic settings
        print(f"✅ Django version: {django.get_version()}")
        print(f"✅ DEBUG mode: {settings.DEBUG}")
        print(f"✅ Allowed hosts: {settings.ALLOWED_HOSTS}")
        print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")
        
        # Test MongoDB settings
        if hasattr(settings, 'MONGODB_URI'):
            print(f"✅ MongoDB URI configured: {'*' * len(settings.MONGODB_URI)}")
        else:
            print("⚠️  MongoDB URI not found in settings")
        
        print("✅ Django settings test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Django settings test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 HisabPro Railway Deployment Test")
    print("=" * 50)
    
    # Test environment variables
    env_test = test_environment_variables()
    
    # Test Django settings
    django_test = test_django_settings()
    
    # Test MongoDB connection
    db_test = test_mongodb_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Environment Variables: {'✅ PASS' if env_test else '❌ FAIL'}")
    print(f"Django Settings: {'✅ PASS' if django_test else '❌ FAIL'}")
    print(f"MongoDB Connection: {'✅ PASS' if db_test else '❌ FAIL'}")
    
    if all([env_test, django_test, db_test]):
        print("\n🎉 All tests passed! Your Railway deployment should work correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the configuration before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
