'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/hooks/useAuth';
import { invoiceAPI } from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Search, Filter, Download, Eye, Edit, Trash2, Send } from 'lucide-react';
import Link from 'next/link';
import { formatCurrency, formatDateShort, getStatusBadgeColor } from '@/lib/utils';
import toast from 'react-hot-toast';

// Force dynamic rendering to prevent SSR issues
export const dynamic = 'force-dynamic';

interface Invoice {
  id: string;
  invoice_number: string;
  client_name: string;
  client_email: string;
  total_amount: number;
  status: string;
  issue_date: string;
  due_date: string;
  created_at: string;
  razorpay_payment_link?: string;
}

function InvoicesPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      loadInvoices();
    }
  }, [user, loading, router]);

  const loadInvoices = async () => {
    try {
      const response = await invoiceAPI.getInvoices();
      setInvoices(response.data.results || response.data);
    } catch (error) {
      toast.error('Failed to load invoices');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (invoiceId: string) => {
    if (!confirm('Are you sure you want to delete this invoice?')) {
      return;
    }

    try {
      await invoiceAPI.deleteInvoice(invoiceId);
      toast.success('Invoice deleted successfully');
      loadInvoices();
    } catch (error) {
      toast.error('Failed to delete invoice');
    }
  };

  const handleDownloadPDF = async (invoiceId: string) => {
    try {
      const response = await invoiceAPI.downloadPDF(invoiceId);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice_${invoiceId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('PDF downloaded successfully');
    } catch (error) {
      toast.error('Failed to download PDF');
    }
  };

  const handleSendReminder = async (invoiceId: string) => {
    try {
      await invoiceAPI.sendReminder(invoiceId);
      toast.success('Payment reminder sent successfully');
    } catch (error) {
      toast.error('Failed to send reminder');
    }
  };

  const handleGeneratePaymentLink = async (invoiceId: string) => {
    try {
      const response = await invoiceAPI.generateRazorpayLink(invoiceId);
      window.open(response.data.payment_link, '_blank');
      toast.success('Payment link generated successfully');
    } catch (error) {
      toast.error('Failed to generate payment link');
    }
  };

  const filteredInvoices = invoices.filter((invoice) => {
    const matchesSearch = 
      invoice.invoice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      invoice.client_email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || invoice.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  if (loading || isLoading) {
    return (
      <AuthProvider>
        <DashboardLayout>
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        </DashboardLayout>
      </AuthProvider>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <AuthProvider>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
              <p className="mt-1 text-sm text-gray-500">
                Manage and track all your invoices
              </p>
            </div>
            <Link
              href="/invoices/create"
              className="btn btn-primary"
            >
              <Plus className="-ml-1 mr-2 h-5 w-5" />
              Create Invoice
            </Link>
          </div>

          {/* Filters */}
          <div className="card">
            <div className="card-content">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Search className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="text"
                      placeholder="Search invoices..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="input pl-10"
                    />
                  </div>
                </div>
                <div className="sm:w-48">
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="input"
                  >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="paid">Paid</option>
                    <option value="overdue">Overdue</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Invoices Table */}
          <div className="card">
            <div className="card-content">
              {filteredInvoices.length === 0 ? (
                <div className="text-center py-12">
                  <div className="mx-auto h-12 w-12 text-gray-400">
                    <Search className="h-12 w-12" />
                  </div>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No invoices found</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    {searchTerm || statusFilter !== 'all' 
                      ? 'Try adjusting your search or filter criteria.'
                      : 'Get started by creating your first invoice.'
                    }
                  </p>
                  {!searchTerm && statusFilter === 'all' && (
                    <div className="mt-6">
                      <Link
                        href="/invoices/create"
                        className="btn btn-primary"
                      >
                        <Plus className="-ml-1 mr-2 h-5 w-5" />
                        Create Invoice
                      </Link>
                    </div>
                  )}
                </div>
              ) : (
                <div className="overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Invoice
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Client
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Issue Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Due Date
                        </th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredInvoices.map((invoice) => (
                        <tr key={invoice.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <Link
                              href={`/invoices/${invoice.id}`}
                              className="text-sm font-medium text-primary-600 hover:text-primary-500"
                            >
                              {invoice.invoice_number}
                            </Link>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {invoice.client_name}
                              </div>
                              <div className="text-sm text-gray-500">
                                {invoice.client_email}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {formatCurrency(invoice.total_amount)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeColor(invoice.status)}`}>
                              {invoice.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDateShort(invoice.issue_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {formatDateShort(invoice.due_date)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end space-x-2">
                              <button
                                onClick={() => router.push(`/invoices/${invoice.id}`)}
                                className="text-primary-600 hover:text-primary-900"
                                title="View"
                              >
                                <Eye className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDownloadPDF(invoice.id)}
                                className="text-gray-600 hover:text-gray-900"
                                title="Download PDF"
                              >
                                <Download className="h-4 w-4" />
                              </button>
                              {invoice.status !== 'paid' && (
                                <>
                                  <button
                                    onClick={() => handleSendReminder(invoice.id)}
                                    className="text-warning-600 hover:text-warning-900"
                                    title="Send Reminder"
                                  >
                                    <Send className="h-4 w-4" />
                                  </button>
                                  <button
                                    onClick={() => handleGeneratePaymentLink(invoice.id)}
                                    className="text-success-600 hover:text-success-900"
                                    title="Generate Payment Link"
                                  >
                                    {/* CreditCard icon was removed, using Send for now */}
                                    <Send className="h-4 w-4" />
                                  </button>
                                </>
                              )}
                              <button
                                onClick={() => handleDelete(invoice.id)}
                                className="text-danger-600 hover:text-danger-900"
                                title="Delete"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </DashboardLayout>
    </AuthProvider>
  );
}

export default function Page() {
  return <InvoicesPage />;
}
