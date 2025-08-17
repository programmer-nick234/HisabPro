#!/usr/bin/env python
"""
Test all imports to verify they work correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def test_imports():
    """Test all problematic imports"""
    print("🧪 Testing All Imports...")
    print("=" * 40)
    
    imports_to_test = [
        # Django REST Framework
        ("rest_framework", "generics, status, permissions"),
        ("rest_framework.response", "Response"),
        ("rest_framework.decorators", "api_view, permission_classes"),
        ("rest_framework.views", "APIView"),
        
        # Django Core
        ("django.shortcuts", "get_object_or_404"),
        ("django.db.models", "Sum, Count"),
        ("django.http", "HttpResponse"),
        ("django.core.mail", "send_mail"),
        ("django.utils", "timezone"),
        ("django.conf", "settings"),
        
        # Third-party libraries
        ("razorpay", "Client"),
        ("io", "BytesIO"),
        
        # ReportLab (PDF generation)
        ("reportlab.pdfgen", "canvas"),
        ("reportlab.lib.pagesizes", "letter, A4"),
        ("reportlab.lib.units", "inch"),
        ("reportlab.lib", "colors"),
        ("reportlab.platypus", "SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer"),
        ("reportlab.lib.styles", "getSampleStyleSheet, ParagraphStyle"),
        ("reportlab.lib.enums", "TA_LEFT, TA_RIGHT, TA_CENTER"),
        
        # Standard library
        ("datetime", "datetime"),
        ("json", "dumps, loads"),
        
        # Local imports
        ("invoices.mongodb_models", "MongoDBInvoice, MongoDBInvoiceItem"),
        ("invoices.mongodb_serializers", "MongoDBInvoiceSerializer"),
        ("invoices.mongodb_views_v2", "MongoDBInvoiceListCreateView"),
        ("lib.mongodb", "mongodb_service"),
    ]
    
    success_count = 0
    total_count = len(imports_to_test)
    
    for module_name, import_names in imports_to_test:
        try:
            if module_name.startswith('.'):
                # Local import
                module = __import__(module_name[1:], fromlist=import_names.split(', '))
            else:
                # External import
                module = __import__(module_name, fromlist=import_names.split(', '))
            
            print(f"✅ {module_name} - {import_names}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {module_name} - {import_names}: {str(e)}")
    
    print("=" * 40)
    print(f"🎯 Results: {success_count}/{total_count} imports successful")
    
    if success_count == total_count:
        print("🎉 All imports working perfectly!")
    else:
        print("⚠️ Some imports failed - check the errors above")

if __name__ == '__main__':
    test_imports()
