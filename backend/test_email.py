#!/usr/bin/env python
"""
Test script to verify Gmail SMTP email configuration
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_configuration():
    """Test Gmail SMTP email configuration"""
    try:
        print("Testing Gmail SMTP email configuration...")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print()
        
        # Test sending a simple email
        subject = 'Test Email from HisabPro'
        message = 'This is a test email to verify Gmail SMTP configuration is working correctly.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.EMAIL_HOST_USER]  # Send to yourself for testing
        
        print(f"Sending test email to: {recipient_list[0]}")
        
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        print("✅ Test email sent successfully!")
        print("📧 Check your Gmail inbox for the test email.")
        return True
        
    except Exception as e:
        print(f"✗ Email test failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you're using an App Password, not your regular Gmail password")
        print("2. Enable 2-factor authentication on your Gmail account")
        print("3. Generate an App Password: Google Account > Security > App Passwords")
        print("4. Check if your Gmail account allows 'less secure app access'")
        return False

if __name__ == '__main__':
    test_email_configuration()
