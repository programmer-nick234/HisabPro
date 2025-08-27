"""
Fix Razorpay Credentials - Step by Step Guide
This script will help you set up correct Razorpay credentials
"""

import os

def fix_razorpay_setup():
    print("🔧 Fixing Razorpay Credentials Setup")
    print("=" * 50)
    
    print("\n📋 Step-by-Step Fix Guide:")
    print("=" * 30)
    
    print("\n1️⃣ GET CORRECT RAZORPAY CREDENTIALS")
    print("   Go to: https://dashboard.razorpay.com/")
    print("   → Login to your account")
    print("   → Go to 'Account & Settings' → 'API Keys'")
    print("   → Generate/Copy your credentials")
    print()
    
    print("2️⃣ YOUR .ENV FILE SHOULD LOOK LIKE THIS:")
    print("   RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXX")
    print("   RAZORPAY_KEY_SECRET=YYYYYYYYYYYYYYYY")
    print("   RAZORPAY_WEBHOOK_SECRET=webhook_secret_from_dashboard")
    print()
    
    print("3️⃣ COMMON ISSUES & FIXES:")
    print("   ❌ Using Live keys in Test mode")
    print("   💡 Use 'rzp_test_' keys for testing")
    print()
    print("   ❌ Wrong webhook secret")
    print("   💡 Webhook secret ≠ Webhook URL")
    print("   💡 Generate secret in Razorpay webhook settings")
    print()
    print("   ❌ Keys not activated")
    print("   💡 Activate your Razorpay account")
    print()
    
    print("4️⃣ TEST YOUR CREDENTIALS:")
    print("   Run this after fixing .env:")
    print("   python debug_payment_issue.py")
    print()
    
    # Check current .env
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    
    print("5️⃣ CURRENT .ENV STATUS:")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
        
        print("   📁 .env file found")
        
        # Check for issues
        if 'rzp_test_' in content:
            print("   ✅ Test key ID format looks correct")
        elif 'rzp_live_' in content:
            print("   ⚠️  You're using LIVE keys (switch to TEST for development)")
        else:
            print("   ❌ Key ID format might be wrong")
        
        if 'https://' in content and 'RAZORPAY_WEBHOOK_SECRET' in content:
            print("   ❌ Webhook secret contains URL (should be just the secret)")
            print("   💡 Fix: RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here")
        
    else:
        print("   ❌ .env file not found")
    
    print("\n🎯 QUICK FIX TEMPLATE:")
    print("Copy this to your .env file:")
    print("-" * 40)
    print("# Razorpay Configuration")
    print("RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID_HERE")
    print("RAZORPAY_KEY_SECRET=YOUR_KEY_SECRET_HERE")
    print("RAZORPAY_WEBHOOK_SECRET=YOUR_WEBHOOK_SECRET_HERE")
    print()
    print("# Email Configuration")
    print("EMAIL_HOST_USER=nikhilbajantri86@gmail.com")
    print("EMAIL_HOST_PASSWORD=your-gmail-app-password")
    print()
    print("# Business Information")
    print("BUSINESS_NAME=HisabPro")
    print("BUSINESS_EMAIL=nikhilbajantri86@gmail.com")
    print("BUSINESS_PHONE=+91 9096471400")
    print("BUSINESS_ADDRESS=Mangalore, Karnataka, India")
    print("-" * 40)
    
    print("\n🚀 AFTER FIXING:")
    print("1. Save your .env file")
    print("2. Restart Django server")
    print("3. Run: python debug_payment_issue.py")
    print("4. Test payment link generation")

if __name__ == '__main__':
    fix_razorpay_setup()
