#!/usr/bin/env python
"""
Customize PDF Company Information
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

def customize_company_info():
    """Show how to customize company information in PDF"""
    print("🏢 PDF Company Information Customization")
    print("=" * 50)
    
    print("\n📋 Current Company Information in PDF:")
    print("   Company Name: Your Company Name")
    print("   Address: 123 Business Street")
    print("   City: City, State 12345")
    print("   Phone: (555) 123-4567")
    print("   Email: info@company.com")
    print("   GST: 22AAAAA0000A1Z5")
    
    print("\n🔧 To customize company information:")
    print("1. Open file: backend/invoices/mongodb_views_v2.py")
    print("2. Find the 'Company and Client Information' section")
    print("3. Update the following lines:")
    
    print("\n   Current code:")
    print("   [Paragraph(\"Your Company Name\", normal_style), Paragraph(invoice.client_name, normal_style)],")
    print("   [Paragraph(\"123 Business Street\", normal_style), ...")
    print("   [Paragraph(\"City, State 12345\", normal_style), ...")
    print("   [Paragraph(\"Phone: (555) 123-4567\", normal_style), ...")
    print("   [Paragraph(\"Email: info@company.com\", normal_style), \"\"],")
    print("   [Paragraph(\"GST: 22AAAAA0000A1Z5\", normal_style), \"\"]")
    
    print("\n   Replace with your information:")
    print("   [Paragraph(\"Your Actual Company Name\", normal_style), Paragraph(invoice.client_name, normal_style)],")
    print("   [Paragraph(\"Your Actual Address\", normal_style), ...")
    print("   [Paragraph(\"Your City, State, PIN\", normal_style), ...")
    print("   [Paragraph(\"Phone: Your Phone Number\", normal_style), ...")
    print("   [Paragraph(\"Email: your@email.com\", normal_style), \"\"],")
    print("   [Paragraph(\"GST: Your GST Number\", normal_style), \"\"]")
    
    print("\n🎨 PDF Design Features:")
    print("   ✅ Professional color scheme (blue theme)")
    print("   ✅ Rounded corners on tables")
    print("   ✅ Proper spacing and typography")
    print("   ✅ Clear section separation")
    print("   ✅ Responsive layout")
    print("   ✅ Professional footer")
    
    print("\n💡 Additional Customization Options:")
    print("   - Add company logo (requires image handling)")
    print("   - Change color scheme (update HexColor values)")
    print("   - Modify fonts (update fontName values)")
    print("   - Add watermarks or headers")
    print("   - Include payment terms")
    print("   - Add QR codes for payments")

if __name__ == '__main__':
    customize_company_info()
