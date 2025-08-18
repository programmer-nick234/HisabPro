from django.urls import path
from .views import (
    InvoiceListCreateView, InvoiceDetailView, InvoiceSummaryView,
    generate_razorpay_payment_link, download_pdf, send_reminder,
    mark_as_paid, recent_invoices, razorpay_webhook
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
    
    # Supabase-based views (Real-time)
    path('supabase/invoices/', SupabaseInvoiceListCreateView.as_view(), name='supabase-invoice-list-create'),
    path('supabase/invoices/<str:pk>/', SupabaseInvoiceDetailView.as_view(), name='supabase-invoice-detail'),
    path('supabase/invoices/summary/', supabase_invoice_summary, name='supabase-invoice-summary'),
    path('supabase/invoices/recent/', supabase_recent_invoices, name='supabase-recent-invoices'),
    path('supabase/invoices/<str:invoice_id>/mark-paid/', mark_invoice_as_paid, name='supabase-mark-invoice-paid'),
    path('supabase/invoices/<str:invoice_id>/pdf/', download_invoice_pdf, name='supabase-download-pdf'),
    path('supabase/invoices/<str:invoice_id>/payment-link/', generate_payment_link, name='supabase-generate-payment-link'),
]
