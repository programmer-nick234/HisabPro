"""
Advanced Payment Views for HisabPro
Complete payment operations center with bulk operations
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta
import logging

from .models import Invoice
from .payment_service import payment_service, webhook_handler
from .serializers import InvoiceSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_generate_payment_links(request):
    """
    Generate payment links for multiple invoices at once
    """
    try:
        invoice_ids = request.data.get('invoice_ids', [])
        send_emails = request.data.get('send_emails', True)
        
        if not invoice_ids:
            return Response({'error': 'No invoice IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get invoices
        invoices = Invoice.objects.filter(
            id__in=invoice_ids, 
            user=request.user,
            status__in=['pending', 'overdue']
        )
        
        if not invoices.exists():
            return Response({'error': 'No valid invoices found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate bulk payment links
        result = payment_service.create_bulk_payment_links(invoices)
        
        # Send emails if requested
        if send_emails:
            email_results = []
            for invoice_result in result['results']:
                if invoice_result['success']:
                    invoice = invoices.get(id=invoice_result['invoice_id'])
                    if invoice.client_email:
                        email_sent = payment_service.send_payment_link_email(invoice, invoice_result)
                        email_results.append({
                            'invoice_id': invoice_result['invoice_id'],
                            'email_sent': email_sent
                        })
            result['email_results'] = email_results
        
        return Response(result)
    
    except Exception as e:
        logger.error(f"Error in bulk payment link generation: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_dashboard_analytics(request):
    """
    Get comprehensive payment analytics for dashboard
    """
    try:
        days = int(request.GET.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Basic invoice stats
        total_invoices = Invoice.objects.filter(user=request.user).count()
        paid_invoices = Invoice.objects.filter(user=request.user, status='paid').count()
        pending_invoices = Invoice.objects.filter(user=request.user, status='pending').count()
        overdue_invoices = Invoice.objects.filter(user=request.user, status='overdue').count()
        
        # Revenue stats
        total_revenue = Invoice.objects.filter(
            user=request.user, 
            status='paid'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        pending_revenue = Invoice.objects.filter(
            user=request.user, 
            status__in=['pending', 'overdue']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        # Recent activity
        recent_payments = Invoice.objects.filter(
            user=request.user,
            status='paid',
            updated_at__gte=start_date
        ).order_by('-updated_at')[:10]
        
        # Payment method analytics (mock data for now)
        payment_methods = {
            'upi': 45,
            'card': 30,
            'netbanking': 20,
            'wallet': 5
        }
        
        analytics_data = {
            'summary': {
                'total_invoices': total_invoices,
                'paid_invoices': paid_invoices,
                'pending_invoices': pending_invoices,
                'overdue_invoices': overdue_invoices,
                'total_revenue': float(total_revenue),
                'pending_revenue': float(pending_revenue),
                'payment_success_rate': round((paid_invoices / total_invoices * 100) if total_invoices > 0 else 0, 2)
            },
            'payment_methods': payment_methods,
            'recent_payments': InvoiceSerializer(recent_payments, many=True).data,
            'trends': {
                'daily_revenue': [],  # Would be calculated from actual data
                'payment_method_trends': payment_methods
            }
        }
        
        return Response(analytics_data)
    
    except Exception as e:
        logger.error(f"Error getting payment analytics: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_link_status(request, invoice_id):
    """
    Get payment link status for an invoice
    """
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        if not hasattr(invoice, 'razorpay_payment_link_id') or not invoice.razorpay_payment_link_id:
            return Response({'error': 'No payment link found for this invoice'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get payment status from Razorpay
        result = payment_service.get_payment_status(invoice.razorpay_payment_link_id)
        
        if result['success']:
            return Response({
                'invoice_id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'payment_link_status': result['status'],
                'amount_paid': result['amount_paid'],
                'payments': result['payments']
            })
        else:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error getting payment link status: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_payment_link(request, invoice_id):
    """
    Cancel payment link for an invoice
    """
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        if not hasattr(invoice, 'razorpay_payment_link_id') or not invoice.razorpay_payment_link_id:
            return Response({'error': 'No payment link found for this invoice'}, status=status.HTTP_404_NOT_FOUND)
        
        # Cancel payment link
        result = payment_service.cancel_payment_link(invoice.razorpay_payment_link_id)
        
        if result['success']:
            # Update invoice
            invoice.razorpay_payment_link = None
            invoice.razorpay_payment_link_id = None
            invoice.save()
            
            return Response({
                'message': 'Payment link cancelled successfully',
                'status': result['status']
            })
        else:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error cancelling payment link: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """
    Get comprehensive payment history
    """
    try:
        # Get query parameters
        status_filter = request.GET.get('status', '')
        days = int(request.GET.get('days', 30))
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Build query
        queryset = Invoice.objects.filter(user=request.user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if days > 0:
            start_date = datetime.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=start_date)
        
        # Order by creation date
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        invoices = queryset[start:end]
        total_count = queryset.count()
        
        # Serialize data
        serialized_invoices = []
        for invoice in invoices:
            invoice_data = InvoiceSerializer(invoice).data
            invoice_data['has_payment_link'] = bool(getattr(invoice, 'razorpay_payment_link', None))
            invoice_data['payment_link'] = getattr(invoice, 'razorpay_payment_link', None)
            serialized_invoices.append(invoice_data)
        
        return Response({
            'invoices': serialized_invoices,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_count,
                'pages': (total_count + per_page - 1) // per_page
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting payment history: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_payment_link(request, invoice_id):
    """
    Resend payment link email for an invoice
    """
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        if not invoice.client_email:
            return Response({'error': 'No email address found for this invoice'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not getattr(invoice, 'razorpay_payment_link', None):
            return Response({'error': 'No payment link found for this invoice'}, status=status.HTTP_404_NOT_FOUND)
        
        # Prepare payment link data for email
        payment_link_data = {
            'short_url': invoice.razorpay_payment_link,
            'expire_by': datetime.now() + timedelta(days=30),  # Default expiry
            'amount': invoice.total_amount
        }
        
        # Send email
        email_sent = payment_service.send_payment_link_email(invoice, payment_link_data)
        
        if email_sent:
            return Response({'message': 'Payment link email sent successfully'})
        else:
            return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error resending payment link: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_methods_stats(request):
    """
    Get payment methods statistics
    """
    try:
        # This would typically come from actual payment data
        # For now, returning mock data based on industry averages
        stats = {
            'methods': {
                'upi': {
                    'name': 'UPI (Google Pay, PhonePe, etc.)',
                    'percentage': 45,
                    'count': 0,  # Would be calculated from actual data
                    'success_rate': 95
                },
                'card': {
                    'name': 'Credit/Debit Cards',
                    'percentage': 30,
                    'count': 0,
                    'success_rate': 92
                },
                'netbanking': {
                    'name': 'Net Banking',
                    'percentage': 20,
                    'count': 0,
                    'success_rate': 88
                },
                'wallet': {
                    'name': 'Digital Wallets',
                    'percentage': 5,
                    'count': 0,
                    'success_rate': 90
                }
            },
            'trends': {
                'upi_growing': True,
                'card_stable': True,
                'netbanking_declining': True,
                'wallet_stable': True
            }
        }
        
        return Response(stats)
    
    except Exception as e:
        logger.error(f"Error getting payment methods stats: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
