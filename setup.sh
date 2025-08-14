#!/bin/bash

# HisabPro Setup Script
# This script will help you set up the HisabPro application

set -e

echo "🚀 Welcome to HisabPro Setup!"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL first."
    echo "   You can download it from: https://www.postgresql.org/download/"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Prerequisites check passed!"

# Create environment files
echo "📝 Creating environment files..."

# Backend .env
cat > backend/.env << EOF
DEBUG=True
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
DB_NAME=hisabpro
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
RAZORPAY_KEY_ID=your_razorpay_key_id_here
RAZORPAY_KEY_SECRET=your_razorpay_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_FROM=noreply@yourdomain.com
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
EOF

# Frontend .env.local
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id_here
EOF

echo "✅ Environment files created!"

# Setup Backend
echo "🐍 Setting up Django backend..."

cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
echo "Please enter details for the admin user:"
python manage.py createsuperuser

cd ..

echo "✅ Backend setup complete!"

# Setup Frontend
echo "⚛️  Setting up Next.js frontend..."

cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo "✅ Frontend setup complete!"

# Create database (if PostgreSQL is available)
if command -v psql &> /dev/null; then
    echo "🗄️  Setting up database..."
    
    # Check if database exists
    if ! psql -U postgres -lqt | cut -d \| -f 1 | grep -qw hisabpro; then
        echo "Creating database 'hisabpro'..."
        createdb -U postgres hisabpro
        echo "✅ Database created!"
    else
        echo "✅ Database 'hisabpro' already exists!"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update the environment variables in backend/.env and frontend/.env.local"
echo "2. Get your Razorpay API keys from: https://dashboard.razorpay.com/app/keys"
echo "3. Get your SendGrid API key from: https://app.sendgrid.com/settings/api_keys"
echo ""
echo "To start the application:"
echo ""
echo "Backend (Terminal 1):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Frontend (Terminal 2):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000/api"
echo "  Admin Panel: http://localhost:8000/admin"
echo ""
echo "Happy invoicing! 🚀"
