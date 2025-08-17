"""
MongoDB Models for Invoice System
These models work directly with MongoDB using PyMongo
"""

from datetime import datetime, date
from decimal import Decimal
from bson import ObjectId
from django.contrib.auth.models import User
from django.conf import settings
from lib.mongodb import mongodb_service
import logging

logger = logging.getLogger(__name__)

class MongoDBInvoice:
    """MongoDB Invoice Model"""
    
    def __init__(self, data=None):
        if data:
            self._id = data.get('_id')
            self.user_id = data.get('user_id')
            self.invoice_number = data.get('invoice_number')
            self.client_name = data.get('client_name')
            self.client_email = data.get('client_email')
            self.client_phone = data.get('client_phone', '')
            self.client_address = data.get('client_address', '')
            self.issue_date = data.get('issue_date')
            self.due_date = data.get('due_date')
            self.status = data.get('status', 'pending')
            self.subtotal = data.get('subtotal', 0.0)
            self.tax_rate = data.get('tax_rate', 18.0)
            self.tax_amount = data.get('tax_amount', 0.0)
            self.total_amount = data.get('total_amount', 0.0)
            self.notes = data.get('notes', '')
            self.terms_conditions = data.get('terms_conditions', '')
            self.razorpay_payment_link = data.get('razorpay_payment_link', '')
            self.razorpay_order_id = data.get('razorpay_order_id', '')
            self.created_at = data.get('created_at')
            self.updated_at = data.get('updated_at')
        else:
            self._id = None
            self.user_id = None
            self.invoice_number = None
            self.client_name = None
            self.client_email = None
            self.client_phone = ''
            self.client_address = ''
            self.issue_date = None
            self.due_date = None
            self.status = 'pending'
            self.subtotal = 0.0
            self.tax_rate = 18.0
            self.tax_amount = 0.0
            self.total_amount = 0.0
            self.notes = ''
            self.terms_conditions = ''
            self.razorpay_payment_link = ''
            self.razorpay_order_id = ''
            self.created_at = None
            self.updated_at = None
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        data = {
            'user_id': self.user_id,
            'invoice_number': self.invoice_number,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_phone': self.client_phone,
            'client_address': self.client_address,
            'issue_date': self.issue_date.isoformat() if isinstance(self.issue_date, date) else self.issue_date,
            'due_date': self.due_date.isoformat() if isinstance(self.due_date, date) else self.due_date,
            'status': self.status,
            'subtotal': float(self.subtotal),
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'razorpay_payment_link': self.razorpay_payment_link,
            'razorpay_order_id': self.razorpay_order_id,
            'updated_at': datetime.utcnow()
        }
        
        if self.created_at:
            data['created_at'] = self.created_at
        else:
            data['created_at'] = datetime.utcnow()
            
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        return cls(data)
    
    def save(self):
        """Save invoice to MongoDB"""
        try:
            data = self.to_dict()
            
            if self._id:
                # Update existing invoice
                result = mongodb_service.db.invoices.update_one(
                    {'_id': ObjectId(self._id)},
                    {'$set': data}
                )
                return result.modified_count > 0
            else:
                # Create new invoice
                result = mongodb_service.db.invoices.insert_one(data)
                self._id = str(result.inserted_id)
                return True
        except Exception as e:
            logger.error(f"Error saving invoice: {str(e)}")
            raise
    
    @classmethod
    def get_by_id(cls, invoice_id):
        """Get invoice by ID"""
        try:
            data = mongodb_service.db.invoices.find_one({'_id': ObjectId(invoice_id)})
            if data:
                data['_id'] = str(data['_id'])
                return cls.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Error getting invoice by ID: {str(e)}")
            return None
    
    @classmethod
    def get_by_user(cls, user_id, limit=20, skip=0, page=1, page_size=20, status=None, search=None):
        """Get invoices for a user with filtering and pagination"""
        try:
            # Convert user_id to int if it's not already
            user_id = int(user_id)
            query = {'user_id': user_id}
            
            # Add status filter
            if status and status != 'all':
                query['status'] = status
            
            # Add search filter
            if search:
                query['$or'] = [
                    {'invoice_number': {'$regex': search, '$options': 'i'}},
                    {'client_name': {'$regex': search, '$options': 'i'}},
                    {'client_email': {'$regex': search, '$options': 'i'}}
                ]
            
            cursor = mongodb_service.db.invoices.find(query).sort('created_at', -1)
            
            # Handle pagination
            if page and page_size:
                skip = (page - 1) * page_size
                cursor = cursor.skip(skip).limit(page_size)
            elif skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            invoices = []
            for data in cursor:
                data['_id'] = str(data['_id'])
                invoices.append(cls.from_dict(data))
            
            return invoices
        except Exception as e:
            logger.error(f"Error getting user invoices: {str(e)}")
            return []
    
    @classmethod
    def delete_by_id(cls, invoice_id):
        """Delete invoice by ID"""
        try:
            # Delete invoice items first
            mongodb_service.db.invoice_items.delete_many({'invoice_id': invoice_id})
            
            # Delete invoice
            result = mongodb_service.db.invoices.delete_one({'_id': ObjectId(invoice_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting invoice: {str(e)}")
            return False
    
    @classmethod
    def get_summary(cls, user_id):
        """Get invoice summary for user"""
        try:
            # Convert user_id to int if it's not already
            user_id = int(user_id)
            
            pipeline = [
                {'$match': {'user_id': user_id}},
                {'$group': {
                    '_id': None,
                    'total_invoices': {'$sum': 1},
                    'total_amount': {'$sum': '$total_amount'},
                    'pending_invoices': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'pending']}, 1, 0]}
                    },
                    'paid_invoices': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'paid']}, 1, 0]}
                    },
                    'overdue_invoices': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'overdue']}, 1, 0]}
                    },
                    'total_pending_amount': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'pending']}, '$total_amount', 0]}
                    },
                    'total_paid_amount': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'paid']}, '$total_amount', 0]}
                    },
                    'total_overdue_amount': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'overdue']}, '$total_amount', 0]}
                    }
                }}
            ]
            
            logger.info(f"Running aggregation pipeline for user_id: {user_id}")
            result = list(mongodb_service.db.invoices.aggregate(pipeline))
            logger.info(f"Aggregation result: {result}")
            
            if result:
                return result[0]
            else:
                return {
                    'total_invoices': 0,
                    'total_amount': 0,
                    'pending_invoices': 0,
                    'paid_invoices': 0,
                    'overdue_invoices': 0,
                    'total_pending_amount': 0,
                    'total_paid_amount': 0,
                    'total_overdue_amount': 0
                }
        except Exception as e:
            logger.error(f"Error getting invoice summary: {str(e)}")
            return {
                'total_invoices': 0,
                'total_amount': 0,
                'pending_invoices': 0,
                'paid_invoices': 0,
                'overdue_invoices': 0,
                'total_pending_amount': 0,
                'total_paid_amount': 0,
                'total_overdue_amount': 0
            }
    
    def calculate_totals(self):
        """Calculate invoice totals"""
        self.subtotal = sum(item.total for item in self.get_items())
        self.tax_amount = (float(self.subtotal) * float(self.tax_rate)) / 100
        self.total_amount = float(self.subtotal) + float(self.tax_amount)
    
    def get_items(self):
        """Get invoice items"""
        return MongoDBInvoiceItem.get_by_invoice(str(self._id))
    
    def add_item(self, description, quantity, unit_price):
        """Add item to invoice"""
        item = MongoDBInvoiceItem()
        item.invoice_id = str(self._id)
        item.description = description
        item.quantity = quantity
        item.unit_price = float(unit_price)
        item.total = float(quantity) * float(unit_price)
        item.save()
        return item

class MongoDBInvoiceItem:
    """MongoDB Invoice Item Model"""
    
    def __init__(self, data=None):
        if data:
            self._id = data.get('_id')
            self.invoice_id = data.get('invoice_id')
            self.description = data.get('description')
            self.quantity = data.get('quantity', 1)
            self.unit_price = data.get('unit_price', 0.0)
            self.total = data.get('total', 0.0)
        else:
            self._id = None
            self.invoice_id = None
            self.description = None
            self.quantity = 1
            self.unit_price = 0.0
            self.total = 0.0
    
    def to_dict(self):
        """Convert to dictionary for MongoDB storage"""
        return {
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total': float(self.total)
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary"""
        return cls(data)
    
    def save(self):
        """Save invoice item to MongoDB"""
        try:
            data = self.to_dict()
            
            if self._id:
                # Update existing item
                result = mongodb_service.db.invoice_items.update_one(
                    {'_id': ObjectId(self._id)},
                    {'$set': data}
                )
                return result.modified_count > 0
            else:
                # Create new item
                result = mongodb_service.db.invoice_items.insert_one(data)
                self._id = str(result.inserted_id)
                return True
        except Exception as e:
            logger.error(f"Error saving invoice item: {str(e)}")
            raise
    
    @classmethod
    def get_by_invoice(cls, invoice_id):
        """Get items for an invoice"""
        try:
            cursor = mongodb_service.db.invoice_items.find({'invoice_id': invoice_id})
            items = []
            for data in cursor:
                data['_id'] = str(data['_id'])
                items.append(cls.from_dict(data))
            return items
        except Exception as e:
            logger.error(f"Error getting invoice items: {str(e)}")
            return []
    
    @classmethod
    def delete_by_id(cls, item_id):
        """Delete invoice item by ID"""
        try:
            result = mongodb_service.db.invoice_items.delete_one({'_id': ObjectId(item_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting invoice item: {str(e)}")
            return False
    
    @classmethod
    def delete_by_invoice_id(cls, invoice_id):
        """Delete all items for an invoice"""
        try:
            result = mongodb_service.db.invoice_items.delete_many({'invoice_id': invoice_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting invoice items: {str(e)}")
            return False
