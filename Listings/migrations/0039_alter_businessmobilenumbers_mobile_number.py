# Generated by Django 4.2.5 on 2023-12-11 17:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0038_clientorder_leadbucket_delete_order2"),
    ]

    operations = [
        migrations.AlterField(
            model_name="businessmobilenumbers",
            name="mobile_number",
            field=models.CharField(
                max_length=40, unique=True, verbose_name="Mobile Number"
            ),
        ),
    ]
