"""
Supabase serializers for HisabPro application
Handles data serialization for invoices, items, and payments
"""

from rest_framework import serializers
from .supabase_models import SupabaseInvoice, SupabaseInvoiceItem, SupabasePayment
from typing import List, Dict, Any

class SupabaseInvoiceItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    invoice_id = serializers.CharField(required=False)
    description = serializers.CharField(max_length=500)
    quantity = serializers.FloatField(min_value=0)
    unit_price = serializers.FloatField(min_value=0)
    total = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def create(self, validated_data):
        """Create a new invoice item"""
        item = SupabaseInvoiceItem(validated_data)
        item.calculate_total()
        return item
    
    def update(self, instance, validated_data):
        """Update an existing invoice item"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.calculate_total()
        return instance

class SupabaseInvoiceSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.IntegerField(required=False)
    invoice_number = serializers.CharField(max_length=50)
    client_name = serializers.CharField(max_length=200)
    client_email = serializers.EmailField(required=False, allow_blank=True)
    client_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    client_address = serializers.CharField(required=False, allow_blank=True)
    issue_date = serializers.DateField(required=False)
    due_date = serializers.DateField(required=False)
    subtotal = serializers.FloatField(min_value=0)
    tax_rate = serializers.FloatField(min_value=0, max_value=100)
    tax_amount = serializers.FloatField(min_value=0)
    total_amount = serializers.FloatField(min_value=0)
    status = serializers.ChoiceField(choices=['pending', 'paid', 'overdue', 'cancelled'], default='pending')
    notes = serializers.CharField(required=False, allow_blank=True)
    terms_conditions = serializers.CharField(required=False, allow_blank=True)
    payment_link = serializers.CharField(required=False, allow_blank=True)
    payment_gateway = serializers.CharField(required=False, allow_blank=True)
    payment_id = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    # Items will be handled separately
    items = SupabaseInvoiceItemSerializer(many=True, required=False)
    
    def create(self, validated_data):
        """Create a new invoice"""
        # Extract items data
        items_data = validated_data.pop('items', [])
        
        # Get user_id from context
        user_id = self.context.get('user_id')
        if user_id:
            validated_data['user_id'] = user_id
        
        # Create invoice
        invoice = SupabaseInvoice(validated_data)
        
        # Add items if provided
        if items_data:
            for item_data in items_data:
                item_data['invoice_id'] = invoice.id
                item = SupabaseInvoiceItem(item_data)
                item.calculate_total()
                invoice.items.append(item)
            
            # Recalculate totals
            invoice.calculate_totals()
        
        return invoice
    
    def update(self, instance, validated_data):
        """Update an existing invoice"""
        # Extract items data
        items_data = validated_data.pop('items', None)
        
        # Update invoice fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update items if provided
        if items_data is not None:
            instance.items = []
            for item_data in items_data:
                item_data['invoice_id'] = instance.id
                item = SupabaseInvoiceItem(item_data)
                item.calculate_total()
                instance.items.append(item)
            
            # Recalculate totals
            instance.calculate_totals()
        
        return instance

class SupabasePaymentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    invoice_id = serializers.CharField()
    amount = serializers.FloatField(min_value=0)
    currency = serializers.CharField(max_length=3, default='INR')
    payment_method = serializers.CharField(max_length=50, required=False, allow_blank=True)
    payment_gateway = serializers.CharField(max_length=50, required=False, allow_blank=True)
    payment_id = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=['pending', 'completed', 'failed', 'refunded'], default='pending')
    payment_date = serializers.DateTimeField(read_only=True)
    transaction_id = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def create(self, validated_data):
        """Create a new payment"""
        payment = SupabasePayment(validated_data)
        return payment
    
    def update(self, instance, validated_data):
        """Update an existing payment"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return instance

class InvoiceSummarySerializer(serializers.Serializer):
    """Serializer for invoice summary data"""
    total_invoices = serializers.IntegerField()
    paid_invoices = serializers.IntegerField()
    pending_invoices = serializers.IntegerField()
    total_amount = serializers.FloatField()
    paid_amount = serializers.FloatField()
    pending_amount = serializers.FloatField()

class InvoiceListSerializer(serializers.Serializer):
    """Serializer for invoice list with pagination"""
    invoices = SupabaseInvoiceSerializer(many=True)
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
