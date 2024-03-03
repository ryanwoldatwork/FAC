from django.core.management.base import BaseCommand
from django.db.models import Q, Subquery
from collections import Counter

from multiprocessing import Pool, Value

from dissemination.models import (
    General,
    Finding,
    FederalAward,
    OversightSearch
)

def process_rid(res):
    # OK. It does come in as a list
    (report_id, ar, rn, imw, imo, iof, iom, iqc, irf, isd) = res
    for (fap, fae, fc, id, im, ae) in FederalAward.objects.filter(report_id=report_id).values_list(
        "federal_agency_prefix",
        "federal_award_extension",
        "findings_count",
        "is_direct",
        "is_major",
        "amount_expended"
    ):
        # OversightSearch.objects.filter(report_id=report_id).delete()
        OversightSearch(
            report_id=General.objects.get(report_id=report_id),
            award_reference=ar,
            reference_number=rn,
            audit_year=General.objects.get(report_id=report_id).audit_year,
            fac_accepted_date=General.objects.get(report_id=report_id).fac_accepted_date,
            federal_agency_prefix=fap,
            federal_award_extension=fae,
            findings_count=fc,
            is_direct=id,
            is_major=im,
            amount_expended=ae,
            is_material_weakness=imw,
            is_modified_opinion=imo,
            is_other_findings=iof,
            is_other_matters=iom,
            is_questioned_costs=iqc,
            is_repeat_finding=irf,
            is_significant_deficiency=isd
        ).save()


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate views for the postgrest API.
    """

    def handle(self, *args, **kwargs):
        q = Q()
        q |= Q(is_modified_opinion="Y")
        q |= Q(is_other_findings="Y")
        q |= Q(is_material_weakness="Y")
        q |= Q(is_significant_deficiency="Y")
        q |= Q(is_other_matters="Y")
        q |= Q(is_questioned_costs="Y")
        q |= Q(is_repeat_finding="Y")
        # Find everything with findings

        res = Finding.objects.filter(q).distinct("report_id").values_list(
            "report_id",
            "award_reference",
            "reference_number",
            "is_material_weakness",
            "is_modified_opinion",
            "is_other_findings",
            "is_other_matters",
            "is_questioned_costs",
            "is_repeat_finding",
            "is_significant_deficiency")
        with Pool(processes=30) as pool:
            print(Counter(pool.map(process_rid, res)))
