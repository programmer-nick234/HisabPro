#!/usr/bin/env python
"""
Create a regular user account
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.contrib.auth.models import User

def create_user():
    """Create a regular user account"""
    print("👤 Creating Regular User Account")
    print("=" * 40)
    
    # Check if user already exists
    username = "user"
    email = "user@example.com"
    
    try:
        existing_user = User.objects.get(username=username)
        print(f"✅ User '{username}' already exists!")
        print(f"   Username: {existing_user.username}")
        print(f"   Email: {existing_user.email}")
        print(f"   Is Staff: {existing_user.is_staff}")
        print(f"   Is Superuser: {existing_user.is_superuser}")
        return
    except User.DoesNotExist:
        pass
    
    # Create new user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password="user123",
            first_name="Regular",
            last_name="User"
        )
        
        print(f"✅ User created successfully!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: user123")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")

def list_users():
    """List all users in the system"""
    print("\n📋 All Users in System")
    print("=" * 40)
    
    users = User.objects.all()
    for user in users:
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print()

def main():
    """Main function"""
    print("🔐 User Management")
    print("=" * 50)
    
    create_user()
    list_users()
    
    print("=" * 50)
    print("💡 Login Credentials:")
    print("   Regular User:")
    print("     Username: user")
    print("     Password: user123")
    print("   Admin User:")
    print("     Username: admin")
    print("     Password: admin123")

if __name__ == '__main__':
    main()
