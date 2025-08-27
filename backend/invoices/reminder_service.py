"""
Advanced Reminder Service for HisabPro
Handles email/SMS sending, template processing, and analytics
"""

import logging
from datetime import datetime, timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import re
import requests
from typing import Dict, List, Optional, Tuple

from .reminder_models import (
    ReminderTemplate, ReminderRule, ReminderSchedule, 
    ReminderLog, ReminderAnalytics, ClientReminderPreference
)
from .models import Invoice

logger = logging.getLogger(__name__)


class ReminderTemplateProcessor:
    """Processes reminder templates with dynamic content"""
    
    @staticmethod
    def _format_date(date_value):
        """Format date value to string, handling both date objects and strings"""
        if not date_value:
            return 'Not set'
        
        # If it's already a string, try to parse it
        if isinstance(date_value, str):
            try:
                from datetime import datetime
                if 'T' in date_value:  # ISO format
                    parsed_date = datetime.fromisoformat(date_value.replace('Z', '+00:00')).date()
                else:  # Simple date format
                    parsed_date = datetime.strptime(date_value, '%Y-%m-%d').date()
                return parsed_date.strftime('%B %d, %Y')
            except:
                return date_value  # Return as-is if parsing fails
        
        # If it's a date/datetime object
        try:
            if hasattr(date_value, 'date'):  # datetime object
                return date_value.date().strftime('%B %d, %Y')
            else:  # date object
                return date_value.strftime('%B %d, %Y')
        except:
            return str(date_value)
    
    @staticmethod
    def _calculate_days_overdue(invoice):
        """Calculate days overdue, handling different date formats"""
        if not invoice.due_date:
            return 0
        
        try:
            from datetime import datetime
            today = timezone.now().date()
            
            # Handle string dates
            if isinstance(invoice.due_date, str):
                if 'T' in invoice.due_date:  # ISO format
                    due_date = datetime.fromisoformat(invoice.due_date.replace('Z', '+00:00')).date()
                else:  # Simple date format
                    due_date = datetime.strptime(invoice.due_date, '%Y-%m-%d').date()
            else:
                # Handle date/datetime objects
                if hasattr(invoice.due_date, 'date'):
                    due_date = invoice.due_date.date()
                else:
                    due_date = invoice.due_date
            
            if today > due_date:
                return (today - due_date).days
            return 0
        except:
            return 0
    
    @staticmethod
    def process_template(template: ReminderTemplate, invoice: Invoice, custom_data: Dict = None) -> Dict[str, str]:
        """
        Process template with invoice data and return rendered content
        """
        # Base template variables
        template_vars = {
            'invoice_number': invoice.invoice_number,
            'client_name': invoice.client_name,
            'client_email': invoice.client_email,
            'amount': f"₹{invoice.total_amount:,.2f}",
            'due_date': ReminderTemplateProcessor._format_date(invoice.due_date),
            'issue_date': ReminderTemplateProcessor._format_date(invoice.issue_date),
            'days_overdue': ReminderTemplateProcessor._calculate_days_overdue(invoice),
            'business_name': getattr(settings, 'BUSINESS_NAME', 'Your Business'),
            'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@yourbusiness.com'),
            'business_phone': getattr(settings, 'BUSINESS_PHONE', '+1 (555) 123-4567'),
        }
        
        # Add custom data if provided
        if custom_data:
            template_vars.update(custom_data)
        
        # Process email subject
        email_subject = template.email_subject
        for key, value in template_vars.items():
            email_subject = email_subject.replace(f'{{{{{key}}}}}', str(value))
        
        # Process email body
        email_body = template.email_body
        for key, value in template_vars.items():
            email_body = email_body.replace(f'{{{{{key}}}}}', str(value))
        
        # Process SMS message
        sms_message = template.sms_message
        for key, value in template_vars.items():
            sms_message = sms_message.replace(f'{{{{{key}}}}}', str(value))
        
        return {
            'email_subject': email_subject,
            'email_body': email_body,
            'sms_message': sms_message,
            'template_vars': template_vars
        }


class SMSService:
    """SMS sending service - Currently disabled to keep system cost-free"""
    
    def __init__(self):
        # SMS service is disabled by default to avoid third-party costs
        self.enabled = getattr(settings, 'SMS_ENABLED', False)
        self.api_key = getattr(settings, 'SMS_API_KEY', '')
        self.sender_id = getattr(settings, 'SMS_SENDER_ID', 'HISABPRO')
        self.base_url = getattr(settings, 'SMS_API_URL', '')
    
    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Send SMS using configured provider
        Returns (success, message/error)
        
        Note: SMS is disabled by default to keep the system cost-free.
        Email reminders are used as the primary channel.
        """
        if not self.enabled:
            logger.info("SMS service is disabled - using email-only delivery")
            return False, "SMS delivery disabled - email reminders will be sent instead"
        
        if not self.api_key or not self.base_url:
            logger.warning("SMS service not configured properly")
            return False, "SMS service not configured - please add SMS provider settings"
        
        try:
            # Clean phone number
            phone = re.sub(r'[^\d+]', '', phone_number)
            if not phone.startswith('+'):
                phone = '+91' + phone  # Default to India
            
            # Example API call (adjust for your SMS provider)
            payload = {
                'apikey': self.api_key,
                'numbers': phone,
                'message': message,
                'sender': self.sender_id
            }
            
            response = requests.post(self.base_url, data=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return True, "SMS sent successfully"
                else:
                    return False, result.get('message', 'SMS sending failed')
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            logger.error(f"SMS sending error: {str(e)}")
            return False, str(e)


class ReminderService:
    """Main service for handling all reminder operations"""
    
    def __init__(self):
        self.template_processor = ReminderTemplateProcessor()
        self.sms_service = SMSService()
    
    def get_applicable_rule(self, invoice: Invoice) -> Optional[ReminderRule]:
        """Find the most specific rule that applies to this invoice"""
        rules = ReminderRule.objects.filter(
            user=invoice.user,
            is_active=True
        ).order_by('min_invoice_amount')
        
        for rule in rules:
            if rule.applies_to_invoice(invoice):
                return rule
        
        return None
    
    def schedule_reminders_for_invoice(self, invoice: Invoice, rule: ReminderRule = None) -> List[ReminderSchedule]:
        """
        Schedule all reminders for an invoice based on rules
        """
        if not rule:
            rule = self.get_applicable_rule(invoice)
            if not rule:
                logger.warning(f"No reminder rule found for invoice {invoice.invoice_number}")
                return []
        
        scheduled_reminders = []
        
        # Calculate reminder dates
        reminder_dates = {
            'pre_due': invoice.due_date - timedelta(days=rule.days_before_due) if invoice.due_date else None,
            'due_date': invoice.due_date if invoice.due_date else None,
            'overdue_1': invoice.due_date + timedelta(days=rule.days_after_due_1) if invoice.due_date else None,
            'overdue_2': invoice.due_date + timedelta(days=rule.days_after_due_2) if invoice.due_date else None,
            'overdue_3': invoice.due_date + timedelta(days=rule.days_after_due_3) if invoice.due_date else None,
        }
        
        # Template mapping
        templates = {
            'pre_due': rule.pre_due_template,
            'due_date': rule.due_date_template,
            'overdue_1': rule.overdue_1_template,
            'overdue_2': rule.overdue_2_template,
            'overdue_3': rule.overdue_3_template,
        }
        
        # Create reminder schedules
        for reminder_type, scheduled_date in reminder_dates.items():
            if scheduled_date and templates.get(reminder_type):
                # Skip if date is in the past
                if scheduled_date < timezone.now().date():
                    continue
                
                # Adjust for weekends/holidays if needed
                if rule.skip_weekends:
                    scheduled_date = self._adjust_for_weekends(scheduled_date)
                
                reminder_schedule = ReminderSchedule.objects.create(
                    invoice=invoice,
                    reminder_rule=rule,
                    reminder_template=templates[reminder_type],
                    reminder_type=reminder_type,
                    scheduled_date=timezone.make_aware(datetime.combine(scheduled_date, datetime.min.time())),
                    send_email=rule.use_email,
                    send_sms=rule.use_sms
                )
                
                scheduled_reminders.append(reminder_schedule)
                logger.info(f"Scheduled {reminder_type} reminder for invoice {invoice.invoice_number} on {scheduled_date}")
        
        return scheduled_reminders
    
    def send_reminder(self, reminder_schedule: ReminderSchedule, custom_message: Dict = None) -> Tuple[bool, str]:
        """
        Send a reminder via email and/or SMS
        """
        try:
            invoice = reminder_schedule.invoice
            template = reminder_schedule.reminder_template
            
            if not template:
                return False, "No template specified for reminder"
            
            # Process template
            if custom_message:
                processed_content = {
                    'email_subject': custom_message.get('subject', ''),
                    'email_body': custom_message.get('email_body', ''),
                    'sms_message': custom_message.get('sms_message', ''),
                }
            else:
                processed_content = self.template_processor.process_template(template, invoice)
            
            email_success = False
            sms_success = False
            error_messages = []
            
            # Send email
            if reminder_schedule.send_email:
                email_success, email_error = self._send_email_reminder(
                    invoice, processed_content, template
                )
                if not email_success:
                    error_messages.append(f"Email: {email_error}")
            
            # Send SMS (if enabled and configured)
            if reminder_schedule.send_sms:
                client_pref = self._get_client_preferences(invoice)
                if client_pref and client_pref.phone_number:
                    sms_success, sms_error = self.sms_service.send_sms(
                        client_pref.phone_number,
                        processed_content['sms_message']
                    )
                    if not sms_success:
                        if "SMS delivery disabled" in sms_error:
                            # SMS is disabled, don't treat as error - email will be primary channel
                            logger.info(f"SMS disabled for invoice {invoice.invoice_number} - email reminder will be sent")
                        else:
                            error_messages.append(f"SMS: {sms_error}")
                else:
                    error_messages.append("SMS: No phone number available")
            
            # Update reminder schedule
            reminder_schedule.status = 'sent' if (email_success or sms_success) else 'failed'
            reminder_schedule.sent_date = timezone.now()
            reminder_schedule.email_sent = email_success
            reminder_schedule.sms_sent = sms_success
            reminder_schedule.error_message = '; '.join(error_messages)
            reminder_schedule.save()
            
            # Log the reminder
            channel = 'both' if (reminder_schedule.send_email and reminder_schedule.send_sms) else ('email' if reminder_schedule.send_email else 'sms')
            result = 'success' if (email_success and sms_success) else ('partial' if (email_success or sms_success) else 'failed')
            
            ReminderLog.objects.create(
                invoice=invoice,
                reminder_schedule=reminder_schedule,
                channel=channel,
                result=result,
                email_subject=processed_content['email_subject'],
                email_body_preview=processed_content['email_body'][:500],
                sms_message=processed_content['sms_message'],
                email_delivered=email_success,
                sms_delivered=sms_success,
                error_details='; '.join(error_messages)
            )
            
            # Update invoice reminder count
            invoice.reminder_count += 1
            invoice.last_reminder_sent = timezone.now()
            invoice.save()
            
            success = email_success or sms_success
            message = "Reminder sent successfully" if success else f"Failed to send reminder: {'; '.join(error_messages)}"
            
            return success, message
            
        except Exception as e:
            logger.error(f"Error sending reminder for invoice {reminder_schedule.invoice.invoice_number}: {str(e)}")
            reminder_schedule.status = 'failed'
            reminder_schedule.error_message = str(e)
            reminder_schedule.save()
            return False, str(e)
    
    def _send_email_reminder(self, invoice: Invoice, content: Dict, template: ReminderTemplate) -> Tuple[bool, str]:
        """Send beautiful HTML email reminder"""
        try:
            from datetime import date
            
            # Determine template file based on template name
            template_mapping = {
                'Friendly Pre-Due Reminder': 'email/friendly_reminder.html',
                'Friendly Overdue Reminder': 'email/friendly_reminder.html',
                'Professional Due Date Reminder': 'email/professional_reminder.html',
                'Professional Overdue Reminder': 'email/professional_reminder.html',
                'Urgent Payment Request': 'email/urgent_reminder.html',
                'Final Notice': 'email/final_notice.html',
                'Legal Notice': 'email/legal_notice.html',
            }
            
            # Get template file or use base template
            template_file = template_mapping.get(template.name, 'email/base_template.html')
            
            # Calculate days overdue and status
            today = date.today()
            if isinstance(invoice.due_date, str):
                try:
                    due_date = datetime.strptime(invoice.due_date, '%Y-%m-%d').date()
                except ValueError:
                    due_date = datetime.strptime(invoice.due_date, '%Y-%m-%d').date()
            else:
                due_date = invoice.due_date
            
            days_overdue = max(0, (today - due_date).days)
            
            # Determine status classes and payment status
            if days_overdue > 0:
                due_status_class = 'status-overdue'
                payment_status = f'{days_overdue} days overdue'
                status_class = 'status-overdue'
            elif (due_date - today).days <= 3:
                due_status_class = 'status-due-soon'
                payment_status = 'Due soon'
                status_class = 'status-due-soon'
            else:
                due_status_class = 'status-pending'
                payment_status = 'Pending'
                status_class = 'status-pending'
            
            # Prepare template context for beautiful HTML email
            context = {
                'email_title': content['email_subject'],
                'greeting': f"Dear {invoice.client_name}," if template.tone == 'formal' else f"Hello {invoice.client_name}! 👋",
                'message_body': content['email_body'],
                'business_name': getattr(settings, 'BUSINESS_NAME', 'DailyDine'),
                'business_email': getattr(settings, 'BUSINESS_EMAIL', 'contact@dailydine.com'),
                'business_phone': getattr(settings, 'BUSINESS_PHONE', '+91 98765 43210'),
                'business_address': getattr(settings, 'BUSINESS_ADDRESS', '123 Business St, Mumbai, MH 400001'),
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client_name,
                'client_email': invoice.client_email,
                'amount': f"₹{invoice.total_amount:,.2f}",
                'due_date': ReminderTemplateProcessor._format_date(invoice.due_date),
                'issue_date': ReminderTemplateProcessor._format_date(invoice.issue_date),
                'days_overdue': days_overdue,
                'due_status_class': due_status_class,
                'payment_status': payment_status,
                'status_class': status_class,
                'payment_url': f"https://dailydine.com/pay/{invoice.id}",
                'invoice_pdf_url': f"https://dailydine.com/api/invoices/{invoice.id}/pdf/",
                'whatsapp_url': f"https://wa.me/{getattr(settings, 'BUSINESS_PHONE', '919876543210').replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')}",
                'support_url': f"mailto:{getattr(settings, 'BUSINESS_EMAIL', 'support@dailydine.com')}",
                'current_year': datetime.now().year,
                'current_date': today.strftime('%B %d, %Y'),
                'legal_deadline': (today + timedelta(days=30)).strftime('%B %d, %Y'),
                'total_with_fees': f"₹{float(invoice.total_amount) * 1.15:,.2f}",  # Add 15% fees for legal
                'additional_content': '',  # Can be customized per template
            }
            
            # Render beautiful HTML email
            try:
                html_content = render_to_string(template_file, context)
                logger.info(f"Successfully rendered HTML template: {template_file}")
            except Exception as e:
                logger.warning(f"Failed to render HTML template {template_file}: {str(e)}")
                # Fallback to simple HTML
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #1e3a8a;">{context['business_name']}</h2>
                        <h3>{context['greeting']}</h3>
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <p><strong>Invoice:</strong> #{context['invoice_number']}</p>
                            <p><strong>Amount:</strong> {context['amount']}</p>
                            <p><strong>Due Date:</strong> {context['due_date']}</p>
                        </div>
                        <p>{context['message_body']}</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{context['payment_url']}" style="background: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold;">Pay Now</a>
                        </div>
                        <p>Best regards,<br>{context['business_name']}</p>
                    </div>
                </body>
                </html>
                """
            
            # Create email with both plain text and beautiful HTML
            email = EmailMultiAlternatives(
                subject=content['email_subject'],
                body=content['email_body'],  # Plain text fallback
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.client_email]
            )
            
            # Add beautiful HTML version
            email.attach_alternative(html_content, "text/html")
            
            # Add PDF attachment if requested
            if template.include_pdf_attachment:
                try:
                    # Try to generate PDF for attachment
                    from .pdf_views import generate_invoice_pdf
                    from django.http import HttpRequest
                    
                    # Create a mock request for PDF generation
                    request = HttpRequest()
                    request.user = invoice.user
                    request.method = 'GET'
                    
                    # Generate PDF using existing PDF service
                    pdf_response = generate_invoice_pdf(request, str(invoice.id))
                    if hasattr(pdf_response, 'content') and pdf_response.content:
                        email.attach(f"invoice_{invoice.invoice_number}.pdf", pdf_response.content, 'application/pdf')
                        logger.info(f"PDF attached to reminder email for invoice {invoice.invoice_number}")
                    else:
                        logger.warning(f"PDF generation returned empty content for invoice {invoice.invoice_number}")
                except Exception as e:
                    logger.warning(f"Failed to attach PDF to reminder email for invoice {invoice.invoice_number}: {str(e)}")
                    # Continue without PDF attachment - don't fail the email
            
            # Send beautiful email
            email.send()
            logger.info(f"Beautiful HTML email reminder sent for invoice {invoice.invoice_number}")
            return True, "Beautiful HTML email sent successfully"
            
        except Exception as e:
            logger.error(f"Failed to send email reminder: {str(e)}")
            return False, str(e)
    
    def _get_client_preferences(self, invoice: Invoice) -> Optional[ClientReminderPreference]:
        """Get client reminder preferences"""
        try:
            return ClientReminderPreference.objects.get(
                user=invoice.user,
                client_email=invoice.client_email
            )
        except ClientReminderPreference.DoesNotExist:
            return None
    
    def _adjust_for_weekends(self, date) -> datetime:
        """Adjust date to skip weekends"""
        while date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            date += timedelta(days=1)
        return date
    
    def process_scheduled_reminders(self) -> Dict[str, int]:
        """
        Process all scheduled reminders that are due
        Called by scheduled task/cron job
        """
        now = timezone.now()
        due_reminders = ReminderSchedule.objects.filter(
            status='scheduled',
            scheduled_date__lte=now
        ).select_related('invoice', 'reminder_template')
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for reminder in due_reminders:
            results['processed'] += 1
            
            # Skip if invoice is already paid
            if reminder.invoice.status == 'paid':
                reminder.status = 'skipped'
                reminder.save()
                results['skipped'] += 1
                continue
            
            # Check client preferences
            client_pref = self._get_client_preferences(reminder.invoice)
            if client_pref and client_pref.reminders_paused:
                if client_pref.pause_until and client_pref.pause_until > now.date():
                    reminder.status = 'skipped'
                    reminder.save()
                    results['skipped'] += 1
                    continue
            
            # Send reminder
            success, message = self.send_reminder(reminder)
            
            if success:
                results['successful'] += 1
                logger.info(f"Successfully sent reminder for invoice {reminder.invoice.invoice_number}")
            else:
                results['failed'] += 1
                logger.error(f"Failed to send reminder for invoice {reminder.invoice.invoice_number}: {message}")
        
        return results
    
    def generate_analytics(self, user, start_date: datetime, end_date: datetime) -> ReminderAnalytics:
        """Generate reminder analytics for a period"""
        
        # Get reminder logs for the period
        logs = ReminderLog.objects.filter(
            invoice__user=user,
            sent_at__date__range=[start_date, end_date]
        )
        
        # Calculate stats
        total_reminders = logs.count()
        email_reminders = logs.filter(channel__in=['email', 'both']).count()
        sms_reminders = logs.filter(channel__in=['sms', 'both']).count()
        
        successful_reminders = logs.filter(result='success').count()
        invoices_paid_after_reminder = logs.filter(payment_received=True).count()
        
        # Calculate amounts
        paid_logs = logs.filter(payment_received=True)
        total_amount_collected = sum(log.invoice.total_amount for log in paid_logs)
        
        # Calculate success rates
        email_success_rate = (logs.filter(channel__in=['email', 'both'], result='success').count() / email_reminders * 100) if email_reminders > 0 else 0
        sms_success_rate = (logs.filter(channel__in=['sms', 'both'], result='success').count() / sms_reminders * 100) if sms_reminders > 0 else 0
        
        # Find best performing template
        template_performance = {}
        for log in logs.filter(payment_received=True):
            template_id = log.reminder_schedule.reminder_template_id
            if template_id:
                if template_id not in template_performance:
                    template_performance[template_id] = {'success': 0, 'total': 0}
                template_performance[template_id]['success'] += 1
        
        for log in logs:
            template_id = log.reminder_schedule.reminder_template_id
            if template_id:
                if template_id not in template_performance:
                    template_performance[template_id] = {'success': 0, 'total': 0}
                template_performance[template_id]['total'] += 1
        
        best_template = None
        best_success_rate = 0
        for template_id, performance in template_performance.items():
            if performance['total'] > 0:
                success_rate = (performance['success'] / performance['total']) * 100
                if success_rate > best_success_rate:
                    best_success_rate = success_rate
                    try:
                        best_template = ReminderTemplate.objects.get(id=template_id)
                    except ReminderTemplate.DoesNotExist:
                        pass
        
        # Calculate average days to payment
        avg_days = 0
        if paid_logs.exists():
            total_days = 0
            count = 0
            for log in paid_logs:
                if log.payment_received_date and log.sent_at:
                    days = (log.payment_received_date - log.sent_at.date()).days
                    total_days += days
                    count += 1
            avg_days = total_days / count if count > 0 else 0
        
        # Create or update analytics record
        analytics, created = ReminderAnalytics.objects.get_or_create(
            user=user,
            period_start=start_date,
            period_end=end_date,
            defaults={
                'total_reminders_sent': total_reminders,
                'email_reminders_sent': email_reminders,
                'sms_reminders_sent': sms_reminders,
                'invoices_paid_after_reminder': invoices_paid_after_reminder,
                'total_amount_collected': total_amount_collected,
                'average_days_to_payment': avg_days,
                'best_performing_template': best_template,
                'best_template_success_rate': best_success_rate,
                'email_success_rate': email_success_rate,
                'sms_success_rate': sms_success_rate,
            }
        )
        
        if not created:
            # Update existing record
            analytics.total_reminders_sent = total_reminders
            analytics.email_reminders_sent = email_reminders
            analytics.sms_reminders_sent = sms_reminders
            analytics.invoices_paid_after_reminder = invoices_paid_after_reminder
            analytics.total_amount_collected = total_amount_collected
            analytics.average_days_to_payment = avg_days
            analytics.best_performing_template = best_template
            analytics.best_template_success_rate = best_success_rate
            analytics.email_success_rate = email_success_rate
            analytics.sms_success_rate = sms_success_rate
            analytics.save()
        
        return analytics


# Global service instance
reminder_service = ReminderService()
