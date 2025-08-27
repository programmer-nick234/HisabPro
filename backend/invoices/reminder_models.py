"""
Advanced Reminder System Models for HisabPro
Supports custom frequency, multiple channels, escalation paths, and analytics
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from .models import Invoice


class ReminderTemplate(models.Model):
    """Templates for different reminder tones and stages"""
    
    TONE_CHOICES = [
        ('friendly', 'Friendly'),
        ('professional', 'Professional'), 
        ('firm', 'Firm'),
        ('urgent', 'Urgent'),
        ('final_notice', 'Final Notice'),
    ]
    
    STAGE_CHOICES = [
        ('pre_due', 'Before Due Date'),
        ('due_date', 'On Due Date'),
        ('overdue_1', 'Overdue - First Reminder'),
        ('overdue_2', 'Overdue - Second Reminder'),
        ('overdue_3', 'Overdue - Final Notice'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_templates')
    name = models.CharField(max_length=200)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES)
    
    # Email content
    email_subject = models.CharField(max_length=300)
    email_body = models.TextField(help_text="Use {{invoice_number}}, {{client_name}}, {{amount}}, {{due_date}} as placeholders")
    
    # SMS content
    sms_message = models.TextField(max_length=500, help_text="SMS message (max 500 chars)")
    
    # Template settings
    include_pdf_attachment = models.BooleanField(default=True)
    include_payment_link = models.BooleanField(default=True)
    include_payment_history = models.BooleanField(default=False)
    include_late_fees = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'tone', 'stage']
        ordering = ['stage', 'tone']
    
    def __str__(self):
        return f"{self.name} - {self.get_tone_display()} ({self.get_stage_display()})"


class ReminderRule(models.Model):
    """Custom reminder rules based on invoice amounts and client types"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_rules')
    name = models.CharField(max_length=200)
    
    # Amount-based rules
    min_invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    max_invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timing rules
    days_before_due = models.IntegerField(default=3, help_text="Days before due date to send first reminder")
    days_after_due_1 = models.IntegerField(default=1, help_text="Days after due date for first overdue reminder")
    days_after_due_2 = models.IntegerField(default=7, help_text="Days after due date for second overdue reminder") 
    days_after_due_3 = models.IntegerField(default=15, help_text="Days after due date for final notice")
    
    # Channel preferences
    use_email = models.BooleanField(default=True)
    use_sms = models.BooleanField(default=False)
    
    # Templates for each stage
    pre_due_template = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='pre_due_rules')
    due_date_template = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='due_date_rules')
    overdue_1_template = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='overdue_1_rules')
    overdue_2_template = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='overdue_2_rules')
    overdue_3_template = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='overdue_3_rules')
    
    # Advanced settings
    skip_weekends = models.BooleanField(default=True)
    skip_holidays = models.BooleanField(default=True)
    max_reminders = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['min_invoice_amount']
    
    def __str__(self):
        max_amount = f"₹{self.max_invoice_amount}" if self.max_invoice_amount else "∞"
        return f"{self.name} (₹{self.min_invoice_amount} - {max_amount})"
    
    def applies_to_invoice(self, invoice):
        """Check if this rule applies to the given invoice"""
        if not self.is_active:
            return False
            
        if invoice.total_amount < self.min_invoice_amount:
            return False
            
        if self.max_invoice_amount and invoice.total_amount > self.max_invoice_amount:
            return False
            
        return True


class ReminderSchedule(models.Model):
    """Scheduled reminders for specific invoices"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('skipped', 'Skipped'),
    ]
    
    REMINDER_TYPE_CHOICES = [
        ('pre_due', 'Before Due Date'),
        ('due_date', 'On Due Date'),
        ('overdue_1', 'Overdue - First'),
        ('overdue_2', 'Overdue - Second'),
        ('overdue_3', 'Overdue - Final'),
        ('manual', 'Manual Reminder'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='reminder_schedules')
    reminder_rule = models.ForeignKey(ReminderRule, on_delete=models.CASCADE, null=True, blank=True)
    reminder_template = models.ForeignKey(ReminderTemplate, on_delete=models.CASCADE, null=True, blank=True)
    
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Channel flags
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    
    # Custom message override
    custom_subject = models.CharField(max_length=300, blank=True)
    custom_email_body = models.TextField(blank=True)
    custom_sms_message = models.TextField(max_length=500, blank=True)
    
    # Tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"Reminder for {self.invoice.invoice_number} - {self.get_reminder_type_display()}"


class ReminderLog(models.Model):
    """Log of all sent reminders for analytics"""
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email & SMS'),
    ]
    
    RESULT_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='reminder_logs')
    reminder_schedule = models.ForeignKey(ReminderSchedule, on_delete=models.CASCADE, related_name='logs')
    
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    
    # Message details
    email_subject = models.CharField(max_length=300, blank=True)
    email_body_preview = models.TextField(max_length=500, blank=True)
    sms_message = models.TextField(max_length=500, blank=True)
    
    # Delivery details
    email_delivered = models.BooleanField(default=False)
    email_opened = models.BooleanField(default=False)
    email_clicked = models.BooleanField(default=False)
    sms_delivered = models.BooleanField(default=False)
    
    # Response tracking
    client_responded = models.BooleanField(default=False)
    payment_received = models.BooleanField(default=False)
    payment_received_date = models.DateTimeField(null=True, blank=True)
    
    # Error details
    error_details = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Reminder Log - {self.invoice.invoice_number} via {self.get_channel_display()}"


class ReminderAnalytics(models.Model):
    """Analytics data for reminder effectiveness"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminder_analytics')
    
    # Time period
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Reminder stats
    total_reminders_sent = models.IntegerField(default=0)
    email_reminders_sent = models.IntegerField(default=0)
    sms_reminders_sent = models.IntegerField(default=0)
    
    # Effectiveness stats
    invoices_paid_after_reminder = models.IntegerField(default=0)
    total_amount_collected = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    average_days_to_payment = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Template performance
    best_performing_template = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    best_template_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Channel performance
    email_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    sms_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'period_start', 'period_end']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"Reminder Analytics - {self.period_start} to {self.period_end}"


class ClientReminderPreference(models.Model):
    """Client-specific reminder preferences"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_email = models.EmailField()
    client_name = models.CharField(max_length=200)
    
    # Preferences
    prefers_email = models.BooleanField(default=True)
    prefers_sms = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Timing preferences
    preferred_reminder_days = models.IntegerField(default=3, help_text="Days before due date")
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    
    # Status
    reminders_paused = models.BooleanField(default=False)
    pause_until = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes about client preferences")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'client_email']
    
    def __str__(self):
        return f"Preferences for {self.client_name} ({self.client_email})"
