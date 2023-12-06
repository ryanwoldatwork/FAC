# Generated by Django 4.2.6 on 2023-11-27 19:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0005_alter_general_cognizant_agency_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="MigrationChangeRecord",
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
                ("audit_year", models.TextField(blank=True, null=True)),
                ("dbkey", models.TextField(blank=True, null=True)),
                ("report_id", models.TextField(blank=True, null=True)),
                (
                    "run_datetime",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("census_data", models.JSONField(blank=True, null=True)),
                ("gsa_fac_data", models.JSONField(blank=True, null=True)),
                ("transformation_function", models.TextField(blank=True, null=True)),
            ],
        ),
    ]