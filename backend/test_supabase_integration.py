#!/usr/bin/env python3
"""
Test Supabase Integration
Verifies that the Supabase integration is working correctly
"""

import os
import sys
import requests
import json
from supabase import create_client, Client
from decouple import config

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🔌 Testing Supabase connection...")
    
    try:
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not configured")
            return False
        
        # Test actual connection
        supabase = create_client(supabase_url, supabase_key)
        
        # Test connection by listing tables (this will fail if connection is bad)
        result = supabase.table('user_profiles').select('id').limit(1).execute()
        print("✅ Supabase connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return False

def test_django_server():
    """Test if Django server is running"""
    print("🌐 Testing Django server...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/api/auth/user/', timeout=5)
        if response.status_code == 401:  # Expected for unauthenticated request
            print("✅ Django server is running")
            return True
        else:
            print(f"⚠️  Django server responded with status: {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running")
        return False
    except Exception as e:
        print(f"❌ Error testing Django server: {str(e)}")
        return False

def test_supabase_api_endpoints():
    """Test Supabase API endpoints"""
    print("🔗 Testing Supabase API endpoints...")
    
    base_url = 'http://127.0.0.1:8000/api'
    endpoints = [
        '/supabase/invoices/',
        '/supabase/invoices/summary/',
        '/supabase/invoices/recent/',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 401:  # Expected for unauthenticated request
                print(f"✅ {endpoint} - Responding (401 Unauthorized - expected)")
            else:
                print(f"⚠️  {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")

def test_supabase_service():
    """Test the Supabase service layer"""
    print("🔧 Testing Supabase service layer...")
    
    try:
        from lib.supabase_service import supabase_service
        
        # Test connection
        supabase_service.connect()
        if supabase_service._connected:
            print("✅ Supabase service connection successful")
            
            # Test getting invoice count
            count = supabase_service.get_invoice_count(1)
            print(f"✅ Invoice count for user 1: {count}")
            
            # Test getting summary
            summary = supabase_service.get_invoice_summary(1)
            print(f"✅ Invoice summary for user 1: {summary}")
            
            return True
        else:
            print("❌ Supabase service connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Supabase service: {str(e)}")
        return False

def test_supabase_models():
    """Test Supabase models"""
    print("📋 Testing Supabase models...")
    
    try:
        from invoices.supabase_models import SupabaseInvoice, SupabaseInvoiceItem
        
        # Test invoice creation
        invoice_data = {
            'user_id': 1,
            'invoice_number': 'TEST-001',
            'client_name': 'Test Client',
            'subtotal': 100.0,
            'tax_rate': 10.0,
            'tax_amount': 10.0,
            'total_amount': 110.0,
            'status': 'pending'
        }
        
        invoice = SupabaseInvoice(invoice_data)
        print("✅ SupabaseInvoice model created successfully")
        
        # Test item creation
        item_data = {
            'invoice_id': 'test-id',
            'description': 'Test Item',
            'quantity': 2,
            'unit_price': 50.0,
            'total': 100.0
        }
        
        item = SupabaseInvoiceItem(item_data)
        print("✅ SupabaseInvoiceItem model created successfully")
        
        # Test calculations
        item.calculate_total()
        print(f"✅ Item total calculation: {item.total}")
        
        invoice.add_item('Test Item 2', 1, 25.0)
        invoice.calculate_totals()
        print(f"✅ Invoice total calculation: {invoice.total_amount}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase models: {str(e)}")
        return False

def test_supabase_serializers():
    """Test Supabase serializers"""
    print("📝 Testing Supabase serializers...")
    
    try:
        from invoices.supabase_serializers import SupabaseInvoiceSerializer, SupabaseInvoiceItemSerializer
        
        # Test invoice serializer
        invoice_data = {
            'invoice_number': 'TEST-002',
            'client_name': 'Test Client 2',
            'subtotal': 200.0,
            'tax_rate': 15.0,
            'tax_amount': 30.0,
            'total_amount': 230.0
        }
        
        serializer = SupabaseInvoiceSerializer(data=invoice_data, context={'user_id': 1})
        if serializer.is_valid():
            print("✅ SupabaseInvoiceSerializer validation successful")
        else:
            print(f"❌ SupabaseInvoiceSerializer validation failed: {serializer.errors}")
            return False
        
        # Test item serializer
        item_data = {
            'description': 'Test Item 3',
            'quantity': 3,
            'unit_price': 66.67
        }
        
        item_serializer = SupabaseInvoiceItemSerializer(data=item_data)
        if item_serializer.is_valid():
            print("✅ SupabaseInvoiceItemSerializer validation successful")
        else:
            print(f"❌ SupabaseInvoiceItemSerializer validation failed: {item_serializer.errors}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase serializers: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Supabase Integration Test Suite")
    print("=" * 40)
    
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("Django Server", test_django_server),
        ("Supabase Service", test_supabase_service),
        ("Supabase Models", test_supabase_models),
        ("Supabase Serializers", test_supabase_serializers),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Test API endpoints
    print(f"\n🔍 Running API Endpoints test...")
    test_supabase_api_endpoints()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Supabase integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
