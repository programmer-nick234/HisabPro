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
    """Download invoice as PDF"""
    try:
        supabase_service.connect()
        
        # Get invoice data
        invoice_data = supabase_service.get_invoice(invoice_id)
        if not invoice_data:
            return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get items
        items_data = supabase_service.get_invoice_items(invoice_id)
        
        # Create PDF (simplified version - you can enhance this)
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        elements = []
        
        # Title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 20))
        
        # Invoice details
        invoice_info = [
            ['Invoice Number:', invoice_data.get('invoice_number', '')],
            ['Issue Date:', invoice_data.get('issue_date', '')],
            ['Due Date:', invoice_data.get('due_date', '')],
            ['Status:', invoice_data.get('status', '').upper()]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[2*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))
        
        # Client information
        elements.append(Paragraph("Bill To:", styles['Heading2']))
        client_info = [
            invoice_data.get('client_name', ''),
            invoice_data.get('client_email', ''),
            invoice_data.get('client_phone', ''),
            invoice_data.get('client_address', '')
        ]
        for info in client_info:
            if info:
                elements.append(Paragraph(info, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Items table
        if items_data:
            elements.append(Paragraph("Items:", styles['Heading2']))
            items_table_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
            for item in items_data:
                items_table_data.append([
                    item.get('description', ''),
                    str(item.get('quantity', 0)),
                    f"₹{item.get('unit_price', 0):.2f}",
                    f"₹{item.get('total', 0):.2f}"
                ])
            
            items_table = Table(items_table_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 20))
        
        # Totals
        totals_data = [
            ['Subtotal:', f"₹{invoice_data.get('subtotal', 0):.2f}"],
            ['Tax ({:.1f}%):'.format(invoice_data.get('tax_rate', 0)), f"₹{invoice_data.get('tax_amount', 0):.2f}"],
            ['Total:', f"₹{invoice_data.get('total_amount', 0):.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(totals_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Create response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_data.get("invoice_number", "unknown")}.pdf"'
        
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
