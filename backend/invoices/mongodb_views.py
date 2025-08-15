"""
MongoDB-based views for invoice management
Uses MongoDB service layer for data operations
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
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
from decimal import Decimal

from lib.mongodb import mongodb_service
from .serializers import (
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceSummarySerializer,
    RazorpayPaymentLinkSerializer, SendReminderSerializer
)

# Configure Razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class MongoDBInvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # This is a dummy queryset for DRF compatibility
        # Actual data comes from MongoDB
        return []
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def list(self, request, *args, **kwargs):
        """Get invoices from MongoDB"""
        try:
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            skip = (page - 1) * page_size
            
            # Get invoices from MongoDB
            invoices = mongodb_service.get_user_invoices(
                user_id=request.user.id,
                limit=page_size,
                skip=skip
            )
            
            # Convert to serializer format
            serialized_invoices = []
            for invoice in invoices:
                # Convert MongoDB document to serializer format
                invoice_data = {
                    'id': invoice.get('id'),
                    'invoice_number': invoice.get('invoice_number'),
                    'client_name': invoice.get('client_name'),
                    'client_email': invoice.get('client_email'),
                    'client_phone': invoice.get('client_phone'),
                    'client_address': invoice.get('client_address'),
                    'issue_date': invoice.get('issue_date'),
                    'due_date': invoice.get('due_date'),
                    'status': invoice.get('status'),
                    'subtotal': str(invoice.get('subtotal', 0)),
                    'tax_rate': str(invoice.get('tax_rate', 0)),
                    'tax_amount': str(invoice.get('tax_amount', 0)),
                    'total_amount': str(invoice.get('total_amount', 0)),
                    'notes': invoice.get('notes', ''),
                    'terms_conditions': invoice.get('terms_conditions', ''),
                    'razorpay_payment_link': invoice.get('razorpay_payment_link', ''),
                    'razorpay_order_id': invoice.get('razorpay_order_id', ''),
                    'created_at': invoice.get('created_at'),
                    'updated_at': invoice.get('updated_at'),
                }
                serialized_invoices.append(invoice_data)
            
            return Response(serialized_invoices)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch invoices: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """Create invoice in MongoDB"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Prepare invoice data for MongoDB
            invoice_data = serializer.validated_data.copy()
            invoice_data['user_id'] = request.user.id
            
            # Generate invoice number if not provided
            if not invoice_data.get('invoice_number'):
                last_invoice = mongodb_service.get_user_invoices(request.user.id, limit=1)
                if last_invoice:
                    try:
                        last_number = int(last_invoice[0]['invoice_number'].split('-')[-1])
                        new_number = last_number + 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                invoice_data['invoice_number'] = f"INV-{request.user.id:04d}-{new_number:04d}"
            
            # Convert Decimal fields to float for MongoDB
            for field in ['subtotal', 'tax_rate', 'tax_amount', 'total_amount']:
                if field in invoice_data and isinstance(invoice_data[field], Decimal):
                    invoice_data[field] = float(invoice_data[field])
            
            # Create invoice in MongoDB
            invoice_id = mongodb_service.create_invoice(invoice_data)
            
            # Add items if provided
            items_data = request.data.get('items', [])
            for item in items_data:
                item['invoice_id'] = invoice_id
                # Convert Decimal fields
                for field in ['quantity', 'unit_price', 'total']:
                    if field in item and isinstance(item[field], Decimal):
                        item[field] = float(item[field])
                mongodb_service.create_invoice_item(item)
            
            return Response(
                {'message': 'Invoice created successfully', 'invoice_id': invoice_id},
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MongoDBInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Dummy queryset for DRF compatibility
        return []
    
    def retrieve(self, request, *args, **kwargs):
        """Get single invoice from MongoDB"""
        try:
            invoice_id = kwargs.get('pk')
            invoice = mongodb_service.get_invoice(invoice_id)
            
            if not invoice:
                return Response(
                    {'error': 'Invoice not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if invoice belongs to user
            if invoice.get('user_id') != request.user.id:
                return Response(
                    {'error': 'Access denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get invoice items
            items = mongodb_service.get_invoice_items(invoice_id)
            invoice['items'] = items
            
            # Convert to serializer format
            invoice_data = {
                'id': invoice.get('id'),
                'invoice_number': invoice.get('invoice_number'),
                'client_name': invoice.get('client_name'),
                'client_email': invoice.get('client_email'),
                'client_phone': invoice.get('client_phone'),
                'client_address': invoice.get('client_address'),
                'issue_date': invoice.get('issue_date'),
                'due_date': invoice.get('due_date'),
                'status': invoice.get('status'),
                'subtotal': str(invoice.get('subtotal', 0)),
                'tax_rate': str(invoice.get('tax_rate', 0)),
                'tax_amount': str(invoice.get('tax_amount', 0)),
                'total_amount': str(invoice.get('total_amount', 0)),
                'notes': invoice.get('notes', ''),
                'terms_conditions': invoice.get('terms_conditions', ''),
                'razorpay_payment_link': invoice.get('razorpay_payment_link', ''),
                'razorpay_order_id': invoice.get('razorpay_order_id', ''),
                'created_at': invoice.get('created_at'),
                'updated_at': invoice.get('updated_at'),
                'items': items,
            }
            
            return Response(invoice_data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Update invoice in MongoDB"""
        try:
            invoice_id = kwargs.get('pk')
            invoice = mongodb_service.get_invoice(invoice_id)
            
            if not invoice:
                return Response(
                    {'error': 'Invoice not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if invoice belongs to user
            if invoice.get('user_id') != request.user.id:
                return Response(
                    {'error': 'Access denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Prepare update data
            update_data = serializer.validated_data.copy()
            
            # Convert Decimal fields to float for MongoDB
            for field in ['subtotal', 'tax_rate', 'tax_amount', 'total_amount']:
                if field in update_data and isinstance(update_data[field], Decimal):
                    update_data[field] = float(update_data[field])
            
            # Update invoice in MongoDB
            success = mongodb_service.update_invoice(invoice_id, update_data)
            
            if success:
                return Response({'message': 'Invoice updated successfully'})
            else:
                return Response(
                    {'error': 'Failed to update invoice'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to update invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete invoice from MongoDB"""
        try:
            invoice_id = kwargs.get('pk')
            invoice = mongodb_service.get_invoice(invoice_id)
            
            if not invoice:
                return Response(
                    {'error': 'Invoice not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if invoice belongs to user
            if invoice.get('user_id') != request.user.id:
                return Response(
                    {'error': 'Access denied'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete invoice from MongoDB
            success = mongodb_service.delete_invoice(invoice_id)
            
            if success:
                return Response({'message': 'Invoice deleted successfully'})
            else:
                return Response(
                    {'error': 'Failed to delete invoice'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to delete invoice: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MongoDBInvoiceSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get invoice summary from MongoDB"""
        try:
            # Get all invoices for the user
            invoices = mongodb_service.get_user_invoices(request.user.id, limit=1000)
            
            # Calculate summary
            total_invoices = len(invoices)
            pending_invoices = len([i for i in invoices if i.get('status') == 'pending'])
            paid_invoices = len([i for i in invoices if i.get('status') == 'paid'])
            overdue_invoices = len([i for i in invoices if i.get('status') == 'overdue'])
            
            total_pending_amount = sum(float(i.get('total_amount', 0)) for i in invoices if i.get('status') == 'pending')
            total_paid_amount = sum(float(i.get('total_amount', 0)) for i in invoices if i.get('status') == 'paid')
            total_overdue_amount = sum(float(i.get('total_amount', 0)) for i in invoices if i.get('status') == 'overdue')
            total_amount = sum(float(i.get('total_amount', 0)) for i in invoices)
            
            summary = {
                'total_invoices': total_invoices,
                'pending_invoices': pending_invoices,
                'paid_invoices': paid_invoices,
                'overdue_invoices': overdue_invoices,
                'total_pending_amount': total_pending_amount,
                'total_paid_amount': total_paid_amount,
                'total_overdue_amount': total_overdue_amount,
                'total_amount': total_amount,
            }
            
            serializer = InvoiceSummarySerializer(summary)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to fetch summary: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mongodb_recent_invoices(request):
    """Get recent invoices for dashboard from MongoDB"""
    try:
        invoices = mongodb_service.get_user_invoices(request.user.id, limit=5)
        
        # Convert to serializer format
        serialized_invoices = []
        for invoice in invoices:
            invoice_data = {
                'id': invoice.get('id'),
                'invoice_number': invoice.get('invoice_number'),
                'client_name': invoice.get('client_name'),
                'client_email': invoice.get('client_email'),
                'status': invoice.get('status'),
                'total_amount': str(invoice.get('total_amount', 0)),
                'due_date': invoice.get('due_date'),
                'created_at': invoice.get('created_at'),
            }
            serialized_invoices.append(invoice_data)
        
        return Response(serialized_invoices)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch recent invoices: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mongodb_search_invoices(request):
    """Search invoices in MongoDB"""
    try:
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        invoices = mongodb_service.search_invoices(request.user.id, query, limit=20)
        
        # Convert to serializer format
        serialized_invoices = []
        for invoice in invoices:
            invoice_data = {
                'id': invoice.get('id'),
                'invoice_number': invoice.get('invoice_number'),
                'client_name': invoice.get('client_name'),
                'client_email': invoice.get('client_email'),
                'status': invoice.get('status'),
                'total_amount': str(invoice.get('total_amount', 0)),
                'due_date': invoice.get('due_date'),
                'created_at': invoice.get('created_at'),
            }
            serialized_invoices.append(invoice_data)
        
        return Response(serialized_invoices)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to search invoices: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
