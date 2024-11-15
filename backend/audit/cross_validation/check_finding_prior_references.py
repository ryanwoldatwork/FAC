from .errors import (
    err_prior_no_report,
    err_bad_repeat_prior_reference,
    err_prior_ref_not_found,
)
from dissemination.models import (
    Finding,
    General,
)

from datetime import date


def check_finding_prior_references(sac_dict, *_args, **_kwargs):
    """
    Check that prior references numbers point to findings that actually exist
    in a previously submitted report
    """
    # Importing here to avoid circular import
    from audit.models import SacValidationWaiver

    if SacValidationWaiver.TYPES.PRIOR_REFERENCES in sac_dict.get("waiver_types", []):
        return []

    all_sections = sac_dict.get("sf_sac_sections")
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )
    all_prior_refs = _get_prior_refs(findings_uniform_guidance)

    # No prior reference numbers to validate
    if not all_prior_refs:
        return []

    general_information = all_sections.get("general_information")
    auditee_uei = general_information["auditee_uei"]
    previous_year = (
        date.fromisoformat(general_information["auditee_fiscal_period_start"]).year - 1
    )

    # Prior reference numbers usually refer to findings from the previous
    # year's report
    try:
        previous_year_report = General.objects.get(
            audit_year=previous_year,
            auditee_uei=auditee_uei,
        )
        previous_year_report_id = previous_year_report.id
    except General.DoesNotExist:
        previous_year_report_id = None

    errors = []

    # Validate all prior reference numbers for each award
    for award_ref, prior_refs_strings in all_prior_refs.items():
        prior_refs = prior_refs_strings.split(",")
        _validate_prior_refs(
            prior_refs,
            award_ref,
            auditee_uei,
            previous_year,
            previous_year_report_id,
            errors,
        )

    return errors


def _get_prior_refs(findings_uniform_guidance):
    """
    Returns a dict that maps award references to a list of prior references
    strings
    """
    all_prior_refs = {}

    for finding in findings_uniform_guidance:
        if finding["findings"]["repeat_prior_reference"] == "Y":
            award_ref = finding["program"]["award_reference"]
            cur_prior_refs = finding["findings"]["prior_references"]
            all_prior_refs[award_ref] = cur_prior_refs

    return all_prior_refs


def _validate_prior_refs(
    prior_refs, award_ref, auditee_uei, previous_year, previous_year_report_id, errors
):
    """
    Performs validation on the given list of prior reference numbers
    """
    for prior_ref in prior_refs:
        if prior_ref == "N/A":
            errors.append(
                {
                    "error": err_bad_repeat_prior_reference(award_ref),
                }
            )
            continue

        try:
            # The first four digits of a prior reference number are the year
            prior_ref_year = int(prior_ref[:4])
            prior_ref_report = General.objects.get(
                audit_year=prior_ref_year,
                auditee_uei=auditee_uei,
            )
            prior_ref_report_id = prior_ref_report.report_id
        except General.DoesNotExist:
            prior_ref_report_id = None

        # UEIs only become reliable as of 2022, so don't bother invalidating
        # prior references before that if we can't find it's report
        if not previous_year_report_id and not prior_ref_report_id:
            if prior_ref_year > 2021:
                errors.append(
                    {
                        "error": err_prior_no_report(auditee_uei, previous_year),
                    }
                )

            continue

        # Try to find the prior finding in either last year's audit or the one
        # indicated in the prior ref number
        if not Finding.objects.filter(
            report_id__in=[previous_year_report_id, prior_ref_report_id],
            reference_number=prior_ref,
        ).exists():
            errors.append(
                {
                    "error": err_prior_ref_not_found(prior_ref),
                }
            )
