'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider } from '@/hooks/useAuth';
import { invoiceAPI } from '@/lib/api';
import DashboardLayout from '@/components/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Trash2, Save, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';

// Force dynamic rendering to prevent SSR issues
export const dynamic = 'force-dynamic';

interface InvoiceItem {
  description: string;
  quantity: number;
  unit_price: number;
  total: number;
}

interface InvoiceFormData {
  client_name: string;
  client_email: string;
  client_phone: string;
  client_address: string;
  issue_date: string;
  due_date: string;
  tax_rate: number;
  notes: string;
  terms_conditions: string;
  items: InvoiceItem[];
}

function CreateInvoicePage() {
  return (
    <AuthProvider>
      <CreateInvoiceContent />
    </AuthProvider>
  );
}

function CreateInvoiceContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState<InvoiceFormData>({
    client_name: '',
    client_email: '',
    client_phone: '',
    client_address: '',
    issue_date: new Date().toISOString().split('T')[0],
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days from now
    tax_rate: 18,
    notes: '',
    terms_conditions: '',
    items: [
      {
        description: '',
        quantity: 1,
        unit_price: 0,
        total: 0,
      },
    ],
  });

  const calculateItemTotal = (item: InvoiceItem) => {
    return item.quantity * item.unit_price;
  };

  const calculateSubtotal = () => {
    return formData.items.reduce((sum, item) => sum + calculateItemTotal(item), 0);
  };

  const calculateTaxAmount = () => {
    return (calculateSubtotal() * formData.tax_rate) / 100;
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTaxAmount();
  };

  const handleInputChange = (field: keyof InvoiceFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleItemChange = (index: number, field: keyof InvoiceItem, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = {
      ...newItems[index],
      [field]: value,
    };
    
    // Recalculate total for this item
    newItems[index].total = calculateItemTotal(newItems[index]);
    
    setFormData(prev => ({
      ...prev,
      items: newItems,
    }));
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [
        ...prev.items,
        {
          description: '',
          quantity: 1,
          unit_price: 0,
          total: 0,
        },
      ],
    }));
  };

  const removeItem = (index: number) => {
    if (formData.items.length > 1) {
      setFormData(prev => ({
        ...prev,
        items: prev.items.filter((_, i) => i !== index),
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.client_name || !formData.client_email) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Validate items
    const validItems = formData.items.filter(item => 
      item.description && item.quantity > 0 && item.unit_price > 0
    );
    
    if (validItems.length === 0) {
      toast.error('Please add at least one valid item');
      return;
    }

    setIsSubmitting(true);

    try {
      // Simplified invoice data that matches our backend structure
      const invoiceData = {
        client_name: formData.client_name,
        client_email: formData.client_email,
        total_amount: calculateTotal(),
        status: 'pending',
        notes: formData.notes || '',
        // Optional fields that may or may not exist in the table
        ...(formData.client_phone && { client_phone: formData.client_phone }),
        ...(formData.client_address && { client_address: formData.client_address }),
      };

      await invoiceAPI.createInvoice(invoiceData);
      toast.success('Invoice created successfully!');
      router.push('/invoices');
    } catch (error: any) {
      console.error('Error creating invoice:', error);
      toast.error(error.response?.data?.error || 'Failed to create invoice');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link
              href="/invoices"
              className="btn btn-secondary"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Invoices
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Create New Invoice</h1>
              <p className="mt-1 text-sm text-gray-500">
                Create a new invoice for your client
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Client Information */}
          <Card>
            <CardHeader>
              <CardTitle>Client Information</CardTitle>
              <CardDescription>
                Enter your client's details
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Client Name *
                  </label>
                  <input
                    type="text"
                    value={formData.client_name}
                    onChange={(e) => handleInputChange('client_name', e.target.value)}
                    className="input w-full"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Client Email *
                  </label>
                  <input
                    type="email"
                    value={formData.client_email}
                    onChange={(e) => handleInputChange('client_email', e.target.value)}
                    className="input w-full"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Client Phone
                  </label>
                  <input
                    type="tel"
                    value={formData.client_phone}
                    onChange={(e) => handleInputChange('client_phone', e.target.value)}
                    className="input w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tax Rate (%)
                  </label>
                  <input
                    type="number"
                    value={formData.tax_rate}
                    onChange={(e) => handleInputChange('tax_rate', parseFloat(e.target.value) || 0)}
                    className="input w-full"
                    min="0"
                    max="100"
                    step="0.01"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Client Address
                </label>
                <textarea
                  value={formData.client_address}
                  onChange={(e) => handleInputChange('client_address', e.target.value)}
                  className="input w-full"
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>

          {/* Invoice Details */}
          <Card>
            <CardHeader>
              <CardTitle>Invoice Details</CardTitle>
              <CardDescription>
                Set invoice dates and terms
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Issue Date
                  </label>
                  <input
                    type="date"
                    value={formData.issue_date}
                    onChange={(e) => handleInputChange('issue_date', e.target.value)}
                    className="input w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Due Date
                  </label>
                  <input
                    type="date"
                    value={formData.due_date}
                    onChange={(e) => handleInputChange('due_date', e.target.value)}
                    className="input w-full"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Invoice Items */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Invoice Items</CardTitle>
                  <CardDescription>
                    Add products or services to your invoice
                  </CardDescription>
                </div>
                <Button
                  type="button"
                  onClick={addItem}
                  className="btn btn-secondary"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Item
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {formData.items.map((item, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Description
                        </label>
                        <input
                          type="text"
                          value={item.description}
                          onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                          className="input w-full"
                          placeholder="Product or service description"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Quantity
                        </label>
                        <input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 0)}
                          className="input w-full"
                          min="1"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Unit Price
                        </label>
                        <input
                          type="number"
                          value={item.unit_price}
                          onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                          className="input w-full"
                          min="0"
                          step="0.01"
                        />
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-4">
                      <div className="text-sm text-gray-600">
                        Total: ₹{calculateItemTotal(item).toFixed(2)}
                      </div>
                      {formData.items.length > 1 && (
                        <Button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="btn btn-danger btn-sm"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Additional Information */}
          <Card>
            <CardHeader>
              <CardTitle>Additional Information</CardTitle>
              <CardDescription>
                Add notes and terms to your invoice
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  className="input w-full"
                  rows={3}
                  placeholder="Additional notes for the client"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Terms & Conditions
                </label>
                <textarea
                  value={formData.terms_conditions}
                  onChange={(e) => handleInputChange('terms_conditions', e.target.value)}
                  className="input w-full"
                  rows={3}
                  placeholder="Payment terms and conditions"
                />
              </div>
            </CardContent>
          </Card>

          {/* Invoice Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Invoice Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="font-medium">₹{calculateSubtotal().toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tax ({formData.tax_rate}%):</span>
                  <span className="font-medium">₹{calculateTaxAmount().toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t pt-2">
                  <span>Total:</span>
                  <span>₹{calculateTotal().toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <Link
              href="/invoices"
              className="btn btn-secondary"
            >
              Cancel
            </Link>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Create Invoice
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}

export default function Page() {
  return <CreateInvoicePage />;
}
