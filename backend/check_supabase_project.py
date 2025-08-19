#!/usr/bin/env python3
"""
Check Supabase Project Status
This script helps check if you have a Supabase project and guides you to get credentials.
"""

import webbrowser
import time

def check_supabase_project():
    """Check if user has a Supabase project and guide them"""
    print("🔍 Checking Supabase Project Status")
    print("=" * 40)
    
    print("\n📋 Let's check if you have a Supabase project set up.")
    print("This will help you get the correct credentials.")
    
    # Ask user if they have a project
    has_project = input("\nDo you have a Supabase project? (y/n): ").lower().strip()
    
    if has_project == 'y':
        print("\n✅ Great! You have a project.")
        print("Let's get your credentials:")
        
        # Open Supabase dashboard
        print("\n🔗 Opening Supabase dashboard...")
        webbrowser.open("https://supabase.com/dashboard")
        
        print("\n📝 Please follow these steps:")
        print("1. Click on your project")
        print("2. In the left sidebar, click 'Settings' → 'API'")
        print("3. Copy the Project URL and anon/public key")
        print("4. Come back here and run: python update_supabase_env.py")
        
    else:
        print("\n❌ You need to create a Supabase project first.")
        print("Let me help you create one:")
        
        # Open Supabase signup
        print("\n🔗 Opening Supabase signup...")
        webbrowser.open("https://supabase.com/dashboard")
        
        print("\n📝 Please follow these steps:")
        print("1. Sign up or log in to Supabase")
        print("2. Click 'New Project'")
        print("3. Choose your organization")
        print("4. Enter project details:")
        print("   - Name: hisabpro (or your preferred name)")
        print("   - Database Password: Create a strong password")
        print("   - Region: Choose closest to your users")
        print("5. Click 'Create new project'")
        print("6. Wait for the project to be created (2-3 minutes)")
        print("7. Go to Settings → API to get your credentials")
        print("8. Come back here and run: python update_supabase_env.py")
    
    print("\n⏳ Waiting 5 seconds before opening the dashboard...")
    time.sleep(5)
    
    print("\n🎯 Next Steps:")
    print("1. Get your Supabase credentials from the dashboard")
    print("2. Run: python update_supabase_env.py")
    print("3. Enter your credentials when prompted")
    print("4. Test the connection")

if __name__ == "__main__":
    check_supabase_project()
