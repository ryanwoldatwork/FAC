# Generated by Django 5.0.4 on 2024-07-09 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0009_ueivalidationwaiver_sacvalidationwaiver"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ueivalidationwaiver",
            name="uei",
            field=models.TextField(verbose_name="UEI"),
        ),
    ]