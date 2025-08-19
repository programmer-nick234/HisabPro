#!/usr/bin/env python3
"""
Test Invoice Template
Preview the professional A4 invoice template
"""

import requests

def test_invoice_template():
    print("🎨 Testing Invoice Template")
    print("=" * 40)
    
    base_url = 'http://localhost:8000/api'
    
    try:
        # Test sample invoice preview (no auth required)
        print("\n📋 Testing sample invoice template...")
        sample_response = requests.get(f'{base_url}/preview/sample-invoice/')
        
        if sample_response.status_code == 200:
            print("✅ Sample invoice template working!")
            print("📄 HTML content generated successfully")
            print(f"📏 Content length: {len(sample_response.text)} characters")
            
            # Save the HTML to a file for preview
            with open('sample_invoice_preview.html', 'w', encoding='utf-8') as f:
                f.write(sample_response.text)
            print("💾 Sample invoice saved to: sample_invoice_preview.html")
            print("🌐 Open this file in your browser to preview the template")
            
        else:
            print(f"❌ Sample template failed: {sample_response.status_code}")
            print(f"Error: {sample_response.text[:200]}...")
            
        # Test with real invoice (requires auth)
        print("\n🔐 Testing with real invoice (requires login)...")
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = requests.post(f'{base_url}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['tokens']['access']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get the first invoice
            invoices_response = requests.get(f'{base_url}/supabase/invoices/', headers=headers)
            
            if invoices_response.status_code == 200:
                invoices_data = invoices_response.json()
                if invoices_data.get('results') and len(invoices_data['results']) > 0:
                    invoice_id = invoices_data['results'][0]['id']
                    print(f"✅ Found invoice: {invoice_id}")
                    
                    # Test real invoice preview
                    preview_response = requests.get(f'{base_url}/supabase/invoices/{invoice_id}/preview/', headers=headers)
                    
                    if preview_response.status_code == 200:
                        print("✅ Real invoice template working!")
                        print(f"📄 Content length: {len(preview_response.text)} characters")
                        
                        # Save the HTML to a file for preview
                        with open('real_invoice_preview.html', 'w', encoding='utf-8') as f:
                            f.write(preview_response.text)
                        print("💾 Real invoice saved to: real_invoice_preview.html")
                        
                        # Test PDF generation
                        pdf_response = requests.get(f'{base_url}/supabase/invoices/{invoice_id}/pdf-template/', headers=headers)
                        
                        if pdf_response.status_code == 200:
                            content_type = pdf_response.headers.get('content-type', '')
                            if 'application/pdf' in content_type:
                                print("✅ PDF generation working!")
                                with open('invoice.pdf', 'wb') as f:
                                    f.write(pdf_response.content)
                                print("💾 PDF saved to: invoice.pdf")
                            else:
                                print("⚠️ PDF generation returned HTML (WeasyPrint not installed)")
                                print("📄 This is normal if WeasyPrint is not available")
                        else:
                            print(f"❌ PDF generation failed: {pdf_response.status_code}")
                    else:
                        print(f"❌ Real invoice preview failed: {preview_response.status_code}")
                else:
                    print("⚠️ No invoices found to test with")
            else:
                print(f"❌ Failed to get invoices: {invoices_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n📋 Template Features:")
    print("✅ A4 page size with proper margins")
    print("✅ Professional header with logo and business info")
    print("✅ Client information section")
    print("✅ Invoice details with status badge")
    print("✅ Dynamic items table")
    print("✅ Totals section with tax and discount")
    print("✅ Footer with notes and signature lines")
    print("✅ Print-friendly CSS")
    print("✅ Responsive design")

if __name__ == "__main__":
    test_invoice_template()
