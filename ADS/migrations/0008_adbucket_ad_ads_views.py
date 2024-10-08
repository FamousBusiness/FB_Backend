# Generated by Django 4.2.5 on 2024-01-22 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ADS", "0007_rename_views_adbucket_assigned_view_adbucket_viewed_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="adbucket",
            name="ad",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="ADS.ads"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ads",
            name="views",
            field=models.BigIntegerField(default=0),
        ),
    ]
