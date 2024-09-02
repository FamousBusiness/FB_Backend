# Generated by Django 4.2.5 on 2024-01-09 07:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("JOB", "0005_alter_brandjobpost_company"),
    ]

    operations = [
        migrations.AddField(
            model_name="brandjobpost",
            name="full_time",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="brandjobpost",
            name="internship",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="brandjobpost",
            name="part_time",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="brandjobpost",
            name="work_abroad",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="brandjobpost",
            name="work_from_home",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="businesspagejobpost",
            name="full_time",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="businesspagejobpost",
            name="internship",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="businesspagejobpost",
            name="part_time",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="businesspagejobpost",
            name="work_abroad",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="businesspagejobpost",
            name="work_from_home",
            field=models.BooleanField(default=False),
        ),
    ]
