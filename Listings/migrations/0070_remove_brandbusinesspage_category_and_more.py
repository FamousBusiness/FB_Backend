# Generated by Django 4.2.5 on 2024-01-08 08:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Brands", "0001_initial"),
        ("JOB", "0005_alter_brandjobpost_company"),
        (
            "Listings",
            "0069_remove_premiumplan_plan_remove_userpremiumplan_plan_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="brandbusinesspage",
            name="category",
        ),
        migrations.RemoveField(
            model_name="brandbusinesspage",
            name="owner",
        ),
        migrations.RemoveField(
            model_name="brandproducts",
            name="brand",
        ),
        migrations.AlterField(
            model_name="business",
            name="brand",
            field=models.ManyToManyField(
                blank=True, to="Brands.brandbusinesspage", verbose_name="Brand Name"
            ),
        ),
        migrations.DeleteModel(
            name="BrandBanner",
        ),
        migrations.DeleteModel(
            name="BrandBusinessPage",
        ),
        migrations.DeleteModel(
            name="BrandProducts",
        ),
    ]