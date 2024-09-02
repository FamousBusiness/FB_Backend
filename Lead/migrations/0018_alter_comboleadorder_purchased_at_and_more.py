# Generated by Django 4.2.5 on 2024-02-06 10:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Lead", "0017_alter_assignedleadperpremiumplan_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comboleadorder",
            name="purchased_at",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Purchased Date"
            ),
        ),
        migrations.AlterField(
            model_name="leadorder",
            name="purchased_at",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Purchased Date"
            ),
        ),
    ]
