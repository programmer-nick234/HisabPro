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
        serializer.save(user=self.request.user)


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
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    try:
        # Create Razorpay order
        order_data = {
            'amount': int(invoice.total_amount * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'invoice_{invoice.invoice_number}',
            'notes': {
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client_name,
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        # Create payment link
        payment_link_data = {
            'amount': int(invoice.total_amount * 100),
            'currency': 'INR',
            'accept_partial': False,
            'reference_id': f'invoice_{invoice.invoice_number}',
            'description': f'Payment for Invoice #{invoice.invoice_number}',
            'callback_url': f'{settings.FRONTEND_URL}/payment-success',
            'callback_method': 'get',
        }
        
        payment_link = razorpay_client.payment_link.create(data=payment_link_data)
        
        # Save payment link and order ID to invoice
        invoice.razorpay_payment_link = payment_link['short_url']
        invoice.razorpay_order_id = order['id']
        invoice.save()
        
        serializer = RazorpayPaymentLinkSerializer({
            'payment_link': payment_link['short_url'],
            'order_id': order['id']
        })
        return Response(serializer.data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Header
    elements.append(Paragraph(f"INVOICE #{invoice.invoice_number}", title_style))
    elements.append(Spacer(1, 20))
    
    # Company and Client Info
    company_info = []
    if invoice.user.userprofile.company_name:
        company_info.append([Paragraph(f"<b>From:</b>", styles['Normal']), 
                           Paragraph(invoice.user.userprofile.company_name, styles['Normal'])])
    if invoice.user.userprofile.address:
        company_info.append(['', Paragraph(invoice.user.userprofile.address, styles['Normal'])])
    if invoice.user.userprofile.phone:
        company_info.append(['', Paragraph(f"Phone: {invoice.user.userprofile.phone}", styles['Normal'])])
    if invoice.user.userprofile.gst_number:
        company_info.append(['', Paragraph(f"GST: {invoice.user.userprofile.gst_number}", styles['Normal'])])
    
    client_info = []
    client_info.append([Paragraph(f"<b>To:</b>", styles['Normal']), 
                       Paragraph(invoice.client_name, styles['Normal'])])
    if invoice.client_address:
        client_info.append(['', Paragraph(invoice.client_address, styles['Normal'])])
    if invoice.client_phone:
        client_info.append(['', Paragraph(f"Phone: {invoice.client_phone}", styles['Normal'])])
    if invoice.client_email:
        client_info.append(['', Paragraph(f"Email: {invoice.client_email}", styles['Normal'])])
    
    # Combine company and client info
    info_data = []
    for i in range(max(len(company_info), len(client_info))):
        row = []
        if i < len(company_info):
            row.extend(company_info[i])
        else:
            row.extend(['', ''])
        if i < len(client_info):
            row.extend(client_info[i])
        else:
            row.extend(['', ''])
        info_data.append(row)
    
    info_table = Table(info_data, colWidths=[1*inch, 2*inch, 1*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Invoice Details
    details_data = [
        ['Issue Date:', invoice.issue_date.strftime('%B %d, %Y')],
        ['Due Date:', invoice.due_date.strftime('%B %d, %Y')],
        ['Status:', invoice.status.title()],
    ]
    
    details_table = Table(details_data, colWidths=[1*inch, 2*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 20))
    
    # Items Table
    items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in invoice.items.all():
        items_data.append([
            item.description,
            str(item.quantity),
            f"₹{item.unit_price:,.2f}",
            f"₹{item.total:,.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals
    totals_data = [
        ['Subtotal:', f"₹{invoice.subtotal:,.2f}"],
        ['Tax ({:.1f}%):'.format(invoice.tax_rate), f"₹{invoice.tax_amount:,.2f}"],
        ['Total:', f"₹{invoice.total_amount:,.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (1, -1), 14),
        ('LINEABOVE', (0, -1), (1, -1), 1, colors.black),
    ]))
    elements.append(totals_table)
    
    # Notes and Terms
    if invoice.notes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Notes:</b>", styles['Heading3']))
        elements.append(Paragraph(invoice.notes, styles['Normal']))
    
    if invoice.terms_conditions:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Terms & Conditions:</b>", styles['Heading3']))
        elements.append(Paragraph(invoice.terms_conditions, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    # Create response
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    return response


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_reminder(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    serializer = SendReminderSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            
            # Prepare email content
            subject = f"Payment Reminder - Invoice #{invoice.invoice_number}"
            
            # Custom message or default
            custom_message = serializer.validated_data.get('message', '')
            if not custom_message:
                custom_message = f"""
                Dear {invoice.client_name},
                
                This is a friendly reminder that payment for Invoice #{invoice.invoice_number} 
                amounting to ₹{invoice.total_amount:,.2f} is due on {invoice.due_date.strftime('%B %d, %Y')}.
                
                Please process the payment at your earliest convenience.
                
                Thank you for your business.
                
                Best regards,
                {request.user.get_full_name() or request.user.username}
                """
            
            # Send email
            send_mail(
                subject=subject,
                message=custom_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invoice.client_email],
                fail_silently=False,
            )
            
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
                    
                    # Send confirmation email to client
                    try:
                        send_mail(
                            subject=f'Payment Received - Invoice #{invoice.invoice_number}',
                            message=f'''
                            Dear {invoice.client_name},
                            
                            We have received your payment of ₹{amount} for Invoice #{invoice.invoice_number}.
                            
                            Thank you for your business!
                            
                            Best regards,
                            {invoice.user.get_full_name() or invoice.user.username}
                            ''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[invoice.client_email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        print(f"Failed to send payment confirmation email: {e}")
                
            except Invoice.DoesNotExist:
                print(f"Invoice not found for order ID: {order_id}")
        
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
