# Generated by Django 4.1.2 on 2022-11-21 20:24

import audit.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0013_singleauditchecklist_federal_awards"),
    ]

    operations = [
        migrations.AlterField(
            model_name="singleauditchecklist",
            name="federal_awards",
            field=models.JSONField(
                blank=True,
                null=True,
                validators=[audit.validators.validate_federal_award_json],
            ),
        ),
    ]
