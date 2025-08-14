'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  TrendingUp, TrendingDown, DollarSign, FileText, 
  Clock, CheckCircle, AlertTriangle, Plus 
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/hooks/useAuth';
import DashboardLayout from '@/components/DashboardLayout';
import { invoiceAPI } from '@/lib/api';
import { formatCurrency, formatDateShort, getStatusBadgeColor } from '@/lib/utils';
import toast from 'react-hot-toast';

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
      const [summaryResponse, recentResponse] = await Promise.all([
        invoiceAPI.getSummary(),
        invoiceAPI.getRecent()
      ]);
      
      setSummary(summaryResponse.data);
      setRecentInvoices(recentResponse.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

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
      color: 'text-warning-600',
      bgColor: 'bg-warning-50',
    },
    {
      title: 'Paid Amount',
      value: formatCurrency(summary?.total_paid_amount || 0),
      icon: CheckCircle,
      color: 'text-success-600',
      bgColor: 'bg-success-50',
    },
    {
      title: 'Overdue Amount',
      value: formatCurrency(summary?.total_overdue_amount || 0),
      icon: AlertTriangle,
      color: 'text-danger-600',
      bgColor: 'bg-danger-50',
    },
  ];

  return (
    <AuthProvider>
      <DashboardLayout>
        <div className="space-y-6">
          {/* Welcome Section */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user.first_name}!
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Here's what's happening with your invoices today.
            </p>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {summaryCards.map((card) => (
              <div key={card.title} className="card">
                <div className="card-content">
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
                </div>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Quick Actions</h3>
            </div>
            <div className="card-content">
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
                    <span className="rounded-lg inline-flex p-3 bg-warning-50 text-warning-700 ring-4 ring-white">
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
                    <span className="rounded-lg inline-flex p-3 bg-success-50 text-success-700 ring-4 ring-white">
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
            </div>
          </div>

          {/* Recent Invoices */}
          <div className="card">
            <div className="card-header">
              <div className="flex items-center justify-between">
                <h3 className="card-title">Recent Invoices</h3>
                <Link
                  href="/invoices"
                  className="text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  View all
                </Link>
              </div>
            </div>
            <div className="card-content">
              {recentInvoices.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No invoices</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Get started by creating your first invoice.
                  </p>
                  <div className="mt-6">
                    <Link
                      href="/invoices/create"
                      className="btn btn-primary"
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
            </div>
          </div>
        </div>
      </DashboardLayout>
    </AuthProvider>
  );
}

export default function Page() {
  return <DashboardPage />;
}
