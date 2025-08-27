#!/usr/bin/env python
"""
Email Configuration Helper for HisabPro
Helps diagnose and fix email sending issues
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')

import django
django.setup()

from django.conf import settings
from django.core.mail import send_mail

def check_email_config():
    """Check current email configuration"""
    print("🔧 Current Email Configuration:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    # Check if using default/placeholder values
    issues = []
    
    if settings.EMAIL_HOST_USER == 'your-email@gmail.com':
        issues.append("EMAIL_HOST_USER is using placeholder value")
    
    if not settings.EMAIL_HOST_PASSWORD or settings.EMAIL_HOST_PASSWORD == 'your-app-password':
        issues.append("EMAIL_HOST_PASSWORD is not set or using placeholder")
    
    if settings.DEFAULT_FROM_EMAIL == 'your-email@gmail.com':
        issues.append("DEFAULT_FROM_EMAIL is using placeholder value")
    
    if issues:
        print("\n⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("\n✅ Configuration looks good!")
        return True

def test_email_sending():
    """Test email sending with current configuration"""
    print("\n📧 Testing Email Sending...")
    
    try:
        result = send_mail(
            subject='DailyDine Email Test',
            message='This is a test email from DailyDine reminder system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        
        if result:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email sending failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Email sending failed: {str(e)}")
        
        # Provide specific help for common errors
        error_str = str(e).lower()
        if 'username and password not accepted' in error_str:
            print("\n🔍 This error usually means:")
            print("   1. Wrong email/password combination")
            print("   2. Need to use Gmail App Password instead of regular password")
            print("   3. Gmail account needs 2-factor authentication enabled")
            print("\n💡 Solution:")
            print("   1. Enable 2-factor authentication on your Gmail account")
            print("   2. Generate an App Password: https://myaccount.google.com/apppasswords")
            print("   3. Use the App Password instead of your regular password")
            
        elif 'connection refused' in error_str:
            print("\n🔍 This error usually means:")
            print("   1. SMTP server is not reachable")
            print("   2. Wrong EMAIL_HOST or EMAIL_PORT")
            print("   3. Firewall blocking the connection")
            
        elif 'authentication failed' in error_str:
            print("\n🔍 This error usually means:")
            print("   1. Wrong credentials")
            print("   2. Less secure app access disabled (enable it in Gmail)")
            
        return False

def provide_fix_instructions():
    """Provide instructions to fix email configuration"""
    print("\n🛠️  How to Fix Email Configuration:")
    print("\n1. Update settings.py with your actual Gmail credentials:")
    print("   EMAIL_HOST_USER = 'your-actual-email@gmail.com'")
    print("   EMAIL_HOST_PASSWORD = 'your-gmail-app-password'")
    print("   DEFAULT_FROM_EMAIL = 'your-actual-email@gmail.com'")
    
    print("\n2. For Gmail App Password:")
    print("   a. Go to https://myaccount.google.com/security")
    print("   b. Enable 2-Step Verification if not already enabled")
    print("   c. Go to https://myaccount.google.com/apppasswords")
    print("   d. Generate an App Password for 'Mail'")
    print("   e. Use this App Password in EMAIL_HOST_PASSWORD")
    
    print("\n3. Alternative: Use environment variables:")
    print("   Create a .env file in backend/ directory with:")
    print("   EMAIL_HOST_USER=your-email@gmail.com")
    print("   EMAIL_HOST_PASSWORD=your-app-password")
    print("   DEFAULT_FROM_EMAIL=your-email@gmail.com")
    
    print("\n4. Test the configuration:")
    print("   python fix_email_config.py")

def main():
    """Main function to check and fix email configuration"""
    print("🚀 DailyDine Email Configuration Helper")
    print("=" * 50)
    
    # Check configuration
    config_ok = check_email_config()
    
    if not config_ok:
        provide_fix_instructions()
        return
    
    # Test email sending
    email_ok = test_email_sending()
    
    if email_ok:
        print("\n🎉 Email configuration is working correctly!")
        print("Your reminder system should now be able to send emails.")
    else:
        print("\n❌ Email configuration needs fixing.")
        provide_fix_instructions()

if __name__ == '__main__':
    main()
