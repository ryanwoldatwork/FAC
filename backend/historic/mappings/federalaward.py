import historic.Mapping
from historic.base import NoMapping, MapRetype, MapOneOf, MapLateRemove
from historic.retyping import to_int_to_str

cfac_to_gfac = {
    # FIXME I have no idea if this should be filtered out or kept...
    'id': NoMapping(),
    'audityear': NoMapping(),
    'dbkey': MapLateRemove(),
    'cfdaseqnum': 'award_seq_number',
    'cfda': NoMapping(),
    'federalprogramname': 'federal_program_name',
    'amount': 'amount_expended',
    'majorprogram': 'is_major',
    'typerequirement': 'type_requirement',
    'qcosts2': NoMapping(),
    'findings': NoMapping(),
    'findingrefnums': NoMapping(),
    'rd': NoMapping(),
    'direct': 'is_direct',
    'cfda_prefix': 'federal_agency_prefix',
    'cfda_ext': 'federal_agency_extension',
    'ein': NoMapping(),
    'cfda2': NoMapping(),
    'typereport_mp': NoMapping(),
    'typereport_mp_override': NoMapping(),
    'arra': NoMapping(),
    'loans': 'is_loan',
    'elecauditsid': NoMapping(),
    'findingscount': 'findings_count',
    'loanbalance': 'loan_balance',
    'passthroughamount': 'passthrough_ammount',
    'awardidentification': 'additional_award_identification',
    'clustername': 'cluster_name',
    'passthroughaward': 'is_passthrough_award',
    'stateclustername': 'state_cluster_name',
    'programtotal': 'federal_program_total',
    'clustertotal': 'cluster_total',
    'otherclustername': 'other_cluster_name',
    'cfdaprogramname': NoMapping(),
    'uei': NoMapping(),
    'multipleueis': NoMapping(),
}
