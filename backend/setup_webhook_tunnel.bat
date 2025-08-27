@echo off
echo ==============================================
echo    HisabPro Webhook Tunnel Setup
echo ==============================================
echo.
echo Step 1: Make sure Django server is running
echo Command: python manage.py runserver 0.0.0.0:8000
echo.
echo Step 2: Starting ngrok tunnel...
echo.
echo Once ngrok starts:
echo 1. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
echo 2. Your webhook URL will be: https://abc123.ngrok.io/api/webhook/razorpay/
echo 3. Enter this URL in Razorpay Dashboard
echo.
pause
ngrok http 8000
