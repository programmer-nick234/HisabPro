# 🚀 HisabPro Free Hosting Deployment Guide

## **Overview**
This guide will help you deploy your HisabPro application using 100% FREE hosting services:
- **Frontend**: Vercel (Next.js)
- **Backend**: Railway (Django)
- **Database**: Supabase PostgreSQL (FREE tier)
- **Redis**: Railway Redis (included)

## **Prerequisites**
- GitHub account
- Supabase account (for database)
- Razorpay account (for payments)
- Gmail account (for email notifications)

---

## **PHASE 1: Set Up Supabase Database (15 minutes)**

### **Step 1: Get Your Supabase Credentials**
Since you're already using Supabase, you need to get these values from your Supabase dashboard:

1. Go to [supabase.com](https://supabase.com) and login
2. Select your project
3. Go to **Settings** → **Database**
4. Copy the **Connection string** (this is your `SUPABASE_DB_URL`)
5. Go to **Settings** → **API**
6. Copy **Project URL** (this is your `SUPABASE_URL`)
7. Copy **anon public** key (this is your `SUPABASE_KEY`)

### **Step 2: Verify Database Tables**
Make sure your Supabase database has all the required tables for HisabPro:
- `invoices`
- `invoice_items`
- `payments`
- `user_profiles`

---

## **PHASE 2: Deploy Backend to Railway (45 minutes)**

### **Step 1: Sign Up for Railway**
1. Go to [railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Authorize Railway to access your GitHub account

### **Step 2: Create New Project**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `HisabPro` repository
4. Select the `backend` folder as the root directory

### **Step 3: Configure Environment Variables**
In Railway dashboard, go to Variables tab and add:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=.railway.app,.vercel.app,localhost,127.0.0.1

# CORS Settings  
CORS_ALLOWED_ORIGINS=https://hisabpro.vercel.app,http://localhost:3000

# Email Settings (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com

# Supabase Database
SUPABASE_DB_URL=postgresql://postgres.your-project-id:your-password@aws-0-region.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_public_key

# Razorpay Settings
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# PDF Generation
USE_PLAYWRIGHT_PDF=True
USE_WEASYPRINT_PDF=True
USE_REPORTLAB_PDF=True
```

### **Step 4: Add Redis (Optional)**
1. In Railway dashboard, click "New" → "Database" → "Redis"
2. Railway will automatically set `REDIS_URL`
3. Your Supabase database is already configured separately

### **Step 5: Deploy**
1. Railway will automatically deploy your backend
2. Wait for deployment to complete (5-10 minutes)
3. Note your Railway URL: `https://your-app-name.up.railway.app`

---

## **PHASE 3: Deploy Frontend to Vercel (30 minutes)**

### **Step 1: Sign Up for Vercel**
1. Go to [vercel.com](https://vercel.com)
2. Click "Continue with GitHub"
3. Authorize Vercel to access your GitHub account

### **Step 2: Import Project**
1. Click "New Project"
2. Select your `HisabPro` repository
3. Set **Root Directory** to `frontend`
4. Framework Preset: Next.js (auto-detected)

### **Step 3: Configure Environment Variables**
In Vercel project settings, add:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app/api
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```

### **Step 4: Deploy**
1. Click "Deploy"
2. Wait for deployment (3-5 minutes)
3. Your app will be available at: `https://your-project.vercel.app`

---

## **PHASE 4: Connect Services (15 minutes)**

### **Step 1: Update Backend CORS**
1. Go to Railway dashboard
2. Update `CORS_ALLOWED_ORIGINS` variable:
   ```
   https://your-project.vercel.app,http://localhost:3000
   ```

### **Step 2: Update Frontend API URL**
1. Go to Vercel dashboard
2. Update `NEXT_PUBLIC_API_URL` variable:
   ```
   https://your-railway-app.up.railway.app/api
   ```

### **Step 3: Test the Connection**
1. Visit your Vercel URL
2. Try to register/login
3. Create a test invoice
4. Verify email notifications work

---

## **Important Notes**

### **Gmail App Password Setup**
1. Enable 2-factor authentication on Gmail
2. Go to Google Account Settings → Security → App passwords
3. Generate app password for "Mail"
4. Use this password in `EMAIL_HOST_PASSWORD`

### **Razorpay Setup**
1. Login to Razorpay Dashboard
2. Go to Settings → API Keys
3. Generate API keys for production
4. Set up webhook URL: `https://your-railway-app.up.railway.app/api/payments/webhook/`

### **Domain Configuration**
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://your-railway-app.up.railway.app`
- **Admin Panel**: `https://your-railway-app.up.railway.app/admin/`

---

## **Troubleshooting**

### **Common Issues**

1. **CORS Error**: Update `CORS_ALLOWED_ORIGINS` in Railway
2. **Database Connection**: Railway auto-configures `DATABASE_URL`
3. **Static Files**: Handled by WhiteNoise middleware
4. **Email Not Sending**: Check Gmail app password

### **Monitoring**
- **Railway Logs**: Check deployment logs in Railway dashboard
- **Vercel Logs**: Check function logs in Vercel dashboard
- **Django Admin**: Access at `/admin/` with superuser account

---

## **Cost Breakdown (FREE)**

| Service | Free Limits | Monthly Cost |
|---------|-------------|--------------|
| Railway | $5 credit/month | $0 |
| Vercel | 100GB bandwidth | $0 |
| Supabase | 500MB database, 2GB bandwidth | $0 |
| Redis | 25MB (Railway) | $0 |
| **Total** | | **$0/month** |

---

## **Next Steps After Deployment**

1. **Create Superuser**: Run in Railway console
   ```bash
   python manage.py createsuperuser
   ```

2. **Set Up Razorpay Webhooks**: Configure webhook URL in Razorpay dashboard

3. **Test Payment Flow**: Create test invoice and payment

4. **Monitor Usage**: Keep track of Railway credit usage

5. **Backup Data**: Export important data regularly

---

## **Support**

If you encounter issues:
1. Check Railway and Vercel logs
2. Verify environment variables
3. Test API endpoints directly
4. Check CORS configuration

---

**🎉 Congratulations! Your HisabPro app is now live and FREE!**
