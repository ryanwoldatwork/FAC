# Generated by Django 5.0.4 on 2024-07-23 15:54

import audit.models.models
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0010_alter_ueivalidationwaiver_uei"),
    ]

    operations = [
        migrations.AddField(
            model_name="ueivalidationwaiver",
            name="expiration",
            field=models.DateTimeField(
                default=audit.models.models.one_month_from_today,
                verbose_name="When the waiver will expire",
            ),
        ),
        migrations.AddField(
            model_name="ueivalidationwaiver",
            name="timestamp",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="When the waiver was created",
            ),
        ),
    ]