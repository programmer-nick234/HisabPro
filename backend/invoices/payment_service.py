"""
Complete Payment Integration Service for HisabPro
Handles payment link generation, processing, and management
"""

import razorpay
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from decimal import Decimal
import json

logger = logging.getLogger(__name__)

class PaymentService:
    """Complete payment service with all payment methods"""
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        self.config = settings.PAYMENT_GATEWAY_CONFIG
        self.link_config = settings.PAYMENT_LINK_CONFIG
    
    def create_payment_link(self, invoice, custom_options=None):
        """
        Create payment link with all payment methods enabled
        """
        try:
            # Calculate expiry time
            expire_by = datetime.now() + timedelta(days=self.link_config['expire_by'])
            expire_timestamp = int(expire_by.timestamp())
            
            # Prepare payment link data
            payment_data = {
                'amount': int(float(invoice.total_amount) * 100),  # Convert to paise
                'currency': self.config['currency'],
                'accept_partial': False,
                'expire_by': expire_timestamp,
                'reference_id': str(invoice.id),
                'description': f'Payment for Invoice #{invoice.invoice_number}',
                'customer': {
                    'name': invoice.client_name,
                    'email': invoice.client_email,
                    'contact': invoice.client_phone or ''
                },
                'notify': {
                    'sms': self.link_config['send_sms'],
                    'email': self.link_config['send_email']
                },
                'reminder_enable': self.link_config['reminder_enable'],
                'options': {
                    'checkout': {
                        'method': {
                            'netbanking': '1',
                            'card': '1',
                            'upi': '1',
                            'wallet': '1'
                        },
                        'theme': {
                            'color': self.config['theme_color']
                        },
                        'prefill': {
                            'name': invoice.client_name,
                            'email': invoice.client_email,
                            'contact': invoice.client_phone or ''
                        }
                    }
                }
            }
            
            # Add custom options if provided
            if custom_options:
                payment_data.update(custom_options)
            
            # Create payment link
            payment_link = self.client.payment_link.create(payment_data)
            
            logger.info(f"Payment link created for invoice {invoice.invoice_number}: {payment_link['short_url']}")
            
            return {
                'success': True,
                'payment_link_id': payment_link['id'],
                'short_url': payment_link['short_url'],
                'full_url': payment_link['short_url'],
                'expire_by': expire_by,
                'amount': invoice.total_amount,
                'currency': self.config['currency']
            }
            
        except Exception as e:
            logger.error(f"Error creating payment link for invoice {invoice.invoice_number}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_bulk_payment_links(self, invoices):
        """
        Create payment links for multiple invoices
        """
        results = []
        success_count = 0
        
        for invoice in invoices:
            result = self.create_payment_link(invoice)
            result['invoice_id'] = str(invoice.id)
            result['invoice_number'] = invoice.invoice_number
            results.append(result)
            
            if result['success']:
                success_count += 1
        
        return {
            'total_processed': len(invoices),
            'successful': success_count,
            'failed': len(invoices) - success_count,
            'results': results
        }
    
    def get_payment_status(self, payment_link_id):
        """
        Get payment status for a payment link
        """
        try:
            payment_link = self.client.payment_link.fetch(payment_link_id)
            payments = self.client.payment_link.fetch(payment_link_id).payments()
            
            return {
                'success': True,
                'status': payment_link['status'],
                'amount_paid': payment_link.get('amount_paid', 0) / 100,
                'payments': payments['items'] if payments else []
            }
        except Exception as e:
            logger.error(f"Error fetching payment status for {payment_link_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_payment_link(self, payment_link_id):
        """
        Cancel a payment link
        """
        try:
            cancelled_link = self.client.payment_link.cancel(payment_link_id)
            return {
                'success': True,
                'status': cancelled_link['status']
            }
        except Exception as e:
            logger.error(f"Error cancelling payment link {payment_link_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_payment_link_email(self, invoice, payment_link_data):
        """
        Send payment link via email with beautiful template
        """
        try:
            subject = f"Payment Request - Invoice #{invoice.invoice_number}"
            
            # Prepare email context
            context = {
                'invoice': invoice,
                'payment_link': payment_link_data['short_url'],
                'amount': invoice.total_amount,
                'expire_date': payment_link_data['expire_by'].strftime('%B %d, %Y'),
                'business_name': settings.BUSINESS_NAME,
                'business_email': settings.BUSINESS_EMAIL,
                'business_phone': settings.BUSINESS_PHONE,
                'business_address': settings.BUSINESS_ADDRESS,
            }
            
            # Render HTML email
            html_content = render_to_string('email/payment_request.html', context)
            
            # Plain text version
            text_content = f"""
            Payment Request - Invoice #{invoice.invoice_number}
            
            Dear {invoice.client_name},
            
            We hope this email finds you well. This is a payment request for your invoice.
            
            Invoice Details:
            - Invoice Number: #{invoice.invoice_number}
            - Amount: ₹{invoice.total_amount:,.2f}
            - Due Date: {invoice.due_date.strftime('%B %d, %Y')}
            
            Please click the link below to make your payment:
            {payment_link_data['short_url']}
            
            Payment Methods Available:
            • Credit/Debit Cards
            • UPI (Google Pay, PhonePe, Paytm)
            • Net Banking
            • Digital Wallets
            
            This payment link expires on {payment_link_data['expire_by'].strftime('%B %d, %Y')}.
            
            If you have any questions, please don't hesitate to contact us.
            
            Best regards,
            {settings.BUSINESS_NAME}
            """
            
            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.client_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            logger.info(f"Payment link email sent to {invoice.client_email} for invoice {invoice.invoice_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending payment link email: {str(e)}")
            return False
    
    def get_payment_analytics(self, user, days=30):
        """
        Get payment analytics for dashboard
        """
        try:
            # This would typically query your database
            # For now, returning mock data structure
            return {
                'total_payment_links': 0,
                'successful_payments': 0,
                'failed_payments': 0,
                'pending_payments': 0,
                'total_amount_collected': 0,
                'average_payment_time': '2.5 hours',
                'most_used_method': 'UPI',
                'payment_methods_breakdown': {
                    'upi': 45,
                    'card': 30,
                    'netbanking': 20,
                    'wallet': 5
                }
            }
        except Exception as e:
            logger.error(f"Error getting payment analytics: {str(e)}")
            return None


class PaymentWebhookHandler:
    """Handle Razorpay webhook events"""
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def verify_signature(self, payload, signature):
        """Verify webhook signature"""
        try:
            return self.client.utility.verify_webhook_signature(
                payload, signature, settings.RAZORPAY_WEBHOOK_SECRET
            )
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return False
    
    def handle_payment_link_paid(self, event_data):
        """Handle payment.link.paid event"""
        try:
            payment_link = event_data.get('payment_link', {})
            payment = event_data.get('payment', {})
            
            # Extract invoice ID from reference_id
            reference_id = payment_link.get('reference_id')
            if not reference_id:
                logger.error("No reference_id found in payment link webhook")
                return False
            
            # Update invoice status and send confirmation
            # This would be implemented based on your invoice model
            logger.info(f"Payment successful for reference_id: {reference_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment link paid event: {str(e)}")
            return False
    
    def handle_payment_failed(self, event_data):
        """Handle payment.failed event"""
        try:
            payment = event_data.get('payment', {})
            logger.info(f"Payment failed: {payment.get('id', 'Unknown')}")
            
            # Handle failed payment logic here
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment failed event: {str(e)}")
            return False


# Initialize payment service
payment_service = PaymentService()
webhook_handler = PaymentWebhookHandler()
