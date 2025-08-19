"""
PDF Generation Views for Invoices
Handles invoice PDF generation using the professional template
"""

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
import io
import os

from .supabase_models import SupabaseInvoice
from lib.supabase_service import supabase_service

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_invoice_pdf(request, invoice_id):
    """
    Generate a professional PDF invoice using the template
    """
    try:
        # Get invoice data from Supabase
        supabase_service.connect()
        invoice_data = supabase_service.get_invoice(invoice_id)
        
        if not invoice_data:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get invoice items
        items_data = supabase_service.get_invoice_items(invoice_id)
        
        # Create invoice object
        invoice = SupabaseInvoice.from_dict(invoice_data)
        invoice.items = items_data
        
        # Business information (you can make this configurable)
        business_info = {
            'business_name': getattr(settings, 'BUSINESS_NAME', 'Your Business Name'),
            'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@yourbusiness.com'),
            'business_phone': getattr(settings, 'BUSINESS_PHONE', '+1 (555) 123-4567'),
            'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business Street\nCity, State 12345'),
            'business_logo': getattr(settings, 'BUSINESS_LOGO', None),
            'payment_terms': getattr(settings, 'PAYMENT_TERMS', 'Net 30 days'),
        }
        
        # Render the template
        html_content = render_to_string('invoice_template.html', {
            'invoice': invoice,
            'business_name': business_info['business_name'],
            'business_email': business_info['business_email'],
            'business_phone': business_info['business_phone'],
            'business_address': business_info['business_address'],
            'business_logo': business_info['business_logo'],
            'payment_terms': business_info['payment_terms'],
        })
        
        # Generate PDF using weasyprint or similar
        try:
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # Configure fonts
            font_config = FontConfiguration()
            
            # Create PDF
            html_doc = HTML(string=html_content)
            css = CSS(string='''
                @page { size: A4; margin: 20mm; }
                body { font-family: Arial, sans-serif; }
            ''', font_config=font_config)
            
            pdf_bytes = html_doc.write_pdf(stylesheets=[css], font_config=font_config)
            
            # Create response
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            
            return response
            
        except ImportError:
            # Fallback: return HTML if weasyprint is not available
            logger.warning("WeasyPrint not available, returning HTML instead")
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.html"'
            return response
            
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_invoice_html(request, invoice_id):
    """
    Preview invoice as HTML (for testing the template)
    """
    try:
        # Get invoice data from Supabase
        supabase_service.connect()
        invoice_data = supabase_service.get_invoice(invoice_id)
        
        if not invoice_data:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get invoice items
        items_data = supabase_service.get_invoice_items(invoice_id)
        
        # Create invoice object
        invoice = SupabaseInvoice.from_dict(invoice_data)
        invoice.items = items_data
        
        # Business information
        business_info = {
            'business_name': getattr(settings, 'BUSINESS_NAME', 'Your Business Name'),
            'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@yourbusiness.com'),
            'business_phone': getattr(settings, 'BUSINESS_PHONE', '+1 (555) 123-4567'),
            'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business Street\nCity, State 12345'),
            'business_logo': getattr(settings, 'BUSINESS_LOGO', None),
            'payment_terms': getattr(settings, 'PAYMENT_TERMS', 'Net 30 days'),
        }
        
        # Render the template
        html_content = render_to_string('invoice_template.html', {
            'invoice': invoice,
            'business_name': business_info['business_name'],
            'business_email': business_info['business_email'],
            'business_phone': business_info['business_phone'],
            'business_address': business_info['business_address'],
            'business_logo': business_info['business_logo'],
            'payment_terms': business_info['payment_terms'],
        })
        
        return HttpResponse(html_content, content_type='text/html')
        
    except Exception as e:
        logger.error(f"Error generating HTML preview: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_sample_invoice_data():
    """
    Get sample invoice data for testing the template
    """
    return {
        'id': 'sample-123',
        'invoice_number': 'INV-2024-001',
        'client_name': 'John Doe',
        'client_email': 'john.doe@example.com',
        'client_phone': '+1 (555) 987-6543',
        'client_address': '456 Client Street\nClient City, State 54321',
        'invoice_date': '2024-01-15',
        'due_date': '2024-02-14',
        'status': 'pending',
        'subtotal': 1000.00,
        'tax_rate': 10.0,
        'tax_amount': 100.00,
        'discount_amount': 50.00,
        'total_amount': 1050.00,
        'notes': 'Thank you for your business. Please pay within 30 days.',
        'items': [
            {
                'name': 'Web Development',
                'description': 'Custom website development with responsive design',
                'quantity': 1,
                'unit_price': 800.00,
                'tax_amount': 80.00,
                'total': 880.00
            },
            {
                'name': 'SEO Optimization',
                'description': 'Search engine optimization services',
                'quantity': 1,
                'unit_price': 200.00,
                'tax_amount': 20.00,
                'total': 220.00
            }
        ]
    }

@api_view(['GET'])
@permission_classes([])  # No authentication required for sample preview
def preview_sample_invoice(request):
    """
    Preview sample invoice template (for testing)
    """
    try:
        # Create sample invoice object
        sample_data = get_sample_invoice_data()
        invoice = SupabaseInvoice.from_dict(sample_data)
        
        # Business information
        business_info = {
            'business_name': 'Your Business Name',
            'business_email': 'contact@yourbusiness.com',
            'business_phone': '+1 (555) 123-4567',
            'business_address': '123 Business Street\nCity, State 12345',
            'business_logo': None,
            'payment_terms': 'Net 30 days',
        }
        
        # Render the template
        html_content = render_to_string('invoice_template.html', {
            'invoice': invoice,
            'business_name': business_info['business_name'],
            'business_email': business_info['business_email'],
            'business_phone': business_info['business_phone'],
            'business_address': business_info['business_address'],
            'business_logo': business_info['business_logo'],
            'payment_terms': business_info['payment_terms'],
        })
        
        return HttpResponse(html_content, content_type='text/html')
        
    except Exception as e:
        logger.error(f"Error generating sample preview: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
