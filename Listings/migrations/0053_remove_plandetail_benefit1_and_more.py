# Generated by Django 4.2.5 on 2023-12-18 12:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Listings", "0052_remove_premiumplan_price_plandetail_price"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit1",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit10",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit2",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit3",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit4",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit5",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit6",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit7",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit8",
        ),
        migrations.RemoveField(
            model_name="plandetail",
            name="benefit9",
        ),
        migrations.AddField(
            model_name="plandetail",
            name="authorized",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Authorized Benefits",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="extra_benefits",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Extra Benefits"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="extra_benefits1",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Extra Benefits-1"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="industry_leader",
            field=models.CharField(
                blank=True,
                max_length=300,
                null=True,
                verbose_name="Industry Leader Benefits",
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="premium",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Premium Benefits"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="sponsor",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Sponsor Benefits"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="super",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Super Benefits"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="trending",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Trending Benefits"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="trusted",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Trusted Benefits"
            ),
        ),
        migrations.AddField(
            model_name="plandetail",
            name="verified",
            field=models.CharField(
                blank=True, max_length=300, null=True, verbose_name="Verified Benefits"
            ),
        ),
    ]
