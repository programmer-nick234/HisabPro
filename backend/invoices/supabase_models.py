"""
Supabase models for HisabPro application
Defines the structure for invoices, items, and payments
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional

class SupabaseInvoiceItem:
    def __init__(self, data: Dict[str, Any] = None):
        self.id = data.get('id') if data else None
        self.invoice_id = data.get('invoice_id') if data else None
        self.description = data.get('description', '')
        self.quantity = float(data.get('quantity', 0))
        self.unit_price = float(data.get('unit_price', 0))
        self.total = float(data.get('total', 0))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total': self.total,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupabaseInvoiceItem':
        return cls(data)
    
    def calculate_total(self):
        """Calculate total for this item"""
        self.total = self.quantity * self.unit_price
        return self.total

class SupabaseInvoice:
    def __init__(self, data: Dict[str, Any] = None):
        self.id = data.get('id') if data else None
        self.user_id = data.get('user_id') if data else None
        self.invoice_number = data.get('invoice_number', '')
        self.client_name = data.get('client_name', '')
        self.client_email = data.get('client_email', '')
        self.client_phone = data.get('client_phone', '')
        self.client_address = data.get('client_address', '')
        
        # Dates
        issue_date_str = data.get('issue_date')
        self.issue_date = issue_date_str if isinstance(issue_date_str, str) else None
        
        due_date_str = data.get('due_date')
        self.due_date = due_date_str if isinstance(due_date_str, str) else None
        
        # Financial data
        self.subtotal = float(data.get('subtotal', 0))
        self.tax_rate = float(data.get('tax_rate', 0))
        self.tax_amount = float(data.get('tax_amount', 0))
        self.total_amount = float(data.get('total_amount', 0))
        
        # Status and metadata
        self.status = data.get('status', 'pending')
        self.notes = data.get('notes', '')
        self.terms_conditions = data.get('terms_conditions', '')
        
        # Payment information
        self.payment_link = data.get('payment_link', '')
        self.payment_gateway = data.get('payment_gateway', '')
        self.payment_id = data.get('payment_id', '')
        
        # Timestamps
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        
        # Items (will be populated separately)
        self.items: List[SupabaseInvoiceItem] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'invoice_number': self.invoice_number,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_phone': self.client_phone,
            'client_address': self.client_address,
            'issue_date': self.issue_date,
            'due_date': self.due_date,
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'status': self.status,
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'payment_link': self.payment_link,
            'payment_gateway': self.payment_gateway,
            'payment_id': self.payment_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupabaseInvoice':
        return cls(data)
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total amounts"""
        # Calculate subtotal from items
        self.subtotal = sum(item.total for item in self.items)
        
        # Calculate tax
        self.tax_amount = (self.subtotal * self.tax_rate) / 100
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount
        
        return {
            'subtotal': self.subtotal,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount
        }
    
    def add_item(self, description: str, quantity: float, unit_price: float) -> SupabaseInvoiceItem:
        """Add an item to the invoice"""
        item = SupabaseInvoiceItem({
            'invoice_id': self.id,
            'description': description,
            'quantity': quantity,
            'unit_price': unit_price
        })
        item.calculate_total()
        self.items.append(item)
        return item
    
    def remove_item(self, item_id: str):
        """Remove an item from the invoice"""
        self.items = [item for item in self.items if item.id != item_id]
    
    def get_items(self) -> List[SupabaseInvoiceItem]:
        """Get all items for this invoice"""
        return self.items
    
    def set_items(self, items: List[SupabaseInvoiceItem]):
        """Set items for this invoice"""
        self.items = items
        # Recalculate totals
        self.calculate_totals()

class SupabasePayment:
    def __init__(self, data: Dict[str, Any] = None):
        self.id = data.get('id') if data else None
        self.invoice_id = data.get('invoice_id') if data else None
        self.amount = float(data.get('amount', 0))
        self.currency = data.get('currency', 'INR')
        self.payment_method = data.get('payment_method', '')
        self.payment_gateway = data.get('payment_gateway', '')
        self.payment_id = data.get('payment_id', '')
        self.status = data.get('status', 'pending')
        self.payment_date = data.get('payment_date')
        self.transaction_id = data.get('transaction_id', '')
        self.notes = data.get('notes', '')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_gateway': self.payment_gateway,
            'payment_id': self.payment_id,
            'status': self.status,
            'payment_date': self.payment_date,
            'transaction_id': self.transaction_id,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupabasePayment':
        return cls(data)
