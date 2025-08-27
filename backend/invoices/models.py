from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=20, unique=True)
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=15, blank=True)
    client_address = models.TextField(blank=True)
    
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)
    
    razorpay_payment_link = models.URLField(blank=True)
    razorpay_payment_link_id = models.CharField(max_length=255, blank=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True)
    
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    reminder_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client_name}"
    
    def save(self, *args, **kwargs):
        # Generate invoice number if not set
        if not self.invoice_number:
            self.generate_invoice_number()
        
        # Calculate totals
        self.calculate_totals()
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total amounts"""
        try:
            # Use getattr to handle cases where items relation might not be accessible
            items = getattr(self, 'items', None)
            if items is not None:
                subtotal = sum(item.total for item in items.all())
            else:
                subtotal = Decimal('0.00')
            
            self.subtotal = subtotal
            self.tax_amount = (subtotal * self.tax_rate) / 100
            self.total_amount = self.subtotal + self.tax_amount
        except Exception as e:
            # If calculation fails, set default values
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to calculate totals for invoice {self.id}: {str(e)}")
            
            self.subtotal = Decimal('0.00')
            self.tax_amount = Decimal('0.00')
            self.total_amount = Decimal('0.00')
    
    def generate_invoice_number(self):
        """Generate unique invoice number"""
        if not self.invoice_number:
            try:
                # Ensure user exists
                if not self.user:
                    raise ValueError("Invoice must have a user to generate invoice number")
                
                # Get last invoice for this user
                last_invoice = Invoice.objects.filter(user=self.user).order_by('-created_at').first()
                
                if last_invoice and last_invoice.invoice_number:
                    try:
                        # Extract number from format INV-XXXX-YYYY
                        parts = last_invoice.invoice_number.split('-')
                        if len(parts) >= 3:
                            last_number = int(parts[-1])
                            new_number = last_number + 1
                        else:
                            new_number = 1
                    except (ValueError, IndexError):
                        new_number = 1
                else:
                    new_number = 1
                
                # Generate unique invoice number
                self.invoice_number = f"INV-{self.user.id:04d}-{new_number:04d}"
                
                # Ensure uniqueness (in case of race conditions)
                max_attempts = 10
                attempt = 0
                while Invoice.objects.filter(invoice_number=self.invoice_number).exists() and attempt < max_attempts:
                    new_number += 1
                    self.invoice_number = f"INV-{self.user.id:04d}-{new_number:04d}"
                    attempt += 1
                
                if attempt >= max_attempts:
                    # Fallback to timestamp-based number
                    from django.utils import timezone
                    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                    self.invoice_number = f"INV-{self.user.id:04d}-{timestamp}"
                    
            except Exception as e:
                # Fallback to timestamp-based invoice number
                from django.utils import timezone
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                self.invoice_number = f"INV-{self.user.id if self.user else 0:04d}-{timestamp}"
                
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to generate sequential invoice number: {str(e)}. Using timestamp fallback.")
    
    def update_status(self):
        """Update invoice status based on due date and payment"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.status == 'paid':
            return
        
        if today > self.due_date:
            self.status = 'overdue'
        else:
            self.status = 'pending'


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Recalculate invoice totals
        self.invoice.calculate_totals()
        self.invoice.save()
    
    def __str__(self):
        return f"{self.description} - {self.quantity} x {self.unit_price}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, default='razorpay')
    transaction_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, default='completed')
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"


# Import reminder models here to include them in migrations
from .reminder_models import *
