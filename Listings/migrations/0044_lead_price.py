# Generated by Django 4.2.5 on 2023-12-13 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0043_leadprice_remove_lead_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="price",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Listings.leadprice",
            ),
        ),
    ]
