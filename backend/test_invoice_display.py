#!/usr/bin/env python3
"""
Test Invoice Display
Check if invoices are being retrieved properly from the API
"""

import requests

def test_invoice_display():
    print("🔍 Testing Invoice Display")
    print("=" * 40)
    
    base_url = 'http://localhost:8000/api'
    headers = {'Content-Type': 'application/json'}
    
    try:
        # Login
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = requests.post(f'{base_url}/auth/login/', json=login_data)
        
        if login_response.status_code == 200:
            token = login_response.json()['tokens']['access']
            headers['Authorization'] = f'Bearer {token}'
            print("✅ Login successful")
            
            # Test invoices list
            print("\n📋 Testing invoices list...")
            invoices_response = requests.get(f'{base_url}/supabase/invoices/', headers=headers)
            print(f"Status: {invoices_response.status_code}")
            
            if invoices_response.status_code == 200:
                invoices_data = invoices_response.json()
                count = invoices_data.get('count', 0)
                results = invoices_data.get('results', [])
                
                print(f"✅ Found {count} invoices")
                print(f"✅ Results array has {len(results)} items")
                
                if results:
                    for i, invoice in enumerate(results[:3]):  # Show first 3
                        print(f"   Invoice {i+1}: {invoice.get('invoice_number')} - {invoice.get('client_name')} - ${invoice.get('total_amount')}")
                else:
                    print("   No invoices in results")
                    
            else:
                print(f"❌ Failed: {invoices_response.text}")
            
            # Test summary
            print("\n📊 Testing summary...")
            summary_response = requests.get(f'{base_url}/supabase/invoices/summary/', headers=headers)
            print(f"Status: {summary_response.status_code}")
            print(f"Raw response: {summary_response.text[:200]}...")
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                print(f"✅ Total Invoices: {summary_data.get('total_invoices', 0)}")
                print(f"✅ Total Amount: ${summary_data.get('total_amount', 0)}")
                print(f"✅ Draft Invoices: {summary_data.get('draft_invoices', 0)}")
            else:
                print(f"❌ Summary failed: {summary_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_invoice_display()
