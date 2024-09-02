# Generated by Django 4.2.5 on 2023-12-16 12:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0048_alter_businesspageleadbucket_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="premiumplan",
            name="quantity",
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit10",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-10",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit4",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-4",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit5",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-5",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit6",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-6",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit7",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-7",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit8",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-8",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="benefit9",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-9",
            ),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="authorized",
            field=models.BooleanField(default=False, verbose_name="Authorized Tag"),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="industry_leader",
            field=models.BooleanField(
                default=False, verbose_name="Industry Leader Tag"
            ),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="job_post",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Job Post Quantity"
            ),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="lead_view",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Lead View Quantity"
            ),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="premium",
            field=models.BooleanField(default=False, verbose_name="Premium Tag"),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="sponsor",
            field=models.BooleanField(default=False, verbose_name="Sponsor Tag"),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="super",
            field=models.BooleanField(default=False, verbose_name="Super Tag"),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="trending",
            field=models.BooleanField(default=False, verbose_name="Trending Tag"),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="trusted",
            field=models.BooleanField(default=False, verbose_name="Trusted Tag"),
        ),
        migrations.AddField(
            model_name="premiumplan",
            name="verified",
            field=models.BooleanField(default=False, verbose_name="Verified Tag"),
        ),
        migrations.AddField(
            model_name="userpremiumplan",
            name="is_paid",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="plandetail",
            name="benefit1",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-1",
            ),
        ),
        migrations.AlterField(
            model_name="plandetail",
            name="benefit2",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-2",
            ),
        ),
        migrations.AlterField(
            model_name="plandetail",
            name="benefit3",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Premium plan benefit-3",
            ),
        ),
        migrations.AlterField(
            model_name="premiumplan",
            name="price",
            field=models.PositiveIntegerField(verbose_name="Plan Price"),
        ),
    ]