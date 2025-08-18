#!/usr/bin/env python3
"""
Create Supabase Tables
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
        print("\n1. user_profiles table:")
        print("""
CREATE TABLE user_profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    company_name VARCHAR(200),
    company_address TEXT,
    company_phone VARCHAR(20),
    company_email VARCHAR(100),
    logo_url TEXT,
    tax_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
        """)
        
        print("\n2. invoices table:")
        print("""
CREATE TABLE invoices (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id INTEGER NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    client_name VARCHAR(200) NOT NULL,
    client_email VARCHAR(100),
    client_phone VARCHAR(20),
    client_address TEXT,
    issue_date DATE,
    due_date DATE,
    subtotal DECIMAL(10,2) DEFAULT 0,
    tax_rate DECIMAL(5,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    notes TEXT,
    terms_conditions TEXT,
    payment_link TEXT,
    payment_gateway VARCHAR(50),
    payment_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
        """)
        
        print("\n3. invoice_items table:")
        print("""
CREATE TABLE invoice_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description VARCHAR(500) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
        """)
        
        print("\n4. payments table:")
        print("""
CREATE TABLE payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(50),
    payment_gateway VARCHAR(50),
    payment_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    payment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    transaction_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
        """)
        
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
    print("🔧 Create Supabase Tables")
    print("=" * 40)
    
    # Test connection first
    if not test_supabase_connection():
        print("\n❌ Cannot proceed without a valid Supabase connection")
        sys.exit(1)
    
    # Create tables
    if create_supabase_tables():
        print("\n✅ All tables are ready!")
    else:
        print("\n⚠️  Please create the tables in Supabase dashboard and run this script again")
        sys.exit(1)
