from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Invoice, InvoiceItem, Payment
from auth_app.serializers import UserSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total']


class InvoiceItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'payment_date', 'payment_method', 'transaction_id', 'status', 'notes']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'user', 'client_name', 'client_email', 'client_phone', 'client_address',
            'issue_date', 'due_date', 'status', 'subtotal', 'tax_rate', 'tax_amount', 'total_amount',
            'notes', 'terms_conditions', 'razorpay_payment_link', 'last_reminder_sent', 'reminder_count',
            'created_at', 'updated_at', 'items', 'payments'
        ]
        read_only_fields = ['id', 'invoice_number', 'subtotal', 'tax_amount', 'total_amount', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemCreateSerializer(many=True)
    
    class Meta:
        model = Invoice
        fields = [
            'client_name', 'client_email', 'client_phone', 'client_address',
            'issue_date', 'due_date', 'tax_rate', 'notes', 'terms_conditions', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Ensure user is set from context
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            validated_data['user'] = user
        
        # Create invoice without items first (invoice number will be auto-generated in save())
        try:
            invoice = Invoice.objects.create(**validated_data)
        except Exception as e:
            raise ValidationError(f"Failed to create invoice: {str(e)}")
        
        # Create invoice items if provided
        if items_data:
            try:
                for item_data in items_data:
                    InvoiceItem.objects.create(invoice=invoice, **item_data)
            except Exception as e:
                # If item creation fails, delete the invoice and re-raise
                invoice.delete()
                raise ValidationError(f"Failed to create invoice items: {str(e)}")
        
        # Recalculate totals after items are created
        try:
            invoice.calculate_totals()
            invoice.save()
        except Exception as e:
            # Log error but don't fail the creation
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to calculate totals for invoice {invoice.id}: {str(e)}")
        
        return invoice
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update invoice items
        if items_data:
            # Delete existing items
            instance.items.all().delete()
            
            # Create new items
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
        
        return instance


class InvoiceSummarySerializer(serializers.Serializer):
    total_invoices = serializers.IntegerField()
    pending_invoices = serializers.IntegerField()
    paid_invoices = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    total_pending_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_paid_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_overdue_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class RazorpayPaymentLinkSerializer(serializers.Serializer):
    payment_link = serializers.URLField()
    order_id = serializers.CharField()


class SendReminderSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)
