# Generated by Django 4.2.1 on 2023-07-19 15:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "dissemination",
            "0007_rename_charts_tables_captext_contains_chart_or_table_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="findingtext",
            old_name="charts_tables",
            new_name="contains_chart_or_table",
        ),
    ]