from historic.base import NoMapping, MapLateRemove, MapRetype
from historic.retyping import to_boolean

cfac_to_gfac = {
    "ID": NoMapping(),
    "AUDITYEAR": NoMapping(),
    "DBKEY": MapLateRemove(),
    "CFDASEQNUM": "award_reference",
    "CFDA": NoMapping(),
    "FEDERALPROGRAMNAME": "federal_program_name",
    "AMOUNT": "amount_expended",
    "MAJORPROGRAM": MapRetype("is_major", to_boolean),
    "TYPEREQUIREMENT": "type_requirement",
    "QCOSTS2": NoMapping(),
    "FINDINGS": NoMapping(),
    "FINDINGREFNUMS": NoMapping(),
    "RD": NoMapping(),
    "DIRECT": MapRetype("is_direct", to_boolean),
    "CFDA_PREFIX": "federal_agency_prefix",
    "CFDA_EXT": "federal_award_extension",
    "EIN": NoMapping(),
    "CFDA2": NoMapping(),
    "TYPEREPORT_MP": NoMapping(),
    "TYPEREPORT_MP_OVERRIDE": NoMapping(),
    "ARRA": NoMapping(),
    "LOANS": MapRetype("is_loan", to_boolean),
    "ELECAUDITSID": NoMapping(),
    "FINDINGSCOUNT": "findings_count",
    "LOANBALANCE": "loan_balance",
    "PASSTHROUGHAMOUNT": "passthrough_amount",
    "AWARDIDENTIFICATION": "additional_award_identification",
    "CLUSTERNAME": "cluster_name",
    "PASSTHROUGHAWARD": MapRetype("is_passthrough_award", to_boolean),
    "STATECLUSTERNAME": "state_cluster_name",
    "PROGRAMTOTAL": "federal_program_total",
    "CLUSTERTOTAL": "cluster_total",
    "OTHERCLUSTERNAME": "other_cluster_name",
    "CFDAPROGRAMNAME": NoMapping(),
    "UEI": NoMapping(),
    "MULTIPLEUEIS": NoMapping(),
}
