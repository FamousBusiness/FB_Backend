# Generated by Django 4.2.5 on 2024-01-10 08:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("JOB", "0010_alter_applicanteducationdetails_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobseekerprofile",
            name="current_salary",
            field=models.CharField(
                blank=True, max_length=15, null=True, verbose_name="Current Salary"
            ),
        ),
    ]
