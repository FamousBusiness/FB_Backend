# Generated by Django 4.2.5 on 2023-12-28 07:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0059_alter_categorywisebusinesssideimage_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="JOBCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(max_length=250, verbose_name="Job Category Name"),
                ),
                (
                    "image",
                    models.FileField(
                        default="Job_Category/default.jpeg", upload_to="Job_Category"
                    ),
                ),
                ("trending", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["id"],
            },
        ),
    ]