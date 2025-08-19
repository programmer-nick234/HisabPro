#!/usr/bin/env python3
"""
Create Supabase Tables - Simple Version
Creates the necessary tables for the HisabPro application using Supabase client
"""

import os
import sys
from supabase import create_client, Client
from decouple import config

def create_supabase_tables():
    """Create tables in Supabase using the client API"""
    
    # Get Supabase credentials
    supabase_url = config('SUPABASE_URL')
    supabase_key = config('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL or SUPABASE_KEY not configured in .env file")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Test if tables already exist by trying to query them
        tables_to_check = ['user_profiles', 'invoices', 'invoice_items', 'payments']
        existing_tables = []
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('id').limit(1).execute()
                existing_tables.append(table)
                print(f"✅ Table '{table}' already exists")
            except Exception as e:
                print(f"❌ Table '{table}' does not exist: {str(e)}")
        
        if len(existing_tables) == len(tables_to_check):
            print("\n🎉 All tables already exist!")
            return True
        
        print(f"\n📝 Need to create {len(tables_to_check) - len(existing_tables)} tables")
        print("⚠️  Please create the following tables in your Supabase dashboard:")
        print("\n1. Go to your Supabase dashboard: https://supabase.com/dashboard")
        print("2. Click on your project")
        print("3. Go to 'Table Editor' in the left sidebar")
        print("4. Click 'Create a new table'")
        print("5. Create each table with the following structure:")
        
        print("\n📋 Table: user_profiles")
        print("Columns:")
        print("  - id: uuid (Primary Key, Default: gen_random_uuid())")
        print("  - user_id: integer (Not Null)")
        print("  - company_name: varchar(200)")
        print("  - company_address: text")
        print("  - company_phone: varchar(20)")
        print("  - company_email: varchar(100)")
        print("  - logo_url: text")
        print("  - tax_number: varchar(50)")
        print("  - created_at: timestamptz (Default: now())")
        print("  - updated_at: timestamptz (Default: now())")
        
        print("\n📋 Table: invoices")
        print("Columns:")
        print("  - id: uuid (Primary Key, Default: gen_random_uuid())")
        print("  - user_id: integer (Not Null)")
        print("  - invoice_number: varchar(50) (Not Null)")
        print("  - client_name: varchar(200) (Not Null)")
        print("  - client_email: varchar(100)")
        print("  - client_phone: varchar(20)")
        print("  - client_address: text")
        print("  - issue_date: date")
        print("  - due_date: date")
        print("  - subtotal: decimal(10,2) (Default: 0)")
        print("  - tax_rate: decimal(5,2) (Default: 0)")
        print("  - tax_amount: decimal(10,2) (Default: 0)")
        print("  - total_amount: decimal(10,2) (Default: 0)")
        print("  - status: varchar(20) (Default: 'pending')")
        print("  - notes: text")
        print("  - terms_conditions: text")
        print("  - payment_link: text")
        print("  - payment_gateway: varchar(50)")
        print("  - payment_id: varchar(100)")
        print("  - created_at: timestamptz (Default: now())")
        print("  - updated_at: timestamptz (Default: now())")
        
        print("\n📋 Table: invoice_items")
        print("Columns:")
        print("  - id: uuid (Primary Key, Default: gen_random_uuid())")
        print("  - invoice_id: uuid (Foreign Key to invoices.id)")
        print("  - description: varchar(500) (Not Null)")
        print("  - quantity: decimal(10,2) (Default: 0)")
        print("  - unit_price: decimal(10,2) (Default: 0)")
        print("  - total: decimal(10,2) (Default: 0)")
        print("  - created_at: timestamptz (Default: now())")
        print("  - updated_at: timestamptz (Default: now())")
        
        print("\n📋 Table: payments")
        print("Columns:")
        print("  - id: uuid (Primary Key, Default: gen_random_uuid())")
        print("  - invoice_id: uuid (Foreign Key to invoices.id)")
        print("  - amount: decimal(10,2) (Not Null)")
        print("  - currency: varchar(3) (Default: 'INR')")
        print("  - payment_method: varchar(50)")
        print("  - payment_gateway: varchar(50)")
        print("  - payment_id: varchar(100)")
        print("  - status: varchar(20) (Default: 'pending')")
        print("  - payment_date: timestamptz (Default: now())")
        print("  - transaction_id: varchar(100)")
        print("  - notes: text")
        print("  - created_at: timestamptz (Default: now())")
        print("  - updated_at: timestamptz (Default: now())")
        
        print("\n📋 After creating the tables, run this script again to verify they exist.")
        return False
        
    except Exception as e:
        print(f"❌ Error creating Supabase tables: {str(e)}")
        return False

def test_supabase_connection():
    """Test the Supabase connection"""
    try:
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not configured")
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Create Supabase Tables - Simple Version")
    print("=" * 50)
    
    # Test connection first
    if not test_supabase_connection():
        print("\n❌ Cannot proceed without a valid Supabase connection")
        sys.exit(1)
    
    # Create tables
    if create_supabase_tables():
        print("\n✅ All tables are ready!")
    else:
        print("\n⚠️  Please create the tables in Supabase dashboard and run this script again")
        print("\n🔗 Quick link to your Supabase dashboard:")
        print("   https://supabase.com/dashboard/project/wetapqjagtipizvsbfok/editor")
        sys.exit(1)
