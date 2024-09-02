# Generated by Django 4.2.5 on 2024-01-06 09:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0068_remove_businesspageleadbucket_business_page_and_more"),
        ("Lead", "0003_alter_comboleadbucket_remaining_lead"),
    ]

    operations = [
        migrations.AddField(
            model_name="comboleadbucket",
            name="category",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Listings.category",
            ),
        ),
    ]