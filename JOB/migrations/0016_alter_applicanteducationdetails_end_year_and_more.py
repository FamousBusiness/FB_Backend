# Generated by Django 4.2.5 on 2024-01-16 13:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("JOB", "0015_alter_applicanteducationdetails_end_year_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="applicanteducationdetails",
            name="end_year",
            field=models.CharField(
                blank=True, max_length=5, null=True, verbose_name="End Year"
            ),
        ),
        migrations.AlterField(
            model_name="applicanteducationdetails",
            name="start_year",
            field=models.CharField(
                blank=True, max_length=5, null=True, verbose_name="Start Year"
            ),
        ),
    ]
