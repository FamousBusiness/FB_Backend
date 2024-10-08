# Generated by Django 4.2.5 on 2024-01-20 08:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ADS", "0003_alter_ads_pictures"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ads",
            name="ad_id",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="ads",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]
