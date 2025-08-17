# MongoDB Invoice System Setup Guide

This guide will help you set up the MongoDB-based invoice system for HisabPro.

## Prerequisites

1. **MongoDB Server**: You need MongoDB running locally or remotely
2. **Python 3.8+**: For Django backend
3. **Node.js 16+**: For Next.js frontend

## Database Configuration

The system is configured to use MongoDB with the following credentials:
- **Database Name**: `hisabpro`
- **Username**: `nikhilbajantri86`
- **Password**: `nikhilbajantri86`
- **Host**: `localhost`
- **Port**: `27017`

## Setup Steps

### 1. Install MongoDB (if not already installed)

#### Windows:
```bash
# Download and install MongoDB Community Server from:
# https://www.mongodb.com/try/download/community

# Or use Chocolatey:
choco install mongodb
```

#### macOS:
```bash
# Using Homebrew:
brew tap mongodb/brew
brew install mongodb-community
```

#### Linux (Ubuntu):
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org
```

### 2. Start MongoDB Service

#### Windows:
```bash
# Start MongoDB service
net start MongoDB

# Or start manually:
"C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" --dbpath="C:\data\db"
```

#### macOS:
```bash
# Start MongoDB service
brew services start mongodb-community
```

#### Linux:
```bash
# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 3. Create MongoDB User

Connect to MongoDB and create the user:

```bash
# Connect to MongoDB
mongosh

# Switch to admin database
use admin

# Create user
db.createUser({
  user: "nikhilbajantri86",
  pwd: "nikhilbajantri86",
  roles: [
    { role: "readWrite", db: "hisabpro" },
    { role: "dbAdmin", db: "hisabpro" }
  ]
})

# Exit MongoDB shell
exit
```

### 4. Setup Django Environment

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

The `.env` file should contain:

```env
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Configuration
MONGODB_URI=mongodb://nikhilbajantri86:nikhilbajantri86@localhost:27017/hisabpro
MONGODB_DATABASE=hisabpro

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Email Settings (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=nikhilbajantri86@gmail.com
EMAIL_HOST_PASSWORD=efleuomllopzfcja
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=nikhilbajantri86@gmail.com
```

### 6. Run MongoDB Setup Script

```bash
# Run the comprehensive setup script
python setup_mongodb_system.py
```

This script will:
- Test MongoDB connection
- Create necessary indexes
- Create sample invoice data
- Test API endpoints

### 7. Start the Application

#### Backend (Django):
```bash
# Start Django development server
python manage.py runserver
```

#### Frontend (Next.js):
```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

## Features

### Real-time Invoice Management

1. **Create Invoice**: 
   - Navigate to `/invoices/create`
   - Fill in client details and invoice items
   - Invoice is immediately saved to MongoDB

2. **View Invoices**: 
   - Dashboard shows real-time invoice summary
   - Invoice list updates automatically

3. **Delete Invoice**: 
   - Click delete button on any invoice
   - Invoice is immediately removed from MongoDB
   - Dashboard updates in real-time

4. **Edit Invoice**: 
   - Click edit on any invoice
   - Modify details and items
   - Changes are saved to MongoDB immediately

### MongoDB Collections

The system uses the following MongoDB collections:

1. **`invoices`**: Main invoice documents
2. **`invoice_items`**: Individual line items for each invoice
3. **`payments`**: Payment records (if implemented)
4. **`user_profiles`**: User profile data (if implemented)

### API Endpoints

- `GET /api/mongodb/invoices/` - List invoices
- `POST /api/mongodb/invoices/` - Create invoice
- `GET /api/mongodb/invoices/{id}/` - Get invoice details
- `PUT /api/mongodb/invoices/{id}/` - Update invoice
- `DELETE /api/mongodb/invoices/{id}/` - Delete invoice
- `GET /api/mongodb/invoices/summary/` - Get dashboard summary
- `GET /api/mongodb/invoices/recent/` - Get recent invoices
- `POST /api/mongodb/invoices/{id}/mark-paid/` - Mark invoice as paid

## Troubleshooting

### MongoDB Connection Issues

1. **Connection Refused**: Ensure MongoDB service is running
2. **Authentication Failed**: Check username/password in `.env` file
3. **Database Not Found**: Create the database and user as shown above

### Performance Issues

1. **Slow Queries**: Ensure indexes are created using `setup_mongodb_indexes.py`
2. **Memory Issues**: Monitor MongoDB memory usage
3. **Network Issues**: Check firewall settings for remote MongoDB

### Development Tips

1. **MongoDB Compass**: Use MongoDB Compass for visual database management
2. **Logs**: Check Django logs for detailed error information
3. **Testing**: Use the test scripts to verify functionality

## Production Deployment

For production deployment:

1. **Security**: Change default passwords and use strong authentication
2. **Backup**: Set up regular MongoDB backups
3. **Monitoring**: Implement MongoDB monitoring and alerting
4. **SSL**: Enable SSL/TLS for MongoDB connections
5. **Environment**: Use proper environment variables for production settings

## Support

If you encounter issues:

1. Check the logs in Django console
2. Verify MongoDB connection using `test_mongodb.py`
3. Ensure all dependencies are installed
4. Check the `.env` file configuration
