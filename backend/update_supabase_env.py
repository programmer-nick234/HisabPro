#!/usr/bin/env python3
"""
Update Supabase Environment Variables
This script helps update the .env file with correct Supabase credentials.
"""

import os
from pathlib import Path

def update_supabase_env():
    """Update the .env file with correct Supabase credentials"""
    print("🔧 Updating Supabase Environment Variables")
    print("=" * 50)
    
    print("\n📋 You need to provide your actual Supabase credentials.")
    print("To get these credentials:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Click on your project")
    print("3. Go to Settings → API")
    print("4. Copy the Project URL and anon/public key")
    print()
    
    # Get user input
    supabase_url = input("Enter your Supabase Project URL (e.g., https://wetapqjagtipizvsbfok.supabase.co): ").strip()
    supabase_key = input("Enter your Supabase anon/public key: ").strip()
    
    if not supabase_url or not supabase_key:
        print("❌ Both URL and key are required!")
        return
    
    # Validate URL format
    if not supabase_url.startswith("https://") or not supabase_url.endswith(".supabase.co"):
        print("❌ Invalid Supabase URL format. Should be: https://[project-id].supabase.co")
        return
    
    # Validate key format
    if not supabase_key.startswith("eyJ"):
        print("❌ Invalid Supabase key format. Should start with 'eyJ'")
        return
    
    # Read current .env file
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return
    
    with open(".env", "r") as f:
        content = f.read()
    
    # Update the Supabase configuration lines
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('SUPABASE_URL='):
            updated_lines.append(f'SUPABASE_URL={supabase_url}')
        elif line.startswith('SUPABASE_KEY='):
            updated_lines.append(f'SUPABASE_KEY={supabase_key}')
        else:
            updated_lines.append(line)
    
    # Write back to .env file
    with open(".env", "w") as f:
        f.write('\n'.join(updated_lines))
    
    print("\n✅ .env file updated successfully!")
    print(f"   URL: {supabase_url}")
    print(f"   Key: {supabase_key[:20]}...")
    
    print("\n🧪 Testing connection...")
    
    # Test the connection
    try:
        from decouple import config
        from supabase import create_client, Client
        
        test_url = config('SUPABASE_URL')
        test_key = config('SUPABASE_KEY')
        
        if test_url == supabase_url and test_key == supabase_key:
            supabase: Client = create_client(test_url, test_key)
            print("✅ Supabase client created successfully")
            
            # Try a simple test query
            try:
                result = supabase.table('user_profiles').select('id').limit(1).execute()
                print("✅ Connection test successful!")
                return True
            except Exception as e:
                if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                    print("✅ Connection successful (tables not created yet)")
                    return True
                else:
                    print(f"❌ Connection test failed: {str(e)}")
                    return False
        else:
            print("❌ Environment variables not updated correctly")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        return False

if __name__ == "__main__":
    success = update_supabase_env()
    
    if success:
        print("\n🎉 Supabase configuration updated successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python setup_supabase_schema.py")
        print("2. Run: python test_supabase_integration.py")
        print("3. Start the application: python manage.py runserver")
    else:
        print("\n❌ Configuration update failed. Please check your credentials.")
