from django.urls import path
from .views import (
    InvoiceListCreateView, InvoiceDetailView, InvoiceSummaryView,
    generate_razorpay_payment_link, download_pdf, send_reminder,
    mark_as_paid, recent_invoices, razorpay_webhook
)

urlpatterns = [
    path('invoices/', InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<uuid:pk>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/summary/', InvoiceSummaryView.as_view(), name='invoice-summary'),
    path('invoices/<uuid:invoice_id>/razorpay-link/', generate_razorpay_payment_link, name='generate-razorpay-link'),
    path('invoices/<uuid:invoice_id>/pdf/', download_pdf, name='download-pdf'),
    path('invoices/<uuid:invoice_id>/send-reminder/', send_reminder, name='send-reminder'),
    path('invoices/<uuid:invoice_id>/mark-paid/', mark_as_paid, name='mark-as-paid'),
    path('invoices/recent/', recent_invoices, name='recent-invoices'),
    path('webhook/razorpay/', razorpay_webhook, name='razorpay-webhook'),
]
