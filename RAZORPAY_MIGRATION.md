# HisabPro: Stripe to Razorpay Migration Guide

This document outlines the complete migration from Stripe to Razorpay payment integration in the HisabPro application.

## Overview

The migration replaces all Stripe payment functionality with Razorpay, which is more suitable for the Indian market and provides better integration for INR transactions.

## Changes Made

### Backend Changes

#### 1. Dependencies
- **Removed**: `stripe==7.6.0`
- **Added**: `razorpay==1.4.1`

#### 2. Django Settings (`backend/hisabpro/settings.py`)
```python
# Old Stripe settings
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')

# New Razorpay settings
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')
RAZORPAY_WEBHOOK_SECRET = config('RAZORPAY_WEBHOOK_SECRET', default='')
```

#### 3. Models (`backend/invoices/models.py`)
```python
# Old Stripe fields
stripe_payment_link = models.URLField(blank=True)
stripe_payment_intent = models.CharField(max_length=255, blank=True)

# New Razorpay fields
razorpay_payment_link = models.URLField(blank=True)
razorpay_order_id = models.CharField(max_length=255, blank=True)

# Payment method default changed
payment_method = models.CharField(max_length=50, default='razorpay')
```

#### 4. Serializers (`backend/invoices/serializers.py`)
```python
# Old Stripe serializer
class StripePaymentLinkSerializer(serializers.Serializer):
    payment_link = serializers.URLField()

# New Razorpay serializer
class RazorpayPaymentLinkSerializer(serializers.Serializer):
    payment_link = serializers.URLField()
    order_id = serializers.CharField()
```

#### 5. Views (`backend/invoices/views.py`)
- **Removed**: `generate_stripe_payment_link` function
- **Added**: `generate_razorpay_payment_link` function
- **Added**: `razorpay_webhook` function for payment verification

Key differences in payment link generation:
- Creates Razorpay order first
- Generates payment link with order reference
- Stores both payment link and order ID
- Supports INR currency natively

#### 6. URLs (`backend/invoices/urls.py`)
```python
# Old Stripe endpoint
path('invoices/<uuid:invoice_id>/stripe-link/', generate_stripe_payment_link, name='generate-stripe-link')

# New Razorpay endpoints
path('invoices/<uuid:invoice_id>/razorpay-link/', generate_razorpay_payment_link, name='generate-razorpay-link')
path('webhook/razorpay/', razorpay_webhook, name='razorpay-webhook')
```

#### 7. Database Migration
Created migration `0002_replace_stripe_with_razorpay.py` to:
- Rename `stripe_payment_link` to `razorpay_payment_link`
- Rename `stripe_payment_intent` to `razorpay_order_id`
- Update payment method default to 'razorpay'

### Frontend Changes

#### 1. API Client (`frontend/lib/api.ts`)
```typescript
// Old Stripe function
generateStripeLink: (id: string) => api.post(`/invoices/${id}/stripe-link/`)

// New Razorpay function
generateRazorpayLink: (id: string) => api.post(`/invoices/${id}/razorpay-link/`)
```

#### 2. Invoice Interface (`frontend/app/invoices/page.tsx`)
```typescript
// Old Stripe field
stripe_payment_link?: string;

// New Razorpay field
razorpay_payment_link?: string;
```

### Environment Variables

#### Backend (.env)
```env
# Old Stripe variables
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key

# New Razorpay variables
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret
```

#### Frontend (.env.local)
```env
# Old Stripe variable
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key

# New Razorpay variable
NEXT_PUBLIC_RAZORPAY_KEY_ID=your_razorpay_key_id
```

### Configuration Files

#### 1. setup.sh
- Updated environment variable creation
- Changed API key instructions to Razorpay dashboard

#### 2. docker-compose.yml
- Added Razorpay environment variables for both backend and frontend services

#### 3. README.md
- Updated tech stack description
- Changed API endpoint documentation
- Updated environment variable examples

#### 4. DEPLOYMENT.md
- Updated deployment instructions with Razorpay variables
- Modified Docker Compose production configuration

## New Features

### 1. Razorpay Webhook Integration
- **Endpoint**: `/api/webhook/razorpay/`
- **Purpose**: Verify payments and update invoice status automatically
- **Features**:
  - Payment verification using webhook signature
  - Automatic invoice status update to 'paid'
  - Payment record creation
  - Email confirmation to clients

### 2. Enhanced Payment Flow
1. User generates payment link
2. Razorpay order is created
3. Payment link is generated with order reference
4. Client makes payment via Razorpay
5. Webhook verifies payment and updates invoice
6. Confirmation email is sent to client

## Setup Instructions

### 1. Get Razorpay API Keys
1. Sign up at [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Go to Settings → API Keys
3. Generate API keys (Key ID and Key Secret)
4. Set up webhook endpoint in Razorpay dashboard

### 2. Configure Webhook
1. In Razorpay dashboard, go to Settings → Webhooks
2. Add webhook URL: `https://yourdomain.com/api/webhook/razorpay/`
3. Select events: `payment.captured`
4. Copy the webhook secret

### 3. Update Environment Variables
```bash
# Backend
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Frontend
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_your_key_id
```

### 4. Run Database Migration
```bash
cd backend
python manage.py migrate
```

## Testing

### 1. Payment Link Generation
```bash
curl -X POST http://localhost:8000/api/invoices/{invoice_id}/razorpay-link/ \
  -H "Authorization: Bearer {your_jwt_token}"
```

### 2. Webhook Testing
Use Razorpay's webhook testing tool or send test payloads to verify webhook handling.

## Benefits of Migration

1. **Better INR Support**: Native INR currency support without conversion
2. **Indian Market Focus**: Optimized for Indian payment methods (UPI, cards, net banking)
3. **Lower Transaction Fees**: Generally lower fees for Indian transactions
4. **Better Documentation**: Comprehensive documentation in Hindi and English
5. **Local Support**: Better customer support for Indian businesses

## Rollback Plan

If needed, the migration can be rolled back by:
1. Reverting all code changes
2. Running reverse migration
3. Updating environment variables back to Stripe
4. Reinstalling Stripe dependency

## Support

For Razorpay integration issues:
- [Razorpay Documentation](https://razorpay.com/docs/)
- [Razorpay Support](https://razorpay.com/support/)
- [Razorpay Dashboard](https://dashboard.razorpay.com)
