#!/usr/bin/env python3
"""
Setup script to create .env file from template
"""
import os
import shutil

def setup_env():
    """Create .env file from template if it doesn't exist"""
    
    template_file = 'env_template.txt'
    env_file = '.env'
    
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    if not os.path.exists(template_file):
        print(f"❌ Template file {template_file} not found!")
        return
    
    try:
        # Copy template to .env
        shutil.copy2(template_file, env_file)
        print(f"✅ Created {env_file} from template")
        print("\n📝 Next steps:")
        print("1. Edit .env file with your actual credentials:")
        print("   - Replace MONGODB_URI with your MongoDB Atlas connection string")
        print("   - Add your SendGrid API key")
        print("   - Add your Razorpay credentials")
        print("   - Update SECRET_KEY with a secure random string")
        print("\n2. Never commit .env file to version control!")
        print("3. Test your application with: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")

if __name__ == "__main__":
    setup_env()
