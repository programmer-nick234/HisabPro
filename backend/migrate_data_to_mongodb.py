#!/usr/bin/env python
"""
Comprehensive data migration script from PostgreSQL to MongoDB Atlas
This script will migrate existing data from Django ORM to MongoDB
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.contrib.auth.models import User
from auth_app.models import UserProfile
from invoices.models import Invoice, InvoiceItem, Payment
from lib.mongodb import mongodb_service
from datetime import datetime
import json

def migrate_users_and_profiles():
    """Migrate users and user profiles to MongoDB"""
    print("Migrating users and profiles...")
    
    try:
        users = User.objects.all()
        migrated_count = 0
        
        for user in users:
            # Check if user profile already exists in MongoDB
            existing_profile = mongodb_service.get_user_profile(user.id)
            if existing_profile:
                print(f"User profile for {user.username} already exists in MongoDB, skipping...")
                continue
            
            # Get user profile from Django ORM
            try:
                profile = user.userprofile
                profile_data = {
                    'company_name': profile.company_name,
                    'phone': profile.phone,
                    'address': profile.address,
                    'gst_number': profile.gst_number,
                    'logo': str(profile.logo) if profile.logo else None,
                }
            except UserProfile.DoesNotExist:
                profile_data = {
                    'company_name': '',
                    'phone': '',
                    'address': '',
                    'gst_number': '',
                    'logo': None,
                }
            
            # Create profile in MongoDB
            mongodb_service.create_user_profile(user.id, profile_data)
            migrated_count += 1
            print(f"✓ Migrated profile for user: {user.username}")
        
        print(f"✓ Successfully migrated {migrated_count} user profiles")
        return True
        
    except Exception as e:
        print(f"✗ Error migrating users: {str(e)}")
        return False

def migrate_invoices():
    """Migrate invoices and related data to MongoDB"""
    print("Migrating invoices...")
    
    try:
        invoices = Invoice.objects.all()
        migrated_count = 0
        
        for invoice in invoices:
            # Check if invoice already exists in MongoDB
            # We'll use a combination of user_id and invoice_number to check
            existing_invoices = mongodb_service.get_user_invoices(invoice.user.id, limit=1000)
            existing_invoice = None
            for inv in existing_invoices:
                if inv.get('invoice_number') == invoice.invoice_number:
                    existing_invoice = inv
                    break
            
            if existing_invoice:
                print(f"Invoice {invoice.invoice_number} already exists in MongoDB, skipping...")
                continue
            
            # Prepare invoice data
            invoice_data = {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client_name,
                'client_email': invoice.client_email,
                'client_phone': invoice.client_phone,
                'client_address': invoice.client_address,
                'issue_date': invoice.issue_date.isoformat() if invoice.issue_date else None,
                'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                'status': invoice.status,
                'subtotal': float(invoice.subtotal),
                'tax_rate': float(invoice.tax_rate),
                'tax_amount': float(invoice.tax_amount),
                'total_amount': float(invoice.total_amount),
                'notes': invoice.notes,
                'terms_conditions': invoice.terms_conditions,
                'razorpay_payment_link': invoice.razorpay_payment_link,
                'razorpay_order_id': invoice.razorpay_order_id,
                'last_reminder_sent': invoice.last_reminder_sent.isoformat() if invoice.last_reminder_sent else None,
                'reminder_count': invoice.reminder_count,
            }
            
            # Create invoice in MongoDB
            mongodb_invoice_id = mongodb_service.create_invoice(invoice_data)
            
            # Migrate invoice items
            items = invoice.items.all()
            for item in items:
                item_data = {
                    'invoice_id': mongodb_invoice_id,
                    'description': item.description,
                    'quantity': float(item.quantity),
                    'unit_price': float(item.unit_price),
                    'total': float(item.total),
                }
                mongodb_service.create_invoice_item(item_data)
            
            # Migrate payments
            payments = invoice.payments.all()
            for payment in payments:
                payment_data = {
                    'invoice_id': mongodb_invoice_id,
                    'amount': float(payment.amount),
                    'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
                    'payment_method': payment.payment_method,
                    'transaction_id': payment.transaction_id,
                    'status': payment.status,
                    'notes': payment.notes,
                }
                mongodb_service.create_payment(payment_data)
            
            migrated_count += 1
            print(f"✓ Migrated invoice: {invoice.invoice_number} with {len(items)} items and {len(payments)} payments")
        
        print(f"✓ Successfully migrated {migrated_count} invoices")
        return True
        
    except Exception as e:
        print(f"✗ Error migrating invoices: {str(e)}")
        return False

def verify_migration():
    """Verify that migration was successful"""
    print("Verifying migration...")
    
    try:
        # Count users in Django vs MongoDB
        django_user_count = User.objects.count()
        mongodb_user_count = mongodb_service.db.user_profiles.count_documents({})
        
        print(f"Django users: {django_user_count}")
        print(f"MongoDB user profiles: {mongodb_user_count}")
        
        # Count invoices in Django vs MongoDB
        django_invoice_count = Invoice.objects.count()
        mongodb_invoice_count = mongodb_service.db.invoices.count_documents({})
        
        print(f"Django invoices: {django_invoice_count}")
        print(f"MongoDB invoices: {mongodb_invoice_count}")
        
        # Count invoice items
        django_item_count = InvoiceItem.objects.count()
        mongodb_item_count = mongodb_service.db.invoice_items.count_documents({})
        
        print(f"Django invoice items: {django_item_count}")
        print(f"MongoDB invoice items: {mongodb_item_count}")
        
        # Count payments
        django_payment_count = Payment.objects.count()
        mongodb_payment_count = mongodb_service.db.payments.count_documents({})
        
        print(f"Django payments: {django_payment_count}")
        print(f"MongoDB payments: {mongodb_payment_count}")
        
        # Check if counts match
        if (django_user_count == mongodb_user_count and 
            django_invoice_count == mongodb_invoice_count and
            django_item_count == mongodb_item_count and
            django_payment_count == mongodb_payment_count):
            print("✓ Migration verification successful - all counts match!")
            return True
        else:
            print("⚠ Migration verification failed - counts don't match")
            return False
            
    except Exception as e:
        print(f"✗ Error during verification: {str(e)}")
        return False

def create_mongodb_indexes():
    """Create indexes for better performance"""
    print("Creating MongoDB indexes...")
    
    try:
        # User profiles indexes
        mongodb_service.db.user_profiles.create_index("user_id", unique=True)
        print("✓ Created user_id index on user_profiles")
        
        # Invoices indexes
        mongodb_service.db.invoices.create_index("user_id")
        mongodb_service.db.invoices.create_index("invoice_number")
        mongodb_service.db.invoices.create_index("status")
        mongodb_service.db.invoices.create_index("created_at")
        print("✓ Created indexes on invoices")
        
        # Invoice items indexes
        mongodb_service.db.invoice_items.create_index("invoice_id")
        print("✓ Created invoice_id index on invoice_items")
        
        # Payments indexes
        mongodb_service.db.payments.create_index("invoice_id")
        mongodb_service.db.payments.create_index("transaction_id")
        print("✓ Created indexes on payments")
        
        print("✓ All indexes created successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error creating indexes: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("🚀 Starting MongoDB Migration")
    print("=" * 50)
    
    try:
        # Test MongoDB connection
        print("Testing MongoDB connection...")
        mongodb_service.client.admin.command('ping')
        print("✓ MongoDB connection successful")
        
        # Create indexes
        if not create_mongodb_indexes():
            print("Failed to create indexes, but continuing...")
        
        # Migrate users and profiles
        if not migrate_users_and_profiles():
            print("Failed to migrate users, stopping...")
            return False
        
        # Migrate invoices
        if not migrate_invoices():
            print("Failed to migrate invoices, stopping...")
            return False
        
        # Verify migration
        if not verify_migration():
            print("Migration verification failed")
            return False
        
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test the MongoDB-based API endpoints:")
        print("   - GET /api/mongodb/invoices/")
        print("   - GET /api/mongodb/invoices/summary/")
        print("   - GET /api/mongodb/invoices/recent/")
        print("2. Update your frontend to use MongoDB endpoints")
        print("3. Once confirmed working, you can remove the old Django ORM endpoints")
        
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
