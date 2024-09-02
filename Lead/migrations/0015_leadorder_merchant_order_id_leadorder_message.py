# Generated by Django 4.2.5 on 2024-02-05 10:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Lead", "0014_alter_leadorder_transaction_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="leadorder",
            name="merchant_order_id",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Merchant Order ID"
            ),
        ),
        migrations.AddField(
            model_name="leadorder",
            name="message",
            field=models.CharField(
                blank=True,
                default="Phonpe Message",
                max_length=100,
                null=True,
                verbose_name="Phonepe Message",
            ),
        ),
    ]
