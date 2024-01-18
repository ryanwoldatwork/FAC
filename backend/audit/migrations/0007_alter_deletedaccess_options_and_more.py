# Generated by Django 4.2.6 on 2023-11-21 23:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0006_deletedaccess"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="deletedaccess",
            options={"verbose_name_plural": "deleted accesses"},
        ),
        migrations.AlterField(
            model_name="deletedaccess",
            name="removed_by_email",
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
