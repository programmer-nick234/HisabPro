"""
Reminder System API Views for HisabPro Dashboard
Handles all reminder operations, templates, rules, and analytics
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
import logging

from .models import Invoice
from .reminder_models import (
    ReminderTemplate, ReminderRule, ReminderSchedule, 
    ReminderLog, ReminderAnalytics, ClientReminderPreference
)
from .reminder_service import reminder_service
from .reminder_serializers import (
    ReminderTemplateSerializer, ReminderRuleSerializer,
    ReminderScheduleSerializer, ReminderLogSerializer,
    ReminderAnalyticsSerializer, ClientReminderPreferenceSerializer,
    BulkReminderSerializer, CustomReminderSerializer
)

logger = logging.getLogger(__name__)


class ReminderTemplateListCreateView(generics.ListCreateAPIView):
    """Manage reminder templates"""
    serializer_class = ReminderTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ReminderTemplate.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReminderTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Individual reminder template operations"""
    serializer_class = ReminderTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ReminderTemplate.objects.filter(user=self.request.user)


class ReminderRuleListCreateView(generics.ListCreateAPIView):
    """Manage reminder rules"""
    serializer_class = ReminderRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ReminderRule.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReminderRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Individual reminder rule operations"""
    serializer_class = ReminderRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ReminderRule.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_manual_reminder(request, invoice_id):
    """Send a manual reminder for a specific invoice"""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        serializer = CustomReminderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Create a manual reminder schedule
        reminder_schedule = ReminderSchedule.objects.create(
            invoice=invoice,
            reminder_type='manual',
            scheduled_date=timezone.now(),
            send_email=data.get('send_email', True),
            send_sms=data.get('send_sms', False),
            custom_subject=data.get('subject', ''),
            custom_email_body=data.get('email_body', ''),
            custom_sms_message=data.get('sms_message', '')
        )
        
        # Send the reminder
        custom_message = {
            'subject': data.get('subject', ''),
            'email_body': data.get('email_body', ''),
            'sms_message': data.get('sms_message', '')
        }
        
        success, message = reminder_service.send_reminder(reminder_schedule, custom_message)
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'reminder_id': str(reminder_schedule.id)
            })
        else:
            return Response({
                'success': False,
                'error': message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error sending manual reminder: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to send reminder'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_bulk_reminders(request):
    """Send reminders to multiple invoices"""
    try:
        serializer = BulkReminderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        invoice_ids = data['invoice_ids']
        
        # Get invoices
        invoices = Invoice.objects.filter(
            id__in=invoice_ids,
            user=request.user,
            status__in=['pending', 'overdue']  # Only remind for unpaid invoices
        )
        
        results = {
            'total_invoices': len(invoice_ids),
            'found_invoices': invoices.count(),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for invoice in invoices:
            try:
                # Create manual reminder schedule
                reminder_schedule = ReminderSchedule.objects.create(
                    invoice=invoice,
                    reminder_type='manual',
                    scheduled_date=timezone.now(),
                    send_email=data.get('send_email', True),
                    send_sms=data.get('send_sms', False),
                    custom_subject=data.get('subject', ''),
                    custom_email_body=data.get('email_body', ''),
                    custom_sms_message=data.get('sms_message', '')
                )
                
                # Send reminder
                custom_message = {
                    'subject': data.get('subject', ''),
                    'email_body': data.get('email_body', ''),
                    'sms_message': data.get('sms_message', '')
                }
                
                success, message = reminder_service.send_reminder(reminder_schedule, custom_message)
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Invoice {invoice.invoice_number}: {message}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Invoice {invoice.invoice_number}: {str(e)}")
        
        return Response(results)
        
    except Exception as e:
        logger.error(f"Error sending bulk reminders: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to send bulk reminders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def schedule_invoice_reminders(request, invoice_id):
    """Schedule automatic reminders for an invoice"""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        # Get or use default rule
        rule_id = request.data.get('rule_id')
        if rule_id:
            rule = get_object_or_404(ReminderRule, id=rule_id, user=request.user)
        else:
            rule = reminder_service.get_applicable_rule(invoice)
        
        if not rule:
            return Response({
                'success': False,
                'error': 'No applicable reminder rule found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Cancel existing scheduled reminders
        ReminderSchedule.objects.filter(
            invoice=invoice,
            status='scheduled'
        ).update(status='cancelled')
        
        # Schedule new reminders
        scheduled_reminders = reminder_service.schedule_reminders_for_invoice(invoice, rule)
        
        return Response({
            'success': True,
            'message': f'Scheduled {len(scheduled_reminders)} reminders',
            'reminders': ReminderScheduleSerializer(scheduled_reminders, many=True).data
        })
        
    except Exception as e:
        logger.error(f"Error scheduling reminders: {str(e)}")
        return Response({
            'success': False,
            'error': 'Failed to schedule reminders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def invoice_reminder_status(request, invoice_id):
    """Get reminder status for an invoice"""
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
        
        # Get scheduled reminders
        scheduled_reminders = ReminderSchedule.objects.filter(
            invoice=invoice
        ).order_by('scheduled_date')
        
        # Get reminder logs
        reminder_logs = ReminderLog.objects.filter(
            invoice=invoice
        ).order_by('-sent_at')[:10]  # Last 10 reminders
        
        # Get applicable rule
        applicable_rule = reminder_service.get_applicable_rule(invoice)
        
        return Response({
            'invoice': {
                'id': str(invoice.id),
                'invoice_number': invoice.invoice_number,
                'client_name': invoice.client_name,
                'total_amount': invoice.total_amount,
                'due_date': invoice.due_date,
                'status': invoice.status,
                'reminder_count': invoice.reminder_count,
                'last_reminder_sent': invoice.last_reminder_sent
            },
            'applicable_rule': ReminderRuleSerializer(applicable_rule).data if applicable_rule else None,
            'scheduled_reminders': ReminderScheduleSerializer(scheduled_reminders, many=True).data,
            'reminder_history': ReminderLogSerializer(reminder_logs, many=True).data
        })
        
    except Exception as e:
        logger.error(f"Error getting reminder status: {str(e)}")
        return Response({
            'error': 'Failed to get reminder status'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def pause_client_reminders(request):
    """Pause reminders for a specific client"""
    try:
        client_email = request.data.get('client_email')
        pause_until = request.data.get('pause_until')  # Date string
        
        if not client_email:
            return Response({
                'error': 'client_email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create client preference
        client_pref, created = ClientReminderPreference.objects.get_or_create(
            user=request.user,
            client_email=client_email,
            defaults={
                'client_name': request.data.get('client_name', ''),
                'reminders_paused': True,
                'pause_until': datetime.strptime(pause_until, '%Y-%m-%d').date() if pause_until else None
            }
        )
        
        if not created:
            client_pref.reminders_paused = True
            client_pref.pause_until = datetime.strptime(pause_until, '%Y-%m-%d').date() if pause_until else None
            client_pref.save()
        
        # Cancel scheduled reminders for this client
        ReminderSchedule.objects.filter(
            invoice__user=request.user,
            invoice__client_email=client_email,
            status='scheduled'
        ).update(status='cancelled')
        
        return Response({
            'success': True,
            'message': f'Reminders paused for {client_email}' + (f' until {pause_until}' if pause_until else ' indefinitely')
        })
        
    except Exception as e:
        logger.error(f"Error pausing client reminders: {str(e)}")
        return Response({
            'error': 'Failed to pause reminders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reminder_dashboard(request):
    """Get reminder dashboard data"""
    try:
        user = request.user
        
        # Get overdue invoices
        overdue_invoices = Invoice.objects.filter(
            user=user,
            status__in=['pending', 'overdue'],
            due_date__lt=timezone.now().date()
        ).count()
        
        # Get upcoming reminders
        upcoming_reminders = ReminderSchedule.objects.filter(
            invoice__user=user,
            status='scheduled',
            scheduled_date__gte=timezone.now(),
            scheduled_date__lte=timezone.now() + timedelta(days=7)
        ).count()
        
        # Get recent reminder activity
        recent_logs = ReminderLog.objects.filter(
            invoice__user=user,
            sent_at__gte=timezone.now() - timedelta(days=30)
        )
        
        recent_stats = {
            'total_sent': recent_logs.count(),
            'email_sent': recent_logs.filter(channel__in=['email', 'both']).count(),
            'sms_sent': recent_logs.filter(channel__in=['sms', 'both']).count(),
            'successful': recent_logs.filter(result='success').count(),
            'payments_received': recent_logs.filter(payment_received=True).count()
        }
        
        # Get template performance
        template_performance = []
        templates = ReminderTemplate.objects.filter(user=user)
        for template in templates:
            logs = recent_logs.filter(reminder_schedule__reminder_template=template)
            total = logs.count()
            successful = logs.filter(payment_received=True).count()
            success_rate = (successful / total * 100) if total > 0 else 0
            
            template_performance.append({
                'template_name': template.name,
                'total_sent': total,
                'payments_received': successful,
                'success_rate': round(success_rate, 2)
            })
        
        # Sort by success rate
        template_performance.sort(key=lambda x: x['success_rate'], reverse=True)
        
        # Get invoices needing attention
        attention_invoices = Invoice.objects.filter(
            user=user,
            status__in=['pending', 'overdue'],
            due_date__lt=timezone.now().date()
        ).annotate(
            days_overdue=timezone.now().date() - models.F('due_date')
        ).order_by('-total_amount')[:10]
        
        return Response({
            'summary': {
                'overdue_invoices': overdue_invoices,
                'upcoming_reminders': upcoming_reminders,
                'recent_stats': recent_stats
            },
            'template_performance': template_performance[:5],  # Top 5 templates
            'attention_invoices': [
                {
                    'id': str(inv.id),
                    'invoice_number': inv.invoice_number,
                    'client_name': inv.client_name,
                    'total_amount': inv.total_amount,
                    'due_date': inv.due_date,
                    'days_overdue': (timezone.now().date() - inv.due_date).days,
                    'reminder_count': inv.reminder_count,
                    'last_reminder_sent': inv.last_reminder_sent
                }
                for inv in attention_invoices
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting reminder dashboard data: {str(e)}")
        return Response({
            'error': 'Failed to load dashboard data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reminder_analytics(request):
    """Get detailed reminder analytics"""
    try:
        user = request.user
        
        # Get date range from query params
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            # Default to last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate analytics
        analytics = reminder_service.generate_analytics(user, start_date, end_date)
        
        return Response(ReminderAnalyticsSerializer(analytics).data)
        
    except Exception as e:
        logger.error(f"Error getting reminder analytics: {str(e)}")
        return Response({
            'error': 'Failed to load analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientReminderPreferenceListCreateView(generics.ListCreateAPIView):
    """Manage client reminder preferences"""
    serializer_class = ClientReminderPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ClientReminderPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ClientReminderPreferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Individual client preference operations"""
    serializer_class = ClientReminderPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ClientReminderPreference.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_payment_received(request, reminder_log_id):
    """Mark that payment was received after a reminder"""
    try:
        reminder_log = get_object_or_404(
            ReminderLog, 
            id=reminder_log_id,
            invoice__user=request.user
        )
        
        # Update reminder log
        reminder_log.payment_received = True
        reminder_log.payment_received_date = timezone.now().date()
        reminder_log.save()
        
        # Update invoice status if needed
        invoice = reminder_log.invoice
        if request.data.get('mark_invoice_paid', False):
            invoice.status = 'paid'
            invoice.save()
        
        return Response({
            'success': True,
            'message': 'Payment marked as received'
        })
        
    except Exception as e:
        logger.error(f"Error marking payment received: {str(e)}")
        return Response({
            'error': 'Failed to mark payment received'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
