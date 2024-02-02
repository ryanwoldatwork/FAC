# Generated by Django 4.2.6 on 2024-02-02 19:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0011_onetimeaccess"),
    ]

    operations = [
        migrations.AlterField(
            model_name="additionalein",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="additionaluei",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="captext",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="federalaward",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="finding",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="findingtext",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="general",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier",
                unique=True,
                verbose_name="Report ID",
            ),
        ),
        migrations.AlterField(
            model_name="note",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="onetimeaccess",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="passthrough",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
        migrations.AlterField(
            model_name="secondaryauditor",
            name="report_id",
            field=models.TextField(
                help_text="GSAFAC generated identifier", verbose_name="Report ID"
            ),
        ),
    ]
