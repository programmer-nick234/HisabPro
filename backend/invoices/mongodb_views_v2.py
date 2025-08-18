"""
MongoDB Views for Invoice System - Real-time functionality
"""

import logging
import json
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import razorpay
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from datetime import datetime
import json

from .mongodb_models import (
    MongoDBInvoice, MongoDBInvoiceItem
)
from .mongodb_serializers import (
    MongoDBInvoiceSerializer, MongoDBInvoiceCreateSerializer,
    MongoDBInvoiceSummarySerializer,
    MongoDBInvoiceItemSerializer
)
from lib.mongodb import mongodb_service

# Import optimized payment system
from .optimized_payment import payment_system

logger = logging.getLogger(__name__)

def ensure_mongodb_connection():
    """Ensure MongoDB connection is established"""
    try:
        if not mongodb_service._connected:
            mongodb_service.connect()
        return mongodb_service._connected
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        return False

def get_cache_key(prefix, user_id, **kwargs):
    """Generate cache key with user-specific prefix"""
    key_parts = [prefix, str(user_id)]
    for k, v in sorted(kwargs.items()):
        key_parts.extend([k, str(v)])
    return f"hisabpro:{':'.join(key_parts)}"

def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a user"""
    try:
        # Get all cache keys for this user
        cache_keys = cache.keys(f"hisabpro:*:{user_id}:*")
        for key in cache_keys:
            cache.delete(key)
    except:
        # If cache.keys is not available, just clear all cache
        cache.clear()

class MongoDBInvoiceListCreateView(generics.ListCreateAPIView):
    """List and create invoices using MongoDB with caching"""
    
    serializer_class = MongoDBInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get invoices for the current user with caching"""
        try:
            # Ensure MongoDB connection
            if not ensure_mongodb_connection():
                logger.error("MongoDB connection failed")
                return []
            
            user_id = self.request.user.id
            page = int(self.request.query_params.get('page', 1))
            page_size = int(self.request.query_params.get('page_size', 20))
            status_filter = self.request.query_params.get('status', '')
            search_term = self.request.query_params.get('search', '')
            
            # Generate cache key
            cache_key = get_cache_key('invoices', user_id, page=page, page_size=page_size, 
                                    status=status_filter, search=search_term)
            
            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_result
            
            # Get from database
            invoices = MongoDBInvoice.get_by_user(
                user_id, 
                page=page, 
                page_size=page_size,
                status=status_filter,
                search=search_term
            )
            
            # Cache for 5 minutes
            cache.set(cache_key, invoices, 300)
            logger.info(f"Cache set for key: {cache_key}")
            
            return invoices
            
        except Exception as e:
            logger.error(f"Error getting invoices: {str(e)}")
            return []
    
    def create(self, request, *args, **kwargs):
        """Create new invoice"""
        try:
            # Ensure MongoDB connection
            if not ensure_mongodb_connection():
                logger.error("MongoDB connection failed")
                return Response(
                    {'error': 'Database connection failed'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            serializer = self.get_serializer(data=request.data, context={
                'user_id': request.user.id,
                'items': request.data.get('items', [])
            })
            serializer.is_valid(raise_exception=True)
            
            # Create invoice using serializer
            invoice = serializer.save()
            
            # Invalidate cache for this user
            invalidate_user_cache(request.user.id)
            
            # Return response
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            return Response(
                {'error': f'Failed to create invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MongoDBInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete invoice using MongoDB with caching"""
    
    serializer_class = MongoDBInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get invoice by ID with caching"""
        try:
            # Ensure MongoDB connection
            if not ensure_mongodb_connection():
                logger.error("MongoDB connection failed")
                return None
            
            invoice_id = self.kwargs.get('pk')
            user_id = self.request.user.id
            
            # Generate cache key
            cache_key = get_cache_key('invoice_detail', user_id, invoice_id=invoice_id)
            
            # Try to get from cache first
            cached_invoice = cache.get(cache_key)
            if cached_invoice:
                logger.info(f"Cache hit for invoice detail: {cache_key}")
                return cached_invoice
            
            # Get from database
            invoice = MongoDBInvoice.get_by_id(invoice_id)
            
            if not invoice:
                return None
            
            # Check if user owns this invoice
            if invoice.user_id != user_id:
                return None
            
            # Cache for 10 minutes
            cache.set(cache_key, invoice, 600)
            logger.info(f"Cache set for invoice detail: {cache_key}")
            
            return invoice
            
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}")
            return None
    
    def update(self, request, *args, **kwargs):
        """Update invoice"""
        try:
            invoice = self.get_object()
            if not invoice:
                return Response(
                    {'error': 'Invoice not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(invoice, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Update invoice
            invoice_data = serializer.validated_data
            for field, value in invoice_data.items():
                if hasattr(invoice, field):
                    setattr(invoice, field, value)
            
            # Update items if provided
            if 'items' in request.data:
                # Delete existing items
                MongoDBInvoiceItem.delete_by_invoice_id(str(invoice._id))
                
                # Add new items
                items_data = request.data['items']
                for item_data in items_data:
                    item = MongoDBInvoiceItem()
                    item.invoice_id = str(invoice._id)
                    item.description = item_data.get('description')
                    item.quantity = item_data.get('quantity')
                    item.unit_price = float(item_data.get('unit_price'))
                    item.total = float(item.quantity * item.unit_price)
                    item.save()
                
                # Recalculate totals
                invoice.calculate_totals()
            
            invoice.save()
            
            # Invalidate cache
            invalidate_user_cache(request.user.id)
            
            response_serializer = MongoDBInvoiceSerializer(invoice)
            return Response(response_serializer.data)
            
        except Exception as e:
            logger.error(f"Error updating invoice: {str(e)}")
            return Response(
                {'error': f'Failed to update invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete invoice"""
        try:
            invoice = self.get_object()
            if not invoice:
                return Response(
                    {'error': 'Invoice not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Delete invoice
            success = MongoDBInvoice.delete_by_id(str(invoice._id))
            
            if success:
                # Invalidate cache
                invalidate_user_cache(request.user.id)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Failed to delete invoice'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error deleting invoice: {str(e)}")
            return Response(
                {'error': f'Failed to delete invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MongoDBInvoiceSummaryView(APIView):
    """Get invoice summary with caching"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get invoice summary"""
        try:
            # Ensure MongoDB connection
            if not ensure_mongodb_connection():
                logger.error("MongoDB connection failed")
                return Response(
                    {'error': 'Database connection failed'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            user_id = request.user.id
            
            # Temporarily disable caching to debug
            # cache_key = get_cache_key('invoice_summary', user_id)
            # cached_summary = cache.get(cache_key)
            # if cached_summary:
            #     logger.info(f"Cache hit for invoice summary: {cache_key}")
            #     return Response(cached_summary)
            
            # Get from database
            logger.info(f"Getting summary for user_id: {user_id}")
            summary = MongoDBInvoice.get_summary(user_id)
            logger.info(f"Summary data: {summary}")
            
            # If summary is empty or has wrong structure, create a default one
            if not summary or not isinstance(summary, dict) or 'total_invoices' not in summary:
                logger.warning("Summary data is invalid, creating default summary")
                summary = {
                    'total_invoices': 0,
                    'total_amount': 0,
                    'pending_invoices': 0,
                    'paid_invoices': 0,
                    'overdue_invoices': 0,
                    'total_pending_amount': 0,
                    'total_paid_amount': 0,
                    'total_overdue_amount': 0
                }
            
            # Ensure summary is a dictionary with the correct keys
            if not isinstance(summary, dict):
                summary = {
                    'total_invoices': 0,
                    'total_amount': 0,
                    'pending_invoices': 0,
                    'paid_invoices': 0,
                    'overdue_invoices': 0,
                    'total_pending_amount': 0,
                    'total_paid_amount': 0,
                    'total_overdue_amount': 0
                }
            
            # Temporarily disable caching
            # cache.set(cache_key, summary, 300)
            # logger.info(f"Cache set for invoice summary: {cache_key}")
            
            return Response(summary)
            
        except Exception as e:
            logger.error(f"Error getting invoice summary: {str(e)}")
            return Response(
                {'error': f'Failed to get summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mongodb_recent_invoices(request):
    """Get recent invoices for dashboard with caching"""
    try:
        # Ensure MongoDB connection
        if not ensure_mongodb_connection():
            logger.error("MongoDB connection failed")
            return Response(
                {'error': 'Database connection failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        user_id = request.user.id
        logger.info(f"Getting recent invoices for user_id: {user_id}")
        
        # Temporarily disable caching to debug
        # cache_key = get_cache_key('recent_invoices', user_id)
        # cached_invoices = cache.get(cache_key)
        # if cached_invoices:
        #     logger.info(f"Cache hit for recent invoices: {cache_key}")
        #     return Response(cached_invoices)
        
        # Get from database
        recent_invoices = MongoDBInvoice.get_by_user(user_id, limit=5)
        logger.info(f"Found {len(recent_invoices)} recent invoices")
        
        # Convert to list of dictionaries for serialization
        invoice_data = []
        for invoice in recent_invoices:
            invoice_dict = {
                'id': str(invoice._id),
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client_name,
                'client_email': invoice.client_email,
                'total_amount': invoice.total_amount,
                'status': invoice.status,
                'due_date': invoice.due_date,
                'created_at': invoice.created_at,
            }
            invoice_data.append(invoice_dict)
        
        data = invoice_data
        
        # Temporarily disable caching
        # cache.set(cache_key, data, 120)
        # logger.info(f"Cache set for recent invoices: {cache_key}")
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Error getting recent invoices: {str(e)}")
        return Response(
            {'error': f'Failed to get recent invoices: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_invoice_as_paid(request, invoice_id):
    """Mark invoice as paid"""
    try:
        # Ensure MongoDB connection
        if not ensure_mongodb_connection():
            logger.error("MongoDB connection failed")
            return Response(
                {'error': 'Database connection failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        invoice = MongoDBInvoice.get_by_id(invoice_id)
        if not invoice:
            return Response(
                {'error': 'Invoice not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user owns this invoice
        if invoice.user_id != request.user.id:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update status
        invoice.status = 'paid'
        invoice.save()
        
        # Invalidate cache
        invalidate_user_cache(request.user.id)
        
        serializer = MongoDBInvoiceSerializer(invoice)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error marking invoice as paid: {str(e)}")
        return Response(
            {'error': f'Failed to mark invoice as paid: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_pdf(request, invoice_id):
    """Download invoice as PDF with beautiful design"""
    try:
        # Ensure MongoDB connection
        if not ensure_mongodb_connection():
            logger.error("MongoDB connection failed")
            return Response(
                {'error': 'Database connection failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get invoice
        invoice = MongoDBInvoice.get_by_id(invoice_id)
        if not invoice:
            return Response(
                {'error': 'Invoice not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user owns this invoice
        if invoice.user_id != request.user.id:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get invoice items
        items = MongoDBInvoiceItem.get_by_invoice(str(invoice._id))
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b7280'),
            fontName='Helvetica'
        )
        
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.HexColor('#4b5563'),
            fontName='Helvetica'
        )
        
        # Header with logo and company info
        header_data = [
            [Paragraph(f"<b>INVOICE</b>", title_style), ""],
            [Paragraph(f"#{invoice.invoice_number}", subtitle_style), ""],
            ["", ""],
            [Paragraph(f"<b>Issue Date:</b> {invoice.issue_date.strftime('%B %d, %Y') if hasattr(invoice.issue_date, 'strftime') else str(invoice.issue_date)}", normal_style), 
             Paragraph(f"<b>Due Date:</b> {invoice.due_date.strftime('%B %d, %Y') if hasattr(invoice.due_date, 'strftime') else str(invoice.due_date)}", normal_style)],
            [Paragraph(f"<b>Status:</b> {invoice.status.upper()}", normal_style), ""]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f9fafb')),
            ('ROUNDEDCORNERS', [6]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 30))
        
        # Company and Client Information
        info_data = [
            [Paragraph(f"<b>FROM:</b>", header_style), Paragraph(f"<b>TO:</b>", header_style)],
            [Paragraph("Your Company Name", normal_style), Paragraph(invoice.client_name, normal_style)],
            [Paragraph("123 Business Street", normal_style), 
             Paragraph(invoice.client_address if invoice.client_address else "N/A", normal_style)],
            [Paragraph("City, State 12345", normal_style), 
             Paragraph(f"Phone: {invoice.client_phone}" if invoice.client_phone else "Phone: N/A", normal_style)],
            [Paragraph("Phone: (555) 123-4567", normal_style), 
             Paragraph(f"Email: {invoice.client_email}" if invoice.client_email else "Email: N/A", normal_style)],
            [Paragraph("Email: info@company.com", normal_style), ""],
            [Paragraph("GST: 22AAAAA0000A1Z5", normal_style), ""]
        ]
        
        info_table = Table(info_data, colWidths=[3*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#3b82f6')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ROUNDEDCORNERS', [6]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 30))
        
        # Items Table
        items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
        
        for item in items:
            items_data.append([
                Paragraph(item.description, normal_style),
                str(item.quantity),
                f"₹{item.unit_price:,.2f}",
                f"₹{item.total:,.2f}"
            ])
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ROUNDEDCORNERS', [6]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 20))
        
        # Totals Section
        totals_data = [
            ['Subtotal:', f"₹{invoice.subtotal:,.2f}"],
            [f'Tax ({invoice.tax_rate}%):', f"₹{invoice.tax_amount:,.2f}"],
            ['', ''],
            ['Total Amount:', f"₹{invoice.total_amount:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (1, -1), 14),
            ('TEXTCOLOR', (0, -1), (1, -1), colors.HexColor('#1f2937')),
            ('LINEABOVE', (0, -1), (1, -1), 2, colors.HexColor('#3b82f6')),
            ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#eff6ff')),
            ('ROUNDEDCORNERS', [6]),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(totals_table)
        elements.append(Spacer(1, 30))
        
        # Notes and Terms
        if invoice.notes:
            elements.append(Paragraph(f"<b>Notes:</b>", header_style))
            elements.append(Paragraph(invoice.notes, normal_style))
            elements.append(Spacer(1, 20))
        
        if invoice.terms_conditions:
            elements.append(Paragraph(f"<b>Terms & Conditions:</b>", header_style))
            elements.append(Paragraph(invoice.terms_conditions, normal_style))
            elements.append(Spacer(1, 20))
        
        # Footer
        footer_data = [
            [Paragraph("Thank you for your business!", subtitle_style)],
            [Paragraph("Please make payment within the due date to avoid any late fees.", normal_style)],
            [Paragraph("For any queries, please contact us at info@company.com", normal_style)]
        ]
        
        footer_table = Table(footer_data, colWidths=[6*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
            ('ROUNDEDCORNERS', [6]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ]))
        elements.append(footer_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Create response
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return Response(
            {'error': f'Failed to generate PDF: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_payment_link(request, invoice_id):
    """Generate optimized payment link for MongoDB invoice"""
    try:
        # Ensure MongoDB connection
        if not ensure_mongodb_connection():
            logger.error("MongoDB connection failed")
            return Response(
                {'error': 'Database connection failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get invoice
        invoice = MongoDBInvoice.get_by_id(invoice_id)
        if not invoice:
            return Response(
                {'error': 'Invoice not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if user owns this invoice
        if invoice.user_id != request.user.id:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if payment link already exists
        if hasattr(invoice, 'payment_link') and invoice.payment_link:
            return Response({
                'payment_link': invoice.payment_link,
                'gateway': getattr(invoice, 'payment_gateway', 'razorpay'),
                'message': 'Payment link already exists'
            })
        
        try:
            # Create payment link using optimized system
            result = payment_system.create_payment_link(
                invoice_id=str(invoice._id),
                amount=invoice.total_amount,
                currency='INR',
                description=f'Payment for Invoice #{invoice.invoice_number}',
                customer_email=invoice.client_email
            )
            
            if result['success']:
                # Update invoice with payment link
                invoice.payment_link = result['payment_url']
                invoice.payment_gateway = result['gateway']
                invoice.payment_id = result['payment_id']
                invoice.save()
                
                # Invalidate cache
                invalidate_user_cache(request.user.id)
                
                return Response({
                    'payment_link': result['payment_url'],
                    'gateway': result['gateway'],
                    'payment_id': result['payment_id']
                })
            else:
                return Response(
                    {'error': result['error']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            logger.error(f"Payment system error: {str(e)}")
            return Response(
                {'error': f'Failed to generate payment link: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        logger.error(f"Error generating payment link: {str(e)}")
        return Response(
            {'error': f'Failed to generate payment link: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])  # No authentication required for webhooks
def razorpay_webhook(request):
    """Handle Razorpay webhook for payment verification"""
    try:
        # Get webhook signature
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            return Response(
                {'error': 'Missing signature'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify webhook signature
        try:
            razorpay_client.utility.verify_webhook_signature(
                request.body.decode('utf-8'),
                signature,
                settings.RAZORPAY_WEBHOOK_SECRET
            )
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return Response(
                {'error': 'Invalid signature'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse webhook data
        webhook_data = json.loads(request.body.decode('utf-8'))
        event = webhook_data.get('event')
        
        if event == 'payment.captured':
            payment_data = webhook_data.get('payload', {}).get('payment', {})
            entity = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
            
            # Extract invoice information from payment notes or reference
            payment_id = entity.get('id')
            order_id = entity.get('order_id')
            amount = entity.get('amount') / 100  # Convert from paise to rupees
            
            logger.info(f"Payment captured: {payment_id}, Order: {order_id}, Amount: {amount}")
            
            # Find invoice by order ID
            if order_id:
                # Search for invoice with this order ID
                invoice = None
                try:
                    # This is a simplified search - you might need to implement a more robust search
                    all_invoices = list(mongodb_service.db.invoices.find({'razorpay_order_id': order_id}))
                    if all_invoices:
                        invoice_data = all_invoices[0]
                        invoice = MongoDBInvoice()
                        invoice._id = invoice_data['_id']
                        invoice.user_id = invoice_data['user_id']
                        invoice.invoice_number = invoice_data['invoice_number']
                        invoice.client_name = invoice_data['client_name']
                        invoice.client_email = invoice_data['client_email']
                        invoice.total_amount = invoice_data['total_amount']
                        invoice.status = invoice_data['status']
                        # Add other fields as needed
                except Exception as e:
                    logger.error(f"Error finding invoice for order {order_id}: {str(e)}")
                
                if invoice:
                    # Update invoice status to paid
                    invoice.status = 'paid'
                    invoice.save()
                    
                    # Create payment record
                    payment_record = {
                        'invoice_id': str(invoice._id),
                        'payment_id': payment_id,
                        'order_id': order_id,
                        'amount': amount,
                        'currency': 'INR',
                        'status': 'completed',
                        'payment_method': 'razorpay',
                        'created_at': datetime.now(),
                        'user_id': invoice.user_id
                    }
                    
                    mongodb_service.db.payments.insert_one(payment_record)
                    
                    # Send confirmation email
                    try:
                        send_mail(
                            subject=f'Payment Received - Invoice #{invoice.invoice_number}',
                            message=f'''
                            Dear {invoice.client_name},
                            
                            Thank you for your payment of ₹{amount:,.2f} for Invoice #{invoice.invoice_number}.
                            
                            Payment Details:
                            - Payment ID: {payment_id}
                            - Amount: ₹{amount:,.2f}
                            - Date: {datetime.now().strftime('%B %d, %Y')}
                            
                            Your invoice has been marked as paid.
                            
                            Best regards,
                            Your Company Name
                            ''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[invoice.client_email],
                            fail_silently=True
                        )
                    except Exception as e:
                        logger.error(f"Error sending payment confirmation email: {str(e)}")
                    
                    logger.info(f"Invoice {invoice.invoice_number} marked as paid")
                else:
                    logger.warning(f"No invoice found for order ID: {order_id}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return Response(
            {'error': f'Webhook processing failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
