# Generated by Django 4.2.5 on 2024-02-08 11:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Lead", "0019_alter_comboleadorder_transaction_id_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="mail_sent",
            field=models.BooleanField(default=False),
        ),
    ]
