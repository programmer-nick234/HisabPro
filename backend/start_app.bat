@echo off
echo 🚀 Starting HisabPro Application...
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Start the application
python start_application.py

echo.
echo ✅ Application startup completed!
echo.
echo 📋 Next steps:
echo 1. Open a new terminal and run: cd frontend && npm run dev
echo 2. Open your browser and go to: http://localhost:3000
echo 3. Login with: admin/admin123
echo 4. Create invoices without any errors!
echo.
pause
