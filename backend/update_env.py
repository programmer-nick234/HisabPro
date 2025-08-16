#!/usr/bin/env python3
"""
Script to update .env file with actual MongoDB connection string
"""
import os
import re

def update_mongodb_uri():
    """Update the MongoDB URI in .env file"""
    
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env file not found! Run setup_env.py first.")
        return
    
    print("🔧 MongoDB Atlas Connection Setup")
    print("=" * 40)
    print()
    print("You need to provide your MongoDB Atlas connection string.")
    print("To get this:")
    print("1. Go to MongoDB Atlas dashboard")
    print("2. Click 'Connect' on your cluster")
    print("3. Choose 'Connect your application'")
    print("4. Copy the connection string")
    print()
    
    # Get the actual connection string
    current_uri = input("Enter your MongoDB Atlas connection string: ").strip()
    
    if not current_uri:
        print("❌ No connection string provided!")
        return
    
    if not current_uri.startswith('mongodb+srv://'):
        print("❌ Invalid MongoDB connection string format!")
        print("Should start with: mongodb+srv://")
        return
    
    try:
        # Read the current .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace the MongoDB URI
        pattern = r'MONGODB_URI=.*'
        replacement = f'MONGODB_URI={current_uri}'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            # Add the MongoDB URI if it doesn't exist
            new_content = content + f'\n{replacement}\n'
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.write(new_content)
        
        print("✅ MongoDB URI updated successfully!")
        print()
        print("📝 Next steps:")
        print("1. Test your application: python manage.py runserver")
        print("2. If you have existing data, run the migration script")
        print("3. Never commit .env file to version control!")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    update_mongodb_uri()
