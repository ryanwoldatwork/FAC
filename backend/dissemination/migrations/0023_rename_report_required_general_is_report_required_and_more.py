# Generated by Django 4.2.3 on 2023-08-01 22:56

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0022_alter_general_auditee_signature_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="general",
            old_name="report_required",
            new_name="is_report_required",
        ),
        migrations.AddField(
            model_name="general",
            name="hist_auditee_address_line_2",
            field=models.TextField(
                null=True, verbose_name="Auditee Street Address Line 2 in C-FAC"
            ),
        ),
        migrations.AddField(
            model_name="general",
            name="hist_auditee_fax",
            field=models.TextField(
                null=True, verbose_name="Auditee Fax Number in C-FAC"
            ),
        ),
        migrations.AddField(
            model_name="general",
            name="hist_auditor_address_line_2",
            field=models.TextField(
                max_length=45,
                null=True,
                verbose_name="CPA Street Address Line 2 in C-FAC",
            ),
        ),
        migrations.AddField(
            model_name="general",
            name="hist_auditor_fax",
            field=models.TextField(null=True, verbose_name="CPA fax number in C-FAC"),
        ),
        migrations.AddField(
            model_name="general",
            name="hist_dbkey",
            field=models.IntegerField(
                null=True,
                verbose_name="Identifier for a submission along with audit_year in C-FAC",
            ),
        ),
        migrations.AddField(
            model_name="secondaryauditor",
            name="hist_address_street_line_2",
            field=models.TextField(
                null=True, verbose_name="CPA Street Address Line 2 in C-FAC"
            ),
        ),
        migrations.AddField(
            model_name="secondaryauditor",
            name="hist_contact_fax",
            field=models.TextField(null=True, verbose_name="CPA fax number"),
        ),
        migrations.AlterField(
            model_name="captext",
            name="contains_chart_or_table",
            field=models.BooleanField(
                help_text="Census mapping: CAPTEXT, CHARTSTABLES",
                null=True,
                verbose_name="Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
            ),
        ),
        migrations.AlterField(
            model_name="federalaward",
            name="amount_expended",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Data sources: SF-SAC 1997-2000: III/6/c; SF-SAC 2001-2003: III/10/d; SF-SAC 2004-2007: III/9/e; SF-SAC 2008-2009: III/9/e; SF-SAC 2010-2012: III/9/f; SF-SAC 2013-2015: III/6/d; SF-SAC 2016-2018: II/1/e; SF-SAC 2019-2021: II/1/e; SF-SAC 2022: II/1/e Census mapping: CFDA INFO, AMOUNT",
                max_digits=10,
                null=True,
                verbose_name="Amount Expended for the Federal Program",
            ),
        ),
        migrations.AlterField(
            model_name="federalaward",
            name="cluster_total",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Data sources: SF-SAC 2016-2018: II/1/h; SF-SAC 2019-2021: II/1/h; SF-SAC 2022: II/1/h Census mapping: CFDA INFO, CLUSTERTOTAL",
                max_digits=10,
                null=True,
                verbose_name="Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name",
            ),
        ),
        migrations.AlterField(
            model_name="federalaward",
            name="federal_program_total",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Data sources: SF-SAC 2016-2018: II/1/g; SF-SAC 2019-2021: II/1/g; SF-SAC 2022: II/1/g Census mapping: CFDA INFO, PROGRAMTOTAL",
                max_digits=10,
                null=True,
                verbose_name="Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension",
            ),
        ),
        migrations.AlterField(
            model_name="federalaward",
            name="passthrough_amount",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Data sources: SF-SAC 2016-2018: II/1/o; SF-SAC 2019-2021: II/1/o; SF-SAC 2022: II/1/o Census mapping: CFDA INFO, PASSTHROUGHAMOUNT",
                max_digits=10,
                null=True,
                verbose_name="Amount passed through to subrecipients",
            ),
        ),
        migrations.AlterField(
            model_name="federalaward",
            name="report_id",
            field=models.CharField(
                max_length=40,
                verbose_name="G-FAC generated identifier. FK  to a General",
            ),
        ),
        migrations.AlterField(
            model_name="findingtext",
            name="contains_chart_or_table",
            field=models.BooleanField(
                help_text="Census mapping: FINDINGSTEXT, CHARTSTABLES",
                null=True,
                verbose_name="Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
            ),
        ),
        migrations.AlterField(
            model_name="general",
            name="auditee_addl_uei_list",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    help_text="Data sources: SF-SAC 2022: I/4/g Census mapping: GENERAL, UEI",
                    null=True,
                    verbose_name="",
                ),
                default=list,
                null=True,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="general",
            name="auditor_ein",
            field=models.CharField(
                help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN",
                max_length=30,
                null=True,
                verbose_name="CPA Firm EIN (only available for audit years 2013 and beyond)",
            ),
        ),
        migrations.AlterField(
            model_name="general",
            name="oversight_agency",
            field=models.CharField(
                help_text="Data sources: SF-SAC 1997-2000: I/9; SF-SAC 2001-2003: I/9 Census mapping: GENERAL, OVERSIGHTAGENCY",
                max_length=2,
                null=True,
                verbose_name="Two digit Federal agency prefix of the oversight agency",
            ),
        ),
        migrations.AlterField(
            model_name="general",
            name="total_fed_expenditures",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Data sources: SF-SAC 1997-2000: III/6/c- Total; SF-SAC 2001-2003: III/10/d -Total; SF-SAC 2004-2007: III/9/e -Total; SF-SAC 2008-2009: III/9/e -Total; SF-SAC 2010-2012: III/9/f -Total; SF-SAC 2013-2015: III/6/d -Total; SF-SAC 2016-2018: II/1/e- Total; SF-SAC 2019-2021: II/1/e - Total; SF-SAC 2022: II/1/e - Total Census mapping: GENERAL, TOTFEDEXPEND",
                max_digits=10,
                null=True,
                verbose_name="Total Federal Expenditures",
            ),
        ),
        migrations.AlterField(
            model_name="secondaryauditor",
            name="auditor_ein",
            field=models.CharField(
                help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN",
                max_length=30,
                null=True,
                verbose_name="CPA Firm EIN (only available for audit years 2013 and beyond)",
            ),
        ),
    ]
