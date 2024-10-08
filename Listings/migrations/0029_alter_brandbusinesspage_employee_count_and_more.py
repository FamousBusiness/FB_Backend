# Generated by Django 4.2.5 on 2023-12-05 13:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0028_category_b2b2c"),
    ]

    operations = [
        migrations.AlterField(
            model_name="brandbusinesspage",
            name="employee_count",
            field=models.CharField(
                blank=True,
                max_length=225,
                null=True,
                verbose_name="Total Number of Employee",
            ),
        ),
        migrations.AlterField(
            model_name="business",
            name="employee_count",
            field=models.CharField(
                blank=True, max_length=225, null=True, verbose_name="Number of Employee"
            ),
        ),
    ]
