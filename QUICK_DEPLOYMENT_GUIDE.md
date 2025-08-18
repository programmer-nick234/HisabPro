# 🚀 Quick Deployment Guide: Vercel + Railway

## ⚡ 5-Minute Setup

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done)
2. **Ensure these files are in your repository**:
   - `backend/requirements.txt`
   - `backend/railway.json`
   - `backend/Procfile`
   - `backend/runtime.txt`
   - `frontend/package.json`
   - `frontend/vercel.json`

### Step 2: Deploy Backend (Railway)

1. **Go to [railway.app](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your HisabPro repository**
5. **Wait for Railway to detect Python project**

#### Configure Environment Variables

In Railway dashboard → Variables tab, add:

```env
DEBUG=False
SECRET_KEY=your_very_secure_secret_key_here
ALLOWED_HOSTS=.railway.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/hisabpro
MONGODB_DATABASE=hisabpro
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

6. **Deploy** - Railway will automatically deploy
7. **Copy your Railway URL** (e.g., `https://your-app.up.railway.app`)

### Step 3: Deploy Frontend (Vercel)

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Import your GitHub repository**
5. **Configure project settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

#### Configure Environment Variables

In Vercel dashboard → Settings → Environment Variables, add:

```env
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app/api
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```

6. **Deploy** - Vercel will automatically deploy
7. **Your app is live!** (e.g., `https://your-app.vercel.app`)

---

## 🔧 Setup Database (MongoDB Atlas)

1. **Go to [cloud.mongodb.com](https://cloud.mongodb.com)**
2. **Create free account**
3. **Create new cluster** (free tier)
4. **Create database user**:
   - Username: `hisabpro_user`
   - Password: `secure_password`
5. **Get connection string**:
   ```
   mongodb+srv://hisabpro_user:secure_password@cluster.mongodb.net/hisabpro
   ```
6. **Add to Railway environment variables** as `MONGODB_URI`

---

## 🧪 Test Your Deployment

### Test Backend
```bash
curl https://your-railway-url.up.railway.app/
# Should return Django welcome page
```

### Test Frontend
1. Visit your Vercel URL
2. Try to login/create account
3. Test invoice creation

### Test Database
```bash
# Run the test script locally
cd backend
python test_db_connection.py
```

---

## 🔄 Continuous Deployment

Both platforms will automatically deploy when you push to `main`:

```bash
git add .
git commit -m "Update app"
git push origin main
# Vercel and Railway will auto-deploy
```

---

## 🚨 Common Issues & Solutions

### Build Fails on Railway
- Check `requirements.txt` exists
- Verify Python version in `runtime.txt`
- Check environment variables are set

### Build Fails on Vercel
- Ensure `package.json` is in `frontend/` directory
- Check all dependencies are listed
- Verify build command is correct

### CORS Errors
- Update `CORS_ALLOWED_ORIGINS` in Railway with your Vercel URL
- Ensure frontend URL is correct in environment variables

### Database Connection Fails
- Verify MongoDB Atlas cluster is running
- Check connection string format
- Ensure database user has correct permissions

---

## 📞 Need Help?

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)

---

## ✅ Success Checklist

- [ ] Backend deployed on Railway
- [ ] Frontend deployed on Vercel
- [ ] Database connected
- [ ] Environment variables set
- [ ] API responding
- [ ] Frontend loading
- [ ] Login working
- [ ] Invoice creation working

**Your HisabPro app is now live! 🎉**
