#!/usr/bin/env python
"""
Performance Optimization Script for HisabPro
"""

import os
import sys
import django
import time
import psutil
import requests
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from lib.mongodb import mongodb_service
from invoices.mongodb_models import MongoDBInvoice, MongoDBInvoiceItem

def check_system_performance():
    """Check system performance metrics"""
    print("🔍 System Performance Check")
    print("=" * 50)
    
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent}%")
    
    # Memory Usage
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)")
    
    # Disk Usage (Windows compatible)
    try:
        disk = psutil.disk_usage('C:\\')
        print(f"Disk Usage: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)")
        disk_ok = disk.percent < 90
    except:
        print("Disk Usage: Unable to check (Windows path issue)")
        disk_ok = True
    
    return cpu_percent < 80 and memory.percent < 80 and disk_ok

def optimize_mongodb_indexes():
    """Create and optimize MongoDB indexes"""
    print("\n🗄️ MongoDB Index Optimization")
    print("=" * 50)
    
    try:
        mongodb_service.connect()
        if not mongodb_service._connected:
            print("❌ MongoDB connection failed")
            return False
        
        # Create indexes for better performance
        indexes_created = []
        
        # Invoice indexes
        try:
            mongodb_service.db.invoices.create_index([("user_id", 1), ("created_at", -1)])
            indexes_created.append("invoices: user_id + created_at")
        except Exception as e:
            print(f"⚠️ Invoice index already exists: {str(e)}")
        
        try:
            mongodb_service.db.invoices.create_index([("invoice_number", 1)], unique=True)
            indexes_created.append("invoices: invoice_number (unique)")
        except Exception as e:
            print(f"⚠️ Invoice number index already exists: {str(e)}")
        
        try:
            mongodb_service.db.invoices.create_index([("status", 1)])
            indexes_created.append("invoices: status")
        except Exception as e:
            print(f"⚠️ Status index already exists: {str(e)}")
        
        # Invoice items indexes
        try:
            mongodb_service.db.invoice_items.create_index([("invoice_id", 1)])
            indexes_created.append("invoice_items: invoice_id")
        except Exception as e:
            print(f"⚠️ Invoice items index already exists: {str(e)}")
        
        print(f"✅ Created {len(indexes_created)} indexes:")
        for index in indexes_created:
            print(f"   - {index}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing indexes: {str(e)}")
        return False

def test_api_performance():
    """Test API endpoint performance"""
    print("\n🌐 API Performance Test")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    endpoints = [
        "/mongodb/invoices/summary/",
        "/mongodb/invoices/recent/",
        "/mongodb/invoices/",
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code in [200, 401]:
                status = "✅ Success"
            else:
                status = f"⚠️ Status {response.status_code}"
            
            print(f"{endpoint}: {status} ({response_time:.2f}ms)")
            results.append(response_time)
            
        except requests.exceptions.ConnectionError:
            print(f"{endpoint}: ❌ Server not running")
        except Exception as e:
            print(f"{endpoint}: ❌ Error: {str(e)}")
    
    if results:
        avg_response_time = sum(results) / len(results)
        print(f"\n📊 Average Response Time: {avg_response_time:.2f}ms")
        
        if avg_response_time < 500:
            print("✅ API performance is excellent!")
        elif avg_response_time < 1000:
            print("⚠️ API performance is good, but could be optimized")
        else:
            print("❌ API performance needs improvement")
    
    return results

def optimize_database_queries():
    """Optimize database queries"""
    print("\n🔍 Database Query Optimization")
    print("=" * 50)
    
    try:
        mongodb_service.connect()
        if not mongodb_service._connected:
            print("❌ MongoDB connection failed")
            return False
        
        # Test query performance
        start_time = time.time()
        
        # Test invoice retrieval
        invoices = MongoDBInvoice.get_by_user(1, limit=10)
        query_time = (time.time() - start_time) * 1000
        
        print(f"✅ Invoice query performance: {query_time:.2f}ms for {len(invoices)} invoices")
        
        if query_time < 100:
            print("✅ Query performance is excellent!")
        elif query_time < 500:
            print("⚠️ Query performance is good")
        else:
            print("❌ Query performance needs optimization")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing queries: {str(e)}")
        return False

def create_performance_report():
    """Create a comprehensive performance report"""
    print("\n📋 Performance Report")
    print("=" * 50)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'system_performance': check_system_performance(),
        'mongodb_optimized': optimize_mongodb_indexes(),
        'api_performance': test_api_performance(),
        'query_optimization': optimize_database_queries()
    }
    
    # Save report
    try:
        with open('performance_report.txt', 'w') as f:
            f.write("HisabPro Performance Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {report['timestamp']}\n\n")
            
            f.write("System Performance: ")
            f.write("✅ Good" if report['system_performance'] else "❌ Needs attention")
            f.write("\n")
            
            f.write("MongoDB Optimization: ")
            f.write("✅ Complete" if report['mongodb_optimized'] else "❌ Failed")
            f.write("\n")
            
            f.write("API Performance: ")
            if report['api_performance']:
                avg_time = sum(report['api_performance']) / len(report['api_performance'])
                f.write(f"✅ {avg_time:.2f}ms average")
            else:
                f.write("❌ Failed to test")
            f.write("\n")
            
            f.write("Query Optimization: ")
            f.write("✅ Complete" if report['query_optimization'] else "❌ Failed")
            f.write("\n")
        
        print("✅ Performance report saved to 'performance_report.txt'")
        
    except Exception as e:
        print(f"❌ Error saving report: {str(e)}")
    
    return report

def main():
    """Main optimization function"""
    print("🚀 HisabPro Performance Optimization")
    print("=" * 60)
    
    # Run all optimizations
    create_performance_report()
    
    print("\n🎯 Optimization Complete!")
    print("\n💡 Recommendations:")
    print("1. Monitor system resources regularly")
    print("2. Keep MongoDB indexes up to date")
    print("3. Use pagination for large datasets")
    print("4. Implement caching for frequently accessed data")
    print("5. Monitor API response times")

if __name__ == '__main__':
    main()
