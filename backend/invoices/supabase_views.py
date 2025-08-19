"""
Supabase views for HisabPro application
Handles API endpoints for invoices, items, and payments
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.http import HttpResponse
import io
import logging

from .supabase_serializers import (
    SupabaseInvoiceSerializer, 
    SupabaseInvoiceItemSerializer,
    SupabasePaymentSerializer,
    InvoiceSummarySerializer,
    InvoiceListSerializer
)
from .supabase_models import SupabaseInvoice, SupabaseInvoiceItem, SupabasePayment
from lib.supabase_service import supabase_service

logger = logging.getLogger(__name__)

class SupabaseInvoicePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class SupabaseInvoiceListCreateView(generics.ListCreateAPIView):
    """List and create invoices using Supabase"""
    serializer_class = SupabaseInvoiceSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SupabaseInvoicePagination
    
    def get_queryset(self):
        """Get invoices for the current user"""
        try:
            supabase_service.connect()
            user_id = self.request.user.id
            invoices_data = supabase_service.get_user_invoices(user_id)
            
            # Convert to SupabaseInvoice objects
            invoices = []
            for data in invoices_data:
                invoice = SupabaseInvoice.from_dict(data)
                # Get items for this invoice
                items_data = supabase_service.get_invoice_items(invoice.id)
                invoice.items = [SupabaseInvoiceItem.from_dict(item) for item in items_data]
                invoices.append(invoice)
            
            return invoices
        except Exception as e:
            logger.error(f"Error getting invoices: {str(e)}")
            return []
    
    def create(self, request, *args, **kwargs):
        """Create a new invoice"""
        try:
            supabase_service.connect()
            
            # Add user_id to context
            serializer = self.get_serializer(data=request.data, context={'user_id': request.user.id})
            serializer.is_valid(raise_exception=True)
            
            # Create invoice in Supabase
            invoice_data = serializer.validated_data
            
            # Auto-generate invoice number if not provided
            if not invoice_data.get('invoice_number'):
                from datetime import datetime
                invoice_data['invoice_number'] = f'INV-{datetime.now().strftime("%Y%m%d%H%M%S")}'
            
            # Add required invoice_date if not provided
            if not invoice_data.get('invoice_date'):
                from datetime import datetime
                invoice_data['invoice_date'] = datetime.now().isoformat()
            
            # Add required due_date if not provided (30 days from now)
            if not invoice_data.get('due_date'):
                from datetime import datetime, timedelta
                due_date = datetime.now() + timedelta(days=30)
                invoice_data['due_date'] = due_date.isoformat()
            
            # Ensure status is valid (use 'draft' instead of 'pending' if needed)
            if invoice_data.get('status') == 'pending':
                invoice_data['status'] = 'draft'
            
            # Filter out fields that don't exist in Supabase table
            allowed_fields = ['invoice_number', 'client_name', 'client_email', 'total_amount', 'status', 'notes', 'payment_link', 'payment_gateway', 'payment_id', 'invoice_date', 'due_date']
            filtered_data = {k: v for k, v in invoice_data.items() if k in allowed_fields}
            
            invoice_id = supabase_service.create_invoice(filtered_data)
            
            if not invoice_id:
                return Response({'error': 'Failed to create invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Create items if provided
            items_data = request.data.get('items', [])
            for item_data in items_data:
                item_data['invoice_id'] = invoice_id
                supabase_service.create_invoice_item(item_data)
            
            # Get the created invoice
            created_invoice_data = supabase_service.get_invoice(invoice_id)
            if created_invoice_data:
                created_invoice = SupabaseInvoice.from_dict(created_invoice_data)
                # Get items
                items_data = supabase_service.get_invoice_items(invoice_id)
                created_invoice.items = [SupabaseInvoiceItem.from_dict(item) for item in items_data]
                
                response_serializer = self.get_serializer(created_invoice)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response({'error': 'Invoice created but could not retrieve'}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SupabaseInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete invoices using Supabase"""
    serializer_class = SupabaseInvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get a specific invoice"""
        try:
            supabase_service.connect()
            invoice_id = self.kwargs.get('pk')
            user_id = self.request.user.id
            
            # Get invoice
            invoice_data = supabase_service.get_invoice(invoice_id)
            if not invoice_data:
                return None
            
            # Check if user owns this invoice
            if invoice_data.get('user_id') != user_id:
                return None
            
            invoice = SupabaseInvoice.from_dict(invoice_data)
            
            # Get items
            items_data = supabase_service.get_invoice_items(invoice_id)
            invoice.items = [SupabaseInvoiceItem.from_dict(item) for item in items_data]
            
            return invoice
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}")
            return None
    
    def update(self, request, *args, **kwargs):
        """Update an invoice"""
        try:
            supabase_service.connect()
            invoice_id = self.kwargs.get('pk')
            
            # Get current invoice
            invoice_data = supabase_service.get_invoice(invoice_id)
            if not invoice_data:
                return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Update invoice
            update_data = request.data.copy()
            success = supabase_service.update_invoice(invoice_id, update_data)
            
            if not success:
                return Response({'error': 'Failed to update invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Update items if provided
            items_data = request.data.get('items')
            if items_data is not None:
                # Delete existing items
                existing_items = supabase_service.get_invoice_items(invoice_id)
                for item in existing_items:
                    supabase_service.delete_invoice_item(item['id'])
                
                # Create new items
                for item_data in items_data:
                    item_data['invoice_id'] = invoice_id
                    supabase_service.create_invoice_item(item_data)
            
            # Get updated invoice
            updated_invoice_data = supabase_service.get_invoice(invoice_id)
            if updated_invoice_data:
                updated_invoice = SupabaseInvoice.from_dict(updated_invoice_data)
                # Get items
                items_data = supabase_service.get_invoice_items(invoice_id)
                updated_invoice.items = [SupabaseInvoiceItem.from_dict(item) for item in items_data]
                
                serializer = self.get_serializer(updated_invoice)
                return Response(serializer.data)
            
            return Response({'error': 'Invoice updated but could not retrieve'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating invoice: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an invoice"""
        try:
            supabase_service.connect()
            invoice_id = self.kwargs.get('pk')
            
            # Delete items first
            items_data = supabase_service.get_invoice_items(invoice_id)
            for item in items_data:
                supabase_service.delete_invoice_item(item['id'])
            
            # Delete invoice
            success = supabase_service.delete_invoice(invoice_id)
            
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'Failed to delete invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error deleting invoice: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supabase_invoice_summary(request):
    """Get invoice summary for dashboard"""
    try:
        supabase_service.connect()
        user_id = request.user.id
        
        summary_data = supabase_service.get_invoice_summary(user_id)
        logger.info(f"Summary data from service: {summary_data}")
        
        # If summary_data is None or not the expected format, return default values
        if not summary_data or not isinstance(summary_data, dict):
            summary_data = {
                'total_invoices': 0,
                'paid_invoices': 0,
                'pending_invoices': 0,
                'draft_invoices': 0,
                'overdue_invoices': 0,
                'total_amount': 0,
                'paid_amount': 0,
                'pending_amount': 0,
                'draft_amount': 0,
                'overdue_amount': 0,
                'total_pending_amount': 0,
                'total_paid_amount': 0,
                'total_overdue_amount': 0
            }
        
        serializer = InvoiceSummarySerializer(summary_data)
        
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting invoice summary: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supabase_recent_invoices(request):
    """Get recent invoices for dashboard"""
    try:
        supabase_service.connect()
        user_id = request.user.id
        
        recent_invoices_data = supabase_service.get_user_invoices(user_id, limit=5)
        
        # Convert to SupabaseInvoice objects
        recent_invoices = []
        for data in recent_invoices_data:
            invoice = SupabaseInvoice.from_dict(data)
            # Get items for this invoice
            items_data = supabase_service.get_invoice_items(invoice.id)
            invoice.items = [SupabaseInvoiceItem.from_dict(item) for item in items_data]
            recent_invoices.append(invoice)
        
        serializer = SupabaseInvoiceSerializer(recent_invoices, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error getting recent invoices: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_invoice_as_paid(request, invoice_id):
    """Mark an invoice as paid"""
    try:
        supabase_service.connect()
        
        # Update invoice status
        success = supabase_service.update_invoice(invoice_id, {'status': 'paid'})
        
        if success:
            return Response({'message': 'Invoice marked as paid'})
        else:
            return Response({'error': 'Failed to update invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error marking invoice as paid: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_invoice_pdf(request, invoice_id):
    """Download invoice as PDF using the professional A4 template"""
    try:
        from django.template.loader import render_to_string
        from django.conf import settings
        
        supabase_service.connect()
        
        # Get invoice data
        invoice_data = supabase_service.get_invoice(invoice_id)
        if not invoice_data:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get items
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
        
        # Render the professional template
        html_content = render_to_string('invoice_template.html', {
            'invoice': invoice,
            'business_name': business_info['business_name'],
            'business_email': business_info['business_email'],
            'business_phone': business_info['business_phone'],
            'business_address': business_info['business_address'],
            'business_logo': business_info['business_logo'],
            'payment_terms': business_info['payment_terms'],
        })
        
        # Generate PDF using reportlab (pure Python, works on all platforms)
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
            
            header_style = ParagraphStyle(
                'Header',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=10,
                textColor=colors.HexColor('#2c3e50')
            )
            
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # Title
            elements.append(Paragraph("INVOICE", title_style))
            elements.append(Spacer(1, 20))
            
            # Header section with business and client info
            header_data = [
                [
                    # Business info (left)
                    Paragraph(f"<b>{business_info['business_name']}</b><br/>"
                             f"{business_info['business_email']}<br/>"
                             f"{business_info['business_phone']}<br/>"
                             f"{business_info['business_address']}", normal_style),
                    # Client info (right)
                    Paragraph(f"<b>Bill To:</b><br/>"
                             f"<b>{invoice.client_name or 'N/A'}</b><br/>"
                             f"{invoice.client_email or ''}<br/>"
                             f"{invoice.client_phone or ''}<br/>"
                             f"{invoice.client_address or ''}", normal_style)
                ]
            ]
            
            header_table = Table(header_data, colWidths=[doc.width/2.0]*2)
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 20))
            
            # Invoice details
            elements.append(Paragraph("Invoice Details", header_style))
            invoice_details = [
                ['Invoice Number:', invoice.invoice_number or 'N/A'],
                ['Issue Date:', invoice.issue_date or 'N/A'],
                ['Due Date:', invoice.due_date or 'N/A'],
                ['Status:', (invoice.status or 'draft').upper()],
                ['Payment Terms:', business_info['payment_terms']]
            ]
            
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
            
            # Items table
            elements.append(Paragraph("Items & Services", header_style))
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
                elements.append(Paragraph("No items added", normal_style))
            
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
            
            # Notes
            if hasattr(invoice, 'notes') and invoice.notes:
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Notes:", header_style))
                elements.append(Paragraph(invoice.notes, normal_style))
            
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
            
            # Build PDF
            doc.build(elements)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            
            # Create response
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
            
            return response
            
        except Exception as e:
            # Fallback: return HTML if reportlab fails
            logger.warning(f"PDF generation failed: {str(e)}, returning HTML instead")
            response = HttpResponse(html_content, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.html"'
            return response
            
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_payment_link(request, invoice_id):
    """Generate payment link for invoice"""
    try:
        supabase_service.connect()
        
        # Get invoice
        invoice_data = supabase_service.get_invoice(invoice_id)
        if not invoice_data:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # For now, return a placeholder payment link
        # You can integrate with actual payment gateways here
        payment_link = f"https://payment.example.com/pay/{invoice_id}"
        
        # Update invoice with payment link
        update_data = {
            'payment_link': payment_link,
            'payment_gateway': 'example',
            'payment_id': f"pay_{invoice_id}"
        }
        success = supabase_service.update_invoice(invoice_id, update_data)
        
        if success:
            return Response({
                'payment_link': payment_link,
                'gateway': 'example',
                'payment_id': f"pay_{invoice_id}"
            })
        else:
            return Response({'error': 'Failed to update invoice'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error generating payment link: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
