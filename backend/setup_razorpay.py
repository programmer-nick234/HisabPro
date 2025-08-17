#!/usr/bin/env python
"""
Setup Razorpay Configuration
"""

import os
import sys

def setup_razorpay():
    """Help user set up Razorpay configuration"""
    print("💳 Razorpay Configuration Setup")
    print("=" * 50)
    
    print("\n📋 To enable payment links, you need to:")
    print("1. Sign up for a Razorpay account at https://razorpay.com")
    print("2. Get your API keys from the Razorpay Dashboard")
    print("3. Add the credentials to your .env file")
    
    print("\n🔑 Required Environment Variables:")
    print("   RAZORPAY_KEY_ID=rzp_test_your_test_key_id")
    print("   RAZORPAY_KEY_SECRET=your_test_key_secret")
    print("   RAZORPAY_WEBHOOK_SECRET=your_webhook_secret")
    
    print("\n📝 Steps to get Razorpay credentials:")
    print("1. Go to https://dashboard.razorpay.com")
    print("2. Sign up or log in to your account")
    print("3. Go to Settings → API Keys")
    print("4. Generate API keys (Key ID and Key Secret)")
    print("5. For development, use test keys (they start with 'rzp_test_')")
    
    print("\n🌐 Webhook Setup (Optional for development):")
    print("1. In Razorpay dashboard, go to Settings → Webhooks")
    print("2. Add webhook URL: http://localhost:8000/api/mongodb/webhook/razorpay/")
    print("3. Select events: payment.captured")
    print("4. Copy the webhook secret")
    
    print("\n📄 Example .env file content:")
    print("""
# Razorpay Settings (Test Credentials)
RAZORPAY_KEY_ID=rzp_test_1234567890abcdef
RAZORPAY_KEY_SECRET=abcdef1234567890abcdef1234567890
RAZORPAY_WEBHOOK_SECRET=webhook_secret_here

# Other settings...
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=nikhilbajantri86@gmail.com
EMAIL_HOST_PASSWORD=efleuomllopzfcja
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=nikhilbajantri86@gmail.com
""")
    
    print("\n⚠️ Important Notes:")
    print("- Use test keys for development (they start with 'rzp_test_')")
    print("- Test keys don't process real payments")
    print("- Switch to live keys only for production")
    print("- Keep your keys secure and never commit them to version control")
    
    print("\n✅ After adding credentials:")
    print("1. Restart your Django server")
    print("2. Run: python test_payment_link.py")
    print("3. Test payment link generation in the frontend")
    
    print("\n🔗 Useful Links:")
    print("- Razorpay Dashboard: https://dashboard.razorpay.com")
    print("- Razorpay Documentation: https://razorpay.com/docs/")
    print("- Test Payment Methods: https://razorpay.com/docs/payments/test-mode/")

if __name__ == '__main__':
    setup_razorpay()
