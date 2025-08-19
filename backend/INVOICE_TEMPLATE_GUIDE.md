# 🎨 Professional A4 Invoice Template Guide

## 📋 **Template Overview**

This professional invoice template includes all the sections you requested and is designed for A4 page size with proper formatting for both screen viewing and PDF generation.

## 🔹 **Template Sections**

### **1. Header Section**
- **Logo**: Business logo (optional, configurable)
- **Business Information**: 
  - Business name
  - Contact info (email, phone, address)
- **Client Information**: 
  - Client name & address
  - Client contact details

### **2. Invoice Details Section**
- **Invoice Number**: Auto-generated (e.g., INV-2024-001)
- **Issue Date**: Date when invoice was created
- **Due Date**: Payment due date
- **Status Badge**: Visual status indicator (Draft, Pending, Paid, Overdue)
- **Payment Terms**: Configurable payment terms

### **3. Items Table**
Dynamic table with columns:
- **Item/Service**: Name of the service or product
- **Description**: Detailed description
- **Quantity**: Number of units
- **Rate**: Unit price
- **Tax**: Tax amount per item
- **Amount**: Total for this item

### **4. Totals Section**
- **Subtotal**: Sum of all items
- **Tax**: Total tax amount (optional)
- **Discount**: Discount amount (optional)
- **Final Total**: Grand total

### **5. Footer Section**
- **Notes**: Custom notes (e.g., "Thank you for your business")
- **Signature Lines**: 
  - Authorized signature
  - Date signature
- **Thank You Message**: Professional closing

## 🎨 **Design Features**

### **A4 Page Setup**
- **Size**: 210mm × 297mm (A4)
- **Margins**: 20mm on all sides
- **Print-friendly**: Optimized for PDF generation

### **Professional Styling**
- **Color Scheme**: Professional dark blue (#2c3e50) with gray accents
- **Typography**: Clean Arial font family
- **Status Badges**: Color-coded status indicators
- **Responsive Layout**: Works on different screen sizes

### **Visual Elements**
- **Header Border**: Professional bottom border
- **Alternating Row Colors**: Easy-to-read table rows
- **Highlighted Totals**: Bold styling for important numbers
- **Signature Lines**: Professional signature areas

## 🚀 **Usage**

### **1. Preview Sample Template**
```bash
# Test the template with sample data
python test_invoice_template.py
```

### **2. API Endpoints**

#### **Sample Invoice Preview** (No Auth Required)
```
GET /api/preview/sample-invoice/
```
- Shows template with sample data
- Perfect for testing the design

#### **Real Invoice Preview** (Auth Required)
```
GET /api/supabase/invoices/{invoice_id}/preview/
```
- Shows template with real invoice data
- Requires authentication

#### **PDF Generation** (Auth Required)
```
GET /api/supabase/invoices/{invoice_id}/pdf-template/
```
- Generates PDF version of invoice
- Requires WeasyPrint for true PDF generation

### **3. Configuration**

#### **Business Information Settings**
Edit `backend/hisabpro/settings.py`:
```python
# Business Information for Invoice Templates
BUSINESS_NAME = 'Your Business Name'
BUSINESS_EMAIL = 'contact@yourbusiness.com'
BUSINESS_PHONE = '+1 (555) 123-4567'
BUSINESS_ADDRESS = '123 Business Street\nCity, State 12345'
BUSINESS_LOGO = None  # Path to logo file
PAYMENT_TERMS = 'Net 30 days'
```

#### **Customizing the Template**
The template is located at: `backend/invoices/templates/invoice_template.html`

## 📊 **Data Structure**

### **Invoice Object**
```python
{
    'id': 'invoice-id',
    'invoice_number': 'INV-2024-001',
    'client_name': 'John Doe',
    'client_email': 'john@example.com',
    'client_phone': '+1 (555) 123-4567',
    'client_address': '123 Client St\nCity, State',
    'invoice_date': '2024-01-15',
    'due_date': '2024-02-14',
    'status': 'pending',
    'subtotal': 1000.00,
    'tax_rate': 10.0,
    'tax_amount': 100.00,
    'discount_amount': 50.00,
    'total_amount': 1050.00,
    'notes': 'Thank you for your business',
    'items': [
        {
            'name': 'Web Development',
            'description': 'Custom website development',
            'quantity': 1,
            'unit_price': 800.00,
            'tax_amount': 80.00,
            'total': 880.00
        }
    ]
}
```

## 🛠 **Technical Implementation**

### **Template Engine**
- **Django Templates**: Uses Django's template engine
- **CSS Styling**: Embedded CSS for consistent rendering
- **Print Media**: Optimized for PDF generation

### **PDF Generation**
- **WeasyPrint**: Primary PDF generation library
- **Fallback**: HTML output if WeasyPrint not available
- **Font Configuration**: Proper font handling

### **File Structure**
```
backend/
├── invoices/
│   ├── templates/
│   │   └── invoice_template.html    # Main template
│   ├── pdf_views.py                 # PDF generation views
│   └── urls.py                      # URL routing
├── test_invoice_template.py         # Test script
└── INVOICE_TEMPLATE_GUIDE.md        # This guide
```

## 🎯 **Features Summary**

### ✅ **What's Included**
- ✅ **A4 Page Size**: Perfect for printing
- ✅ **Professional Header**: Logo, business info, client info
- ✅ **Invoice Details**: Number, dates, status, payment terms
- ✅ **Dynamic Items Table**: Supports multiple services/products
- ✅ **Totals Section**: Subtotal, tax, discount, final total
- ✅ **Footer**: Notes, signature lines, thank you message
- ✅ **Status Badges**: Visual status indicators
- ✅ **Print-Friendly**: Optimized for PDF generation
- ✅ **Responsive Design**: Works on different screen sizes
- ✅ **Configurable**: Easy to customize business information

### 🔧 **Customization Options**
- **Business Information**: Name, contact, logo, address
- **Payment Terms**: Configurable payment terms
- **Color Scheme**: Professional dark blue theme
- **Logo Support**: Optional business logo
- **Notes Section**: Custom notes for each invoice

## 📱 **Frontend Integration**

### **Download PDF**
```javascript
// Frontend code to download PDF
const downloadPDF = async (invoiceId) => {
    const response = await fetch(`/api/supabase/invoices/${invoiceId}/pdf-template/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `invoice_${invoiceId}.pdf`;
        link.click();
    }
};
```

### **Preview Invoice**
```javascript
// Frontend code to preview invoice
const previewInvoice = async (invoiceId) => {
    const response = await fetch(`/api/supabase/invoices/${invoiceId}/preview/`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (response.ok) {
        const html = await response.text();
        // Open in new window or modal
        const newWindow = window.open('', '_blank');
        newWindow.document.write(html);
    }
};
```

## 🎉 **Ready to Use!**

Your professional A4 invoice template is now ready! It includes all the sections you requested and is fully integrated with your existing invoice system.

### **Next Steps**
1. **Test the template**: Run `python test_invoice_template.py`
2. **Customize business info**: Update settings in `settings.py`
3. **Add your logo**: Set `BUSINESS_LOGO` path in settings
4. **Integrate with frontend**: Use the provided API endpoints

**Your invoice system now has a professional, A4-sized template that looks great both on screen and in print! 🚀**
