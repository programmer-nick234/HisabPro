"""
MongoDB service layer for HisabPro application
Handles MongoDB operations for invoices, users, and payments
"""

import pymongo
from django.conf import settings
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        self.client = None
        self.db = None
        self._connected = False
    
    def connect(self):
        """Connect to MongoDB Atlas"""
        if self._connected:
            return
            
        try:
            if not settings.MONGODB_URI:
                logger.warning("MONGODB_URI not configured. MongoDB features will be disabled.")
                return
                
            self.client = pymongo.MongoClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DATABASE]
            # Test the connection
            self.client.admin.command('ping')
            self._connected = True
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self._connected = False
            # Don't raise the exception, just log it
            logger.warning("MongoDB connection failed. Application will continue without MongoDB features.")
    
    def _ensure_connected(self):
        """Ensure MongoDB is connected before operations"""
        if not self._connected:
            self.connect()
        return self._connected
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    # User Profile Operations
    def create_user_profile(self, user_id, profile_data):
        """Create a new user profile in MongoDB"""
        if not self._ensure_connected():
            return None
            
        try:
            profile_data['user_id'] = user_id
            profile_data['created_at'] = datetime.utcnow()
            profile_data['updated_at'] = datetime.utcnow()
            
            result = self.db.user_profiles.insert_one(profile_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            raise
    
    def get_user_profile(self, user_id):
        """Get user profile by user_id"""
        if not self._ensure_connected():
            return None
            
        try:
            profile = self.db.user_profiles.find_one({'user_id': user_id})
            if profile:
                profile['_id'] = str(profile['_id'])
            return profile
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            raise
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile"""
        if not self._ensure_connected():
            return False
            
        try:
            profile_data['updated_at'] = datetime.utcnow()
            result = self.db.user_profiles.update_one(
                {'user_id': user_id},
                {'$set': profile_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise
    
    # Invoice Operations
    def create_invoice(self, invoice_data):
        """Create a new invoice in MongoDB"""
        if not self._ensure_connected():
            return None
            
        try:
            invoice_data['created_at'] = datetime.utcnow()
            invoice_data['updated_at'] = datetime.utcnow()
            
            result = self.db.invoices.insert_one(invoice_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating invoice: {str(e)}")
            raise
    
    def get_invoice(self, invoice_id):
        """Get invoice by ID"""
        if not self._ensure_connected():
            return None
            
        try:
            invoice = self.db.invoices.find_one({'_id': ObjectId(invoice_id)})
            if invoice:
                invoice['_id'] = str(invoice['_id'])
            return invoice
        except Exception as e:
            logger.error(f"Error getting invoice: {str(e)}")
            raise
    
    def get_user_invoices(self, user_id, limit=20, skip=0):
        """Get invoices for a specific user"""
        if not self._ensure_connected():
            return []
            
        try:
            cursor = self.db.invoices.find(
                {'user_id': user_id}
            ).sort('created_at', -1).skip(skip).limit(limit)
            
            invoices = []
            for invoice in cursor:
                invoice['_id'] = str(invoice['_id'])
                invoices.append(invoice)
            
            return invoices
        except Exception as e:
            logger.error(f"Error getting user invoices: {str(e)}")
            raise
    
    def update_invoice(self, invoice_id, invoice_data):
        """Update invoice"""
        if not self._ensure_connected():
            return False
            
        try:
            invoice_data['updated_at'] = datetime.utcnow()
            result = self.db.invoices.update_one(
                {'_id': ObjectId(invoice_id)},
                {'$set': invoice_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating invoice: {str(e)}")
            raise
    
    def delete_invoice(self, invoice_id):
        """Delete invoice"""
        if not self._ensure_connected():
            return False
            
        try:
            result = self.db.invoices.delete_one({'_id': ObjectId(invoice_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting invoice: {str(e)}")
            raise
    
    # Invoice Item Operations
    def create_invoice_item(self, item_data):
        """Create a new invoice item"""
        if not self._ensure_connected():
            return None
            
        try:
            result = self.db.invoice_items.insert_one(item_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating invoice item: {str(e)}")
            raise
    
    def get_invoice_items(self, invoice_id):
        """Get all items for an invoice"""
        if not self._ensure_connected():
            return []
            
        try:
            cursor = self.db.invoice_items.find({'invoice_id': invoice_id})
            items = []
            for item in cursor:
                item['_id'] = str(item['_id'])
                items.append(item)
            return items
        except Exception as e:
            logger.error(f"Error getting invoice items: {str(e)}")
            raise
    
    def update_invoice_item(self, item_id, item_data):
        """Update invoice item"""
        if not self._ensure_connected():
            return False
            
        try:
            result = self.db.invoice_items.update_one(
                {'_id': ObjectId(item_id)},
                {'$set': item_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating invoice item: {str(e)}")
            raise
    
    def delete_invoice_item(self, item_id):
        """Delete invoice item"""
        if not self._ensure_connected():
            return False
            
        try:
            result = self.db.invoice_items.delete_one({'_id': ObjectId(item_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting invoice item: {str(e)}")
            raise
    
    # Payment Operations
    def create_payment(self, payment_data):
        """Create a new payment"""
        if not self._ensure_connected():
            return None
            
        try:
            payment_data['payment_date'] = datetime.utcnow()
            result = self.db.payments.insert_one(payment_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            raise
    
    def get_invoice_payments(self, invoice_id):
        """Get all payments for an invoice"""
        if not self._ensure_connected():
            return []
            
        try:
            cursor = self.db.payments.find({'invoice_id': invoice_id})
            payments = []
            for payment in cursor:
                payment['_id'] = str(payment['_id'])
                payments.append(payment)
            return payments
        except Exception as e:
            logger.error(f"Error getting invoice payments: {str(e)}")
            raise
    
    # Utility Methods
    def get_invoice_count(self, user_id):
        """Get total invoice count for a user"""
        if not self._ensure_connected():
            return 0
            
        try:
            return self.db.invoices.count_documents({'user_id': user_id})
        except Exception as e:
            logger.error(f"Error getting invoice count: {str(e)}")
            raise
    
    def search_invoices(self, user_id, query, limit=20):
        """Search invoices by client name or invoice number"""
        if not self._ensure_connected():
            return []
            
        try:
            cursor = self.db.invoices.find({
                'user_id': user_id,
                '$or': [
                    {'client_name': {'$regex': query, '$options': 'i'}},
                    {'invoice_number': {'$regex': query, '$options': 'i'}}
                ]
            }).sort('created_at', -1).limit(limit)
            
            invoices = []
            for invoice in cursor:
                invoice['_id'] = str(invoice['_id'])
                invoices.append(invoice)
            
            return invoices
        except Exception as e:
            logger.error(f"Error searching invoices: {str(e)}")
            raise

# Global MongoDB service instance
mongodb_service = MongoDBService()
