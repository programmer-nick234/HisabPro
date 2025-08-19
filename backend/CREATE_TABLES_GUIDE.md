# 🗄️ Create Supabase Tables Guide

## ✅ **Connection Status: WORKING!**

Great news! Your Supabase connection is working perfectly. Now you just need to create the database tables.

## 🔗 **Quick Access**

**Your Supabase Dashboard**: https://supabase.com/dashboard/project/wetapqjagtipizvsbfok/editor

## 📋 **Step-by-Step Instructions**

### **Step 1: Access Table Editor**

1. Go to: https://supabase.com/dashboard/project/wetapqjagtipizvsbfok/editor
2. Click on **"Table Editor"** in the left sidebar
3. Click **"Create a new table"**

### **Step 2: Create Each Table**

You need to create **4 tables** in this order:

#### **Table 1: user_profiles**

**Table Name**: `user_profiles`

**Columns**:
- `id` - Type: `uuid` - Primary Key - Default: `gen_random_uuid()`
- `user_id` - Type: `integer` - Not Null
- `company_name` - Type: `varchar(200)`
- `company_address` - Type: `text`
- `company_phone` - Type: `varchar(20)`
- `company_email` - Type: `varchar(100)`
- `logo_url` - Type: `text`
- `tax_number` - Type: `varchar(50)`
- `created_at` - Type: `timestamptz` - Default: `now()`
- `updated_at` - Type: `timestamptz` - Default: `now()`

#### **Table 2: invoices**

**Table Name**: `invoices`

**Columns**:
- `id` - Type: `uuid` - Primary Key - Default: `gen_random_uuid()`
- `user_id` - Type: `integer` - Not Null
- `invoice_number` - Type: `varchar(50)` - Not Null
- `client_name` - Type: `varchar(200)` - Not Null
- `client_email` - Type: `varchar(100)`
- `client_phone` - Type: `varchar(20)`
- `client_address` - Type: `text`
- `issue_date` - Type: `date`
- `due_date` - Type: `date`
- `subtotal` - Type: `decimal(10,2)` - Default: `0`
- `tax_rate` - Type: `decimal(5,2)` - Default: `0`
- `tax_amount` - Type: `decimal(10,2)` - Default: `0`
- `total_amount` - Type: `decimal(10,2)` - Default: `0`
- `status` - Type: `varchar(20)` - Default: `'pending'`
- `notes` - Type: `text`
- `terms_conditions` - Type: `text`
- `payment_link` - Type: `text`
- `payment_gateway` - Type: `varchar(50)`
- `payment_id` - Type: `varchar(100)`
- `created_at` - Type: `timestamptz` - Default: `now()`
- `updated_at` - Type: `timestamptz` - Default: `now()`

#### **Table 3: invoice_items**

**Table Name**: `invoice_items`

**Columns**:
- `id` - Type: `uuid` - Primary Key - Default: `gen_random_uuid()`
- `invoice_id` - Type: `uuid` - Foreign Key to `invoices.id`
- `description` - Type: `varchar(500)` - Not Null
- `quantity` - Type: `decimal(10,2)` - Default: `0`
- `unit_price` - Type: `decimal(10,2)` - Default: `0`
- `total` - Type: `decimal(10,2)` - Default: `0`
- `created_at` - Type: `timestamptz` - Default: `now()`
- `updated_at` - Type: `timestamptz` - Default: `now()`

#### **Table 4: payments**

**Table Name**: `payments`

**Columns**:
- `id` - Type: `uuid` - Primary Key - Default: `gen_random_uuid()`
- `invoice_id` - Type: `uuid` - Foreign Key to `invoices.id`
- `amount` - Type: `decimal(10,2)` - Not Null
- `currency` - Type: `varchar(3)` - Default: `'INR'`
- `payment_method` - Type: `varchar(50)`
- `payment_gateway` - Type: `varchar(50)`
- `payment_id` - Type: `varchar(100)`
- `status` - Type: `varchar(20)` - Default: `'pending'`
- `payment_date` - Type: `timestamptz` - Default: `now()`
- `transaction_id` - Type: `varchar(100)`
- `notes` - Type: `text`
- `created_at` - Type: `timestamptz` - Default: `now()`
- `updated_at` - Type: `timestamptz` - Default: `now()`

## 🔧 **How to Create Tables in Supabase**

### **For Each Table:**

1. **Click "Create a new table"**
2. **Enter table name** (e.g., `user_profiles`)
3. **Add columns one by one:**
   - Click "Add column"
   - Enter column name
   - Select data type
   - Set constraints (Primary Key, Not Null, etc.)
   - Set default values if needed
4. **Click "Save"**

### **For Foreign Keys:**

After creating the `invoices` table, when creating `invoice_items`:
- Set `invoice_id` as Foreign Key
- Reference: `invoices.id`
- On Delete: `Cascade`

After creating the `invoices` table, when creating `payments`:
- Set `invoice_id` as Foreign Key
- Reference: `invoices.id`
- On Delete: `Cascade`

## ✅ **Verification**

After creating all tables, run this command to verify:

```bash
python create_supabase_tables_simple.py
```

You should see:
```
✅ Table 'user_profiles' already exists
✅ Table 'invoices' already exists
✅ Table 'invoice_items' already exists
✅ Table 'payments' already exists

🎉 All tables are ready!
```

## 🚀 **Next Steps**

Once all tables are created:

1. **Test the application:**
   ```bash
   python test_supabase_integration.py
   ```

2. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

3. **Start the frontend:**
   ```bash
   cd ../frontend
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Login: admin/admin123

## 🆘 **Need Help?**

If you encounter any issues:

1. **Check the Supabase dashboard** for any error messages
2. **Verify column types** match exactly
3. **Ensure foreign keys** are set up correctly
4. **Run the verification script** to check table status

## 🎉 **Success!**

Once all tables are created and verified, your HisabPro application will be fully connected to Supabase and ready to use!
