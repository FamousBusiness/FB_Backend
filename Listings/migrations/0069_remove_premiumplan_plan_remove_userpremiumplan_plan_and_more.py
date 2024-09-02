# Generated by Django 4.2.5 on 2024-01-08 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("PremiumPlan", "0001_initial"),
        ("Listings", "0068_remove_businesspageleadbucket_business_page_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="premiumplan",
            name="plan",
        ),
        migrations.RemoveField(
            model_name="userpremiumplan",
            name="plan",
        ),
        migrations.RemoveField(
            model_name="userpremiumplan",
            name="user",
        ),
        migrations.AlterField(
            model_name="assigned_benefits",
            name="plan",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="Plan_benefits",
                to="PremiumPlan.premiumplan",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="PremiumPlan.premiumplan",
            ),
        ),
        migrations.AlterField(
            model_name="wallet",
            name="plan",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="PremiumPlan.premiumplan",
            ),
        ),
        migrations.DeleteModel(
            name="PlanCancelRequest",
        ),
        migrations.DeleteModel(
            name="PlanDetail",
        ),
        migrations.DeleteModel(
            name="PremiumPlan",
        ),
        migrations.DeleteModel(
            name="UserPremiumPlan",
        ),
    ]