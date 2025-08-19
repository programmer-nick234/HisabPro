#!/usr/bin/env python
"""
Direct test of PDF generation function
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hisabpro.settings')
django.setup()

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from invoices.supabase_models import SupabaseInvoice
from lib.supabase_service import supabase_service

def test_pdf_generation_direct():
    print("🔍 Direct PDF Generation Test")
    print("=" * 35)
    
    try:
        # Get invoice data
        supabase_service.connect()
        invoices_result = supabase_service.get_all_invoices()
        if not invoices_result:
            print("❌ No invoices found")
            return
        
        invoice_data = invoices_result[0]
        invoice_id = invoice_data['id']
        print(f"✅ Found invoice: {invoice_data.get('invoice_number', 'Unknown')}")
        
        # Get items
        items_data = supabase_service.get_invoice_items(invoice_id)
        print(f"✅ Found {len(items_data)} items")
        
        # Create invoice object
        invoice = SupabaseInvoice.from_dict(invoice_data)
        invoice.items = items_data
        print("✅ Invoice object created")
        
        # Business info
        business_info = {
            'business_name': getattr(settings, 'BUSINESS_NAME', 'Your Business Name'),
            'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@yourbusiness.com'),
            'business_phone': getattr(settings, 'BUSINESS_PHONE', '+1 (555) 123-4567'),
            'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business Street\nCity, State 12345'),
            'business_logo': getattr(settings, 'BUSINESS_LOGO', None),
            'payment_terms': getattr(settings, 'PAYMENT_TERMS', 'Net 30 days'),
        }
        
        # Render HTML template
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
        
        # Test ReportLab PDF generation with error handling
        print("\n🔍 Testing ReportLab PDF generation...")
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, mm
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
            from io import BytesIO
            
            print("✅ ReportLab imports successful")
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
            elements = []
            
            print("✅ PDF document created")
            
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
            
            print("✅ Styles created")
            
            # Title
            elements.append(Paragraph("INVOICE", title_style))
            elements.append(Spacer(1, 20))
            
            print("✅ Title added")
            
            # Header section with business and client info
            header_data = [
                [
                    # Business info (left)
                    Paragraph(f"<b>{business_info['business_name']}</b><br/>"
                             f"{business_info['business_email']}<br/>"
                             f"{business_info['business_phone']}<br/>"
                             f"{business_info['business_address']}", styles['Normal']),
                    # Client info (right)
                    Paragraph(f"<b>Bill To:</b><br/>"
                             f"<b>{invoice.client_name or 'N/A'}</b><br/>"
                             f"{invoice.client_email or ''}<br/>"
                             f"{invoice.client_phone or ''}<br/>"
                             f"{invoice.client_address or ''}", styles['Normal'])
                ]
            ]
            
            print("✅ Header data prepared")
            
            header_table = Table(header_data, colWidths=[doc.width/2.0]*2)
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 20))
            
            print("✅ Header table added")
            
            # Invoice details
            elements.append(Paragraph("Invoice Details", styles['Heading2']))
            invoice_details = [
                ['Invoice Number:', invoice.invoice_number or 'N/A'],
                ['Issue Date:', invoice.issue_date or 'N/A'],
                ['Due Date:', invoice.due_date or 'N/A'],
                ['Status:', (invoice.status or 'draft').upper()],
                ['Payment Terms:', business_info['payment_terms']]
            ]
            
            print("✅ Invoice details prepared")
            
            details_table = Table(invoice_details, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ]))
            elements.append(details_table)
            elements.append(Spacer(1, 20))
            
            print("✅ Invoice details table added")
            
            # Items table
            elements.append(Paragraph("Items & Services", styles['Heading2']))
            if invoice.items:
                items_data = [['Item/Service', 'Description', 'Qty', 'Rate', 'Tax', 'Amount']]
                for item in invoice.items:
                    items_data.append([
                        item.get('name', 'Service'),
                        item.get('description', '-'),
                        str(item.get('quantity', 1)),
                        f"${item.get('unit_price', 0):.2f}",
                        f"${item.get('tax_amount', 0):.2f}",
                        f"${item.get('total', 0):.2f}"
                    ])
                
                items_table = Table(items_data, colWidths=[1.5*inch, 2*inch, 0.5*inch, 1*inch, 0.8*inch, 1*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                elements.append(items_table)
            else:
                elements.append(Paragraph("No items added", styles['Normal']))
            
            print("✅ Items table added")
            
            elements.append(Spacer(1, 20))
            
            # Totals
            totals_data = [
                ['Total:', f"${invoice.total_amount or 0:.2f}"]
            ]
            
            # Add optional fields if they exist
            if hasattr(invoice, 'subtotal') and invoice.subtotal:
                totals_data.insert(0, ['Subtotal:', f"${invoice.subtotal:.2f}"])
            if hasattr(invoice, 'tax_amount') and invoice.tax_amount:
                totals_data.insert(-1, ['Tax:', f"${invoice.tax_amount:.2f}"])
            if hasattr(invoice, 'discount_amount') and invoice.discount_amount:
                totals_data.insert(-1, ['Discount:', f"-${invoice.discount_amount:.2f}"])
            
            print("✅ Totals data prepared")
            
            totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, -1), (1, -1), colors.white),
            ]))
            elements.append(totals_table)
            
            print("✅ Totals table added")
            
            # Notes
            if hasattr(invoice, 'notes') and invoice.notes:
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Notes:", styles['Heading2']))
                elements.append(Paragraph(invoice.notes, styles['Normal']))
            
            print("✅ Notes added")
            
            # Footer
            elements.append(Spacer(1, 30))
            footer_text = "Thank you for your business!"
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            elements.append(Paragraph(footer_text, footer_style))
            
            print("✅ Footer added")
            
            # Build PDF
            print("🔨 Building PDF...")
            doc.build(elements)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            
            print(f"✅ PDF generated successfully! ({len(pdf_bytes)} bytes)")
            
            # Save test PDF
            with open('direct_test.pdf', 'wb') as f:
                f.write(pdf_bytes)
            print("💾 Test PDF saved as: direct_test.pdf")
            
        except Exception as e:
            print(f"❌ ReportLab PDF generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Error in PDF generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation_direct()
