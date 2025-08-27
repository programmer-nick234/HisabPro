"""
Serializers for the Reminder System
"""

from rest_framework import serializers
from .models import Invoice
from .reminder_models import (
    ReminderTemplate, ReminderRule, ReminderSchedule,
    ReminderLog, ReminderAnalytics, ClientReminderPreference
)


class ReminderTemplateSerializer(serializers.ModelSerializer):
    """Serializer for reminder templates"""
    
    class Meta:
        model = ReminderTemplate
        fields = [
            'id', 'name', 'tone', 'stage', 'email_subject', 'email_body',
            'sms_message', 'include_pdf_attachment', 'include_payment_link',
            'include_payment_history', 'include_late_fees', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReminderRuleSerializer(serializers.ModelSerializer):
    """Serializer for reminder rules"""
    
    pre_due_template_name = serializers.CharField(source='pre_due_template.name', read_only=True)
    due_date_template_name = serializers.CharField(source='due_date_template.name', read_only=True)
    overdue_1_template_name = serializers.CharField(source='overdue_1_template.name', read_only=True)
    overdue_2_template_name = serializers.CharField(source='overdue_2_template.name', read_only=True)
    overdue_3_template_name = serializers.CharField(source='overdue_3_template.name', read_only=True)
    
    class Meta:
        model = ReminderRule
        fields = [
            'id', 'name', 'min_invoice_amount', 'max_invoice_amount',
            'days_before_due', 'days_after_due_1', 'days_after_due_2', 'days_after_due_3',
            'use_email', 'use_sms', 'pre_due_template', 'due_date_template',
            'overdue_1_template', 'overdue_2_template', 'overdue_3_template',
            'skip_weekends', 'skip_holidays', 'max_reminders', 'is_active',
            'pre_due_template_name', 'due_date_template_name', 'overdue_1_template_name',
            'overdue_2_template_name', 'overdue_3_template_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReminderScheduleSerializer(serializers.ModelSerializer):
    """Serializer for reminder schedules"""
    
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    client_name = serializers.CharField(source='invoice.client_name', read_only=True)
    template_name = serializers.CharField(source='reminder_template.name', read_only=True)
    rule_name = serializers.CharField(source='reminder_rule.name', read_only=True)
    
    class Meta:
        model = ReminderSchedule
        fields = [
            'id', 'invoice', 'reminder_rule', 'reminder_template', 'reminder_type',
            'scheduled_date', 'sent_date', 'status', 'send_email', 'send_sms',
            'custom_subject', 'custom_email_body', 'custom_sms_message',
            'email_sent', 'sms_sent', 'error_message', 'invoice_number',
            'client_name', 'template_name', 'rule_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sent_date', 'email_sent', 'sms_sent', 'error_message',
            'invoice_number', 'client_name', 'template_name', 'rule_name',
            'created_at', 'updated_at'
        ]


class ReminderLogSerializer(serializers.ModelSerializer):
    """Serializer for reminder logs"""
    
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    client_name = serializers.CharField(source='invoice.client_name', read_only=True)
    template_name = serializers.CharField(source='reminder_schedule.reminder_template.name', read_only=True)
    
    class Meta:
        model = ReminderLog
        fields = [
            'id', 'invoice', 'reminder_schedule', 'channel', 'result',
            'email_subject', 'email_body_preview', 'sms_message',
            'email_delivered', 'email_opened', 'email_clicked', 'sms_delivered',
            'client_responded', 'payment_received', 'payment_received_date',
            'error_details', 'sent_at', 'invoice_number', 'client_name', 'template_name'
        ]
        read_only_fields = [
            'id', 'sent_at', 'invoice_number', 'client_name', 'template_name'
        ]


class ReminderAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for reminder analytics"""
    
    best_template_name = serializers.CharField(source='best_performing_template.name', read_only=True)
    
    class Meta:
        model = ReminderAnalytics
        fields = [
            'id', 'period_start', 'period_end', 'total_reminders_sent',
            'email_reminders_sent', 'sms_reminders_sent', 'invoices_paid_after_reminder',
            'total_amount_collected', 'average_days_to_payment', 'best_performing_template',
            'best_template_success_rate', 'email_success_rate', 'sms_success_rate',
            'best_template_name', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'best_template_name', 'created_at', 'updated_at'
        ]


class ClientReminderPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for client reminder preferences"""
    
    class Meta:
        model = ClientReminderPreference
        fields = [
            'id', 'client_email', 'client_name', 'prefers_email', 'prefers_sms',
            'phone_number', 'preferred_reminder_days', 'timezone',
            'reminders_paused', 'pause_until', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomReminderSerializer(serializers.Serializer):
    """Serializer for custom/manual reminders"""
    
    subject = serializers.CharField(max_length=300, required=False, allow_blank=True)
    email_body = serializers.CharField(required=False, allow_blank=True)
    sms_message = serializers.CharField(max_length=500, required=False, allow_blank=True)
    send_email = serializers.BooleanField(default=True)
    send_sms = serializers.BooleanField(default=False)
    include_pdf = serializers.BooleanField(default=True)
    include_payment_link = serializers.BooleanField(default=True)


class BulkReminderSerializer(serializers.Serializer):
    """Serializer for bulk reminder operations"""
    
    invoice_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=100
    )
    subject = serializers.CharField(max_length=300, required=False, allow_blank=True)
    email_body = serializers.CharField(required=False, allow_blank=True)
    sms_message = serializers.CharField(max_length=500, required=False, allow_blank=True)
    send_email = serializers.BooleanField(default=True)
    send_sms = serializers.BooleanField(default=False)
    include_pdf = serializers.BooleanField(default=True)
    include_payment_link = serializers.BooleanField(default=True)


class InvoiceReminderSummarySerializer(serializers.ModelSerializer):
    """Serializer for invoice reminder summary"""
    
    days_overdue = serializers.SerializerMethodField()
    next_reminder_date = serializers.SerializerMethodField()
    last_reminder_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'client_email',
            'total_amount', 'due_date', 'status', 'reminder_count',
            'last_reminder_sent', 'days_overdue', 'next_reminder_date',
            'last_reminder_type'
        ]
    
    def get_days_overdue(self, obj):
        if obj.due_date and obj.status != 'paid':
            from django.utils import timezone
            today = timezone.now().date()
            if today > obj.due_date:
                return (today - obj.due_date).days
        return 0
    
    def get_next_reminder_date(self, obj):
        next_reminder = ReminderSchedule.objects.filter(
            invoice=obj,
            status='scheduled'
        ).order_by('scheduled_date').first()
        
        return next_reminder.scheduled_date if next_reminder else None
    
    def get_last_reminder_type(self, obj):
        last_log = ReminderLog.objects.filter(
            invoice=obj
        ).order_by('-sent_at').first()
        
        return last_log.reminder_schedule.get_reminder_type_display() if last_log else None
