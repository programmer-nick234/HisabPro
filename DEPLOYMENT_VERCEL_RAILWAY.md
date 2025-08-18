# HisabPro Deployment Guide: Vercel + Railway

This guide will help you deploy HisabPro using Vercel for the frontend and Railway for the backend.

## 🚀 Quick Start

### Prerequisites
- GitHub repository with your HisabPro code
- Railway account (railway.app)
- Vercel account (vercel.com)
- MongoDB Atlas account (for database)
- Razorpay account (for payments)

---

## 📋 Step 1: Backend Deployment (Railway)

### 1.1 Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your HisabPro repository
4. Railway will automatically detect it's a Python project

### 1.2 Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here_make_it_long_and_random
ALLOWED_HOSTS=.railway.app,your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# Database (MongoDB Atlas)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/hisabpro?retryWrites=true&w=majority
MONGODB_DATABASE=hisabpro

# Redis (Railway Redis Plugin)
REDIS_URL=redis://your-redis-url-from-railway

# Razorpay
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Static Files
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media
```

### 1.3 Add Database (MongoDB Atlas)

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a free cluster
3. Create a database user
4. Get your connection string
5. Add it to Railway environment variables as `MONGODB_URI`

### 1.4 Add Redis (Optional)

1. In Railway dashboard, go to "New" → "Plugin"
2. Search for "Redis" and add it
3. Railway will automatically add `REDIS_URL` to your environment variables

### 1.5 Deploy Backend

1. Railway will automatically deploy when you push to your main branch
2. Or manually trigger deployment from Railway dashboard
3. Check the deployment logs for any errors

### 1.6 Get Backend URL

After successful deployment, Railway will provide a URL like:
`https://your-app-name-production.up.railway.app`

---

## 📋 Step 2: Frontend Deployment (Vercel)

### 2.1 Connect to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect it's a Next.js project

### 2.2 Configure Build Settings

In Vercel project settings:

- **Framework Preset**: Next.js
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`

### 2.3 Configure Environment Variables

In Vercel dashboard, go to Settings → Environment Variables and add:

```env
NEXT_PUBLIC_API_URL=https://your-railway-backend-url.up.railway.app/api
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```

### 2.4 Deploy Frontend

1. Vercel will automatically deploy when you push to your main branch
2. Or manually trigger deployment from Vercel dashboard
3. Your app will be available at: `https://your-app-name.vercel.app`

---

## 🔧 Step 3: Domain Configuration

### 3.1 Custom Domain (Optional)

#### For Railway Backend:
1. In Railway dashboard, go to Settings → Domains
2. Add your custom domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed by Railway

#### For Vercel Frontend:
1. In Vercel dashboard, go to Settings → Domains
2. Add your custom domain (e.g., `yourdomain.com`)
3. Update DNS records as instructed by Vercel

### 3.2 Update Environment Variables

After setting up custom domains, update your environment variables:

**Railway (Backend)**:
```env
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com,.railway.app
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Vercel (Frontend)**:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

---

## 🧪 Step 4: Testing Deployment

### 4.1 Test Backend API

```bash
# Test backend health
curl https://your-railway-backend-url.up.railway.app/

# Test API endpoints
curl https://your-railway-backend-url.up.railway.app/api/auth/login/
```

### 4.2 Test Frontend

1. Visit your Vercel URL
2. Test login functionality
3. Test invoice creation
4. Test payment integration

### 4.3 Test Database Connection

Create a test script to verify MongoDB connection:

```python
# test_db_connection.py
import os
from pymongo import MongoClient
from decouple import config

def test_mongodb():
    try:
        client = MongoClient(config('MONGODB_URI'))
        db = client[config('MONGODB_DATABASE')]
        # Test connection
        db.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb()
```

---

## 🔄 Step 5: Continuous Deployment

### 5.1 Automatic Deployments

Both Vercel and Railway will automatically deploy when you push to your main branch:

```bash
# Make changes to your code
git add .
git commit -m "Update invoice system"
git push origin main

# Vercel and Railway will automatically deploy
```

### 5.2 Environment-Specific Deployments

You can set up different environments:

**Development**:
- Branch: `develop`
- Railway: Development environment
- Vercel: Preview deployments

**Production**:
- Branch: `main`
- Railway: Production environment
- Vercel: Production deployment

---

## 📊 Step 6: Monitoring & Maintenance

### 6.1 Railway Monitoring

1. **Logs**: View real-time logs in Railway dashboard
2. **Metrics**: Monitor CPU, memory, and network usage
3. **Health Checks**: Railway automatically checks your app health

### 6.2 Vercel Monitoring

1. **Analytics**: View page views and performance
2. **Functions**: Monitor API function performance
3. **Edge Network**: View global performance metrics

### 6.3 Database Monitoring

1. **MongoDB Atlas**: Monitor database performance
2. **Backups**: Set up automatic backups
3. **Alerts**: Configure performance alerts

---

## 🔒 Step 7: Security Configuration

### 7.1 SSL/HTTPS

Both Vercel and Railway provide automatic SSL certificates.

### 7.2 Environment Variables

Never commit sensitive data to your repository:

```bash
# .gitignore
.env
.env.local
.env.production
```

### 7.3 CORS Configuration

Update your Django CORS settings:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.vercel.app",
    "https://yourdomain.com",
]

CORS_ALLOW_CREDENTIALS = True
```

---

## 💰 Cost Breakdown

### Railway (Backend)
- **Free Tier**: $0/month (limited usage)
- **Pro Plan**: $5/month (recommended)
- **Usage-based**: $0.000463 per second

### Vercel (Frontend)
- **Hobby Plan**: $0/month (unlimited)
- **Pro Plan**: $20/month (if needed)

### MongoDB Atlas
- **Free Tier**: $0/month (512MB storage)
- **Shared Cluster**: $9/month (if needed)

### Total Estimated Cost: $5-15/month

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures

**Railway Backend**:
```bash
# Check logs in Railway dashboard
# Common issues:
# - Missing requirements.txt
# - Python version mismatch
# - Environment variables not set
```

**Vercel Frontend**:
```bash
# Check build logs in Vercel dashboard
# Common issues:
# - Missing dependencies
# - Build command errors
# - Environment variables not set
```

#### 2. Database Connection Issues

```bash
# Test MongoDB connection
python test_db_connection.py

# Check MONGODB_URI format
mongodb+srv://username:password@cluster.mongodb.net/hisabpro?retryWrites=true&w=majority
```

#### 3. CORS Issues

```bash
# Check browser console for CORS errors
# Verify CORS_ALLOWED_ORIGINS in Railway environment variables
# Ensure frontend URL is correct
```

#### 4. Payment Integration Issues

```bash
# Test Razorpay keys
# Verify webhook URLs
# Check payment logs
```

### Getting Help

1. **Railway Support**: [docs.railway.app](https://docs.railway.app)
2. **Vercel Support**: [vercel.com/docs](https://vercel.com/docs)
3. **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)

---

## 🎉 Success Checklist

- [ ] Backend deployed on Railway
- [ ] Frontend deployed on Vercel
- [ ] Database connected and working
- [ ] Environment variables configured
- [ ] SSL certificates active
- [ ] API endpoints responding
- [ ] Frontend loading correctly
- [ ] Login functionality working
- [ ] Invoice creation working
- [ ] Payment integration tested
- [ ] Custom domain configured (optional)
- [ ] Monitoring set up
- [ ] Backups configured

Your HisabPro application is now live! 🚀
