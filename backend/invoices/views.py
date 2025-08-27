from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
import razorpay
import io
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from datetime import datetime
import json

# Configure logger
logger = logging.getLogger(__name__)

from .models import Invoice, InvoiceItem, Payment
from .serializers import (
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceSummarySerializer,
    RazorpayPaymentLinkSerializer, SendReminderSerializer
)

# Configure Razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


class InvoiceListCreateView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        try:
            logger.info(f"Creating invoice for user {self.request.user.id}")
            logger.debug(f"Invoice data: {serializer.validated_data}")
            
            invoice = serializer.save(user=self.request.user)
            
            logger.info(f"Successfully created invoice {invoice.id} with number {invoice.invoice_number}")
        except Exception as e:
            logger.error(f"Failed to create invoice for user {self.request.user.id}: {str(e)}")
            raise
    
    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Invoice creation request from user {request.user.id}")
            logger.debug(f"Request data: {request.data}")
            
            response = super().create(request, *args, **kwargs)
            
            logger.info(f"Invoice creation successful for user {request.user.id}")
            return response
        except ValidationError as e:
            logger.warning(f"Validation error during invoice creation for user {request.user.id}: {str(e)}")
            return Response(
                {'error': 'Validation failed', 'details': e.detail}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error during invoice creation for user {request.user.id}: {str(e)}")
            return Response(
                {'error': 'Internal server error. Please try again.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InvoiceCreateSerializer
        return InvoiceSerializer


class InvoiceSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user_invoices = Invoice.objects.filter(user=request.user)
        
        summary = {
            'total_invoices': user_invoices.count(),
            'pending_invoices': user_invoices.filter(status='pending').count(),
            'paid_invoices': user_invoices.filter(status='paid').count(),
            'overdue_invoices': user_invoices.filter(status='overdue').count(),
            'total_pending_amount': user_invoices.filter(status='pending').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            'total_paid_amount': user_invoices.filter(status='paid').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            'total_overdue_amount': user_invoices.filter(status='overdue').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            'total_amount': user_invoices.aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        serializer = InvoiceSummarySerializer(summary)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_razorpay_payment_link(request, invoice_id):
    """
    Enhanced payment link generation with all payment methods
    """
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    try:
        # Import payment service
        from .payment_service import payment_service
        
        # Get options from request
        send_email = request.data.get('send_email', True)
        custom_options = request.data.get('options', {})
        
        # Create payment link with all payment methods
        result = payment_service.create_payment_link(invoice, custom_options)
        
        if not result['success']:
            return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save payment link to invoice
        invoice.razorpay_payment_link = result['short_url']
        invoice.razorpay_payment_link_id = result['payment_link_id']
        invoice.save()
        
        # Send email if requested
        if send_email and invoice.client_email:
            email_sent = payment_service.send_payment_link_email(invoice, result)
            result['email_sent'] = email_sent
        
        # Return response
        response_data = {
            'payment_link': result['short_url'],
            'payment_link_id': result['payment_link_id'],
            'amount': result['amount'],
            'currency': result['currency'],
            'expire_by': result['expire_by'].isoformat(),
            'email_sent': result.get('email_sent', False)
        }
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f"Error generating payment link for invoice {invoice_id}: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_pdf(request, invoice_id):
    """Generate and download PDF invoice using optimized PDF service"""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        # Import PDF service
        from lib.pdf_service import pdf_service
        
        # Prepare context for template
        context = {
            'invoice': invoice,
            'items': invoice.items.all() if hasattr(invoice, 'items') else [],
        }
        
        # PDF generation options
        pdf_options = {
            'format': 'A4',
            'margin': {
                'top': '20mm',
                'right': '20mm',
                'bottom': '20mm',
                'left': '20mm'
            },
            'printBackground': True,
            'preferCSSPageSize': True,
        }
        
        # Generate PDF using the new service
        pdf_bytes = pdf_service.generate_pdf_from_template(
            template_name='invoice_pdf_template.html',
            context=context,
            options=pdf_options,
            method='auto'  # Will try Playwright first, then WeasyPrint, then ReportLab
        )
        
        # Create response
        filename = f"invoice_{invoice.invoice_number}.pdf"
        response = pdf_service.create_pdf_response(
            pdf_bytes=pdf_bytes,
            filename=filename,
            inline=False  # Force download
        )
        
        return response
        
    except Exception as e:
        logger.error(f"PDF generation failed for invoice {invoice_id}: {e}")
        return Response(
            {'error': 'Failed to generate PDF. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_reminder(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    serializer = SendReminderSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            from datetime import date, timedelta
            
            # Calculate days overdue
            today = date.today()
            if isinstance(invoice.due_date, str):
                due_date = timezone.datetime.strptime(invoice.due_date, '%Y-%m-%d').date()
            else:
                due_date = invoice.due_date
            
            days_overdue = max(0, (today - due_date).days)
            
            # Determine template and subject based on status
            if days_overdue > 0:
                template_name = 'email/urgent_reminder.html'
                subject = f"🚨 URGENT: Payment Overdue - Invoice #{invoice.invoice_number}"
                greeting = f"Dear {invoice.client_name},"
            elif (due_date - today).days <= 3:
                template_name = 'email/friendly_reminder.html'
                subject = f"💰 Friendly Reminder - Invoice #{invoice.invoice_number}"
                greeting = f"Hello {invoice.client_name}! 👋"
            else:
                template_name = 'email/professional_reminder.html'
                subject = f"📋 Payment Reminder - Invoice #{invoice.invoice_number}"
                greeting = f"Dear {invoice.client_name},"
            
            # Custom message or default
            custom_message = serializer.validated_data.get('message', '')
            if not custom_message:
                if days_overdue > 0:
                    custom_message = f'''<p>We hope this email finds you well.</p>
<p>This is an urgent reminder that your invoice <strong>#{invoice.invoice_number}</strong> for <strong>₹{invoice.total_amount:,.2f}</strong> is now <strong>{days_overdue} days overdue</strong>.</p>
<p>To avoid any service disruption, please process the payment immediately or contact us to discuss payment arrangements.</p>'''
                else:
                    custom_message = f'''<p>We hope this email finds you well!</p>
<p>This is a friendly reminder that your invoice <strong>#{invoice.invoice_number}</strong> for <strong>₹{invoice.total_amount:,.2f}</strong> is due on <strong>{due_date.strftime('%B %d, %Y')}</strong>.</p>
<p>If you've already processed this payment, please disregard this message. If you have any questions, we're here to help!</p>'''
            
            # Format dates
            def format_date(date_value):
                if isinstance(date_value, str):
                    try:
                        parsed_date = timezone.datetime.strptime(date_value, '%Y-%m-%d').date()
                        return parsed_date.strftime('%B %d, %Y')
                    except:
                        return date_value
                else:
                    return date_value.strftime('%B %d, %Y')
            
            # Prepare template context for beautiful HTML email
            context = {
                'email_title': subject,
                'greeting': greeting,
                'message_body': custom_message,
                'business_name': getattr(settings, 'BUSINESS_NAME', 'DailyDine'),
                'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@dailydine.com'),
                'business_phone': getattr(settings, 'BUSINESS_PHONE', '+91 98765 43210'),
                'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business St, Mumbai, MH 400001'),
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client_name,
                'client_email': invoice.client_email,
                'amount': f"₹{invoice.total_amount:,.2f}",
                'due_date': format_date(invoice.due_date),
                'issue_date': format_date(invoice.issue_date),
                'days_overdue': days_overdue,
                'due_status_class': 'status-overdue' if days_overdue > 0 else 'status-due-soon',
                'payment_status': f'{days_overdue} days overdue' if days_overdue > 0 else 'Due soon',
                'status_class': 'status-overdue' if days_overdue > 0 else 'status-due-soon',
                'payment_url': f"https://dailydine.com/pay/{invoice.id}",
                'invoice_pdf_url': f"https://dailydine.com/api/invoices/{invoice.id}/pdf/",
                'whatsapp_url': f"https://wa.me/{getattr(settings, 'BUSINESS_PHONE', '919876543210').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}",
                'support_url': f"mailto:{getattr(settings, 'BUSINESS_EMAIL', 'support@dailydine.com')}",
                'current_year': timezone.now().year,
                'current_date': today.strftime('%B %d, %Y'),
                'legal_deadline': (today + timedelta(days=30)).strftime('%B %d, %Y'),
                'total_with_fees': f"₹{float(invoice.total_amount) * 1.15:,.2f}",
                'additional_content': '',
            }
            
            # Plain text fallback
            plain_text = f"""
            Dear {invoice.client_name},
            
            This is a reminder about Invoice #{invoice.invoice_number} for ₹{invoice.total_amount:,.2f}.
            
            {"This invoice is now overdue." if days_overdue > 0 else "This invoice is due soon."}
            
            Please process the payment at your earliest convenience.
            
            Thank you for your business.
            
            Best regards,
            {getattr(settings, 'BUSINESS_NAME', 'DailyDine')}
            """
            
            # Render beautiful HTML email
            try:
                html_content = render_to_string(template_name, context)
            except Exception as e:
                logger.error(f"Template rendering failed: {str(e)}")
                # Fallback to simple HTML
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #1e3a8a;">DailyDine</h2>
                        <h3>{context['greeting']}</h3>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Invoice:</strong> #{context['invoice_number']}</p>
                            <p><strong>Amount:</strong> {context['amount']}</p>
                            <p><strong>Due Date:</strong> {context['due_date']}</p>
                            <p><strong>Status:</strong> {context['payment_status']}</p>
                        </div>
                        {context['message_body']}
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{context['payment_url']}" style="background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Pay Now</a>
                        </div>
                        <p>Best regards,<br>{context['business_name']}</p>
                    </div>
                </body>
                </html>
                """
            
            # Create and send beautiful email
            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.client_email]
            )
            
            # Add beautiful HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            # Update reminder info
            invoice.last_reminder_sent = timezone.now()
            invoice.reminder_count += 1
            invoice.save()
            
            return Response({'message': 'Reminder sent successfully'})
        
        except Exception as e:
            return Response({'error': f'Failed to send reminder: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_paid(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    invoice.status = 'paid'
    invoice.save()
    
    return Response({'message': 'Invoice marked as paid'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_invoices(request):
    """Get recent invoices for dashboard"""
    invoices = Invoice.objects.filter(user=request.user).order_by('-created_at')[:5]
    serializer = InvoiceSerializer(invoices, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def razorpay_webhook(request):
    """Handle Razorpay webhook for payment verification"""
    try:
        # Get the webhook payload
        payload = request.body.decode('utf-8')
        signature = request.headers.get('X-Razorpay-Signature')
        
        # Verify webhook signature
        razorpay_client.utility.verify_webhook_signature(
            payload, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
        
        # Parse the webhook data
        webhook_data = json.loads(payload)
        event = webhook_data.get('event')
        
        if event == 'payment.captured':
            payment_data = webhook_data.get('payload', {}).get('payment', {})
            entity_data = webhook_data.get('payload', {}).get('payment', {}).get('entity', {})
            
            # Extract payment details
            payment_id = entity_data.get('id')
            order_id = entity_data.get('order_id')
            amount = entity_data.get('amount') / 100  # Convert from paise to rupees
            status = entity_data.get('status')
            
            # Find the invoice by order ID
            try:
                invoice = Invoice.objects.get(razorpay_order_id=order_id)
                
                if status == 'captured':
                    # Create payment record
                    Payment.objects.create(
                        invoice=invoice,
                        amount=amount,
                        payment_method='razorpay',
                        transaction_id=payment_id,
                        status='completed',
                        notes=f'Payment captured via Razorpay webhook'
                    )
                    
                    # Update invoice status to paid
                    invoice.status = 'paid'
                    invoice.save()
                    
                    # Send beautiful payment confirmation email
                    try:
                        from django.core.mail import EmailMultiAlternatives
                        from django.template.loader import render_to_string
                        from datetime import date, timedelta
                        
                        subject = f'🎉 Payment Received - Invoice #{invoice.invoice_number}'
                        
                        # Prepare context for beautiful payment confirmation
                        context = {
                            'email_title': subject,
                            'greeting': f'Dear {invoice.client_name}! 🎉',
                            'message_body': f'''
                            <p><strong>Great news!</strong> We have successfully received your payment.</p>
                            <p>✅ <strong>Payment Amount:</strong> ₹{amount:,.2f}</p>
                            <p>📋 <strong>Invoice Number:</strong> #{invoice.invoice_number}</p>
                            <p>📅 <strong>Payment Date:</strong> {date.today().strftime('%B %d, %Y')}</p>
                            <p>Your invoice has been marked as <strong style="color: #10b981;">PAID</strong>.</p>
                            <p>Thank you for your prompt payment and continued business with us!</p>
                            ''',
                            'business_name': getattr(settings, 'BUSINESS_NAME', 'DailyDine'),
                            'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@dailydine.com'),
                            'business_phone': getattr(settings, 'BUSINESS_PHONE', '+91 98765 43210'),
                            'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business St, Mumbai, MH 400001'),
                            'invoice_number': invoice.invoice_number,
                            'client_name': invoice.client_name,
                            'client_email': invoice.client_email,
                            'amount': f"₹{amount:,.2f}",
                            'due_date': invoice.due_date.strftime('%B %d, %Y') if hasattr(invoice.due_date, 'strftime') else str(invoice.due_date),
                            'issue_date': invoice.issue_date.strftime('%B %d, %Y') if hasattr(invoice.issue_date, 'strftime') else str(invoice.issue_date),
                            'days_overdue': 0,
                            'due_status_class': 'status-paid',
                            'payment_status': 'PAID ✅',
                            'status_class': 'status-paid',
                            'payment_url': f"https://dailydine.com/invoices/{invoice.id}",
                            'invoice_pdf_url': f"https://dailydine.com/api/invoices/{invoice.id}/pdf/",
                            'whatsapp_url': f"https://wa.me/{getattr(settings, 'BUSINESS_PHONE', '919876543210').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}",
                            'support_url': f"mailto:{getattr(settings, 'BUSINESS_EMAIL', 'support@dailydine.com')}",
                            'current_year': timezone.now().year,
                            'current_date': date.today().strftime('%B %d, %Y'),
                            'legal_deadline': '',
                            'total_with_fees': f"₹{amount:,.2f}",
                            'additional_content': '''
                            <div style="background: #dcfce7; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">
                                <h3 style="color: #059669; margin-bottom: 10px;">🎉 Payment Successfully Received!</h3>
                                <ul style="color: #047857; margin-left: 20px;">
                                    <li>Invoice status updated to PAID</li>
                                    <li>Receipt available for download</li>
                                    <li>Thank you for your business!</li>
                                </ul>
                            </div>
                            ''',
                        }
                        
                        # Plain text fallback
                        plain_text = f"""
                        Dear {invoice.client_name},
                        
                        Great news! We have successfully received your payment of ₹{amount:,.2f} for Invoice #{invoice.invoice_number}.
                        
                        Your invoice has been marked as PAID.
                        
                        Thank you for your business!
                        
                        Best regards,
                        {getattr(settings, 'BUSINESS_NAME', 'DailyDine')}
                        """
                        
                        # Use friendly template for payment confirmation
                        try:
                            html_content = render_to_string('email/friendly_reminder.html', context)
                        except Exception as e:
                            # Fallback HTML
                            html_content = f"""
                            <html>
                            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                                    <h2 style="color: #10b981;">🎉 Payment Received!</h2>
                                    <h3>Dear {invoice.client_name}!</h3>
                                    <div style="background: #dcfce7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
                                        <p><strong>Payment Amount:</strong> ₹{amount:,.2f}</p>
                                        <p><strong>Invoice:</strong> #{invoice.invoice_number}</p>
                                        <p><strong>Status:</strong> <span style="color: #10b981; font-weight: bold;">PAID ✅</span></p>
                                    </div>
                                    <p>We have successfully received your payment. Thank you for your business!</p>
                                    <p>Best regards,<br>DailyDine</p>
                                </div>
                            </body>
                            </html>
                            """
                        
                        # Create and send beautiful confirmation email
                        email = EmailMultiAlternatives(
                            subject=subject,
                            body=plain_text,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[invoice.client_email]
                        )
                        
                        # Add beautiful HTML version
                        email.attach_alternative(html_content, "text/html")
                        
                        # Send email
                        email.send()
                        
                    except Exception as e:
                        print(f"Failed to send beautiful payment confirmation email: {e}")
                
            except Invoice.DoesNotExist:
                print(f"Invoice not found for order ID: {order_id}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
