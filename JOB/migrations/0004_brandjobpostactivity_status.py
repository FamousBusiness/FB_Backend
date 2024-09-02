# Generated by Django 4.2.5 on 2024-01-02 07:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("JOB", "0003_businessjobpostactivity_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="brandjobpostactivity",
            name="status",
            field=models.CharField(
                choices=[
                    ("Selected", "Selected"),
                    ("Rejected", "Rejected"),
                    ("Pending", "Pending"),
                    ("Viewed", "Viewed"),
                    ("Applied", "Applied"),
                ],
                default="Applied",
                max_length=20,
                verbose_name="Job Status",
            ),
        ),
    ]