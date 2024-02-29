from django.core.management.base import BaseCommand
from django.db.models import Q, Subquery

from dissemination.models import (
    General,
    Finding,
    FederalAward,
    OversightSearch
)


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

        for (report_id, imw, imo, iof, iom, iqc, irf, isd) in Finding.objects.filter(q).distinct("report_id").values_list(
            "report_id",
            "is_material_weakness",
            "is_modified_opinion",
            "is_other_findings",
            "is_other_matters",
            "is_questioned_costs",
            "is_repeat_finding",
            "is_significant_deficiency"
        ):
            print(report_id)
            for (fap, fae, fc, id, im) in FederalAward.objects.filter(report_id=report_id).values_list(
                "federal_agency_prefix",
                "federal_award_extension",
                "findings_count",
                "is_direct",
                "is_major",
            ):
                OversightSearch(
                    report_id=General.objects.get(report_id=report_id),
                    federal_agency_prefix=fap,
                    federal_award_extension=fae,
                    findings_count=fc,
                    is_direct=id,
                    is_major=im,
                    is_material_weakness=imw,
                    is_modified_opinion=imo,
                    is_other_findings=iof,
                    is_other_matters=iom,
                    is_questioned_costs=iqc,
                    is_repeat_finding=irf,
                    is_significant_deficiency=isd
                ).save()
