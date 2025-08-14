from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['payment_date']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'client_name', 'user', 'total_amount', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'created_at', 'due_date', 'user']
    search_fields = ['invoice_number', 'client_name', 'client_email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_reminder_sent', 'reminder_count']
    inlines = [InvoiceItemInline, PaymentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'invoice_number', 'client_name', 'client_email', 'client_phone', 'client_address')
        }),
        ('Invoice Details', {
            'fields': ('issue_date', 'due_date', 'status', 'tax_rate')
        }),
        ('Financial', {
            'fields': ('subtotal', 'tax_amount', 'total_amount')
        }),
        ('Additional', {
            'fields': ('notes', 'terms_conditions', 'razorpay_payment_link', 'razorpay_order_id')
        }),
        ('System', {
            'fields': ('last_reminder_sent', 'reminder_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'unit_price', 'total']
    list_filter = ['invoice__status']
    search_fields = ['description', 'invoice__invoice_number']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['payment_method', 'status', 'payment_date']
    search_fields = ['invoice__invoice_number', 'transaction_id']
    readonly_fields = ['payment_date']
