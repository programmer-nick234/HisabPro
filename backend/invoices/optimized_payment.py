"""
Optimized Payment System for HisabPro
Multiple payment gateways with fallback and caching
"""

import logging
import json
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from enum import Enum

import stripe
import razorpay
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

class PaymentGateway(Enum):
    RAZORPAY = "razorpay"
    STRIPE = "stripe"
    PAYPAL = "paypal"

class OptimizedPaymentSystem:
    """Optimized payment system with multiple gateways"""
    
    def __init__(self):
        self.gateways = {}
        self.cache_timeout = 300  # 5 minutes
        self._initialize_gateways()
    
    def _initialize_gateways(self):
        """Initialize payment gateways"""
        # Razorpay
        if hasattr(settings, 'RAZORPAY_KEY_ID') and hasattr(settings, 'RAZORPAY_KEY_SECRET'):
            self.gateways[PaymentGateway.RAZORPAY] = {
                'client': razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)),
                'enabled': True,
                'priority': 1
            }
            logger.info("✅ Razorpay initialized")
        
        # Stripe
        if hasattr(settings, 'STRIPE_SECRET_KEY'):
            stripe.api_key = settings.STRIPE_SECRET_KEY
            self.gateways[PaymentGateway.STRIPE] = {
                'client': stripe,
                'enabled': True,
                'priority': 2
            }
            logger.info("✅ Stripe initialized")
    
    def get_available_gateways(self) -> List[PaymentGateway]:
        """Get list of available payment gateways"""
        return [gateway for gateway, config in self.gateways.items() 
                if config.get('enabled', False)]
    
    def get_best_gateway(self, currency: str = "INR") -> PaymentGateway:
        """Get best gateway for currency"""
        available_gateways = self.get_available_gateways()
        
        if not available_gateways:
            raise ValueError("No payment gateways available")
        
        if currency == "INR" and PaymentGateway.RAZORPAY in available_gateways:
            return PaymentGateway.RAZORPAY
        elif PaymentGateway.STRIPE in available_gateways:
            return PaymentGateway.STRIPE
        else:
            return available_gateways[0]
    
    def create_payment_link(self, invoice_id: str, amount: Decimal, currency: str = "INR", 
                          description: str = "", customer_email: str = "") -> Dict[str, Any]:
        """Create payment link with fallback"""
        logger.info(f"Creating payment link for invoice {invoice_id}")
        
        # Try primary gateway
        primary_gateway = self.get_best_gateway(currency)
        
        try:
            result = self._create_payment_link_gateway(
                primary_gateway, invoice_id, amount, currency, description, customer_email
            )
            if result['success']:
                return result
        except Exception as e:
            logger.warning(f"Primary gateway {primary_gateway} failed: {str(e)}")
        
        # Fallback to other gateways
        for gateway in self.gateways.keys():
            if gateway == primary_gateway:
                continue
            
            try:
                result = self._create_payment_link_gateway(
                    gateway, invoice_id, amount, currency, description, customer_email
                )
                if result['success']:
                    logger.info(f"Fallback to {gateway} successful")
                    return result
            except Exception as e:
                logger.warning(f"Gateway {gateway} failed: {str(e)}")
        
        return {
            'success': False,
            'error': 'All payment gateways failed'
        }
    
    def _create_payment_link_gateway(self, gateway: PaymentGateway, invoice_id: str, 
                                   amount: Decimal, currency: str, description: str, 
                                   customer_email: str) -> Dict[str, Any]:
        """Create payment link using specific gateway"""
        if gateway == PaymentGateway.RAZORPAY:
            return self._create_razorpay_link(invoice_id, amount, currency, description, customer_email)
        elif gateway == PaymentGateway.STRIPE:
            return self._create_stripe_link(invoice_id, amount, currency, description, customer_email)
        else:
            raise ValueError(f"Unsupported gateway: {gateway}")
    
    def _create_razorpay_link(self, invoice_id: str, amount: Decimal, currency: str, 
                            description: str, customer_email: str) -> Dict[str, Any]:
        """Create Razorpay payment link"""
        try:
            client = self.gateways[PaymentGateway.RAZORPAY]['client']
            
            # Create order
            order_data = {
                'amount': int(float(amount) * 100),
                'currency': currency,
                'receipt': f'invoice_{invoice_id}',
                'notes': {
                    'invoice_id': invoice_id,
                    'customer_email': customer_email,
                }
            }
            
            order = client.order.create(data=order_data)
            
            # Create payment link
            payment_link_data = {
                'amount': int(float(amount) * 100),
                'currency': currency,
                'accept_partial': False,
                'reference_id': f'invoice_{invoice_id}',
                'description': description or f'Payment for Invoice #{invoice_id}',
                'callback_url': f'{getattr(settings, "FRONTEND_URL", "http://localhost:3000")}/payment-success',
                'callback_method': 'get',
            }
            
            payment_link = client.payment_link.create(data=payment_link_data)
            
            return {
                'success': True,
                'payment_id': order['id'],
                'payment_url': payment_link['short_url'],
                'gateway': 'razorpay',
                'order_id': order['id'],
                'payment_link_id': payment_link['id']
            }
            
        except Exception as e:
            logger.error(f"Razorpay error: {str(e)}")
            return {
                'success': False,
                'error': f"Razorpay error: {str(e)}",
                'gateway': 'razorpay'
            }
    
    def _create_stripe_link(self, invoice_id: str, amount: Decimal, currency: str, 
                          description: str, customer_email: str) -> Dict[str, Any]:
        """Create Stripe payment link"""
        try:
            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Invoice #{invoice_id}',
                            'description': description,
                        },
                        'unit_amount': int(float(amount) * 100),
                    },
                    'quantity': 1,
                }],
                after_completion={'type': 'redirect', 'redirect': {'url': f'{getattr(settings, "FRONTEND_URL", "http://localhost:3000")}/payment-success'}},
                metadata={
                    'invoice_id': invoice_id,
                    'customer_email': customer_email,
                }
            )
            
            return {
                'success': True,
                'payment_id': payment_link.id,
                'payment_url': payment_link.url,
                'gateway': 'stripe',
                'payment_link_id': payment_link.id
            }
            
        except Exception as e:
            logger.error(f"Stripe error: {str(e)}")
            return {
                'success': False,
                'error': f"Stripe error: {str(e)}",
                'gateway': 'stripe'
            }
    
    def verify_payment(self, payment_id: str, gateway: str) -> Dict[str, Any]:
        """Verify payment status"""
        try:
            if gateway == 'razorpay':
                return self._verify_razorpay_payment(payment_id)
            elif gateway == 'stripe':
                return self._verify_stripe_payment(payment_id)
            else:
                return {'status': 'unknown', 'error': f'Unknown gateway: {gateway}'}
        except Exception as e:
            logger.error(f"Payment verification failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
    
    def _verify_razorpay_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify Razorpay payment"""
        try:
            client = self.gateways[PaymentGateway.RAZORPAY]['client']
            payment = client.payment.fetch(payment_id)
            
            return {
                'status': payment['status'],
                'amount': payment['amount'] / 100,
                'currency': payment['currency'],
                'method': payment['method'],
                'captured': payment['captured'],
                'email': payment['email'],
                'contact': payment['contact']
            }
        except Exception as e:
            logger.error(f"Razorpay verification failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
    
    def get_payment_statistics(self) -> Dict[str, Any]:
        """Get payment system statistics"""
        try:
            stats = {
                'total_gateways': len(self.gateways),
                'enabled_gateways': len(self.get_available_gateways()),
                'gateway_status': {}
            }
            
            for gateway, config in self.gateways.items():
                stats['gateway_status'][gateway.value] = {
                    'enabled': config.get('enabled', False),
                    'priority': config.get('priority', 999)
                }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting payment statistics: {str(e)}")
            return {'error': str(e)}
    
    def _verify_stripe_payment(self, payment_id: str) -> Dict[str, Any]:
        """Verify Stripe payment"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            
            return {
                'status': payment_intent.status,
                'amount': payment_intent.amount / 100,
                'currency': payment_intent.currency,
                'payment_method': payment_intent.payment_method,
                'captured': payment_intent.captured,
                'receipt_email': payment_intent.receipt_email
            }
        except Exception as e:
            logger.error(f"Stripe verification failed: {str(e)}")
            return {'status': 'failed', 'error': str(e)}

# Global payment system instance
payment_system = OptimizedPaymentSystem()
