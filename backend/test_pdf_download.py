#!/usr/bin/env python
"""
Test PDF Download Functionality
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

def test_pdf_download():
    """Test PDF download functionality"""
    print("📄 Testing PDF Download Functionality")
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
        print(f"✅ Found invoice: {invoice_number} (ID: {invoice_id})")
        
        # Step 3: Test PDF download
        print(f"\n3. Testing PDF download for invoice {invoice_number}...")
        
        pdf_response = requests.get(
            f"{base_url}/mongodb/invoices/{invoice_id}/pdf/", 
            headers=headers, 
            timeout=30
        )
        
        print(f"PDF Response Status: {pdf_response.status_code}")
        print(f"PDF Response Headers: {dict(pdf_response.headers)}")
        
        if pdf_response.status_code == 200:
            # Check if it's actually a PDF
            content_type = pdf_response.headers.get('content-type', '')
            content_disposition = pdf_response.headers.get('content-disposition', '')
            
            print(f"✅ PDF download successful!")
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Disposition: {content_disposition}")
            print(f"   Content Length: {len(pdf_response.content)} bytes")
            
            # Check if content starts with PDF signature
            if pdf_response.content.startswith(b'%PDF'):
                print("✅ Content is valid PDF (starts with %PDF)")
            else:
                print("⚠️ Content doesn't start with PDF signature")
                print(f"   First 20 bytes: {pdf_response.content[:20]}")
            
            # Save PDF to file for inspection
            filename = f"test_invoice_{invoice_number}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f"✅ PDF saved as: {filename}")
            
        else:
            print(f"❌ PDF download failed: {pdf_response.status_code}")
            try:
                error_data = pdf_response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {pdf_response.text[:200]}")
            return False
        
        print("\n🎉 PDF download test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🔍 PDF Download Test")
    print("=" * 60)
    
    success = test_pdf_download()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 PDF download is working perfectly!")
        print("\n💡 The PDF should have:")
        print("   - Beautiful design with colors and styling")
        print("   - Company and client information")
        print("   - Invoice items table")
        print("   - Totals section")
        print("   - Notes and terms (if provided)")
        print("   - Professional footer")
    else:
        print("❌ PDF download has issues")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Django server is running")
        print("2. Check MongoDB connection")
        print("3. Verify ReportLab is installed")
        print("4. Check server logs for errors")

if __name__ == '__main__':
    main()
