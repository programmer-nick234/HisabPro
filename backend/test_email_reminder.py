#!/usr/bin/env python
"""
Test script for email reminder functionality
Run this to debug email sending issues
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.models import User
from invoices.models import Invoice
from invoices.reminder_service import reminder_service
from invoices.reminder_models import ReminderTemplate, ReminderRule
from invoices.reminder_templates import setup_reminder_system_for_user
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_email():
    """Test basic Django email functionality"""
    print("\n=== Testing Basic Email Functionality ===")
    
    try:
        print(f"Email Backend: {settings.EMAIL_BACKEND}")
        print(f"Email Host: {settings.EMAIL_HOST}")
        print(f"Email Port: {settings.EMAIL_PORT}")
        print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
        print(f"Email Host User: {settings.EMAIL_HOST_USER}")
        print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
        
        # Test basic email
        result = send_mail(
            subject='HisabPro Email Test',
            message='This is a test email from HisabPro reminder system.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['nikhilbajantri86@gmail.com'],  # Send to yourself for testing
            fail_silently=False,
        )
        
        if result:
            print("✅ Basic email test successful!")
            return True
        else:
            print("❌ Basic email test failed - no result returned")
            return False
            
    except Exception as e:
        print(f"❌ Basic email test failed: {str(e)}")
        return False


def test_html_email():
    """Test HTML email with EmailMultiAlternatives"""
    print("\n=== Testing HTML Email ===")
    
    try:
        html_content = """
        <html>
        <body>
            <h2>HisabPro Reminder System Test</h2>
            <p>This is a test of the HTML email functionality.</p>
            <p><strong>Business:</strong> DailyDine</p>
            <p><strong>Email:</strong> nikhilbajantri86@gmail.com</p>
            <p><strong>Phone:</strong> +91 9019647142</p>
            <p><strong>Address:</strong> Mangalore, Karnataka, India</p>
        </body>
        </html>
        """
        
        email = EmailMultiAlternatives(
            subject='HisabPro HTML Email Test',
            body='This is the plain text version of the email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['nikhilbajantri86@gmail.com']
        )
        
        email.attach_alternative(html_content, "text/html")
        result = email.send()
        
        if result:
            print("✅ HTML email test successful!")
            return True
        else:
            print("❌ HTML email test failed")
            return False
            
    except Exception as e:
        print(f"❌ HTML email test failed: {str(e)}")
        return False


def test_reminder_system():
    """Test the actual reminder system"""
    print("\n=== Testing Reminder System ===")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'nikhilbajantri86@gmail.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print(f"✅ Created test user: {user.username}")
        else:
            print(f"✅ Using existing test user: {user.username}")
        
        # Set up reminder system for user if not exists
        templates = ReminderTemplate.objects.filter(user=user)
        if not templates.exists():
            setup_result = setup_reminder_system_for_user(user)
            print(f"✅ Set up reminder system: {setup_result['templates_created']} templates, {setup_result['rules_created']} rules")
        else:
            print("✅ Reminder system already set up")
        
        # Create or get a test invoice
        invoice, created = Invoice.objects.get_or_create(
            user=user,
            client_name='Test Client',
            client_email='nikhilbajantri86@gmail.com',  # Send to yourself for testing
            defaults={
                'invoice_number': 'TEST-001',
                'issue_date': '2024-01-15',
                'due_date': '2024-02-15',
                'total_amount': 1000.00,
                'status': 'pending'
            }
        )
        
        if created:
            print(f"✅ Created test invoice: {invoice.invoice_number}")
        else:
            print(f"✅ Using existing test invoice: {invoice.invoice_number}")
        
        # Get a friendly template
        template = ReminderTemplate.objects.filter(
            user=user,
            tone='friendly',
            stage='pre_due'
        ).first()
        
        if not template:
            print("❌ No friendly template found")
            return False
        
        print(f"✅ Using template: {template.name}")
        
        # Process the template
        from invoices.reminder_service import ReminderTemplateProcessor
        processor = ReminderTemplateProcessor()
        processed = processor.process_template(template, invoice)
        
        print(f"✅ Template processed successfully")
        print(f"Subject: {processed['email_subject']}")
        print(f"Body preview: {processed['email_body'][:100]}...")
        
        # Test sending the email
        success, message = reminder_service._send_email_reminder(invoice, processed, template)
        
        if success:
            print("✅ Reminder email sent successfully!")
            return True
        else:
            print(f"❌ Reminder email failed: {message}")
            return False
            
    except Exception as e:
        print(f"❌ Reminder system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    """Clean up test data"""
    print("\n=== Cleaning Up Test Data ===")
    
    try:
        # Delete test invoices
        test_invoices = Invoice.objects.filter(client_name='Test Client')
        count = test_invoices.count()
        test_invoices.delete()
        print(f"✅ Deleted {count} test invoices")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {str(e)}")


def main():
    """Run all email tests"""
    print("🚀 Starting Email Reminder System Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic email
    if test_basic_email():
        tests_passed += 1
    
    # Test 2: HTML email
    if test_html_email():
        tests_passed += 1
    
    # Test 3: Reminder system
    if test_reminder_system():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Email reminder system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    # Ask about cleanup
    cleanup = input("\nDo you want to clean up test data? (y/N): ").lower().strip()
    if cleanup in ['y', 'yes']:
        cleanup_test_data()
    
    return tests_passed == total_tests


if __name__ == '__main__':
    main()
