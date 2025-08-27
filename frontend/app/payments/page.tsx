'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import DashboardLayout from '@/components/DashboardLayout'
import { toast } from 'react-hot-toast'

interface PaymentAnalytics {
  summary: {
    total_invoices: number
    paid_invoices: number
    pending_invoices: number
    overdue_invoices: number
    total_revenue: number
    pending_revenue: number
    payment_success_rate: number
  }
  payment_methods: {
    [key: string]: number
  }
  recent_payments: any[]
}

interface Invoice {
  id: string
  invoice_number: string
  client_name: string
  client_email: string
  total_amount: number
  status: string
  created_at: string
  has_payment_link: boolean
  payment_link?: string
}

export default function PaymentDashboard() {
  const [analytics, setAnalytics] = useState<PaymentAnalytics | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [selectedInvoices, setSelectedInvoices] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [bulkLoading, setBulkLoading] = useState(false)

  useEffect(() => {
    fetchAnalytics()
    fetchInvoices()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/payments/analytics/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      } else {
        toast.error('Failed to fetch analytics')
      }
    } catch (error) {
      console.error('Error fetching analytics:', error)
      toast.error('Error fetching analytics')
    }
  }

  const fetchInvoices = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/payments/history/?status=pending&per_page=50', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setInvoices(data.invoices)
      } else {
        toast.error('Failed to fetch invoices')
      }
    } catch (error) {
      console.error('Error fetching invoices:', error)
      toast.error('Error fetching invoices')
    } finally {
      setLoading(false)
    }
  }

  const generatePaymentLink = async (invoiceId: string, sendEmail = true) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/invoices/${invoiceId}/razorpay-link/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ send_email: sendEmail })
      })
      
      if (response.ok) {
        const data = await response.json()
        toast.success(`Payment link generated! ${data.email_sent ? 'Email sent to customer.' : ''}`)
        fetchInvoices() // Refresh the list
        return data
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to generate payment link')
        return null
      }
    } catch (error) {
      console.error('Error generating payment link:', error)
      toast.error('Error generating payment link')
      return null
    }
  }

  const bulkGeneratePaymentLinks = async () => {
    if (selectedInvoices.length === 0) {
      toast.error('Please select invoices first')
      return
    }

    setBulkLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/payments/bulk-generate-links/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          invoice_ids: selectedInvoices,
          send_emails: true
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        toast.success(`Generated ${data.successful} payment links out of ${data.total_processed}`)
        setSelectedInvoices([])
        fetchInvoices()
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to generate bulk payment links')
      }
    } catch (error) {
      console.error('Error generating bulk payment links:', error)
      toast.error('Error generating bulk payment links')
    } finally {
      setBulkLoading(false)
    }
  }

  const copyPaymentLink = (link: string) => {
    navigator.clipboard.writeText(link)
    toast.success('Payment link copied to clipboard!')
  }

  const resendPaymentLink = async (invoiceId: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/payments/${invoiceId}/resend/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        toast.success('Payment link email resent successfully!')
      } else {
        const error = await response.json()
        toast.error(error.error || 'Failed to resend payment link')
      }
    } catch (error) {
      console.error('Error resending payment link:', error)
      toast.error('Error resending payment link')
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(amount)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'text-green-600 bg-green-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      case 'overdue': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Payment Operations Center</h1>
          <p className="text-gray-600">Complete payment management with all payment methods</p>
        </div>

        {/* Analytics Cards */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(analytics.summary.total_revenue)}
                </div>
                <p className="text-xs text-gray-500">
                  {analytics.summary.paid_invoices} paid invoices
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Pending Revenue</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {formatCurrency(analytics.summary.pending_revenue)}
                </div>
                <p className="text-xs text-gray-500">
                  {analytics.summary.pending_invoices + analytics.summary.overdue_invoices} unpaid
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Success Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {analytics.summary.payment_success_rate}%
                </div>
                <p className="text-xs text-gray-500">
                  Payment completion rate
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Invoices</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.summary.total_invoices}
                </div>
                <p className="text-xs text-gray-500">
                  All time invoices
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Payment Methods Stats */}
        {analytics && (
          <Card>
            <CardHeader>
              <CardTitle>Payment Methods Distribution</CardTitle>
              <CardDescription>Popular payment methods among your customers</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(analytics.payment_methods).map(([method, percentage]) => (
                  <div key={method} className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{percentage}%</div>
                    <div className="text-sm text-gray-600 capitalize">
                      {method === 'upi' ? 'UPI' : method}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Bulk Operations */}
        <Card>
          <CardHeader>
            <CardTitle>Bulk Payment Link Generation</CardTitle>
            <CardDescription>Generate payment links for multiple invoices at once</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                onClick={bulkGeneratePaymentLinks}
                disabled={selectedInvoices.length === 0 || bulkLoading}
                className="flex-1"
              >
                {bulkLoading ? 'Generating...' : `Generate Links (${selectedInvoices.length} selected)`}
              </Button>
              <Button
                variant="outline"
                onClick={() => setSelectedInvoices([])}
                disabled={selectedInvoices.length === 0}
              >
                Clear Selection
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Invoices List */}
        <Card>
          <CardHeader>
            <CardTitle>Pending Invoices</CardTitle>
            <CardDescription>Generate and manage payment links for unpaid invoices</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {invoices.map((invoice) => (
                <div key={invoice.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <input
                        type="checkbox"
                        checked={selectedInvoices.includes(invoice.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedInvoices([...selectedInvoices, invoice.id])
                          } else {
                            setSelectedInvoices(selectedInvoices.filter(id => id !== invoice.id))
                          }
                        }}
                        className="h-4 w-4 text-blue-600 rounded"
                      />
                      <div>
                        <div className="font-medium">#{invoice.invoice_number}</div>
                        <div className="text-sm text-gray-600">{invoice.client_name}</div>
                        <div className="text-sm text-gray-500">{invoice.client_email}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="font-medium">{formatCurrency(invoice.total_amount)}</div>
                        <div className={`text-xs px-2 py-1 rounded-full ${getStatusColor(invoice.status)}`}>
                          {invoice.status.toUpperCase()}
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        {invoice.has_payment_link ? (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyPaymentLink(invoice.payment_link!)}
                            >
                              Copy Link
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => resendPaymentLink(invoice.id)}
                            >
                              Resend Email
                            </Button>
                          </>
                        ) : (
                          <Button
                            size="sm"
                            onClick={() => generatePaymentLink(invoice.id)}
                          >
                            Generate Link
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {invoices.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No pending invoices found. All invoices are paid! 🎉
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
