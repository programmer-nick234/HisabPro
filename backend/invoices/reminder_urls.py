"""
URL patterns for the Reminder System
"""

from django.urls import path
from . import reminder_views

urlpatterns = [
    # Reminder Templates
    path('reminder-templates/', reminder_views.ReminderTemplateListCreateView.as_view(), name='reminder-templates'),
    path('reminder-templates/<uuid:pk>/', reminder_views.ReminderTemplateDetailView.as_view(), name='reminder-template-detail'),
    
    # Reminder Rules
    path('reminder-rules/', reminder_views.ReminderRuleListCreateView.as_view(), name='reminder-rules'),
    path('reminder-rules/<uuid:pk>/', reminder_views.ReminderRuleDetailView.as_view(), name='reminder-rule-detail'),
    
    # Manual Reminders
    path('invoices/<uuid:invoice_id>/send-reminder/', reminder_views.send_manual_reminder, name='send-manual-reminder'),
    path('send-bulk-reminders/', reminder_views.send_bulk_reminders, name='send-bulk-reminders'),
    
    # Reminder Scheduling
    path('invoices/<uuid:invoice_id>/schedule-reminders/', reminder_views.schedule_invoice_reminders, name='schedule-reminders'),
    path('invoices/<uuid:invoice_id>/reminder-status/', reminder_views.invoice_reminder_status, name='reminder-status'),
    
    # Client Management
    path('pause-client-reminders/', reminder_views.pause_client_reminders, name='pause-client-reminders'),
    path('client-preferences/', reminder_views.ClientReminderPreferenceListCreateView.as_view(), name='client-preferences'),
    path('client-preferences/<uuid:pk>/', reminder_views.ClientReminderPreferenceDetailView.as_view(), name='client-preference-detail'),
    
    # Dashboard & Analytics
    path('reminder-dashboard/', reminder_views.reminder_dashboard, name='reminder-dashboard'),
    path('reminder-analytics/', reminder_views.reminder_analytics, name='reminder-analytics'),
    
    # Payment Tracking
    path('reminder-logs/<uuid:reminder_log_id>/mark-payment/', reminder_views.mark_payment_received, name='mark-payment-received'),
]
