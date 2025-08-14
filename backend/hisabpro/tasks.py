from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from invoices.models import Invoice


@shared_task
def send_overdue_reminders():
    """Send automatic reminders for overdue invoices"""
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(
        status='overdue',
        due_date__lt=today,
        last_reminder_sent__lt=timezone.now() - timedelta(days=7)  # Send reminder every 7 days
    )
    
    for invoice in overdue_invoices:
        try:
            subject = f"Payment Overdue - Invoice #{invoice.invoice_number}"
            message = f"""
            Dear {invoice.client_name},
            
            This is a reminder that payment for Invoice #{invoice.invoice_number} 
            amounting to ₹{invoice.total_amount:,.2f} was due on {invoice.due_date.strftime('%B %d, %Y')}.
            
            The payment is now overdue. Please process the payment immediately to avoid any late fees.
            
            If you have already made the payment, please disregard this message.
            
            Thank you for your prompt attention to this matter.
            
            Best regards,
            {invoice.user.get_full_name() or invoice.user.username}
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invoice.client_email],
                fail_silently=False,
            )
            
            # Update reminder info
            invoice.last_reminder_sent = timezone.now()
            invoice.reminder_count += 1
            invoice.save()
            
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
    """Send reminders for invoices due in the next 3 days"""
    today = timezone.now().date()
    reminder_date = today + timedelta(days=3)
    
    due_soon_invoices = Invoice.objects.filter(
        status='pending',
        due_date=reminder_date,
        last_reminder_sent__isnull=True  # Only send if no reminder sent yet
    )
    
    for invoice in due_soon_invoices:
        try:
            subject = f"Payment Due Soon - Invoice #{invoice.invoice_number}"
            message = f"""
            Dear {invoice.client_name},
            
            This is a friendly reminder that payment for Invoice #{invoice.invoice_number} 
            amounting to ₹{invoice.total_amount:,.2f} is due on {invoice.due_date.strftime('%B %d, %Y')}.
            
            Please ensure the payment is processed before the due date to avoid any late fees.
            
            Thank you for your business.
            
            Best regards,
            {invoice.user.get_full_name() or invoice.user.username}
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invoice.client_email],
                fail_silently=False,
            )
            
            # Update reminder info
            invoice.last_reminder_sent = timezone.now()
            invoice.reminder_count += 1
            invoice.save()
            
        except Exception as e:
            print(f"Failed to send due date reminder for invoice {invoice.invoice_number}: {str(e)}")
