# Generated by Django 4.2.5 on 2024-01-08 10:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("Listings", "0073_delete_banner"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Banner",
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
                (
                    "image",
                    models.FileField(
                        default="Banner/default-banner.jpeg",
                        upload_to="Category_Banner",
                    ),
                ),
                ("state", models.CharField(max_length=25, verbose_name="State")),
                ("city", models.CharField(max_length=25, verbose_name="City")),
                ("verified", models.BooleanField(default=False)),
                ("expired", models.BooleanField(default=False)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Listings.category",
                    ),
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
    ]
