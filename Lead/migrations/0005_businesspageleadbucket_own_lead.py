# Generated by Django 4.2.5 on 2024-01-11 12:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Lead", "0004_comboleadbucket_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="businesspageleadbucket",
            name="own_lead",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Lead.businesspagelead",
            ),
        ),
    ]
