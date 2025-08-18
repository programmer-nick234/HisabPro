# MongoDB to Supabase Migration Guide

## Overview

This guide documents the complete migration from MongoDB Atlas to Supabase (PostgreSQL) for the HisabPro invoice management system.

## What Was Changed

### 1. **Database Layer**
- ❌ **Removed:** MongoDB Atlas connection and PyMongo
- ✅ **Added:** Supabase PostgreSQL connection
- ✅ **Added:** Row Level Security (RLS) policies
- ✅ **Added:** Proper relational database schema

### 2. **Backend Changes**
- ❌ **Removed:** `lib/mongodb.py` (MongoDB service)
- ❌ **Removed:** `invoices/mongodb_models.py` (MongoDB models)
- ❌ **Removed:** `invoices/mongodb_serializers.py` (MongoDB serializers)
- ❌ **Removed:** `invoices/mongodb_views_v2.py` (MongoDB views)
- ❌ **Removed:** `invoices/optimized_payment.py` (MongoDB payment system)
- ✅ **Added:** `lib/supabase_service.py` (Supabase service)
- ✅ **Added:** `invoices/supabase_models.py` (Supabase models)
- ✅ **Added:** `invoices/supabase_serializers.py` (Supabase serializers)
- ✅ **Added:** `invoices/supabase_views.py` (Supabase views)

### 3. **Configuration Changes**
- ❌ **Removed:** `MONGODB_URI` environment variable
- ✅ **Added:** `SUPABASE_URL` and `SUPABASE_KEY` environment variables
- ✅ **Updated:** Django settings to use Supabase configuration

### 4. **API Endpoints**
- ❌ **Removed:** `/mongodb/invoices/` endpoints
- ✅ **Added:** `/supabase/invoices/` endpoints
- ✅ **Updated:** Frontend API calls to use new endpoints

### 5. **Frontend Changes**
- ✅ **Updated:** `frontend/lib/api.ts` to use Supabase endpoints
- ✅ **Maintained:** Same API response format for backward compatibility

## Database Schema

### Tables Created

#### 1. `user_profiles`
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

#### 2. `invoices`
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

#### 3. `invoice_items`
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

#### 4. `payments`
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

### Security Features

#### Row Level Security (RLS)
- All tables have RLS enabled
- Users can only access their own data
- Policies ensure data isolation between users

#### Indexes
- Performance indexes on frequently queried columns
- Composite indexes for complex queries

## Setup Instructions

### 1. **Environment Configuration**

Update your `.env` file:
```bash
# Remove MongoDB configuration
# MONGODB_URI=...

# Add Supabase configuration
SUPABASE_URL=postgresql://postgres:12345678@db.wetapqjagtipizvsbfok.supabase.co:5432/postgres
SUPABASE_KEY=your-supabase-anon-key
```

### 2. **Install Dependencies**

```bash
# Install Supabase client
pip install supabase

# Update requirements.txt
pip freeze > requirements.txt
```

### 3. **Setup Database Schema**

```bash
# Run the schema setup script
python setup_supabase_schema.py
```

### 4. **Test Integration**

```bash
# Run the integration test suite
python test_supabase_integration.py
```

### 5. **Start the Application**

```bash
# Start Django server
python manage.py runserver

# Start frontend (in another terminal)
cd ../frontend
npm run dev
```

## API Endpoints

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

## Benefits of Migration

### 1. **Reliability**
- PostgreSQL is more reliable than MongoDB for transactional data
- Better ACID compliance
- Consistent data integrity

### 2. **Performance**
- Optimized queries with proper indexing
- Better query planning
- Faster complex joins

### 3. **Security**
- Row Level Security (RLS) policies
- Built-in authentication integration
- Better access control

### 4. **Scalability**
- Horizontal and vertical scaling options
- Better resource utilization
- Cost-effective for structured data

### 5. **Developer Experience**
- SQL queries are more familiar
- Better tooling and ecosystem
- Easier debugging and monitoring

## Troubleshooting

### Common Issues

#### 1. **Connection Errors**
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python test_supabase_integration.py
```

#### 2. **Schema Issues**
```bash
# Re-run schema setup
python setup_supabase_schema.py
```

#### 3. **API Errors**
```bash
# Check Django server logs
python manage.py runserver --verbosity=2

# Test API endpoints
curl http://127.0.0.1:8000/api/supabase/invoices/
```

#### 4. **Frontend Issues**
```bash
# Check browser console for errors
# Verify API endpoint URLs in frontend/lib/api.ts
```

### Performance Optimization

#### 1. **Database Indexes**
- Ensure all indexes are created
- Monitor query performance
- Add indexes for slow queries

#### 2. **Caching**
- Implement Redis caching for frequently accessed data
- Cache invoice summaries and recent invoices

#### 3. **Pagination**
- Use proper pagination for large datasets
- Implement cursor-based pagination for better performance

## Migration Checklist

- [ ] Update environment variables
- [ ] Install Supabase dependencies
- [ ] Run database schema setup
- [ ] Test Supabase connection
- [ ] Verify API endpoints
- [ ] Test frontend integration
- [ ] Update documentation
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Backup old MongoDB data (if needed)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Supabase documentation
3. Check Django logs for errors
4. Test individual components

## Future Enhancements

### 1. **Real-time Features**
- Implement Supabase real-time subscriptions
- Live invoice updates
- Real-time notifications

### 2. **Advanced Queries**
- Complex reporting queries
- Analytics and insights
- Data aggregation

### 3. **Integration**
- Payment gateway integration
- Email service integration
- File storage integration

### 4. **Performance**
- Query optimization
- Caching strategies
- Database tuning
