# MongoDB Atlas Migration Guide

This guide will help you migrate your HisabPro Django application from PostgreSQL to MongoDB Atlas.

## Prerequisites

1. MongoDB Atlas account with a cluster set up
2. Your MongoDB connection string (already provided)
3. Python virtual environment activated

## Migration Steps

### 1. Install MongoDB Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Update Environment Variables

Create a `.env` file in the `backend` directory with the following content:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://nikhilbajantri86:NZfz6nbhOhREFy0t@hisabpro.hjtknwz.mongodb.net/?retryWrites=true&w=majority&appName=HisabPro

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Email Settings (SendGrid)
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@hisabpro.com

# Razorpay Settings
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-razorpay-webhook-secret

# Redis Settings
REDIS_URL=redis://localhost:6379/0
```

### 3. Run Migration Script

```bash
cd backend
python migrate_to_mongodb.py
```

### 4. Alternative Manual Migration

If the script doesn't work, you can run these commands manually:

```bash
cd backend

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser
```

### 5. Test the Application

```bash
# Start the development server
python manage.py runserver

# Test the API endpoints
curl http://localhost:8000/api/
```

## Changes Made

### Database Configuration
- Updated `settings.py` to use MongoDB Atlas instead of PostgreSQL
- Added `djongo` and `pymongo` dependencies
- Configured MongoDB connection string

### Model Updates
- Added `_id` fields with `ObjectIdField()` for MongoDB compatibility
- Added explicit table names in Meta classes
- Maintained all existing functionality

### Dependencies
- Replaced `psycopg2-binary` with `djongo` and `pymongo`
- All other dependencies remain the same

## Troubleshooting

### Connection Issues
1. Check your MongoDB Atlas network access settings
2. Verify the connection string is correct
3. Ensure your IP is whitelisted in MongoDB Atlas

### Migration Issues
1. Delete existing migration files if they conflict
2. Run `python manage.py makemigrations --empty` to create fresh migrations
3. Check the Django logs for specific error messages

### Model Issues
1. Ensure all models have `_id` fields
2. Check that table names are properly specified in Meta classes
3. Verify that all field types are compatible with MongoDB

## Security Notes

1. **Never commit your `.env` file** - it contains sensitive information
2. **Rotate your MongoDB password** regularly
3. **Use environment variables** for all sensitive configuration
4. **Enable MongoDB Atlas security features** like IP whitelisting and authentication

## Performance Considerations

1. MongoDB Atlas provides automatic scaling
2. Consider using MongoDB indexes for frequently queried fields
3. Monitor your MongoDB Atlas usage and costs
4. Use MongoDB Compass for database management and monitoring

## Support

If you encounter any issues during migration:
1. Check the Django logs for error messages
2. Verify your MongoDB Atlas cluster is running
3. Test the connection string in MongoDB Compass
4. Review the MongoDB Atlas documentation for troubleshooting
