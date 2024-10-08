# Generated by Django 4.2.5 on 2023-12-11 13:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("Listings", "0037_image_remove_businessimage_image_businessimage_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClientOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.FloatField(null=True, verbose_name="Amount")),
                ("isPaid", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        default="Pending", max_length=254, verbose_name="Payment Status"
                    ),
                ),
                ("details", models.CharField(blank=True, max_length=255, null=True)),
                ("currency", models.CharField(default="INR", max_length=50)),
                (
                    "provider_order_id",
                    models.CharField(max_length=40, verbose_name="Order ID"),
                ),
                (
                    "payment_id",
                    models.CharField(max_length=36, verbose_name="Payment ID"),
                ),
                (
                    "signature_id",
                    models.CharField(max_length=128, verbose_name="Signature ID"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeadBucket",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_paid", models.BooleanField(default=False)),
                (
                    "lead",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="Listings.lead"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Order2",
        ),
    ]
