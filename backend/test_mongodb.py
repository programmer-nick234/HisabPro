#!/usr/bin/env python
"""
Test script to verify MongoDB Atlas connection
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        print("Testing MongoDB Atlas connection...")
        
        # Ensure connection is established
        mongodb_service.connect()
        
        if not mongodb_service._connected:
            print("✗ Failed to connect to MongoDB Atlas")
            return False
        
        # Test basic connection
        mongodb_service.client.admin.command('ping')
        print("✓ Successfully connected to MongoDB Atlas")
        
        # Test database access
        db_list = mongodb_service.client.list_database_names()
        print(f"✓ Available databases: {db_list}")
        
        # Test collection creation
        test_collection = mongodb_service.db.test_collection
        test_doc = {"test": "data", "timestamp": "2024-01-01"}
        result = test_collection.insert_one(test_doc)
        print(f"✓ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test data
        test_collection.delete_one({"_id": result.inserted_id})
        print("✓ Test document cleaned up")
        
        print("\n🎉 MongoDB Atlas connection test successful!")
        return True
        
    except Exception as e:
        print(f"✗ MongoDB connection test failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_mongodb_connection()
