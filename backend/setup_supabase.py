#!/usr/bin/env python3
"""
Supabase Setup Script for HisabPro
This script will help you set up Supabase integration for the HisabPro application.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    try:
        import supabase
        print("✅ Supabase client is installed")
    except ImportError:
        print("❌ Supabase client not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase"])
        print("✅ Supabase client installed")
    
    try:
        from decouple import config
        print("✅ python-decouple is installed")
    except ImportError:
        print("❌ python-decouple not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-decouple"])
        print("✅ python-decouple installed")

def create_env_file():
    """Create .env file with Supabase configuration"""
    print("\n📝 Setting up environment configuration...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("⚠️  .env file already exists. Do you want to update it? (y/n): ", end="")
        response = input().lower()
        if response != 'y':
            print("Skipping .env file creation")
            return
    
    print("\n🔧 Please provide your Supabase credentials:")
    print("You can find these in your Supabase project dashboard:")
    print("1. Go to https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Go to Settings > API")
    print("4. Copy the Project URL and anon/public key")
    print()
    
    supabase_url = input("Enter your Supabase Project URL: ").strip()
    supabase_key = input("Enter your Supabase anon/public key: ").strip()
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials are required!")
        return
    
    # Create .env content
    env_content = f"""# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Email Settings (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Razorpay Settings
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

# Redis Settings
REDIS_URL=redis://localhost:6379/0
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def test_supabase_connection():
    """Test the Supabase connection"""
    print("\n🔌 Testing Supabase connection...")
    
    try:
        from decouple import config
        from supabase import create_client, Client
        
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not configured in .env file")
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test connection by making a simple query
        try:
            # Try to access a table that might exist
            result = supabase.table('user_profiles').select('id').limit(1).execute()
            print("✅ Supabase connection test successful")
            return True
        except Exception as e:
            if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                print("✅ Supabase connection successful (tables not created yet)")
                return True
            else:
                print(f"❌ Supabase connection test failed: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Supabase connection: {str(e)}")
        return False

def setup_database_schema():
    """Set up the database schema"""
    print("\n🗄️  Setting up database schema...")
    
    try:
        # Import and run the schema setup
        from setup_supabase_schema import setup_supabase_schema
        
        if setup_supabase_schema():
            print("✅ Database schema setup completed!")
            return True
        else:
            print("❌ Database schema setup failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up database schema: {str(e)}")
        return False

def create_test_data():
    """Create test data in Supabase"""
    print("\n📊 Creating test data...")
    
    try:
        from decouple import config
        from supabase import create_client, Client
        
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Create a test user profile
        test_profile = {
            'user_id': 1,
            'company_name': 'Test Company',
            'company_email': 'test@example.com',
            'company_phone': '+1234567890'
        }
        
        result = supabase.table('user_profiles').insert(test_profile).execute()
        print("✅ Test user profile created")
        
        # Create a test invoice
        test_invoice = {
            'user_id': 1,
            'invoice_number': 'INV-001',
            'client_name': 'Test Client',
            'client_email': 'client@example.com',
            'subtotal': 100.00,
            'tax_rate': 10.00,
            'tax_amount': 10.00,
            'total_amount': 110.00,
            'status': 'pending'
        }
        
        result = supabase.table('invoices').insert(test_invoice).execute()
        print("✅ Test invoice created")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not create test data: {str(e)}")
        print("This is normal if tables don't exist yet or if test data already exists")
        return True

def run_tests():
    """Run integration tests"""
    print("\n🧪 Running integration tests...")
    
    try:
        # Import and run the integration test
        from test_supabase_integration import test_supabase_connection, test_supabase_api_endpoints
        
        if test_supabase_connection():
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
            return False
        
        # Test API endpoints
        test_supabase_api_endpoints()
        return True
        
    except Exception as e:
        print(f"❌ Error running tests: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 HisabPro Supabase Setup")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Create environment file
    create_env_file()
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Cannot proceed without a valid Supabase connection")
        print("Please check your Supabase credentials and try again")
        return
    
    # Setup schema
    if not setup_database_schema():
        print("\n❌ Database schema setup failed")
        print("Please check your Supabase project settings and try again")
        return
    
    # Create test data
    create_test_data()
    
    # Run tests
    if run_tests():
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️  Some tests failed, but setup may still work")
    
    print("\n🎉 Supabase setup completed!")
    print("\n📋 Next steps:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Start the frontend: cd ../frontend && npm run dev")
    print("3. Access the application: http://localhost:3000")
    print("4. Login with: admin/admin123")
    print("\n🔗 Supabase Dashboard: https://supabase.com/dashboard")
    print("📚 Documentation: https://supabase.com/docs")

if __name__ == "__main__":
    main()
