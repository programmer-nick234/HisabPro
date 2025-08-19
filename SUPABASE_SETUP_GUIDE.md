# 🔗 Supabase Connection Guide for HisabPro

This guide will help you connect your HisabPro application to Supabase (PostgreSQL database).

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
cd backend
python setup_supabase.py
```

### Option 2: Manual Setup
Follow the step-by-step instructions below.

## 📋 Prerequisites

1. **Supabase Account**: Sign up at [https://supabase.com](https://supabase.com)
2. **Python 3.9+**: Ensure Python is installed
3. **HisabPro Project**: Clone or download the project

## 🔧 Step-by-Step Setup

### 1. Create Supabase Project

1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `hisabpro` (or your preferred name)
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project"
6. Wait for the project to be created (2-3 minutes)

### 2. Get Supabase Credentials

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key-here

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Email Settings (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Razorpay Settings
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

# Redis Settings
REDIS_URL=redis://localhost:6379/0
```

### 4. Install Dependencies

```bash
cd backend

# Install Supabase client
pip install supabase

# Install other dependencies
pip install -r requirements.txt
```

### 5. Setup Database Schema

```bash
# Run the schema setup script
python setup_supabase_schema.py
```

This will create the following tables:
- `user_profiles` - User company information
- `invoices` - Invoice data
- `invoice_items` - Individual invoice items
- `payments` - Payment records

### 6. Test Connection

```bash
# Test Supabase connection
python test_supabase_integration.py
```

### 7. Create Test Data (Optional)

```bash
# Create test data in Supabase
python create_supabase_tables.py
```

## 🗄️ Database Schema

The application creates these tables automatically:

### user_profiles
```sql
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
```

### invoices
```sql
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
```

### invoice_items
```sql
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
```

### payments
```sql
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
```

## 🔒 Security Features

### Row Level Security (RLS)
- All tables have RLS enabled
- Users can only access their own data
- Policies ensure data isolation between users

### Indexes
- Performance indexes on frequently queried columns
- Composite indexes for complex queries

## 🚀 Start the Application

```bash
# Start Django backend
cd backend
python manage.py runserver

# Start Next.js frontend (in another terminal)
cd frontend
npm run dev
```

## 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **Login Credentials**: admin/admin123

## 🔗 API Endpoints

### Invoice Management
- `GET /api/supabase/invoices/` - List invoices
- `POST /api/supabase/invoices/` - Create invoice
- `GET /api/supabase/invoices/{id}/` - Get invoice details
- `PUT /api/supabase/invoices/{id}/` - Update invoice
- `DELETE /api/supabase/invoices/{id}/` - Delete invoice

### Dashboard
- `GET /api/supabase/invoices/summary/` - Get invoice summary
- `GET /api/supabase/invoices/recent/` - Get recent invoices

### Invoice Actions
- `POST /api/supabase/invoices/{id}/mark-paid/` - Mark invoice as paid
- `GET /api/supabase/invoices/{id}/pdf/` - Download PDF
- `POST /api/supabase/invoices/{id}/payment-link/` - Generate payment link

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Errors
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python test_supabase_integration.py
```

#### 2. Schema Issues
```bash
# Re-run schema setup
python setup_supabase_schema.py
```

#### 3. API Errors
```bash
# Check Django server logs
python manage.py runserver --verbosity=2

# Test API endpoints
curl http://127.0.0.1:8000/api/supabase/invoices/
```

#### 4. Frontend Issues
```bash
# Check browser console for errors
# Verify API endpoint URLs in frontend/lib/api.ts
```

### Error Messages

#### "SUPABASE_URL or SUPABASE_KEY not configured"
- Check your `.env` file exists in the `backend/` directory
- Verify the environment variables are correctly set
- Restart your terminal/IDE after creating the `.env` file

#### "relation does not exist"
- Run the schema setup: `python setup_supabase_schema.py`
- Check if tables were created in Supabase dashboard

#### "permission denied"
- Check Row Level Security policies in Supabase
- Verify user authentication is working

## 📊 Monitoring

### Supabase Dashboard
- **Database**: Monitor table data and performance
- **API**: Check API usage and logs
- **Auth**: Manage user authentication
- **Storage**: Handle file uploads (if needed)

### Django Admin
- Access at http://localhost:8000/admin
- Manage Django users and permissions
- Monitor application data

## 🔄 Migration from MongoDB

If you're migrating from MongoDB:

1. **Export MongoDB Data**: Use MongoDB export tools
2. **Transform Data**: Convert to PostgreSQL format
3. **Import to Supabase**: Use Supabase import tools
4. **Update Configuration**: Change from MongoDB to Supabase
5. **Test Application**: Verify all functionality works

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Django Documentation](https://docs.djangoproject.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Supabase documentation
3. Check Django logs for errors
4. Test individual components
5. Create an issue in the project repository

## 🎉 Success!

Once setup is complete, you'll have:
- ✅ Real-time PostgreSQL database with Supabase
- ✅ Secure Row Level Security policies
- ✅ Optimized database schema
- ✅ Full CRUD operations for invoices
- ✅ Payment integration ready
- ✅ Email notifications configured
- ✅ Modern web interface

Your HisabPro application is now ready to use with Supabase! 🚀
