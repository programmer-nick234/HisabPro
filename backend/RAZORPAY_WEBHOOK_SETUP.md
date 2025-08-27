# 🔗 Razorpay Webhook Setup Guide for HisabPro

## 📍 Your Webhook Endpoint
Your HisabPro application has a webhook endpoint configured at:
```
/api/webhook/razorpay/
```

## 🚀 Complete Setup Instructions

### Step 1: Get Your Webhook URL

#### For Local Development (Testing):
1. **Start your Django server:**
   ```bash
   cd backend
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Install and run ngrok:**
   ```bash
   # Download ngrok from https://ngrok.com/download
   # Then run:
   ngrok http 8000
   ```

3. **Copy the HTTPS URL from ngrok** (e.g., `https://abc123.ngrok.io`)

4. **Your webhook URL will be:**
   ```
   https://abc123.ngrok.io/api/webhook/razorpay/
   ```

#### For Production:
```
https://your-domain.com/api/webhook/razorpay/
```

### Step 2: Configure Razorpay Dashboard

1. **Login to Razorpay Dashboard**
2. **Go to Settings → Webhooks**
3. **Click "Add New Webhook"**
4. **Fill in the details:**
   - **Webhook URL**: `https://your-ngrok-url.ngrok.io/api/webhook/razorpay/`
   - **Secret**: Generate a strong secret (save this!)
   - **Alert Email**: `nikhilbajantri86@gmail.com`

5. **Select Active Events:**
   - ✅ `payment.authorized`
   - ✅ `payment.captured`
   - ✅ `payment.failed`
   - ✅ `payment.dispute.created`

6. **Click "Create Webhook"**

### Step 3: Update Your Environment Variables

Add these to your `.env` file in the backend directory:

```env
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_from_step2

# Email Configuration (already configured)
EMAIL_HOST_USER=nikhilbajantri86@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# Business Information
BUSINESS_NAME=DailyDine
BUSINESS_EMAIL=contact@dailydine.com
BUSINESS_PHONE=+91 98765 43210
BUSINESS_ADDRESS=Mumbai, Maharashtra, India
```

### Step 4: Test Your Webhook

1. **Start your server and ngrok**
2. **Create a test invoice in HisabPro**
3. **Generate a payment link**
4. **Make a test payment**
5. **Check if the webhook receives the event**

## 🔧 Webhook Event Handling

Your HisabPro application handles these events:

### `payment.captured`
- ✅ Updates invoice status to "paid"
- ✅ Sends beautiful payment confirmation email
- ✅ Records payment details

### `payment.failed`
- ✅ Updates invoice status
- ✅ Logs failure reason

### `payment.authorized`
- ✅ Updates payment status
- ✅ Waits for capture

## 🚨 Important Notes

### For Local Development:
- **Always use HTTPS** (ngrok provides this)
- **Keep ngrok running** while testing
- **Update webhook URL** if ngrok URL changes

### For Production:
- **Use your actual domain** with HTTPS
- **Keep webhook secret secure**
- **Monitor webhook logs** in Razorpay dashboard

## 🧪 Testing Your Webhook

### Quick Test:
1. Create an invoice in HisabPro
2. Generate payment link
3. Make a small test payment (₹1)
4. Check if:
   - Invoice status updates to "paid"
   - Customer receives payment confirmation email
   - Payment appears in invoice history

### Webhook Logs:
- Check Razorpay Dashboard → Webhooks → Your Webhook → Logs
- Look for successful 200 responses
- Debug any failed webhook calls

## 🎯 What Happens When Payment is Made:

1. **Customer pays** via Razorpay payment link
2. **Razorpay sends webhook** to your URL
3. **HisabPro receives webhook** and verifies signature
4. **Invoice status updated** to "paid"
5. **Beautiful confirmation email sent** to customer
6. **Payment recorded** in database

## 📞 Support

If you encounter issues:
1. Check webhook logs in Razorpay dashboard
2. Check Django server logs
3. Verify webhook URL is accessible
4. Ensure webhook secret matches

Your webhook endpoint is ready to receive payments! 🚀
