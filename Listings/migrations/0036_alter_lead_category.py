# Generated by Django 4.2.5 on 2023-12-06 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0035_alter_lead_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="Listings.category"
            ),
        ),
    ]
