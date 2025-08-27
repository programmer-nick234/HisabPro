"""
Default Reminder Templates for HisabPro
Pre-built templates with different tones and stages
"""

DEFAULT_TEMPLATES = {
    # FRIENDLY TONE TEMPLATES
    'friendly_pre_due': {
        'name': 'Friendly Pre-Due Reminder',
        'tone': 'friendly',
        'stage': 'pre_due',
        'email_subject': 'Friendly Reminder: Invoice {{invoice_number}} Due Soon',
        'email_body': '''
Dear {{client_name}},

I hope this email finds you well! 

This is a gentle reminder that your invoice {{invoice_number}} for {{amount}} is due on {{due_date}}. 

We truly appreciate your business and wanted to give you a heads up so you have plenty of time to process the payment.

If you have any questions about this invoice or need any assistance, please don't hesitate to reach out. We're always here to help!

Thank you for being a valued client.

Best regards,
{{business_name}}
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'Hi {{client_name}}! Friendly reminder that invoice {{invoice_number}} ({{amount}}) is due on {{due_date}}. Thank you! - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': False,
        'include_late_fees': False
    },
    
    'friendly_due_date': {
        'name': 'Friendly Due Date Reminder',
        'tone': 'friendly',
        'stage': 'due_date',
        'email_subject': 'Invoice {{invoice_number}} Due Today',
        'email_body': '''
Hi {{client_name}},

Just a quick reminder that invoice {{invoice_number}} for {{amount}} is due today ({{due_date}}).

If you've already processed the payment, please disregard this message. If not, we'd appreciate if you could take care of it at your earliest convenience.

As always, if you have any questions or concerns, feel free to reach out to us.

Thanks so much!

{{business_name}}
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'Hi {{client_name}}! Invoice {{invoice_number}} ({{amount}}) is due today. Please process when convenient. Thanks! - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': False,
        'include_late_fees': False
    },
    
    'friendly_overdue_1': {
        'name': 'Friendly First Overdue',
        'tone': 'friendly',
        'stage': 'overdue_1',
        'email_subject': 'Gentle Reminder: Invoice {{invoice_number}} Past Due',
        'email_body': '''
Dear {{client_name}},

I hope everything is going well with you!

I wanted to reach out regarding invoice {{invoice_number}} for {{amount}}, which was due on {{due_date}} and is now {{days_overdue}} days overdue.

I understand that things can get busy, so this is just a gentle reminder to help keep things on track.

If there are any issues with the invoice or if you need to discuss payment arrangements, please let me know. We're always happy to work with our valued clients.

Looking forward to hearing from you soon.

Warm regards,
{{business_name}}
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'Hi {{client_name}}, invoice {{invoice_number}} ({{amount}}) is {{days_overdue}} days overdue. Please let us know if you need assistance. - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': True,
        'include_late_fees': False
    },
    
    # PROFESSIONAL TONE TEMPLATES
    'professional_pre_due': {
        'name': 'Professional Pre-Due Notice',
        'tone': 'professional',
        'stage': 'pre_due',
        'email_subject': 'Payment Reminder: Invoice {{invoice_number}} Due {{due_date}}',
        'email_body': '''
Dear {{client_name}},

This is to remind you that invoice {{invoice_number}} in the amount of {{amount}} is due on {{due_date}}.

Please ensure that payment is processed by the due date to avoid any late fees or service interruptions.

If you have already processed this payment, please disregard this notice. If you have any questions regarding this invoice, please contact us immediately.

We appreciate your prompt attention to this matter.

Sincerely,
{{business_name}}
Accounts Receivable Department
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'Payment reminder: Invoice {{invoice_number}} ({{amount}}) due {{due_date}}. Please process payment by due date. - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': False,
        'include_late_fees': False
    },
    
    'professional_overdue_2': {
        'name': 'Professional Second Notice',
        'tone': 'professional',
        'stage': 'overdue_2',
        'email_subject': 'SECOND NOTICE: Invoice {{invoice_number}} - {{days_overdue}} Days Overdue',
        'email_body': '''
Dear {{client_name}},

This is our second notice regarding invoice {{invoice_number}} in the amount of {{amount}}, which was due on {{due_date}} and is now {{days_overdue}} days overdue.

Despite our previous reminder, payment has not been received. We request immediate payment to bring your account current.

If payment has been sent, please provide payment details so we can locate and apply the payment. If there are any disputes regarding this invoice, please contact us immediately to resolve the matter.

Failure to respond to this notice may result in additional collection activities and potential service suspension.

We trust you will give this matter your immediate attention.

Sincerely,
{{business_name}}
Accounts Receivable Department
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'SECOND NOTICE: Invoice {{invoice_number}} ({{amount}}) is {{days_overdue}} days overdue. Immediate payment required. - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': True,
        'include_late_fees': True
    },
    
    # FIRM TONE TEMPLATES
    'firm_overdue_2': {
        'name': 'Firm Second Overdue Notice',
        'tone': 'firm',
        'stage': 'overdue_2',
        'email_subject': 'URGENT: Payment Required for Invoice {{invoice_number}}',
        'email_body': '''
{{client_name}},

Your account is seriously past due. Invoice {{invoice_number}} for {{amount}} was due on {{due_date}} and is now {{days_overdue}} days overdue.

This is your final courtesy notice before we take further action. Payment must be received within 5 business days to avoid:
• Additional late fees and interest charges
• Referral to our collections department
• Potential legal action
• Suspension of services

If you are experiencing financial difficulties, contact us immediately to discuss payment arrangements. Ignoring this notice will not make it go away.

Pay online immediately using the link below or contact us today.

{{business_name}}
Collections Department
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'URGENT: Invoice {{invoice_number}} ({{amount}}) {{days_overdue}} days overdue. Payment required within 5 days to avoid collections. - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': True,
        'include_late_fees': True
    },
    
    # URGENT TONE TEMPLATES
    'urgent_overdue_3': {
        'name': 'Urgent Final Demand',
        'tone': 'urgent',
        'stage': 'overdue_3',
        'email_subject': 'URGENT FINAL DEMAND: Invoice {{invoice_number}} - {{days_overdue}} Days Overdue',
        'email_body': '''
{{client_name}},

This is your FINAL NOTICE for invoice {{invoice_number}} in the amount of {{amount}}.

Your payment is now {{days_overdue}} days overdue. Despite multiple attempts to contact you, this invoice remains unpaid.

IMMEDIATE ACTION REQUIRED:
• Payment must be received within 48 hours
• Failure to pay will result in immediate collection action
• Your account will be reported to credit agencies
• Legal proceedings may be initiated
• All future services will be suspended

This is not a threat - it is a statement of our collection policy. We have been patient, but your continued non-payment forces us to take these steps.

Contact us immediately if you wish to avoid these consequences.

{{business_name}}
Collections Department
{{business_email}}
{{business_phone}}
        ''',
        'sms_message': 'FINAL NOTICE: Invoice {{invoice_number}} ({{amount}}) {{days_overdue}} days overdue. Payment required in 48 hours or collections action begins. - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': True,
        'include_late_fees': True
    },
    
    # FINAL NOTICE TEMPLATES
    'final_notice': {
        'name': 'Final Legal Notice',
        'tone': 'final_notice',
        'stage': 'overdue_3',
        'email_subject': 'FINAL LEGAL NOTICE - Invoice {{invoice_number}} - Account {{invoice_number}}',
        'email_body': '''
FINAL LEGAL NOTICE

TO: {{client_name}}
RE: Invoice {{invoice_number}} - Amount Due: {{amount}}

This account is now {{days_overdue}} days past due. This constitutes our final attempt to collect this debt before taking legal action.

NOTICE OF INTENT TO:
1. Report this delinquent account to all major credit bureaus
2. Engage legal counsel for collection proceedings
3. File suit for the full amount plus court costs, attorney fees, and interest
4. Pursue all available legal remedies including wage garnishment and asset seizure

You have 72 hours from receipt of this notice to contact us to resolve this matter. After this time, your account will be forwarded to our legal department without further notice.

This is a legal notice. Failure to respond will result in immediate legal action.

{{business_name}}
Legal Collections Department
{{business_email}}
{{business_phone}}

NOTICE: This is an attempt to collect a debt. Any information obtained will be used for that purpose.
        ''',
        'sms_message': 'FINAL LEGAL NOTICE: Invoice {{invoice_number}} ({{amount}}) forwarded to legal in 72 hours. Contact immediately. - {{business_name}}',
        'include_pdf_attachment': True,
        'include_payment_link': True,
        'include_payment_history': True,
        'include_late_fees': True
    }
}


def create_default_templates(user):
    """Create default reminder templates for a new user"""
    from .reminder_models import ReminderTemplate
    
    created_templates = []
    
    for template_key, template_data in DEFAULT_TEMPLATES.items():
        template, created = ReminderTemplate.objects.get_or_create(
            user=user,
            tone=template_data['tone'],
            stage=template_data['stage'],
            defaults=template_data
        )
        
        if created:
            created_templates.append(template)
    
    return created_templates


def create_default_rules(user, templates_dict):
    """Create default reminder rules with different escalation paths"""
    from .reminder_models import ReminderRule
    from decimal import Decimal
    
    # Small Invoice Rule (₹0 - ₹10,000) - Email Only
    small_rule = ReminderRule.objects.create(
        user=user,
        name='Small Invoices (₹0 - ₹10,000) - Email Only',
        min_invoice_amount=Decimal('0.00'),
        max_invoice_amount=Decimal('10000.00'),
        days_before_due=3,
        days_after_due_1=1,
        days_after_due_2=7,
        days_after_due_3=15,
        use_email=True,
        use_sms=False,  # SMS disabled to keep system cost-free
        pre_due_template=templates_dict.get('friendly_pre_due'),
        due_date_template=templates_dict.get('friendly_due_date'),
        overdue_1_template=templates_dict.get('friendly_overdue_1'),
        overdue_2_template=templates_dict.get('professional_overdue_2'),
        overdue_3_template=templates_dict.get('firm_overdue_2'),
        max_reminders=4
    )
    
    # Medium Invoice Rule (₹10,001 - ₹50,000) - Email Only
    medium_rule = ReminderRule.objects.create(
        user=user,
        name='Medium Invoices (₹10,001 - ₹50,000) - Email Only',
        min_invoice_amount=Decimal('10000.01'),
        max_invoice_amount=Decimal('50000.00'),
        days_before_due=5,
        days_after_due_1=1,
        days_after_due_2=5,
        days_after_due_3=10,
        use_email=True,
        use_sms=False,  # SMS disabled to keep system cost-free
        pre_due_template=templates_dict.get('professional_pre_due'),
        due_date_template=templates_dict.get('friendly_due_date'),
        overdue_1_template=templates_dict.get('professional_overdue_2'),
        overdue_2_template=templates_dict.get('firm_overdue_2'),
        overdue_3_template=templates_dict.get('urgent_overdue_3'),
        max_reminders=5
    )
    
    # Large Invoice Rule (₹50,001+) - Email Only with More Frequent Reminders
    large_rule = ReminderRule.objects.create(
        user=user,
        name='Large Invoices (₹50,001+) - Email Priority',
        min_invoice_amount=Decimal('50000.01'),
        max_invoice_amount=None,
        days_before_due=7,
        days_after_due_1=1,
        days_after_due_2=3,
        days_after_due_3=7,
        use_email=True,
        use_sms=False,  # SMS disabled to keep system cost-free
        pre_due_template=templates_dict.get('professional_pre_due'),
        due_date_template=templates_dict.get('professional_overdue_2'),
        overdue_1_template=templates_dict.get('firm_overdue_2'),
        overdue_2_template=templates_dict.get('urgent_overdue_3'),
        overdue_3_template=templates_dict.get('final_notice'),
        max_reminders=6  # Extra reminder for large amounts
    )
    
    return [small_rule, medium_rule, large_rule]


def setup_reminder_system_for_user(user):
    """Complete setup of reminder system for a new user"""
    # Create templates
    templates = create_default_templates(user)
    
    # Create template lookup dict
    templates_dict = {}
    for template in templates:
        key = f"{template.tone}_{template.stage}"
        templates_dict[key] = template
    
    # Create rules
    rules = create_default_rules(user, templates_dict)
    
    return {
        'templates_created': len(templates),
        'rules_created': len(rules),
        'templates': templates,
        'rules': rules
    }
