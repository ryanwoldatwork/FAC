# Generated by Django 4.2.1 on 2023-07-19 07:00

import audit.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0028_singleauditchecklist_notes_to_sefa"),
    ]

    operations = [
        migrations.AddField(
            model_name="singleauditchecklist",
            name="secondary_auditors",
            field=models.JSONField(
                blank=True,
                null=True,
                validators=[audit.validators.validate_secondary_auditors_json],
            ),
        ),
    ]