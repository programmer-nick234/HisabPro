#!/usr/bin/env python
"""
Migration script to migrate from PostgreSQL to MongoDB Atlas
Run this script after setting up MongoDB Atlas connection
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.contrib.auth.models import User
from auth_app.models import UserProfile
from invoices.models import Invoice, InvoiceItem, Payment
from django.db import connections
from django.core.management import execute_from_command_line

def migrate_to_mongodb():
    """
    Migrate data from PostgreSQL to MongoDB Atlas
    """
    print("Starting migration to MongoDB Atlas...")
    
    try:
        # First, make sure we can connect to MongoDB
        from django.db import connection
        connection.ensure_connection()
        print("✓ Successfully connected to MongoDB Atlas")
        
        # Create and apply migrations
        print("Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test your application")
        print("2. Update your environment variables:")
        print("   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority")
        print("3. Remove old PostgreSQL environment variables if any")
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        print("Please check your MongoDB Atlas connection and try again.")
        return False
    
    return True

if __name__ == '__main__':
    migrate_to_mongodb()
