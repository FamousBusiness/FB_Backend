# Generated by Django 4.2.5 on 2023-12-02 06:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0026_alter_businessmobilenumbers_mobile_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="business",
            name="locality",
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
