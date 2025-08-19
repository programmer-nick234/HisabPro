#!/usr/bin/env python3
"""
Fix Supabase URL Configuration
This script helps fix the Supabase URL configuration issue.
"""

import os
from pathlib import Path

def fix_supabase_config():
    """Fix the Supabase configuration"""
    print("🔧 Fixing Supabase Configuration")
    print("=" * 40)
    
    print("\n❌ Issue detected: You provided the dashboard URL instead of the project URL")
    print("\n📋 Here's how to get the correct Supabase credentials:")
    
    print("\n1. Go to https://supabase.com/dashboard")
    print("2. Click on your project (or create a new one)")
    print("3. In the left sidebar, click 'Settings' → 'API'")
    print("4. You'll see two important values:")
    print("   - Project URL: https://[project-id].supabase.co")
    print("   - anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    
    print("\n🔗 The Project URL should look like:")
    print("   https://wetapqjagtipizvsbfok.supabase.co")
    print("   (NOT https://supabase.com/dashboard/project/wetapqjagtipizvsbfok)")
    
    print("\n📝 Please update your .env file with the correct values:")
    
    # Read current .env file
    env_path = Path(".env")
    if env_path.exists():
        with open(".env", "r") as f:
            content = f.read()
        
        # Show current content
        print("\nCurrent .env content:")
        print("-" * 30)
        for line in content.split('\n'):
            if line.startswith('SUPABASE_URL=') or line.startswith('SUPABASE_KEY='):
                if line.startswith('SUPABASE_URL='):
                    print(f"SUPABASE_URL=https://[your-project-id].supabase.co")
                else:
                    print(f"SUPABASE_KEY=[your-anon-public-key]")
            else:
                print(line)
    
    print("\n✅ After updating the .env file, run:")
    print("   python test_supabase_integration.py")
    
    print("\n🔗 Quick Links:")
    print("   - Supabase Dashboard: https://supabase.com/dashboard")
    print("   - Supabase Documentation: https://supabase.com/docs")
    print("   - Project Settings: https://supabase.com/dashboard/project/[your-project-id]/settings/api")

if __name__ == "__main__":
    fix_supabase_config()
