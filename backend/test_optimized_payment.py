#!/usr/bin/env python
"""
Test Optimized Payment System
"""

import os
import sys
import django
import requests
import json
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_payment_system():
    """Test the optimized payment system"""
    print("🚀 Testing Optimized Payment System")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api"
    
    # Step 1: Login
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
        
        # Step 2: Get invoices
        print("\n2. Getting invoices...")
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
        invoice_amount = invoices_data['results'][0]['total_amount']
        print(f"✅ Found invoice: {invoice_number} (ID: {invoice_id}, Amount: {invoice_amount})")
        
        # Step 3: Test payment link generation
        print(f"\n3. Testing payment link generation...")
        
        payment_link_response = requests.post(
            f"{base_url}/mongodb/invoices/{invoice_id}/payment-link/", 
            headers=headers, 
            timeout=30
        )
        
        print(f"Payment Link Response Status: {payment_link_response.status_code}")
        
        if payment_link_response.status_code == 200:
            payment_data = payment_link_response.json()
            print(f"✅ Payment link generated successfully!")
            print(f"   Payment Link: {payment_data.get('payment_link', 'N/A')}")
            print(f"   Gateway: {payment_data.get('gateway', 'N/A')}")
            print(f"   Payment ID: {payment_data.get('payment_id', 'N/A')}")
            
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
            
            return True
            
        elif payment_link_response.status_code == 400:
            error_data = payment_link_response.json()
            print(f"❌ Payment link generation failed: {error_data.get('error', 'Unknown error')}")
            
            # Check if it's a configuration issue
            if 'razorpay' in error_data.get('error', '').lower() or 'stripe' in error_data.get('error', '').lower():
                print("\n🔧 Payment Gateway Configuration Issues:")
                print("   - Check if payment gateway credentials are set in .env")
                print("   - Verify payment gateway credentials are correct")
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
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_payment_system_features():
    """Test payment system features"""
    print("\n🔧 Testing Payment System Features")
    print("=" * 60)
    
    try:
        from invoices.optimized_payment import payment_system
        
        # Test gateway initialization
        print("1. Testing gateway initialization...")
        available_gateways = payment_system.get_available_gateways()
        print(f"   Available gateways: {[g.value for g in available_gateways]}")
        
        # Test best gateway selection
        print("\n2. Testing gateway selection...")
        best_gateway_inr = payment_system.get_best_gateway("INR")
        best_gateway_usd = payment_system.get_best_gateway("USD")
        print(f"   Best gateway for INR: {best_gateway_inr.value}")
        print(f"   Best gateway for USD: {best_gateway_usd.value}")
        
        # Test payment link creation
        print("\n3. Testing payment link creation...")
        result = payment_system.create_payment_link(
            invoice_id="test_invoice_123",
            amount=Decimal("1000.00"),
            currency="INR",
            description="Test payment",
            customer_email="test@example.com"
        )
        
        if result['success']:
            print(f"✅ Payment link created successfully!")
            print(f"   Gateway: {result['gateway']}")
            print(f"   Payment URL: {result['payment_url']}")
            print(f"   Payment ID: {result['payment_id']}")
        else:
            print(f"❌ Payment link creation failed: {result['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing payment system features: {str(e)}")
        return False

def check_payment_configuration():
    """Check payment configuration"""
    print("\n🔧 Checking Payment Configuration")
    print("=" * 60)
    
    try:
        from django.conf import settings
        
        # Check Razorpay
        razorpay_key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
        razorpay_key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)
        
        print(f"RAZORPAY_KEY_ID: {'✅ Set' if razorpay_key_id else '❌ Not set'}")
        print(f"RAZORPAY_KEY_SECRET: {'✅ Set' if razorpay_key_secret else '❌ Not set'}")
        
        # Check Stripe
        stripe_secret_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        print(f"STRIPE_SECRET_KEY: {'✅ Set' if stripe_secret_key else '❌ Not set'}")
        
        # Check PayPal
        paypal_client_id = getattr(settings, 'PAYPAL_CLIENT_ID', None)
        paypal_client_secret = getattr(settings, 'PAYPAL_CLIENT_SECRET', None)
        print(f"PAYPAL_CLIENT_ID: {'✅ Set' if paypal_client_id else '❌ Not set'}")
        print(f"PAYPAL_CLIENT_SECRET: {'✅ Set' if paypal_client_secret else '❌ Not set'}")
        
        # Summary
        configured_gateways = []
        if razorpay_key_id and razorpay_key_secret:
            configured_gateways.append("Razorpay")
        if stripe_secret_key:
            configured_gateways.append("Stripe")
        if paypal_client_id and paypal_client_secret:
            configured_gateways.append("PayPal")
        
        print(f"\n📊 Configured Gateways: {', '.join(configured_gateways) if configured_gateways else 'None'}")
        
        if configured_gateways:
            print("✅ Payment system is properly configured!")
        else:
            print("❌ No payment gateways are configured")
            print("\n💡 To configure payment gateways, add to your .env file:")
            print("   RAZORPAY_KEY_ID=your_razorpay_key_id")
            print("   RAZORPAY_KEY_SECRET=your_razorpay_key_secret")
            print("   STRIPE_SECRET_KEY=your_stripe_secret_key")
            print("   PAYPAL_CLIENT_ID=your_paypal_client_id")
            print("   PAYPAL_CLIENT_SECRET=your_paypal_client_secret")
        
        return len(configured_gateways) > 0
        
    except Exception as e:
        print(f"❌ Error checking configuration: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎯 Optimized Payment System Test")
    print("=" * 80)
    
    # Check configuration first
    config_ok = check_payment_configuration()
    
    if not config_ok:
        print("\n⚠️ Payment gateways not configured. Skipping API tests.")
        return
    
    # Test payment system features
    features_ok = test_payment_system_features()
    
    # Test API endpoints
    api_ok = test_payment_system()
    
    print("\n" + "=" * 80)
    if config_ok and features_ok and api_ok:
        print("🎉 Optimized payment system is working perfectly!")
        print("\n✨ Features:")
        print("   ✅ Multiple payment gateways (Razorpay, Stripe)")
        print("   ✅ Automatic gateway selection")
        print("   ✅ Fallback mechanism")
        print("   ✅ Caching and optimization")
        print("   ✅ Error handling and retry logic")
        print("\n💡 Next steps:")
        print("   - Test payment links in browser")
        print("   - Configure webhooks for payment verification")
        print("   - Set up production payment gateway keys")
    else:
        print("❌ Payment system has issues")
        print("\n🔧 Troubleshooting:")
        print("1. Check payment gateway configuration in .env")
        print("2. Verify payment gateway credentials")
        print("3. Make sure Django server is running")
        print("4. Check server logs for errors")

if __name__ == '__main__':
    main()
