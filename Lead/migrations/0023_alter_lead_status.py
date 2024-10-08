# Generated by Django 4.2.5 on 2024-02-14 10:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Lead", "0022_lead_category_lead"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Open", "Open"),
                    ("Closed", "Closed"),
                    ("Expired", "Expired"),
                    ("High Priority", "High Priority"),
                    ("Premium Quality", "Premium Quality"),
                    ("Viewed", "Viewed"),
                    ("Purchased", "Purchased"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
