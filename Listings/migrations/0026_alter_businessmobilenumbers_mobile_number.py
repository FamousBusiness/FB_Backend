# Generated by Django 4.2.5 on 2023-11-30 14:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "Listings",
            "0025_alter_business_mobile_number_alter_business_pincode_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="businessmobilenumbers",
            name="mobile_number",
            field=models.CharField(
                max_length=20, unique=True, verbose_name="Mobile Number"
            ),
        ),
    ]
