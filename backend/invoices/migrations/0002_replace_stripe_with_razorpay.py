# Generated manually to replace Stripe with Razorpay

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoice',
            old_name='stripe_payment_link',
            new_name='razorpay_payment_link',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='stripe_payment_intent',
            new_name='razorpay_order_id',
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(default='razorpay', max_length=50),
        ),
    ]
