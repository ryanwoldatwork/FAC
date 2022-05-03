# Generated by Django 4.0.4 on 2022-04-22 19:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("audit", "0001_initial_sac"),
    ]

    operations = [
        migrations.AlterField(
            model_name="singleauditchecklist",
            name="user_provided_organization_type",
            field=models.CharField(
                choices=[
                    ("state", "State"),
                    ("local", "Local Government"),
                    ("tribal", "Indian Tribe or Tribal Organization"),
                    ("higher-ed", "Institution of higher education (IHE)"),
                    ("non-profit", "Non-profit"),
                    ("unknown", "Unknown"),
                    ("none", "None of these (for example, for-profit"),
                ],
                max_length=12,
            ),
        ),
        migrations.CreateModel(
            name="Access",
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
                    "role",
                    models.CharField(
                        choices=[
                            ("auditee_contact", "Auditee Contact"),
                            ("auditee_cert", "Auditee Certifying Official"),
                            ("auditor_contact", "Auditor Contact"),
                            ("auditor_cert", "Auditor Certifying Official"),
                        ],
                        help_text="Access type granted to this user",
                        max_length=15,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                (
                    "sac",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="users",
                        to="audit.singleauditchecklist",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        help_text="User ID associated with this email address, empty if no FAC account exists",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
