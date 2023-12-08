from django.db.models import Q

from dissemination.models import General, FederalAward, Finding


def search_general(
    alns=None,
    names=None,
    uei_or_eins=None,
    start_date=None,
    end_date=None,
    cog_or_oversight=None,
    agency_name=None,
    audit_years=None,
    auditee_state=None,
    include_private=False,
):
    query = Q()

    # 'alns' gets processed before the match query function, as they get used again after the main search.
    if alns:
        split_alns, agency_numbers = _split_alns(alns)
        query.add(_get_aln_match_query(split_alns, agency_numbers), Q.AND)

    query.add(_get_names_match_query(names), Q.AND)
    query.add(_get_uei_or_eins_match_query(uei_or_eins), Q.AND)
    query.add(_get_start_date_match_query(start_date), Q.AND)
    query.add(_get_end_date_match_query(end_date), Q.AND)
    query.add(_get_cog_or_oversight_match_query(agency_name, cog_or_oversight), Q.AND)
    query.add(_get_audit_years_match_query(audit_years), Q.AND)
    query.add(_get_auditee_state_match_query(auditee_state), Q.AND)

    if not include_private:
        query.add(Q(is_public=True), Q.AND)

    results = General.objects.filter(query).order_by("-fac_accepted_date")

    if alns:
        results = _attach_finding_my_aln_and_finding_all_aln_fields(
            results, split_alns, agency_numbers
        )

    return results


def _split_alns(alns):
    """
    Split an ALN query string into two sets.
        1. split_alns: {(federal_agency_prefix, federal_award_extension), ...}
        2. agency_numbers: {('federal_agency_prefix'), ...}
    """
    split_alns = set()
    agency_numbers = set()
    for aln in alns:
        if len(aln) == 2:
            # If we don't wrap the `aln` with [], the string
            # goes in as individual characters. A weirdness of Python sets.
            agency_numbers.update([aln])
        else:
            split_aln = aln.split(".")
            if len(split_aln) == 2:
                # The [wrapping] is so the tuple goes into the set as a tuple.
                # Otherwise, the individual elements go in unpaired.
                split_alns.update([tuple(split_aln)])

    return split_alns, agency_numbers


def _get_aln_report_ids(split_alns, agency_numbers):
    """
    Given a set of ALNs and a set agency numbers, find the relevant awards and return a set of report_ids.
    Utilizing sets helps to avoid duplicate reports.
    """
    report_ids = set()
    # Matching on a specific ALN, such as '12.345'
    for aln_list in split_alns:
        matching_awards = FederalAward.objects.filter(
            federal_agency_prefix=aln_list[0], federal_award_extension=aln_list[1]
        ).values()
        if matching_awards:
            for matching_award in matching_awards:
                # Again, adding in a string requires [] so the individual
                # characters of the report ID don't go in... we want the whole string.
                report_ids.update([matching_award.get("report_id")])
    # Matching on a whole agency, such as '12'
    for agency_number in agency_numbers:
        matching_awards = FederalAward.objects.filter(
            federal_agency_prefix=agency_number
        ).values()
        if matching_awards:
            for matching_award in matching_awards:
                report_ids.update([matching_award.get("report_id")])

    return report_ids


def _attach_finding_my_aln_and_finding_all_aln_fields(
    results, split_alns, agency_numbers
):
    """
    Given the results QuerySet (full of 'General' objects) and an ALN query string,
    return the modified QuerySet, where each 'General' object has two new fields.

    The process:
    1. Get findings that fall under the given reports.
    2. For each finding, get the relevant award. This is to access its ALN.
    3. For each finding/award pair, they are either:
       a. Under one of my ALNs, so we update finding_my_aln to True.
       b. Under any other ALN, so we update finding_all_aln to True.
    """
    for result in results:
        result.finding_my_aln = False
        result.finding_all_aln = False
        matching_findings = Finding.objects.filter(report_id=result.report_id)

        for finding in matching_findings:
            matching_award = FederalAward.objects.get(
                report_id=result.report_id, award_reference=finding.award_reference
            )
            prefix = matching_award.federal_agency_prefix
            extension = matching_award.federal_award_extension

            if ((prefix, extension) in split_alns) or (prefix in agency_numbers):
                result.finding_my_aln = True
            else:
                result.finding_all_aln = True

    return results


def _get_aln_match_query(split_alns, agency_numbers):
    """
    Given split ALNs and agency numbers, return the match query for ALNs.
    """
    # Search for relevant awards
    report_ids = _get_aln_report_ids(split_alns, agency_numbers)

    # Add the report_id's from the award search to the full search params
    alns_match = Q()
    for report_id in report_ids:
        alns_match.add(Q(report_id=report_id), Q.OR)
    return alns_match


def _get_names_match_query(names):
    """
    Given a list of (potential) names, return the query object that searches auditee and firm names.
    """
    if not names:
        return Q()

    name_fields = [
        "auditee_city",
        "auditee_contact_name",
        "auditee_email",
        "auditee_name",
        "auditee_state",
        "auditor_city",
        "auditor_contact_name",
        "auditor_email",
        "auditor_firm_name",
        "auditor_state",
    ]

    names_match = Q()

    # turn ["name1", "name2", "name3"] into "name1 name2 name3"
    names = " ".join(names)
    for field in name_fields:
        names_match.add(Q(**{"%s__search" % field: names}), Q.OR)

    return names_match


def _get_uei_or_eins_match_query(uei_or_eins):
    if not uei_or_eins:
        return Q()

    uei_or_ein_match = Q(
        Q(auditee_uei__in=uei_or_eins) | Q(auditee_ein__in=uei_or_eins)
    )
    return uei_or_ein_match


def _get_start_date_match_query(start_date):
    if not start_date:
        return Q()

    return Q(fac_accepted_date__gte=start_date)


def _get_end_date_match_query(end_date):
    if not end_date:
        return Q()

    return Q(fac_accepted_date__lte=end_date)


def _get_cog_or_oversight_match_query(agency_name, cog_or_oversight):
    if not cog_or_oversight:
        return Q()

    if cog_or_oversight.lower() == "cog":
        return Q(cognizant_agency__in=[agency_name])
    elif cog_or_oversight.lower() == "oversight":
        return Q(oversight_agency__in=[agency_name])


def _get_audit_years_match_query(audit_years):
    if not audit_years:
        return Q()

    return Q(audit_year__in=audit_years)


def _get_auditee_state_match_query(auditee_state):
    if not auditee_state:
        return Q()

    return Q(auditee_state__in=[auditee_state])
