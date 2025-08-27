#!/usr/bin/env python
"""
Quick Gmail Setup Test for DailyDine
"""

import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail_connection():
    """Test Gmail connection with current settings"""
    print("🔧 Testing Gmail Connection for DailyDine...")
    print(f"   Email: {settings.EMAIL_HOST_USER}")
    print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        # Send test email
        result = send_mail(
            subject='✅ DailyDine Email System Test',
            message='''
Hello!

This is a test email from your DailyDine reminder system.

If you receive this email, your email configuration is working perfectly!

System Details:
- Business: DailyDine
- Location: Mangalore, Karnataka, India
- Phone: +91 9019647142

Your reminder system is now ready to send payment reminders to customers.

Best regards,
DailyDine Automated System
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        
        if result:
            print("🎉 SUCCESS! Email sent successfully!")
            print("✅ Your DailyDine reminder system is ready to use!")
            print("📧 Check your inbox for the test email.")
            return True
        else:
            print("❌ Failed to send email - no result returned")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email test failed: {error_msg}")
        
        # Provide specific help
        if "Username and Password not accepted" in error_msg:
            print("\n🔍 This means you need to set up Gmail App Password:")
            print("1. Go to: https://myaccount.google.com/security")
            print("2. Enable 2-Step Verification")
            print("3. Go to: https://myaccount.google.com/apppasswords")
            print("4. Generate App Password for 'Mail'")
            print("5. Update .env file with the 16-character password")
            
        elif "Connection refused" in error_msg:
            print("\n🔍 Network connection issue:")
            print("- Check your internet connection")
            print("- Verify firewall settings")
            
        return False

if __name__ == '__main__':
    print("🚀 DailyDine Gmail Setup Test")
    print("=" * 40)
    test_gmail_connection()
