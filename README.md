# HisabPro - Real-Time Invoice System with MongoDB

A modern, real-time invoice management system built with Django, MongoDB, and Next.js. Features instant invoice creation, real-time dashboard updates, and seamless MongoDB integration for optimal performance.

## 🚀 **Key Features**

- ⚡ **Real-Time MongoDB Integration** - Instant invoice creation and deletion
- 📱 **Mobile-first responsive design** with Next.js and Tailwind CSS
- 🔐 **JWT Authentication** for secure user management
- 📊 **Live Dashboard** with real-time MongoDB data
- 📄 **PDF Invoice Generation** with company branding
- 💳 **Razorpay Payment Links** for faster collections
- 📧 **Gmail SMTP Integration** for email notifications
- 🎨 **Modern UI** with intuitive interface
- 🔄 **Real-time Updates** - Dashboard reflects MongoDB state instantly

## 🛠️ **Tech Stack**

### Frontend
- **Next.js 15** - React framework with App Router
- **Tailwind CSS** - Utility-first CSS framework
- **React Hook Form** - Form handling
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - API framework
- **MongoDB** - NoSQL database with PyMongo
- **JWT** - Authentication
- **Razorpay** - Payment processing
- **Gmail SMTP** - Email service

## 🚀 **Quick Start**

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- MongoDB Community Server
- Razorpay account
- Gmail account (for SMTP)

### Environment Variables

Create `.env` file in the `backend/` directory:

```env
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/hisabpro
MONGODB_DATABASE=hisabpro

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
```

### Installation & Setup

#### 1. **Install MongoDB**
```bash
# Windows (using winget)
winget install MongoDB.Server

# Create data directory
mkdir C:\data\db
```

#### 2. **Start MongoDB Server**
```bash
# Start MongoDB manually
& "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath="C:\data\db"
```

#### 3. **Setup Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup MongoDB system
python setup_mongodb_system.py

# Create admin user
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

#### 4. **Setup Frontend**
```bash
cd frontend
npm install
```

#### 5. **Start All Services**

**Option A: Automated Startup (Recommended)**
```bash
cd backend
python start_application.py
```

**Option B: Manual Startup**
```bash
# Terminal 1: Start MongoDB
& "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath="C:\data\db"

# Terminal 2: Start Django
cd backend
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000

# Terminal 3: Start Frontend
cd frontend
npm run dev
```

#### 6. **Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin
- **Login Credentials**: admin/admin123

## 📊 **MongoDB Integration**

### Real-Time Features
- ✅ **Instant Invoice Creation** - Saves directly to MongoDB
- ✅ **Real-Time Dashboard** - Always reflects MongoDB state
- ✅ **Instant Deletion** - Removes from MongoDB immediately
- ✅ **Live Updates** - No page refresh needed

### MongoDB Collections
- `invoices` - Invoice documents
- `invoice_items` - Invoice line items
- `payments` - Payment records

### Database Schema
```javascript
// Invoice Document
{
  _id: ObjectId,
  user_id: Number,
  invoice_number: String,
  client_name: String,
  client_email: String,
  issue_date: String,
  due_date: String,
  status: String,
  subtotal: Number,
  tax_rate: Number,
  tax_amount: Number,
  total_amount: Number,
  created_at: Date,
  updated_at: Date
}

// Invoice Item Document
{
  _id: ObjectId,
  invoice_id: String,
  description: String,
  quantity: Number,
  unit_price: Number,
  total: Number
}
```

## 🔌 **API Endpoints**

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user

### MongoDB Invoice Endpoints (Real-time)
- `GET /api/mongodb/invoices/` - List all invoices
- `POST /api/mongodb/invoices/` - Create new invoice
- `GET /api/mongodb/invoices/{id}/` - Get invoice details
- `PUT /api/mongodb/invoices/{id}/` - Update invoice
- `DELETE /api/mongodb/invoices/{id}/` - Delete invoice
- `GET /api/mongodb/invoices/summary/` - Get dashboard summary
- `GET /api/mongodb/invoices/recent/` - Get recent invoices
- `POST /api/mongodb/invoices/{id}/mark-paid/` - Mark invoice as paid

### Legacy Django ORM Endpoints
- `GET /api/invoices/` - List invoices (Django ORM)
- `POST /api/invoices/` - Create invoice (Django ORM)
- `GET /api/invoices/{id}/` - Get invoice (Django ORM)
- `PUT /api/invoices/{id}/` - Update invoice (Django ORM)
- `DELETE /api/invoices/{id}/` - Delete invoice (Django ORM)

### Additional Features
- `POST /api/invoices/{id}/send-reminder/` - Send payment reminder
- `GET /api/invoices/{id}/pdf/` - Download PDF invoice
- `POST /api/invoices/{id}/razorpay-link/` - Generate Razorpay payment link

## 🔧 **Troubleshooting**

### Common Issues & Solutions

#### **Error: "AxiosError: Request failed with status code 500"**
**Cause:** Django server not running
**Solution:**
```bash
cd backend
python start_application.py
```

#### **Error: "MongoDB connection failed"**
**Cause:** MongoDB server not running
**Solution:**
```bash
# Start MongoDB
& "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath="C:\data\db"
```

#### **Error: "Invoice creation failed"**
**Cause:** Frontend not connected to correct API
**Solution:**
```bash
# Test endpoints
python test_mongodb_endpoints.py
```

### Diagnostic Commands
```bash
# Check MongoDB connection
python test_mongodb.py

# Test Django server
python test_django_endpoints.py

# Test MongoDB endpoints
python test_mongodb_endpoints.py

# Test invoice creation
python test_mongodb_invoice_creation.py

# Clear MongoDB data
python clear_mongodb_data.py

# Setup MongoDB system
python setup_mongodb_system.py
```

## 🛠️ **Development Tools**

### Startup Scripts
- `start_application.py` - Automated startup with health checks
- `start_app.bat` - Windows batch file for easy startup
- `setup_mongodb_system.py` - Complete MongoDB setup and testing

### Test Scripts
- `test_mongodb.py` - MongoDB connection test
- `test_django_endpoints.py` - Django API test
- `test_mongodb_endpoints.py` - MongoDB API test
- `test_mongodb_invoice_creation.py` - Invoice creation test
- `clear_mongodb_data.py` - Clear test data

### MongoDB Models
- `mongodb_models.py` - MongoDB document models
- `mongodb_serializers.py` - DRF serializers for MongoDB
- `mongodb_views_v2.py` - API views for MongoDB operations

## 📋 **System Requirements**

- ✅ **MongoDB Server**: Running on localhost:27017
- ✅ **Django Server**: Running on localhost:8000
- ✅ **Frontend Server**: Running on localhost:3000
- ✅ **Python Virtual Environment**: Activated
- ✅ **Node.js**: Installed and working

## 🚀 **Deployment**

### Backend (Railway/Render)
1. Push code to GitHub
2. Connect repository to Railway/Render
3. Set environment variables (MongoDB Atlas URI)
4. Deploy

### Frontend (Vercel)
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Deploy

### MongoDB Atlas (Production)
1. Create MongoDB Atlas cluster
2. Update `MONGODB_URI` in environment variables
3. Configure network access
4. Update connection settings

## 📚 **Documentation**

- [MongoDB Setup Guide](backend/MONGODB_SETUP.md)
- [Troubleshooting Guide](backend/TROUBLESHOOTING.md)
- [Migration Guide](backend/MONGODB_MIGRATION.md)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with MongoDB integration
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details.

## 🆘 **Support**

If you encounter issues:
1. Check the [Troubleshooting Guide](backend/TROUBLESHOOTING.md)
2. Run diagnostic commands
3. Ensure all services are running
4. Check MongoDB connection

**Remember:** The most common cause of 500 errors is the Django server not running!
