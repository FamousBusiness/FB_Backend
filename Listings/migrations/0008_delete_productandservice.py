# Generated by Django 4.2.5 on 2023-11-25 12:42

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0007_business_cin_no_business_din_business_roc_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProductAndService",
        ),
    ]