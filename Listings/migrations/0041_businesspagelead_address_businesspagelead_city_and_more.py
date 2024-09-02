# Generated by Django 4.2.5 on 2023-12-12 12:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0040_brandbusinesspage_din"),
    ]

    operations = [
        migrations.AddField(
            model_name="businesspagelead",
            name="address",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="businesspagelead",
            name="city",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="businesspagelead",
            name="pincode",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="businesspagelead",
            name="state",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="lead",
            name="address",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="lead",
            name="city",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="lead",
            name="pincode",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="lead",
            name="state",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]