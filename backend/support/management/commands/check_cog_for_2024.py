from django.core.management.base import BaseCommand
from django.db.models.functions import Cast
from django.db.models import BigIntegerField, Q


from dissemination.models import General, FederalAward
from audit.models import SingleAuditChecklist, User
from support.models import CognizantAssignment
from support.cog_over import compute_cog_over

from config.settings import ENVIRONMENT

import pandas as pd


class Command(BaseCommand):
    help = """
    Verify cog for 2024 submissions in LOCAL environment only.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--year", help="Year(2024)", type=str, default="2024"
        )

    def is_year_invalid(self, year):
        valid_years = ["2024"]
        return year not in valid_years

    def handle(self, *args, **options):
        if ENVIRONMENT != "LOCAL":
            print(f"Environment is not LOCAL, ENVIRONMENT={ENVIRONMENT}")
            return

        year = options.get("year")
        if self.is_year_invalid(year):
            print(f"Invalid year {year}.  Expecting 2024")
            return

        df = pd.DataFrame(columns=['cog_in_Prod_w_2019_base', 'cog_w_2024_base'])

        print("Getting data from General\n")
        gens = General.objects.annotate(
            amt=Cast("total_amount_expended", output_field=BigIntegerField())
        ).filter(Q(audit_year=year))
        print(f"Count of {year} submissions: {len(gens)}")
        processed = cog_mismatches = over_mismatches = 0
        cog_count = oversight_count = 0

        for gen in gens:
            sac = self.make_sac(gen)
            sac.submission_status = sac.STATUS.SUBMITTED
            sac.oversight_agency = None
            sac.cognizant_agency = None

            cognizant_agency, oversight_agency, cog_is_calculated = compute_cog_over(
                sac.federal_awards, sac.submission_status, sac.general_information["ein"], sac.general_information["auditee_uei"]
            )
            if oversight_agency:
                sac.oversight_agency = oversight_agency
                oversight_count += 1
            else:
                sac.cognizant_agency = cognizant_agency
                cog_count += 1

            processed += 1
            if gen.cognizant_agency == "":
                gen.cognizant_agency = None
            if gen.oversight_agency == "":
                gen.oversight_agency = None

            if gen.cognizant_agency is not None and cog_is_calculated:
                new_row = {'cog_in_Prod_w_2019_base': gen.cognizant_agency, 'cog_w_2024_base': sac.cognizant_agency}
                df.loc[len(df)] = new_row

            if gen.cognizant_agency != sac.cognizant_agency:
                cog_mismatches += 1
                print(
                    f"Cog mismatch. Calculated {sac.cognizant_agency} Expected {gen.cognizant_agency}"
                )
                self.show_mismatch(sac)
            if gen.oversight_agency != sac.oversight_agency:
                over_mismatches += 1
                print(
                    f"Oversight mismatch. Calculated {sac.oversight_agency} Expected {gen.oversight_agency}"
                )
                self.show_mismatch(sac)
            if processed % 1000 == 0:
                print(
                    f"""
                      Processed {processed} rows so far.
                      Found {cog_mismatches} cog and {over_mismatches} over mismatches.
                      ..."""
                )
        print(
            f"""
                Processed all {processed} rows.
                Found {cog_mismatches} cog and {over_mismatches} over mismatches.
                """
        )
        print(f"cog_count = {cog_count}, oversight_count = {oversight_count}")
        df.to_csv("cog_Prod_2019_cog_2024.csv")

    def show_mismatch(self, sac):
        print(
            sac.ein,
            sac.auditee_uei,
            sac.cognizant_agency,
            sac.oversight_agency,
            sac.federal_awards["FederalAwards"]["total_amount_expended"],
        )
        for award in sac.federal_awards["FederalAwards"]["federal_awards"]:
            print(
                "Award:",
                award["award_reference"],
                award["program"]["amount_expended"],
                award["program"]["federal_agency_prefix"],
                award["program"]["three_digit_extension"],
                award["direct_or_indirect_award"]["is_direct"],
            )

    def make_sac(self, gen: General):
        general_information = {
            "auditee_fiscal_period_start": "2022-11-01",
            "auditee_fiscal_period_end": "2023-11-01",
            "met_spending_threshold": True,
            "is_usa_based": True,
        }
        general_information["ein"] = gen.auditee_ein
        general_information["auditee_uei"] = gen.auditee_uei
        federal_awards = self.make_awards(gen)
        sac = SingleAuditChecklist.objects.create(
            submitted_by=User.objects.first(),
            submission_status="in_progress",
            general_information=general_information,
            federal_awards=federal_awards,
        )
        return sac

    def make_awards(self, gen: General):
        awards = {
            "FederalAwards": {
                "auditee_uei": gen.auditee_uei,
                "federal_awards": [],
                "total_amount_expended": gen.amt,
            }
        }
        cfdas = FederalAward.objects.annotate(
            amt=Cast("amount_expended", output_field=BigIntegerField())
        ).filter(report_id=gen.report_id)
        for cfda in cfdas:
            awards["FederalAwards"]["federal_awards"].append(
                {
                    "award_reference": cfda.award_reference,
                    "program": {
                        "program_name": cfda.federal_program_name,
                        "amount_expended": cfda.amt,
                        "federal_agency_prefix": cfda.federal_agency_prefix,
                        "three_digit_extension": cfda.federal_award_extension,
                    },
                    "direct_or_indirect_award": {"is_direct": cfda.is_direct},
                },
            )
        return awards

