# Generated by Django 4.2.1 on 2023-07-12 15:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="federalaward",
            name="award_seq_number",
            field=models.IntegerField(
                default=1, verbose_name="Order that the award line was reported"
            ),
            preserve_default=False,
        ),
    ]
