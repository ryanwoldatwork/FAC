# Generated by Django 4.2.6 on 2023-11-23 00:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("support", "0005_alter_cognizantbaseline_cognizant_agency_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminApiEvent",
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
                ("api_key_uuid", models.TextField()),
                (
                    "event",
                    models.CharField(
                        choices=[
                            ("tribal-access-email-added", "Tribal access granted"),
                            ("tribal-access-email-removed", "Trbial access removed"),
                        ]
                    ),
                ),
                ("event_data", models.JSONField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
