# Generated by Django 4.2.5 on 2024-01-30 14:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("PremiumPlan", "0004_trialplanrequest_lead_view"),
    ]

    operations = [
        migrations.AddField(
            model_name="premiumplanbenefits",
            name="is_paid",
            field=models.BooleanField(default=False),
        ),
    ]
