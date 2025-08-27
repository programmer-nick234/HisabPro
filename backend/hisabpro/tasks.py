from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta, date
from invoices.models import Invoice


def send_beautiful_email_reminder(invoice, template_type='overdue'):
    """Send beautiful HTML email reminder"""
    try:
        # Calculate days overdue
        today = date.today()
        if isinstance(invoice.due_date, str):
            due_date = timezone.datetime.strptime(invoice.due_date, '%Y-%m-%d').date()
        else:
            due_date = invoice.due_date
        
        days_overdue = max(0, (today - due_date).days)
        
        # Determine status classes and payment status
        if days_overdue > 0:
            due_status_class = 'status-overdue'
            payment_status = f'{days_overdue} days overdue'
            status_class = 'status-overdue'
            template_name = 'email/urgent_reminder.html'
            subject = f"🚨 URGENT: Payment Overdue - Invoice #{invoice.invoice_number}"
        elif (due_date - today).days <= 3:
            due_status_class = 'status-due-soon'
            payment_status = 'Due soon'
            status_class = 'status-due-soon'
            template_name = 'email/friendly_reminder.html'
            subject = f"💰 Friendly Reminder - Invoice #{invoice.invoice_number}"
        else:
            due_status_class = 'status-pending'
            payment_status = 'Pending'
            status_class = 'status-pending'
            template_name = 'email/professional_reminder.html'
            subject = f"📋 Payment Reminder - Invoice #{invoice.invoice_number}"
        
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
            'greeting': f"Dear {invoice.client_name}," if template_type == 'overdue' else f"Hello {invoice.client_name}! 👋",
            'message_body': f'''<p>We hope this email finds you well!</p>
<p>This is a {"urgent" if template_type == "overdue" else "friendly"} reminder that your invoice <strong>#{invoice.invoice_number}</strong> for <strong>₹{invoice.total_amount:,.2f}</strong> {"is now overdue" if days_overdue > 0 else "is due soon"}.</p>
<p>{"Please process the payment immediately to avoid service disruption." if days_overdue > 0 else "Please process the payment at your earliest convenience."}</p>
<p>If you have any questions, we're here to help!</p>''',
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
            'due_status_class': due_status_class,
            'payment_status': payment_status,
            'status_class': status_class,
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
        
        # Render beautiful HTML email
        try:
            html_content = render_to_string(template_name, context)
        except Exception as e:
            print(f"Template rendering failed: {str(e)}")
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
        print(f"Beautiful HTML email sent for invoice {invoice.invoice_number}")
        return True
        
    except Exception as e:
        print(f"Failed to send beautiful email for invoice {invoice.invoice_number}: {str(e)}")
        return False


@shared_task
def send_overdue_reminders():
    """Send automatic beautiful reminders for overdue invoices"""
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(
        status='overdue',
        due_date__lt=today,
        last_reminder_sent__lt=timezone.now() - timedelta(days=7)  # Send reminder every 7 days
    )
    
    for invoice in overdue_invoices:
        try:
            success = send_beautiful_email_reminder(invoice, 'overdue')
            
            if success:
                # Update reminder info
                invoice.last_reminder_sent = timezone.now()
                invoice.reminder_count += 1
                invoice.save()
                print(f"✅ Beautiful overdue reminder sent for {invoice.invoice_number}")
            
        except Exception as e:
            print(f"Failed to send reminder for invoice {invoice.invoice_number}: {str(e)}")


@shared_task
def update_invoice_statuses():
    """Update invoice statuses based on due dates"""
    today = timezone.now().date()
    
    # Update pending invoices to overdue
    pending_invoices = Invoice.objects.filter(
        status='pending',
        due_date__lt=today
    )
    pending_invoices.update(status='overdue')
    
    # Update overdue invoices to pending if due date is in the future
    overdue_invoices = Invoice.objects.filter(
        status='overdue',
        due_date__gte=today
    )
    overdue_invoices.update(status='pending')


@shared_task
def send_due_date_reminders():
    """Send beautiful reminders for invoices due in the next 3 days"""
    today = timezone.now().date()
    reminder_date = today + timedelta(days=3)
    
    due_soon_invoices = Invoice.objects.filter(
        status='pending',
        due_date=reminder_date,
        last_reminder_sent__isnull=True  # Only send if no reminder sent yet
    )
    
    for invoice in due_soon_invoices:
        try:
            success = send_beautiful_email_reminder(invoice, 'due_soon')
            
            if success:
                # Update reminder info
                invoice.last_reminder_sent = timezone.now()
                invoice.reminder_count += 1
                invoice.save()
                print(f"✅ Beautiful due date reminder sent for {invoice.invoice_number}")
            
        except Exception as e:
            print(f"Failed to send due date reminder for invoice {invoice.invoice_number}: {str(e)}")
