# Generated by Django 4.2.5 on 2024-09-15 13:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("PremiumPlan", "0011_phonepeautopayorder"),
    ]

    operations = [
        migrations.AddField(
            model_name="phonepeautopayorder",
            name="premium_plan_is",
            field=models.IntegerField(null=True),
        ),
    ]
