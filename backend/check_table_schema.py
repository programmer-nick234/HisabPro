#!/usr/bin/env python3
"""
Check Table Schema in Supabase
This script checks the actual schema of tables in Supabase
"""

import os
import sys
from supabase import create_client, Client
from decouple import config

def check_table_schema():
    """Check the schema of tables in Supabase"""
    print("🔍 Checking Supabase Table Schema")
    print("=" * 40)
    
    try:
        # Get Supabase credentials
        supabase_url = config('SUPABASE_URL')
        supabase_key = config('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL or SUPABASE_KEY not configured")
            return
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Check each table
        tables = ['user_profiles', 'invoices', 'invoice_items', 'payments']
        
        for table in tables:
            print(f"\n📋 Table: {table}")
            print("-" * 30)
            
            try:
                # Try to get one record to see the structure
                result = supabase.table(table).select('*').limit(1).execute()
                
                if result.data:
                    # Show the columns from the first record
                    columns = list(result.data[0].keys())
                    print(f"Columns found: {len(columns)}")
                    for col in columns:
                        print(f"  - {col}")
                else:
                    print("Table exists but is empty")
                    
            except Exception as e:
                print(f"❌ Error checking table {table}: {str(e)}")
        
        print("\n✅ Schema check completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_table_schema()
