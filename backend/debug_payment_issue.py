"""
Debug Payment Link Generation Issues
This script will help identify and fix payment link generation problems
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from invoices.models import Invoice, InvoiceItem
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_payment_configuration():
    """Debug payment system configuration"""
    
    print("🔍 Debugging Payment System Configuration")
    print("=" * 60)
    
    # 1. Check Environment Variables
    print("\n1️⃣ Environment Variables Check:")
    
    razorpay_configs = {
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID,
        'RAZORPAY_KEY_SECRET': settings.RAZORPAY_KEY_SECRET,
        'RAZORPAY_WEBHOOK_SECRET': settings.RAZORPAY_WEBHOOK_SECRET,
    }
    
    for key, value in razorpay_configs.items():
        if value:
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"   ✅ {key}: {masked_value}")
        else:
            print(f"   ❌ {key}: NOT SET")
    
    # 2. Check Payment Service Import
    print("\n2️⃣ Payment Service Import Check:")
    
    try:
        from invoices.payment_service import payment_service
        print("   ✅ Payment service imported successfully")
        
        # Check if Razorpay client is initialized
        if hasattr(payment_service, 'client'):
            print("   ✅ Razorpay client initialized")
        else:
            print("   ❌ Razorpay client not initialized")
            
    except Exception as e:
        print(f"   ❌ Payment service import failed: {str(e)}")
        return False
    
    # 3. Test Razorpay Authentication
    print("\n3️⃣ Razorpay Authentication Test:")
    
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Try to fetch payment methods (this will test authentication)
        try:
            # This is a simple API call that doesn't create anything
            methods = client.payment.all({'count': 1})
            print("   ✅ Razorpay authentication successful")
        except razorpay.errors.BadRequestError as e:
            print(f"   ⚠️ Razorpay authentication issue: {str(e)}")
            if "Invalid api key" in str(e).lower():
                print("   💡 Solution: Check your RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET")
        except Exception as e:
            print(f"   ❌ Razorpay connection failed: {str(e)}")
            
    except ImportError:
        print("   ❌ Razorpay package not installed")
        print("   💡 Solution: pip install razorpay")
        return False
    except Exception as e:
        print(f"   ❌ Razorpay client creation failed: {str(e)}")
        return False
    
    # 4. Test Payment Link Creation (Mock)
    print("\n4️⃣ Payment Link Creation Test:")
    
    # Create a test invoice
    try:
        user, created = User.objects.get_or_create(
            username='debug_user',
            defaults={'email': 'debug@test.com'}
        )
        
        # Check if test invoice exists
        test_invoice = Invoice.objects.filter(
            user=user,
            client_email='debug@test.com'
        ).first()
        
        if not test_invoice:
            test_invoice = Invoice.objects.create(
                user=user,
                client_name='Debug Test',
                client_email='debug@test.com',
                client_phone='+91 9876543210',
                client_address='Test Address',
                issue_date='2024-01-15',
                due_date='2024-02-15',
                tax_rate=Decimal('18.00'),
                status='pending'
            )
            
            InvoiceItem.objects.create(
                invoice=test_invoice,
                description='Debug Test Service',
                quantity=1,
                unit_price=Decimal('1000.00')
            )
            
            test_invoice.calculate_totals()
            test_invoice.save()
        
        print(f"   ✅ Test invoice created: {test_invoice.invoice_number}")
        print(f"   Amount: ₹{test_invoice.total_amount}")
        
        # Now test payment link creation
        try:
            result = payment_service.create_payment_link(test_invoice)
            
            if result['success']:
                print("   ✅ Payment link creation successful!")
                print(f"      Link: {result['short_url']}")
            else:
                print(f"   ❌ Payment link creation failed: {result['error']}")
                
                # Common error solutions
                error_msg = result['error'].lower()
                if 'authentication' in error_msg or 'invalid api key' in error_msg:
                    print("   💡 Solution: Check your Razorpay API credentials")
                elif 'bad request' in error_msg:
                    print("   💡 Solution: Check payment link data format")
                elif 'network' in error_msg or 'connection' in error_msg:
                    print("   💡 Solution: Check internet connection")
                    
        except Exception as e:
            print(f"   ❌ Payment link creation error: {str(e)}")
            
    except Exception as e:
        print(f"   ❌ Test invoice creation failed: {str(e)}")
    
    # 5. Check Frontend API Call
    print("\n5️⃣ Frontend API Endpoint Check:")
    
    from django.urls import reverse
    try:
        url = reverse('generate-razorpay-link', kwargs={'invoice_id': 'test-uuid'})
        print(f"   ✅ API endpoint URL: {url}")
    except Exception as e:
        print(f"   ❌ URL reverse failed: {str(e)}")
    
    # 6. Environment File Check
    print("\n6️⃣ Environment File Analysis:")
    
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_file_path):
        print(f"   ✅ .env file found at: {env_file_path}")
        
        try:
            with open(env_file_path, 'r') as f:
                content = f.read()
                
            if 'RAZORPAY_KEY_ID' in content:
                print("   ✅ RAZORPAY_KEY_ID found in .env")
            else:
                print("   ❌ RAZORPAY_KEY_ID missing from .env")
                
            if 'RAZORPAY_KEY_SECRET' in content:
                print("   ✅ RAZORPAY_KEY_SECRET found in .env")
            else:
                print("   ❌ RAZORPAY_KEY_SECRET missing from .env")
                
            if 'RAZORPAY_WEBHOOK_SECRET' in content:
                print("   ✅ RAZORPAY_WEBHOOK_SECRET found in .env")
            else:
                print("   ❌ RAZORPAY_WEBHOOK_SECRET missing from .env")
                
        except Exception as e:
            print(f"   ❌ Error reading .env file: {str(e)}")
    else:
        print("   ❌ .env file not found")
        print("   💡 Solution: Create .env file in backend directory")
    
    # 7. Quick Fix Recommendations
    print("\n🔧 Quick Fix Recommendations:")
    print("=" * 60)
    
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        print("1. ❌ Missing Razorpay Credentials")
        print("   💡 Solution:")
        print("   - Go to Razorpay Dashboard → Account & Settings → API Keys")
        print("   - Copy your Key ID and Key Secret")
        print("   - Add them to your .env file:")
        print("     RAZORPAY_KEY_ID=rzp_test_your_key_id")
        print("     RAZORPAY_KEY_SECRET=your_key_secret")
        print()
    
    print("2. ✅ Test Payment Link Generation")
    print("   💡 Try this API call:")
    print("   POST http://localhost:8000/api/invoices/{invoice_id}/razorpay-link/")
    print("   Headers: Authorization: Bearer {your_token}")
    print("   Body: {\"send_email\": false}")
    print()
    
    print("3. 🔍 Check Browser Network Tab")
    print("   💡 Open browser dev tools → Network tab")
    print("   - Look for the API call to razorpay-link")
    print("   - Check the response for specific error messages")
    print()
    
    return True

if __name__ == '__main__':
    try:
        debug_payment_configuration()
    except Exception as e:
        print(f"\n❌ Debug script failed: {str(e)}")
        import traceback
        traceback.print_exc()
