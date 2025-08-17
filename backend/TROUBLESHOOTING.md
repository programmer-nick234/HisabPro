# 🔧 Troubleshooting Guide - HisabPro Invoice System

## 🚨 **Common Errors and Solutions**

### **Error: "AxiosError: Request failed with status code 500"**

**Cause:** Django server is not running or MongoDB connection failed.

**Solution:**
1. **Start Django Server:**
   ```bash
   cd backend
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Check MongoDB Connection:**
   ```bash
   python test_mongodb.py
   ```

3. **Use the Startup Script:**
   ```bash
   python start_application.py
   ```

### **Error: "MongoDB connection failed"**

**Cause:** MongoDB server is not running.

**Solution:**
1. **Start MongoDB Server:**
   ```bash
   & "C:\Program Files\MongoDB\Server\8.0\bin\mongod.exe" --dbpath="C:\data\db"
   ```

2. **Check if MongoDB is installed:**
   ```bash
   winget install MongoDB.Server
   ```

3. **Create data directory:**
   ```bash
   mkdir C:\data\db
   ```

### **Error: "Invoice creation failed"**

**Cause:** Frontend is not connected to the correct API endpoints.

**Solution:**
1. **Check API Configuration:**
   - Ensure `frontend/lib/api.ts` is using MongoDB endpoints
   - Verify Django server is running on port 8000

2. **Test API Endpoints:**
   ```bash
   python test_mongodb_endpoints.py
   ```

## 🚀 **Quick Start Guide**

### **Step 1: Start All Services**
```bash
cd backend
python start_application.py
```

### **Step 2: Start Frontend**
```bash
cd frontend
npm run dev
```

### **Step 3: Access Application**
- URL: http://localhost:3000
- Login: admin/admin123

## 🔍 **Diagnostic Commands**

### **Check MongoDB Status:**
```bash
python test_mongodb.py
```

### **Check Django Server:**
```bash
python test_django_endpoints.py
```

### **Check MongoDB Endpoints:**
```bash
python test_mongodb_endpoints.py
```

### **Test Invoice Creation:**
```bash
python test_mongodb_invoice_creation.py
```

## 📋 **System Requirements**

- ✅ **MongoDB Server**: Running on localhost:27017
- ✅ **Django Server**: Running on localhost:8000
- ✅ **Frontend Server**: Running on localhost:3000
- ✅ **Python Virtual Environment**: Activated
- ✅ **Node.js**: Installed and working

## 🛠️ **Prevention Checklist**

### **Before Creating Invoices:**
1. ✅ MongoDB server is running
2. ✅ Django server is running
3. ✅ Frontend is connected to correct API
4. ✅ User is logged in
5. ✅ All services are healthy

### **Regular Maintenance:**
1. ✅ Clear old test data: `python clear_mongodb_data.py`
2. ✅ Update indexes: `python setup_mongodb_indexes.py`
3. ✅ Test all endpoints: `python test_mongodb_endpoints.py`

## 🆘 **Emergency Fixes**

### **If Nothing Works:**
1. **Restart Everything:**
   ```bash
   # Stop all servers (Ctrl+C)
   # Clear terminal
   # Start fresh
   cd backend
   python start_application.py
   ```

2. **Reset MongoDB Data:**
   ```bash
   python clear_mongodb_data.py
   python setup_mongodb_system.py
   ```

3. **Check Logs:**
   - Django logs: Check terminal output
   - MongoDB logs: Check MongoDB terminal
   - Frontend logs: Check browser console

## 📞 **Support**

If you still encounter issues:
1. Check this troubleshooting guide
2. Run diagnostic commands
3. Check system requirements
4. Restart all services

**Remember:** The most common cause of 500 errors is the Django server not running!
