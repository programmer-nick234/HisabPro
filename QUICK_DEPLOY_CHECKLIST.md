# ⚡ Quick Deploy Checklist

## **Before You Start**
- [ ] GitHub repository is ready
- [ ] Gmail app password generated
- [ ] Razorpay account created

## **Railway Backend (45 min)**
- [ ] Sign up at railway.app with GitHub
- [ ] Create new project from GitHub repo
- [ ] Set root directory to `backend`
- [ ] Add PostgreSQL database
- [ ] Add Redis database
- [ ] Configure environment variables:
  - [ ] SECRET_KEY
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS
  - [ ] CORS_ALLOWED_ORIGINS
  - [ ] EMAIL_HOST_USER & EMAIL_HOST_PASSWORD
  - [ ] RAZORPAY_KEY_ID & RAZORPAY_KEY_SECRET
- [ ] Deploy and note Railway URL

## **Vercel Frontend (30 min)**
- [ ] Sign up at vercel.com with GitHub
- [ ] Import project from GitHub
- [ ] Set root directory to `frontend`
- [ ] Configure environment variables:
  - [ ] NEXT_PUBLIC_API_URL (Railway URL + /api)
  - [ ] NEXT_PUBLIC_RAZORPAY_KEY_ID
- [ ] Deploy and note Vercel URL

## **Connect Services (15 min)**
- [ ] Update Railway CORS_ALLOWED_ORIGINS with Vercel URL
- [ ] Test login/registration
- [ ] Create test invoice
- [ ] Verify email sending

## **Post-Deployment**
- [ ] Create Django superuser in Railway console
- [ ] Set up Razorpay webhook URL
- [ ] Test payment flow

## **URLs to Remember**
- Frontend: `https://your-project.vercel.app`
- Backend API: `https://your-railway-app.up.railway.app/api`
- Admin Panel: `https://your-railway-app.up.railway.app/admin`

## **Emergency Contacts**
- Railway Support: help@railway.app
- Vercel Support: support@vercel.com
