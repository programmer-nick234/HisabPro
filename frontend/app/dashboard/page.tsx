'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/hooks/useAuth';
import { invoiceAPI } from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, TrendingUp, TrendingDown, DollarSign, FileText, Clock, CheckCircle, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { formatCurrency, formatDateShort, getStatusBadgeColor } from '@/lib/utils';
import toast from 'react-hot-toast';

// Force dynamic rendering to prevent SSR issues
export const dynamic = 'force-dynamic';

interface InvoiceSummary {
  total_invoices: number;
  pending_invoices: number;
  paid_invoices: number;
  overdue_invoices: number;
  total_pending_amount: number;
  total_paid_amount: number;
  total_overdue_amount: number;
  total_amount: number;
}

interface Invoice {
  id: string;
  invoice_number: string;
  client_name: string;
  total_amount: number;
  status: string;
  due_date: string;
  created_at: string;
}

function DashboardPage() {
  return (
    <AuthProvider>
      <DashboardContent />
    </AuthProvider>
  );
}

function DashboardContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [summary, setSummary] = useState<InvoiceSummary | null>(null);
  const [recentInvoices, setRecentInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      loadDashboardData();
    }
  }, [user, loading, router]);

  const loadDashboardData = async () => {
    try {
      console.log('Loading dashboard data...');
      
      // Load summary data
      const summaryResponse = await invoiceAPI.getSummary();
      console.log('Summary response:', summaryResponse);
      
      // Handle summary data - it might be a single object or have a different structure
      let summaryData = summaryResponse.data;
      if (summaryData && typeof summaryData === 'object') {
        // If it's a single invoice object, create a summary from it
        if (summaryData.invoice_number) {
          summaryData = {
            total_invoices: 1,
            pending_invoices: summaryData.status === 'pending' ? 1 : 0,
            paid_invoices: summaryData.status === 'paid' ? 1 : 0,
            overdue_invoices: summaryData.status === 'overdue' ? 1 : 0,
            total_pending_amount: summaryData.status === 'pending' ? (summaryData.total_amount || 0) : 0,
            total_paid_amount: summaryData.status === 'paid' ? (summaryData.total_amount || 0) : 0,
            total_overdue_amount: summaryData.status === 'overdue' ? (summaryData.total_amount || 0) : 0,
            total_amount: summaryData.total_amount || 0
          };
        }
      }
      setSummary(summaryData);
      
      // Load recent invoices data
      const recentResponse = await invoiceAPI.getRecent();
      console.log('Recent response:', recentResponse);
      
      // Handle recent invoices data - it might be a single object or an array
      let recentData = recentResponse.data;
      if (recentData && typeof recentData === 'object') {
        // If it's a single invoice object, wrap it in an array
        if (recentData.invoice_number) {
          recentData = [recentData];
        }
        // If it's not an array, try to get the results property
        else if (!Array.isArray(recentData) && recentData.results) {
          recentData = recentData.results;
        }
        // If it's still not an array, make it an empty array
        else if (!Array.isArray(recentData)) {
          recentData = [];
        }
      } else {
        recentData = [];
      }
      setRecentInvoices(recentData);
      
    } catch (error) {
      console.error('Dashboard data error:', error);
      toast.error('Failed to load dashboard data');
      // Set default values
      setSummary({
        total_invoices: 0,
        pending_invoices: 0,
        paid_invoices: 0,
        overdue_invoices: 0,
        total_pending_amount: 0,
        total_paid_amount: 0,
        total_overdue_amount: 0,
        total_amount: 0
      });
      setRecentInvoices([]);
    } finally {
      setIsLoading(false);
    }
  };

  if (loading || isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!user) {
    return null;
  }

  const summaryCards = [
    {
      title: 'Total Invoices',
      value: summary?.total_invoices || 0,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Pending Amount',
      value: formatCurrency(summary?.total_pending_amount || 0),
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Paid Amount',
      value: formatCurrency(summary?.total_paid_amount || 0),
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Overdue Amount',
      value: formatCurrency(summary?.total_overdue_amount || 0),
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user.first_name || user.username}!
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Here's what's happening with your invoices today.
          </p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {summaryCards.map((card) => (
            <Card key={card.title} className="overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 ${card.bgColor} rounded-md p-3`}>
                    <card.icon className={`h-6 w-6 ${card.color}`} />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {card.title}
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {card.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <Link
                href="/invoices/create"
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <div>
                  <span className="rounded-lg inline-flex p-3 bg-primary-50 text-primary-700 ring-4 ring-white">
                    <Plus className="h-6 w-6" />
                  </span>
                </div>
                <div className="mt-8">
                  <h3 className="text-lg font-medium">
                    <span className="absolute inset-0" aria-hidden="true" />
                    Create Invoice
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Generate a new invoice for your client
                  </p>
                </div>
              </Link>

              <Link
                href="/invoices"
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <div>
                  <span className="rounded-lg inline-flex p-3 bg-yellow-50 text-yellow-700 ring-4 ring-white">
                    <FileText className="h-6 w-6" />
                  </span>
                </div>
                <div className="mt-8">
                  <h3 className="text-lg font-medium">
                    <span className="absolute inset-0" aria-hidden="true" />
                    View All Invoices
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Manage and track all your invoices
                  </p>
                </div>
              </Link>

              <Link
                href="/analytics"
                className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary-500 rounded-lg border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <div>
                  <span className="rounded-lg inline-flex p-3 bg-green-50 text-green-700 ring-4 ring-white">
                    <TrendingUp className="h-6 w-6" />
                  </span>
                </div>
                <div className="mt-8">
                  <h3 className="text-lg font-medium">
                    <span className="absolute inset-0" aria-hidden="true" />
                    View Analytics
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    Analyze your business performance
                  </p>
                </div>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Recent Invoices */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Recent Invoices</CardTitle>
              <Link
                href="/invoices"
                className="text-sm font-medium text-primary-600 hover:text-primary-500"
              >
                View all
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {!Array.isArray(recentInvoices) || recentInvoices.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No invoices</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by creating your first invoice.
                </p>
                <div className="mt-6">
                  <Link
                    href="/invoices/create"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    <Plus className="-ml-1 mr-2 h-5 w-5" />
                    Create Invoice
                  </Link>
                </div>
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
                        Due Date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {recentInvoices.map((invoice) => (
                      <tr key={invoice.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Link
                            href={`/invoices/${invoice.id}`}
                            className="text-sm font-medium text-primary-600 hover:text-primary-500"
                          >
                            {invoice.invoice_number}
                          </Link>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {invoice.client_name}
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
                          {formatDateShort(invoice.due_date)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

export default function Page() {
  return <DashboardPage />;
}
