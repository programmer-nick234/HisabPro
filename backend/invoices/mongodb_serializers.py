"""
MongoDB Serializers for Invoice System
"""

from rest_framework import serializers
from .mongodb_models import MongoDBInvoice, MongoDBInvoiceItem
from datetime import datetime

class MongoDBInvoiceItemSerializer(serializers.Serializer):
    """Serializer for MongoDB Invoice Item"""
    
    id = serializers.CharField(source='_id', read_only=True)
    invoice_id = serializers.CharField(write_only=True)
    description = serializers.CharField(max_length=500)
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    def create(self, validated_data):
        """Create invoice item"""
        item = MongoDBInvoiceItem()
        item.invoice_id = validated_data['invoice_id']
        item.description = validated_data['description']
        item.quantity = validated_data['quantity']
        item.unit_price = validated_data['unit_price']
        item.total = item.quantity * item.unit_price
        item.save()
        return item
    
    def update(self, instance, validated_data):
        """Update invoice item"""
        instance.description = validated_data.get('description', instance.description)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.unit_price = validated_data.get('unit_price', instance.unit_price)
        instance.total = instance.quantity * instance.unit_price
        instance.save()
        return instance

class MongoDBInvoiceSerializer(serializers.Serializer):
    """Serializer for MongoDB Invoice"""
    
    id = serializers.CharField(source='_id', read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False)
    invoice_number = serializers.CharField(max_length=20, read_only=True)
    client_name = serializers.CharField(max_length=200)
    client_email = serializers.EmailField()
    client_phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    client_address = serializers.CharField(required=False, allow_blank=True)
    issue_date = serializers.DateField()
    due_date = serializers.DateField()
    status = serializers.CharField(max_length=20, default='pending')
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    tax_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    terms_conditions = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    items = MongoDBInvoiceItemSerializer(many=True, read_only=True)
    
    def create(self, validated_data):
        """Create invoice with items"""
        # Get user_id from context or validated_data
        user_id = validated_data.get('user_id')
        if not user_id and self.context.get('user_id'):
            user_id = self.context['user_id']
        
        if not user_id:
            raise serializers.ValidationError("user_id is required")
        
        # Generate invoice number
        last_invoice = MongoDBInvoice.get_by_user(user_id, limit=1)
        if last_invoice:
            try:
                last_number = int(last_invoice[0].invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        invoice_number = f"INV-{user_id:04d}-{new_number:04d}"
        
        # Create invoice
        invoice = MongoDBInvoice()
        invoice.user_id = user_id
        invoice.invoice_number = invoice_number
        invoice.client_name = validated_data['client_name']
        invoice.client_email = validated_data['client_email']
        invoice.client_phone = validated_data.get('client_phone', '')
        invoice.client_address = validated_data.get('client_address', '')
        invoice.issue_date = validated_data['issue_date']
        invoice.due_date = validated_data['due_date']
        invoice.status = validated_data.get('status', 'pending')
        invoice.tax_rate = validated_data.get('tax_rate', 18.0)
        invoice.notes = validated_data.get('notes', '')
        invoice.terms_conditions = validated_data.get('terms_conditions', '')
        
        # Save invoice first to get ID
        invoice.save()
        
        # Add items if provided
        items_data = self.context.get('items', [])
        if not items_data and hasattr(self, 'initial_data') and 'items' in self.initial_data:
            items_data = self.initial_data['items']
        
        for item_data in items_data:
            item = MongoDBInvoiceItem()
            item.invoice_id = str(invoice._id)
            item.description = item_data['description']
            item.quantity = item_data['quantity']
            item.unit_price = float(item_data['unit_price'])
            item.total = float(item_data['quantity']) * float(item_data['unit_price'])
            item.save()
        
        # Calculate totals
        invoice.calculate_totals()
        invoice.save()
        
        return invoice
    
    def update(self, instance, validated_data):
        """Update invoice"""
        instance.client_name = validated_data.get('client_name', instance.client_name)
        instance.client_email = validated_data.get('client_email', instance.client_email)
        instance.client_phone = validated_data.get('client_phone', instance.client_phone)
        instance.client_address = validated_data.get('client_address', instance.client_address)
        instance.issue_date = validated_data.get('issue_date', instance.issue_date)
        instance.due_date = validated_data.get('due_date', instance.due_date)
        instance.status = validated_data.get('status', instance.status)
        instance.tax_rate = validated_data.get('tax_rate', instance.tax_rate)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.terms_conditions = validated_data.get('terms_conditions', instance.terms_conditions)
        
        # Update items if provided
        items_data = self.context.get('items')
        if items_data is not None:
            # Delete existing items
            for item in instance.get_items():
                item.delete_by_id(item._id)
            
            # Create new items
            for item_data in items_data:
                item = MongoDBInvoiceItem()
                item.invoice_id = str(instance._id)
                item.description = item_data['description']
                item.quantity = item_data['quantity']
                item.unit_price = item_data['unit_price']
                item.total = item.quantity * item.unit_price
                item.save()
        
        # Recalculate totals
        instance.calculate_totals()
        instance.save()
        
        return instance

class MongoDBInvoiceCreateSerializer(serializers.Serializer):
    """Serializer for creating invoices"""
    
    client_name = serializers.CharField(max_length=200)
    client_email = serializers.EmailField()
    client_phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    client_address = serializers.CharField(required=False, allow_blank=True)
    issue_date = serializers.DateField()
    due_date = serializers.DateField()
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    notes = serializers.CharField(required=False, allow_blank=True)
    terms_conditions = serializers.CharField(required=False, allow_blank=True)
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_items(self, value):
        """Validate items data"""
        for item in value:
            if not item.get('description'):
                raise serializers.ValidationError("Item description is required")
            if not item.get('quantity') or item['quantity'] <= 0:
                raise serializers.ValidationError("Item quantity must be greater than 0")
            if not item.get('unit_price') or item['unit_price'] <= 0:
                raise serializers.ValidationError("Item unit price must be greater than 0")
        return value

class MongoDBInvoiceSummarySerializer(serializers.Serializer):
    """Serializer for invoice summary"""
    
    total_invoices = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_invoices = serializers.IntegerField()
    paid_invoices = serializers.IntegerField()
    overdue_invoices = serializers.IntegerField()
    total_pending_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_overdue_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
