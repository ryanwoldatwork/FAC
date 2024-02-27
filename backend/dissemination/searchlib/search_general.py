from django.db.models import Q
from dissemination.models import General
import time
from math import ceil
import logging

logger = logging.getLogger(__name__)


def search_general(params=None):
    params = params or {}
    # Time general reduction
    t0 = time.time()

    ##############
    # Initialize query.
    # This is where tribal/is_public is set by default.
    q_base = _initialize_query(params.get("include_private", False))
    r_base = General.objects.filter(q_base)

    ##############
    # Audit years
    # query.add(_get_audit_years_match_query(audit_years), Q.AND)
    q_audit_year = _get_audit_years_match_query(params.get("audit_years", None))
    r_audit_year = General.objects.filter(q_audit_year)

    ##############
    # State
    q_state = _get_auditee_state_match_query(params.get("auditee_state", None))
    r_state = General.objects.filter(q_state)

    ##############
    # Names
    q_names = _get_names_match_query(params.get("names", None))
    r_names = General.objects.filter(q_names)

    ##############
    # UEI/EIN
    q_uei = _get_uei_or_eins_match_query(params.get("uei_or_eins", None))
    r_uei = General.objects.filter(q_uei)

    ##############
    # Start/end dates
    q_start_date = _get_start_date_match_query(params.get("start_date", None))
    r_start_date = General.objects.filter(q_start_date)
    q_end_date = _get_end_date_match_query(params.get("end_date", None))
    r_end_date = General.objects.filter(q_end_date)

    ##############
    # Cog/Over
    q_cogover = _get_cog_or_oversight_match_query(
        params.get("agency_name", None), params.get("cog_or_oversight", None)
    )
    r_cogover = General.objects.filter(q_cogover)

    ##############
    # Intersection
    # Intersection on result sets is an &.
    results = (
        r_audit_year
        & r_start_date
        & r_end_date
        & r_state
        & r_cogover
        & r_names
        & r_uei
        & r_base
    )

    t1 = time.time()
    report_timing("search_general", params, t0, t1)
    return results


def report_timing(tag, params, start, end):
    readable = int(ceil((end - start) * 1000))
    logger.info(f"SEARCH_TIMING {hex(id(params))[8:]} {tag} {readable}ms")


def _initialize_query(include_private: bool):
    query = Q()
    # Always include the public stuff
    if include_private:
        # If we are including private, we want everything to come back.
        # That is the same as the empty query in this context.
        pass
    else:
        # Limit our search to public data.
        query = Q(is_public=True)
    return query


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
