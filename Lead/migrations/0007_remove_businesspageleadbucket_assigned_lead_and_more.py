# Generated by Django 4.2.5 on 2024-01-30 05:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Lead", "0006_leadorder"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="businesspageleadbucket",
            name="assigned_lead",
        ),
        migrations.RemoveField(
            model_name="businesspageleadbucket",
            name="own_lead",
        ),
        migrations.RemoveField(
            model_name="businesspageleadbucket",
            name="viewed_lead",
        ),
    ]
