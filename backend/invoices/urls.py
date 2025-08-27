from django.urls import path, include
from .views import (
    InvoiceListCreateView, InvoiceDetailView, InvoiceSummaryView,
    generate_razorpay_payment_link, download_pdf, send_reminder,
    mark_as_paid, recent_invoices, razorpay_webhook
)
from .payment_views import (
    bulk_generate_payment_links, payment_dashboard_analytics,
    payment_link_status, cancel_payment_link, payment_history,
    resend_payment_link, payment_methods_stats
)
from .supabase_views import (
    SupabaseInvoiceListCreateView,
    SupabaseInvoiceDetailView,
    supabase_invoice_summary,
    supabase_recent_invoices,
    mark_invoice_as_paid,
    download_invoice_pdf,
    generate_payment_link
)
from .pdf_views import (
    generate_invoice_pdf,
    preview_invoice_html,
    preview_sample_invoice
)

urlpatterns = [
    # Original Django ORM views (for backward compatibility)
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<uuid:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/summary/', InvoiceSummaryView.as_view(), name='invoice-summary'),
    path('invoices/<uuid:invoice_id>/razorpay-link/', generate_razorpay_payment_link, name='generate-razorpay-link'),
    path('invoices/<uuid:invoice_id>/pdf/', download_pdf, name='download-pdf'),
    path('invoices/<uuid:invoice_id>/send-reminder/', send_reminder, name='send-reminder'),
    path('invoices/<uuid:invoice_id>/mark-paid/', mark_as_paid, name='mark-as-paid'),
    path('invoices/recent/', recent_invoices, name='recent-invoices'),
    path('webhook/razorpay/', razorpay_webhook, name='razorpay-webhook'),
    
    # Advanced Payment System URLs
    path('payments/bulk-generate-links/', bulk_generate_payment_links, name='bulk-payment-links'),
    path('payments/analytics/', payment_dashboard_analytics, name='payment-analytics'),
    path('payments/history/', payment_history, name='payment-history'),
    path('payments/methods-stats/', payment_methods_stats, name='payment-methods-stats'),
    path('payments/<uuid:invoice_id>/status/', payment_link_status, name='payment-link-status'),
    path('payments/<uuid:invoice_id>/cancel/', cancel_payment_link, name='cancel-payment-link'),
    path('payments/<uuid:invoice_id>/resend/', resend_payment_link, name='resend-payment-link'),
    
    # Supabase-based views (Real-time)
    path('supabase/invoices/', SupabaseInvoiceListCreateView.as_view(), name='supabase-invoice-list-create'),
    path('supabase/invoices/summary/', supabase_invoice_summary, name='supabase-invoice-summary'),
    path('supabase/invoices/recent/', supabase_recent_invoices, name='supabase-recent-invoices'),
    path('supabase/invoices/<str:pk>/', SupabaseInvoiceDetailView.as_view(), name='supabase-invoice-detail'),
    path('supabase/invoices/<str:invoice_id>/mark-paid/', mark_invoice_as_paid, name='supabase-mark-invoice-paid'),
    path('supabase/invoices/<str:invoice_id>/pdf/', download_invoice_pdf, name='supabase-download-pdf'),
    path('supabase/invoices/<str:invoice_id>/payment-link/', generate_payment_link, name='supabase-generate-payment-link'),
    
    # PDF Generation URLs
    path('supabase/invoices/<str:invoice_id>/pdf-template/', generate_invoice_pdf, name='generate-invoice-pdf'),
    path('supabase/invoices/<str:invoice_id>/preview/', preview_invoice_html, name='preview-invoice-html'),
    path('preview/sample-invoice/', preview_sample_invoice, name='preview-sample-invoice'),
    
    # Advanced Reminder System
    path('reminders/', include('invoices.reminder_urls')),
]
