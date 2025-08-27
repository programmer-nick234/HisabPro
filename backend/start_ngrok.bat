@echo off
echo Starting ngrok tunnel for HisabPro...
echo.
echo Make sure your Django server is running on port 8000
echo Then copy the HTTPS URL from ngrok and add /api/webhook/razorpay/ to it
echo.
echo Example: https://abc123.ngrok.io/api/webhook/razorpay/
echo.
pause
ngrok http 8000
