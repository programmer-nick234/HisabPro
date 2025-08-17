#!/usr/bin/env python
"""
Test invoice creation with Django ORM
"""

import os
import sys
import django
from datetime import date, timedelta, datetime
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from invoices.models import Invoice, InvoiceItem
from django.contrib.auth.models import User

def test_invoice_creation():
    """Test creating an invoice with Django ORM"""
    try:
        print("Testing Invoice Creation with Django ORM...")
        print("=" * 50)
        
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"✅ Found admin user: {admin_user.username}")
        
        # Create a test invoice
        invoice = Invoice.objects.create(
            user=admin_user,
            invoice_number=f'TEST-{int(datetime.now().timestamp())}',
            client_name='Test Client',
            client_email='test@example.com',
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            subtotal=Decimal('100.00'),
            tax_rate=Decimal('18.00'),
            tax_amount=Decimal('18.00'),
            total_amount=Decimal('118.00'),
            status='pending'
        )
        print(f"✅ Created invoice: {invoice.invoice_number}")
        
        # Create invoice items
        item1 = InvoiceItem.objects.create(
            invoice=invoice,
            description='Test Service 1',
            quantity=1,
            unit_price=Decimal('50.00'),
            total=Decimal('50.00')
        )
        print(f"✅ Created item 1: {item1.description}")
        
        item2 = InvoiceItem.objects.create(
            invoice=invoice,
            description='Test Service 2',
            quantity=1,
            unit_price=Decimal('50.00'),
            total=Decimal('50.00')
        )
        print(f"✅ Created item 2: {item2.description}")
        
        # Verify invoice
        print(f"\n📋 Invoice Details:")
        print(f"   Invoice Number: {invoice.invoice_number}")
        print(f"   Client: {invoice.client_name}")
        print(f"   Total Amount: ${invoice.total_amount}")
        print(f"   Status: {invoice.status}")
        print(f"   Items: {invoice.items.count()}")
        
        # Clean up - delete test invoice
        invoice.delete()
        print(f"\n🧹 Cleaned up test invoice")
        
        print("\n🎉 Invoice creation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_invoice_creation()
