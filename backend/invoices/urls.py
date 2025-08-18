from django.urls import path
from .views import (
    InvoiceListCreateView, InvoiceDetailView, InvoiceSummaryView,
    generate_razorpay_payment_link, download_pdf, send_reminder,
    mark_as_paid, recent_invoices, razorpay_webhook
)
from .mongodb_views_v2 import (
    MongoDBInvoiceListCreateView, MongoDBInvoiceDetailView, MongoDBInvoiceSummaryView,
    mongodb_recent_invoices, mark_invoice_as_paid, download_pdf, generate_payment_link, razorpay_webhook
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
    
    # MongoDB-based views (Real-time)
    path('mongodb/invoices/', MongoDBInvoiceListCreateView.as_view(), name='mongodb-invoice-list-create'),
    path('mongodb/invoices/<str:pk>/', MongoDBInvoiceDetailView.as_view(), name='mongodb-invoice-detail'),
    path('mongodb/invoices/summary/', MongoDBInvoiceSummaryView.as_view(), name='mongodb-invoice-summary'),
    path('mongodb/invoices/recent/', mongodb_recent_invoices, name='mongodb-recent-invoices'),
    path('mongodb/invoices/<str:invoice_id>/mark-paid/', mark_invoice_as_paid, name='mongodb-mark-invoice-paid'),
    path('mongodb/invoices/<str:invoice_id>/pdf/', download_pdf, name='mongodb-download-pdf'),
            path('mongodb/invoices/<str:invoice_id>/payment-link/', generate_payment_link, name='mongodb-generate-payment-link'),
    path('mongodb/webhook/razorpay/', razorpay_webhook, name='mongodb-razorpay-webhook'),
]
