# Generated by Django 4.2.1 on 2023-06-23 15:59

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0028_alter_singleauditchecklist_transition_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="singleauditchecklist",
            name="transition_date",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.DateTimeField(),
                default=[datetime.date.today],
                size=None,
            ),
        ),
    ]
