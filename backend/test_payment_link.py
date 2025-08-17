#!/usr/bin/env python
"""
Test Payment Link Functionality
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_payment_link():
    """Test payment link generation functionality"""
    print("💳 Testing Payment Link Functionality")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # Step 1: Login to get token
    print("1. Logging in...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data.get('tokens', {}).get('access')
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print("✅ Login successful")
        
        # Step 2: Get invoices list
        print("\n2. Getting invoices list...")
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        invoices_response = requests.get(f"{base_url}/mongodb/invoices/", headers=headers, timeout=10)
        if invoices_response.status_code != 200:
            print(f"❌ Failed to get invoices: {invoices_response.status_code}")
            return False
        
        invoices_data = invoices_response.json()
        if not invoices_data.get('results'):
            print("❌ No invoices found")
            return False
        
        invoice_id = invoices_data['results'][0]['id']
        invoice_number = invoices_data['results'][0]['invoice_number']
        invoice_status = invoices_data['results'][0]['status']
        print(f"✅ Found invoice: {invoice_number} (ID: {invoice_id}, Status: {invoice_status})")
        
        # Step 3: Test payment link generation
        print(f"\n3. Testing payment link generation for invoice {invoice_number}...")
        
        payment_link_response = requests.post(
            f"{base_url}/mongodb/invoices/{invoice_id}/razorpay-link/", 
            headers=headers, 
            timeout=30
        )
        
        print(f"Payment Link Response Status: {payment_link_response.status_code}")
        
        if payment_link_response.status_code == 200:
            payment_data = payment_link_response.json()
            print(f"✅ Payment link generated successfully!")
            print(f"   Payment Link: {payment_data.get('payment_link', 'N/A')}")
            print(f"   Order ID: {payment_data.get('order_id', 'N/A')}")
            print(f"   Message: {payment_data.get('message', 'N/A')}")
            
            # Test if payment link is accessible
            if payment_data.get('payment_link'):
                print(f"\n4. Testing payment link accessibility...")
                try:
                    link_response = requests.get(payment_data['payment_link'], timeout=10)
                    print(f"   Link Status: {link_response.status_code}")
                    if link_response.status_code == 200:
                        print("✅ Payment link is accessible")
                    else:
                        print("⚠️ Payment link returned non-200 status")
                except Exception as e:
                    print(f"⚠️ Could not test payment link: {str(e)}")
            
        elif payment_link_response.status_code == 400:
            error_data = payment_link_response.json()
            print(f"❌ Payment link generation failed: {error_data.get('error', 'Unknown error')}")
            
            # Check if it's a Razorpay configuration issue
            if 'razorpay' in error_data.get('error', '').lower():
                print("\n🔧 Razorpay Configuration Issues:")
                print("   - Check if RAZORPAY_KEY_ID is set in .env")
                print("   - Check if RAZORPAY_KEY_SECRET is set in .env")
                print("   - Verify Razorpay credentials are correct")
                print("   - Make sure you're using test keys for development")
            return False
        else:
            print(f"❌ Payment link generation failed: {payment_link_response.status_code}")
            try:
                error_data = payment_link_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {payment_link_response.text[:200]}")
            return False
        
        print("\n🎉 Payment link test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def check_razorpay_config():
    """Check Razorpay configuration"""
    print("\n🔧 Checking Razorpay Configuration")
    print("=" * 50)
    
    try:
        from django.conf import settings
        
        key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', None)
        
        print(f"RAZORPAY_KEY_ID: {'✅ Set' if key_id else '❌ Not set'}")
        print(f"RAZORPAY_KEY_SECRET: {'✅ Set' if key_secret else '❌ Not set'}")
        print(f"RAZORPAY_WEBHOOK_SECRET: {'✅ Set' if webhook_secret else '❌ Not set'}")
        
        if key_id and key_secret:
            print("\n✅ Razorpay configuration looks good!")
            print("💡 Make sure you're using test keys for development")
        else:
            print("\n❌ Razorpay configuration is incomplete")
            print("💡 Add Razorpay credentials to your .env file")
            
    except Exception as e:
        print(f"❌ Error checking configuration: {str(e)}")

def main():
    """Main test function"""
    print("🔍 Payment Link Test")
    print("=" * 60)
    
    # Check configuration first
    check_razorpay_config()
    
    # Test payment link functionality
    success = test_payment_link()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Payment link functionality is working perfectly!")
        print("\n💡 Next steps:")
        print("   - Test the payment link in browser")
        print("   - Configure webhook for payment verification")
        print("   - Set up production Razorpay keys")
    else:
        print("❌ Payment link has issues")
        print("\n🔧 Troubleshooting:")
        print("1. Check Razorpay configuration in .env")
        print("2. Verify Razorpay credentials")
        print("3. Make sure Django server is running")
        print("4. Check server logs for errors")

if __name__ == '__main__':
    main()
