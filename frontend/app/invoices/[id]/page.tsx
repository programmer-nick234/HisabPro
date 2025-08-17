'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/hooks/useAuth';
import { invoiceAPI } from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, Send, Edit, Trash2, Eye, Printer } from 'lucide-react';
import Link from 'next/link';
import { formatCurrency, formatDate, getStatusBadgeColor } from '@/lib/utils';
import toast from 'react-hot-toast';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

interface InvoiceItem {
  id: string;
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

interface Invoice {
  id: string;
  invoice_number: string;
  client_name: string;
  client_email: string;
  client_phone: string;
  client_address: string;
  total_amount: number;
  subtotal: number;
  tax_rate: number;
  tax_amount: number;
  status: string;
  issue_date: string;
  due_date: string;
  notes: string;
  terms_conditions: string;
  created_at: string;
  items: InvoiceItem[];
  razorpay_payment_link?: string;
}

function InvoiceDetailPage() {
  return (
    <AuthProvider>
      <InvoiceDetailContent />
    </AuthProvider>
  );
}

function InvoiceDetailContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const invoiceId = params.id as string;
  
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
      return;
    }

    if (user && invoiceId) {
      loadInvoice();
    }
  }, [user, loading, invoiceId, router]);

  const loadInvoice = async () => {
    try {
      const response = await invoiceAPI.getInvoice(invoiceId);
      setInvoice(response.data);
    } catch (error) {
      toast.error('Failed to load invoice');
      router.push('/invoices');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this invoice? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(true);
    try {
      await invoiceAPI.deleteInvoice(invoiceId);
      toast.success('Invoice deleted successfully');
      router.push('/invoices');
    } catch (error) {
      toast.error('Failed to delete invoice');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await invoiceAPI.downloadPDF(invoiceId);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice_${invoice?.invoice_number}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSendReminder = async () => {
    try {
      await invoiceAPI.sendReminder(invoiceId);
      toast.success('Payment reminder sent successfully');
    } catch (error) {
      toast.error('Failed to send reminder');
    }
  };

  const handleGeneratePaymentLink = async () => {
    try {
      const response = await invoiceAPI.generateRazorpayLink(invoiceId);
      if (response.data.payment_link) {
        // Update the invoice with the payment link
        setInvoice(prev => prev ? { ...prev, razorpay_payment_link: response.data.payment_link } : null);
        toast.success('Payment link generated successfully');
      }
    } catch (error) {
      toast.error('Failed to generate payment link');
    }
  };

  if (loading || isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!invoice) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900">Invoice not found</h2>
          <p className="mt-2 text-gray-600">The invoice you're looking for doesn't exist.</p>
          <Link href="/invoices" className="btn btn-primary mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Invoices
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/invoices" className="btn btn-outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Invoices
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Invoice Details</h1>
              <p className="text-gray-600">{invoice.invoice_number}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button onClick={handlePrint} variant="outline" size="sm">
              <Printer className="mr-2 h-4 w-4" />
              Print
            </Button>
            <Button onClick={handleDownloadPDF} variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download PDF
            </Button>
            <Button onClick={handleSendReminder} variant="outline" size="sm">
              <Send className="mr-2 h-4 w-4" />
              Send Reminder
            </Button>
            <Link href={`/invoices/${invoiceId}/edit`}>
              <Button variant="outline" size="sm">
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Button>
            </Link>
            <Button 
              onClick={handleDelete} 
              variant="destructive" 
              size="sm"
              disabled={isDeleting}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </div>
        </div>

        {/* Invoice Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Invoice Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Invoice Header */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Invoice #{invoice.invoice_number}</span>
                  <span className={`px-3 py-1 text-sm font-semibold rounded-full ${getStatusBadgeColor(invoice.status)}`}>
                    {invoice.status.toUpperCase()}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Issue Date</label>
                    <p className="text-sm text-gray-900">{formatDate(invoice.issue_date)}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Due Date</label>
                    <p className="text-sm text-gray-900">{formatDate(invoice.due_date)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Client Information */}
            <Card>
              <CardHeader>
                <CardTitle>Client Information</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Name</label>
                    <p className="text-sm text-gray-900">{invoice.client_name}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Email</label>
                    <p className="text-sm text-gray-900">{invoice.client_email}</p>
                  </div>
                  {invoice.client_phone && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Phone</label>
                      <p className="text-sm text-gray-900">{invoice.client_phone}</p>
                    </div>
                  )}
                  {invoice.client_address && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Address</label>
                      <p className="text-sm text-gray-900">{invoice.client_address}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Invoice Items */}
            <Card>
              <CardHeader>
                <CardTitle>Invoice Items</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Description</th>
                        <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">Quantity</th>
                        <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">Unit Price</th>
                        <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">Total</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {invoice.items?.map((item) => (
                        <tr key={item.id}>
                          <td className="px-4 py-2 text-sm text-gray-900">{item.description}</td>
                          <td className="px-4 py-2 text-sm text-gray-900 text-right">{item.quantity}</td>
                          <td className="px-4 py-2 text-sm text-gray-900 text-right">{formatCurrency(item.unit_price)}</td>
                          <td className="px-4 py-2 text-sm text-gray-900 text-right">{formatCurrency(item.total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Notes and Terms */}
            {(invoice.notes || invoice.terms_conditions) && (
              <Card>
                <CardHeader>
                  <CardTitle>Additional Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {invoice.notes && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Notes</label>
                      <p className="text-sm text-gray-900 mt-1">{invoice.notes}</p>
                    </div>
                  )}
                  {invoice.terms_conditions && (
                    <div>
                      <label className="text-sm font-medium text-gray-500">Terms & Conditions</label>
                      <p className="text-sm text-gray-900 mt-1">{invoice.terms_conditions}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>

          {/* Invoice Summary */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Invoice Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Subtotal</span>
                    <span className="text-sm font-medium">{formatCurrency(invoice.subtotal)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Tax ({invoice.tax_rate}%)</span>
                    <span className="text-sm font-medium">{formatCurrency(invoice.tax_amount)}</span>
                  </div>
                  <div className="border-t pt-3">
                    <div className="flex justify-between">
                      <span className="text-lg font-semibold">Total</span>
                      <span className="text-lg font-semibold">{formatCurrency(invoice.total_amount)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Payment Actions */}
            {invoice.status === 'pending' && (
              <Card>
                <CardHeader>
                  <CardTitle>Payment</CardTitle>
                </CardHeader>
                <CardContent>
                  {invoice.razorpay_payment_link ? (
                    <Button 
                      onClick={() => window.open(invoice.razorpay_payment_link, '_blank')}
                      className="w-full"
                    >
                      Pay Now
                    </Button>
                  ) : (
                    <Button 
                      onClick={handleGeneratePaymentLink}
                      className="w-full"
                    >
                      Generate Payment Link
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default InvoiceDetailPage;
