# Generated by Django 4.2.1 on 2023-07-08 17:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dissemination", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenAuditor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "report_id",
                    models.CharField(
                        max_length=40,
                        verbose_name="G-FAC generated identifier. FK to General",
                    ),
                ),
                (
                    "auditor_seq_number",
                    models.IntegerField(
                        verbose_name="Order that the Auditor was reported"
                    ),
                ),
                (
                    "auditor_city",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPACITY (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/d; SF-SAC 2016-2018: I/8/d; SF-SAC 2019-2021: I/6/h/iv; SF-SAC 2022: I/6/h/iv Census mapping: MULTIPLE CPAS INFO, CPACITY",
                        max_length=30,
                        null=True,
                        verbose_name="CPA City",
                    ),
                ),
                (
                    "auditor_contact_title",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/c; SF-SAC 2001-2003: I/7/c; SF-SAC 2004-2007: I/7/c; SF-SAC 2008-2009: I/6/c; SF-SAC 2010-2012: I/6/c; SF-SAC 2013-2015: I/6/d; SF-SAC 2016-2018: I/6/d; SF-SAC 2019-2021: I/6/d; SF-SAC 2022: I/6/d Census mapping: GENERAL, CPATITLE (AND) Data sources: SF-SAC 2008-2009: I/8/c; SF-SAC 2010-2012: I/8/c; SF-SAC 2013-2015: I/8/h; SF-SAC 2016-2018: I/8/h; SF-SAC 2019-2021: I/6/h/viii; SF-SAC 2022: I/6/h/viii Census mapping: MULTIPLE CPAS INFO, CPATITLE",
                        max_length=40,
                        null=True,
                        verbose_name="Title of CPA Contact",
                    ),
                ),
                (
                    "auditor_country",
                    models.CharField(
                        help_text="Data sources: SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPACOUNTRY",
                        max_length=45,
                        null=True,
                        verbose_name="CPA Country",
                    ),
                ),
                (
                    "auditor_ein",
                    models.IntegerField(
                        help_text="Data sources: SF-SAC 2013-2015: I/6/b; SF-SAC 2016-2018: I/6/b; SF-SAC 2019-2021: I/6/b; SF-SAC 2022: I/6/b Census mapping: GENERAL, AUDITOR_EIN (AND) Data sources: SF-SAC 2013-2015: I/8/b; SF-SAC 2016-2018: I/8/b; SF-SAC 2019-2021: I/6/h/ii; SF-SAC 2022: I/6/h/ii Census mapping: MULTIPLE CPAS INFO, CPAEIN",
                        null=True,
                        verbose_name="CPA Firm EIN (only available for audit years 2013 and beyond)",
                    ),
                ),
                (
                    "auditor_email",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/f; SF-SAC 2001-2003: I/7/f; SF-SAC 2004-2007: I/7/f; SF-SAC 2008-2009: I/6/f; SF-SAC 2010-2012: I/6/f; SF-SAC 2013-2015: I/6/g; SF-SAC 2016-2018: I/6/f; SF-SAC 2019-2021: I/6/f; SF-SAC 2022: I/6/f Census mapping: GENERAL, CPAEMAIL (AND) Data sources: SF-SAC 2008-2009: I/8/f; SF-SAC 2010-2012: I/8/f; SF-SAC 2013-2015: I/8/k; SF-SAC 2016-2018: I/8/k; SF-SAC 2019-2021: I/6/h/x; SF-SAC 2022: I/6/h/x Census mapping: MULTIPLE CPAS INFO, CPAEMAIL",
                        max_length=60,
                        null=True,
                        verbose_name="CPA mail address (optional)",
                    ),
                ),
                (
                    "auditor_phone",
                    models.PositiveBigIntegerField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/d; SF-SAC 2001-2003: I/7/d; SF-SAC 2004-2007: I/7/d; SF-SAC 2008-2009: I/6/d; SF-SAC 2010-2012: I/6/d; SF-SAC 2013-2015: I/6/e; SF-SAC 2016-2018: I/6/e; SF-SAC 2019-2021: I/6/e; SF-SAC 2022: I/6/e Census mapping: GENERAL, CPAPHONE (AND) Data sources: SF-SAC 2008-2009: I/8/d; SF-SAC 2010-2012: I/8/d; SF-SAC 2013-2015: I/8/i; SF-SAC 2016-2018: I/8/i; SF-SAC 2019-2021: I/6/h/ix; SF-SAC 2022: I/6/h/ix Census mapping: MULTIPLE CPAS INFO, CPAPHONE",
                        null=True,
                        verbose_name="CPA phone number",
                    ),
                ),
                (
                    "auditor_state",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPASTATE (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/e; SF-SAC 2016-2018: I/8/e; SF-SAC 2019-2021: I/6/h/v; SF-SAC 2022: I/6/h/v Census mapping: MULTIPLE CPAS INFO, CPASTATE",
                        max_length=2,
                        null=True,
                        verbose_name="CPA State",
                    ),
                ),
                (
                    "auditor_address_line_1",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPASTREET1 (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/c; SF-SAC 2016-2018: I/8/c; SF-SAC 2019-2021: I/6/h/iii; SF-SAC 2022: I/6/h/iii Census mapping: MULTIPLE CPAS INFO, CPASTREET1",
                        max_length=45,
                        null=True,
                        verbose_name="CPA Street Address",
                    ),
                ),
                (
                    "auditor_zip",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/b; SF-SAC 2001-2003: I/7/b; SF-SAC 2004-2007: I/7/b; SF-SAC 2008-2009: I/6/b; SF-SAC 2010-2012: I/6/b; SF-SAC 2013-2015: I/6/c; SF-SAC 2016-2018: I/6/c; SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPAZIPCODE (AND) Data sources: SF-SAC 2008-2009: I/8/b; SF-SAC 2010-2012: I/8/b; SF-SAC 2013-2015: I/8/f; SF-SAC 2016-2018: I/8/f; SF-SAC 2019-2021: I/6/h/vi; SF-SAC 2022: I/6/h/vi Census mapping: MULTIPLE CPAS INFO, CPAZIPCODE",
                        max_length=12,
                        null=True,
                        verbose_name="CPA Zip Code",
                    ),
                ),
                (
                    "auditor_firm_name",
                    models.CharField(
                        help_text="Data sources: SF-SAC 1997-2000: I/7/a; SF-SAC 2001-2003: I/7/a; SF-SAC 2004-2007: I/7/a; SF-SAC 2008-2009: I/6/a; SF-SAC 2010-2012: I/6/a; SF-SAC 2013-2015: I/6/a; SF-SAC 2016-2018: I/6/a; SF-SAC 2019-2021: I/6/a; SF-SAC 2022: I/6/a Census mapping: GENERAL, CPAFIRMNAME (AND) Data sources: SF-SAC 2008-2009: I/8/a; SF-SAC 2010-2012: I/8/a; SF-SAC 2013-2015: I/8/a; SF-SAC 2016-2018: I/8/a; SF-SAC 2019-2021: I/6/h/i; SF-SAC 2022: I/6/h/i Census mapping: MULTIPLE CPAS INFO, CPAFIRMNAME",
                        max_length=64,
                        verbose_name="CPA Firm Name",
                    ),
                ),
                (
                    "auditor_foreign_addr",
                    models.CharField(
                        help_text="Data sources: SF-SAC 2019-2021: I/6/c; SF-SAC 2022: I/6/c Census mapping: GENERAL, CPAFOREIGN",
                        max_length=200,
                        null=True,
                        verbose_name="CPA Address - if international",
                    ),
                ),
            ],
            options={
                "unique_together": {("report_id", "auditor_seq_number")},
            },
        ),
    ]
