#!/usr/bin/env python
"""
Debug script to test PDF generation step by step
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.template.loader import render_to_string
from django.conf import settings
from invoices.supabase_models import SupabaseInvoice
from lib.supabase_service import supabase_service

def test_pdf_generation():
    print("🔍 Debugging PDF Generation")
    print("=" * 40)
    
    try:
        # Step 1: Connect to Supabase
        print("1️⃣ Connecting to Supabase...")
        supabase_service.connect()
        print("✅ Connected successfully")
        
        # Step 2: Get invoice data
        print("\n2️⃣ Getting invoice data...")
        invoices_result = supabase_service.get_all_invoices()
        if not invoices_result:
            print("❌ No invoices found")
            return
        
        invoice_data = invoices_result[0]
        invoice_id = invoice_data['id']
        print(f"✅ Found invoice: {invoice_data.get('invoice_number', 'Unknown')}")
        
        # Step 3: Get invoice items
        print("\n3️⃣ Getting invoice items...")
        items_data = supabase_service.get_invoice_items(invoice_id)
        print(f"✅ Found {len(items_data)} items")
        
        # Step 4: Create invoice object
        print("\n4️⃣ Creating invoice object...")
        invoice = SupabaseInvoice.from_dict(invoice_data)
        invoice.items = items_data
        print("✅ Invoice object created")
        
        # Step 5: Get business info
        print("\n5️⃣ Getting business info...")
        business_info = {
            'business_name': getattr(settings, 'BUSINESS_NAME', 'Your Business Name'),
            'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@yourbusiness.com'),
            'business_phone': getattr(settings, 'BUSINESS_PHONE', '+1 (555) 123-4567'),
            'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business Street\nCity, State 12345'),
            'business_logo': getattr(settings, 'BUSINESS_LOGO', None),
            'payment_terms': getattr(settings, 'PAYMENT_TERMS', 'Net 30 days'),
        }
        print("✅ Business info retrieved")
        
        # Step 6: Render HTML template
        print("\n6️⃣ Rendering HTML template...")
        html_content = render_to_string('invoice_template.html', {
            'invoice': invoice,
            'business_name': business_info['business_name'],
            'business_email': business_info['business_email'],
            'business_phone': business_info['business_phone'],
            'business_address': business_info['business_address'],
            'business_logo': business_info['business_logo'],
            'payment_terms': business_info['payment_terms'],
        })
        print(f"✅ HTML template rendered ({len(html_content)} characters)")
        
        # Step 7: Test ReportLab PDF generation
        print("\n7️⃣ Testing ReportLab PDF generation...")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, mm
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
            from io import BytesIO
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            # Title
            elements.append(Paragraph("INVOICE", title_style))
            elements.append(Spacer(1, 20))
            
            # Simple test content
            elements.append(Paragraph(f"Invoice Number: {invoice.invoice_number}", styles['Normal']))
            elements.append(Paragraph(f"Client: {invoice.client_name}", styles['Normal']))
            elements.append(Paragraph(f"Total: ${invoice.total_amount or 0:.2f}", styles['Normal']))
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            
            print(f"✅ PDF generated successfully! ({len(pdf_bytes)} bytes)")
            
            # Save test PDF
            with open('debug_test.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("💾 Test PDF saved as: debug_test.pdf")
            
        except Exception as e:
            print(f"❌ ReportLab PDF generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error in PDF generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
