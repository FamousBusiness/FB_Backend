# Generated by Django 4.2.5 on 2023-12-19 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0053_remove_plandetail_benefit1_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Listings.premiumplan",
            ),
        ),
    ]