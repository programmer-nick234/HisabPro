# HisabPro - Invoice Tracker for Freelancers

A simple, fully responsive invoice tracker built for freelancers in India who want to manage their billing without the complexity of tools like FreshBooks or QuickBooks.

## Features

- 📱 **Mobile-first responsive design** with Next.js and Tailwind CSS
- 🔐 **JWT Authentication** for secure user management
- 📊 **Dashboard** with visual summary cards (Pending, Paid, Overdue counts)
- 📄 **PDF Invoice Generation** with company branding
- 💳 **Razorpay Payment Links** for faster collections
- 📧 **Automatic Email Reminders** for overdue invoices
- 🎨 **Modern UI** with intuitive interface

## Tech Stack

### Frontend
- **Next.js 14** - React framework
- **Tailwind CSS** - Utility-first CSS framework
- **React Hook Form** - Form handling
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - API framework
- **PostgreSQL** - Database
- **JWT** - Authentication
- **Razorpay** - Payment processing
- **SendGrid** - Email service

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL
- Razorpay account
- SendGrid account

### Environment Variables

Create `.env` files in both `frontend/` and `backend/` directories:

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```

#### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://user:password@localhost:5432/hisabpro
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret
SENDGRID_API_KEY=your_sendgrid_api_key
EMAIL_FROM=noreply@yourdomain.com
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd HisabPro
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. **Setup Frontend**
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user

### Invoices
- `GET /api/invoices/` - List all invoices
- `POST /api/invoices/` - Create new invoice
- `GET /api/invoices/{id}/` - Get invoice details
- `PUT /api/invoices/{id}/` - Update invoice
- `DELETE /api/invoices/{id}/` - Delete invoice
- `POST /api/invoices/{id}/send-reminder/` - Send payment reminder
- `GET /api/invoices/{id}/pdf/` - Download PDF invoice
- `POST /api/invoices/{id}/razorpay-link/` - Generate Razorpay payment link

## Deployment

### Backend (Railway/Render)
1. Push code to GitHub
2. Connect repository to Railway/Render
3. Set environment variables
4. Deploy

### Frontend (Vercel)
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Deploy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
