'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/hooks/useAuth';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Bell, Send, Clock, TrendingUp, Mail, MessageSquare, 
  AlertTriangle, CheckCircle, XCircle, Settings,
  Users, DollarSign, Calendar, BarChart3
} from 'lucide-react';
import toast from 'react-hot-toast';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

interface ReminderDashboardData {
  summary: {
    overdue_invoices: number;
    upcoming_reminders: number;
    recent_stats: {
      total_sent: number;
      email_sent: number;
      sms_sent: number;
      successful: number;
      payments_received: number;
    };
  };
  template_performance: Array<{
    template_name: string;
    total_sent: number;
    payments_received: number;
    success_rate: number;
  }>;
  attention_invoices: Array<{
    id: string;
    invoice_number: string;
    client_name: string;
    total_amount: number;
    due_date: string;
    days_overdue: number;
    reminder_count: number;
    last_reminder_sent: string | null;
  }>;
}

function RemindersPage() {
  return (
    <AuthProvider>
      <RemindersContent />
    </AuthProvider>
  );
}

function RemindersContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<ReminderDashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedInvoices, setSelectedInvoices] = useState<string[]>([]);

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
      const response = await fetch('/api/reminders/reminder-dashboard/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        toast.error('Failed to load reminder dashboard');
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast.error('Failed to load reminder dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const sendBulkReminders = async () => {
    if (selectedInvoices.length === 0) {
      toast.error('Please select invoices to send reminders');
      return;
    }

    try {
      const response = await fetch('/api/reminders/send-bulk-reminders/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          invoice_ids: selectedInvoices,
          send_email: true,
          send_sms: false,  // SMS disabled to keep system cost-free
          subject: 'Payment Reminder',
          email_body: 'This is a friendly reminder about your outstanding invoice. Please process payment at your earliest convenience.'
        })
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(`Sent ${result.successful} reminders successfully`);
        setSelectedInvoices([]);
        loadDashboardData();
      } else {
        toast.error('Failed to send bulk reminders');
      }
    } catch (error) {
      console.error('Error sending bulk reminders:', error);
      toast.error('Failed to send bulk reminders');
    }
  };

  const sendManualReminder = async (invoiceId: string) => {
    try {
      const response = await fetch(`/api/reminders/invoices/${invoiceId}/send-reminder/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          send_email: true,
          send_sms: false,  // SMS disabled to keep system cost-free
          subject: 'Payment Reminder',
          email_body: 'This is a friendly reminder about your outstanding invoice. Please process payment at your earliest convenience.'
        })
      });

      if (response.ok) {
        toast.success('Reminder sent successfully');
        loadDashboardData();
      } else {
        toast.error('Failed to send reminder');
      }
    } catch (error) {
      console.error('Error sending reminder:', error);
      toast.error('Failed to send reminder');
    }
  };

  const toggleInvoiceSelection = (invoiceId: string) => {
    setSelectedInvoices(prev => 
      prev.includes(invoiceId) 
        ? prev.filter(id => id !== invoiceId)
        : [...prev, invoiceId]
    );
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

  if (!user || !dashboardData) {
    return null;
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Bell className="h-8 w-8 mr-3 text-blue-600" />
              Reminder System
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Manage payment reminders and track collection performance
            </p>
            <div className="mt-2 flex items-center text-sm">
              <Mail className="h-4 w-4 text-green-600 mr-2" />
              <span className="text-green-600 font-medium">Email reminders active</span>
              <span className="mx-2 text-gray-400">•</span>
              <MessageSquare className="h-4 w-4 text-gray-400 mr-2" />
              <span className="text-gray-500">SMS temporarily disabled (cost-free operation)</span>
            </div>
          </div>
          <div className="flex space-x-3">
            <Button
              onClick={() => router.push('/reminders/templates')}
              className="btn btn-secondary"
            >
              <Settings className="h-4 w-4 mr-2" />
              Manage Templates
            </Button>
            <Button
              onClick={() => router.push('/reminders/analytics')}
              className="btn btn-primary"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              View Analytics
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overdue Invoices</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {dashboardData.summary.overdue_invoices}
              </div>
              <p className="text-xs text-gray-600">
                Require immediate attention
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Upcoming Reminders</CardTitle>
              <Clock className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">
                {dashboardData.summary.upcoming_reminders}
              </div>
              <p className="text-xs text-gray-600">
                Scheduled for next 7 days
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recent Reminders</CardTitle>
              <Send className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {dashboardData.summary.recent_stats.total_sent}
              </div>
              <p className="text-xs text-gray-600">
                Sent in last 30 days
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">
                {dashboardData.summary.recent_stats.total_sent > 0 
                  ? Math.round((dashboardData.summary.recent_stats.payments_received / dashboardData.summary.recent_stats.total_sent) * 100)
                  : 0}%
              </div>
              <p className="text-xs text-gray-600">
                Payment after reminder
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Channel Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Channel Performance</CardTitle>
              <CardDescription>Reminder delivery statistics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Mail className="h-4 w-4 text-blue-600 mr-2" />
                    <span className="text-sm font-medium">Email</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{dashboardData.summary.recent_stats.email_sent}</div>
                    <div className="text-xs text-gray-500">sent</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <MessageSquare className="h-4 w-4 text-green-600 mr-2" />
                    <span className="text-sm font-medium">SMS</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{dashboardData.summary.recent_stats.sms_sent}</div>
                    <div className="text-xs text-gray-500">sent</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-purple-600 mr-2" />
                    <span className="text-sm font-medium">Successful</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">{dashboardData.summary.recent_stats.successful}</div>
                    <div className="text-xs text-gray-500">delivered</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Top Performing Templates</CardTitle>
              <CardDescription>Templates with highest payment rates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {dashboardData.template_performance.slice(0, 3).map((template, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-sm font-medium truncate">
                        {template.template_name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {template.total_sent} sent • {template.payments_received} paid
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-bold text-green-600">
                        {template.success_rate}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Invoices Requiring Attention */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Invoices Requiring Attention</CardTitle>
                <CardDescription>Overdue invoices that need reminders</CardDescription>
              </div>
              <div className="flex space-x-2">
                {selectedInvoices.length > 0 && (
                  <Button
                    onClick={sendBulkReminders}
                    className="btn btn-primary"
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Send {selectedInvoices.length} Reminders
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">
                      <input
                        type="checkbox"
                        checked={selectedInvoices.length === dashboardData.attention_invoices.length}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedInvoices(dashboardData.attention_invoices.map(inv => inv.id));
                          } else {
                            setSelectedInvoices([]);
                          }
                        }}
                        className="rounded"
                      />
                    </th>
                    <th className="text-left p-2">Invoice</th>
                    <th className="text-left p-2">Client</th>
                    <th className="text-left p-2">Amount</th>
                    <th className="text-left p-2">Days Overdue</th>
                    <th className="text-left p-2">Reminders</th>
                    <th className="text-left p-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.attention_invoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b hover:bg-gray-50">
                      <td className="p-2">
                        <input
                          type="checkbox"
                          checked={selectedInvoices.includes(invoice.id)}
                          onChange={() => toggleInvoiceSelection(invoice.id)}
                          className="rounded"
                        />
                      </td>
                      <td className="p-2">
                        <div className="font-medium">{invoice.invoice_number}</div>
                        <div className="text-sm text-gray-500">
                          Due: {new Date(invoice.due_date).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="p-2">
                        <div className="font-medium">{invoice.client_name}</div>
                      </td>
                      <td className="p-2">
                        <div className="font-medium">₹{invoice.total_amount.toLocaleString()}</div>
                      </td>
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          invoice.days_overdue > 30 
                            ? 'bg-red-100 text-red-800'
                            : invoice.days_overdue > 7
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {invoice.days_overdue} days
                        </span>
                      </td>
                      <td className="p-2">
                        <div className="text-sm">
                          {invoice.reminder_count} sent
                        </div>
                        {invoice.last_reminder_sent && (
                          <div className="text-xs text-gray-500">
                            Last: {new Date(invoice.last_reminder_sent).toLocaleDateString()}
                          </div>
                        )}
                      </td>
                      <td className="p-2">
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => sendManualReminder(invoice.id)}
                            size="sm"
                            className="btn btn-secondary btn-sm"
                          >
                            <Send className="h-3 w-3" />
                          </Button>
                          <Button
                            onClick={() => router.push(`/invoices/${invoice.id}`)}
                            size="sm"
                            className="btn btn-outline btn-sm"
                          >
                            View
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

export default function Page() {
  return <RemindersPage />;
}
