import logging
from copy import deepcopy

from .xform_clean_version_value import remove_equals_and_quotes

from .xform_resize_award_references import resize_award_reference

from .xform_all_amount_expended_need_to_be_integers import (
    convert_amount_expended_to_integers,
)
from .xform_all_cluster_total_need_to_be_integers import (
    convert_cluster_total_to_integers,
)
from .xform_all_federal_program_total_need_to_be_integers import (
    convert_federal_program_total_to_integers,
)
from .xform_federal_awards_cluster_name_to_uppercase import (
    convert_federal_awards_cluster_name_to_uppercase,
)
from .xform_total_amount_expended_need_to_be_integers import (
    convert_total_amount_expended_to_integers,
)
from .xform_subrecipient_amount_need_to_be_integers import (
    convert_subrecipient_amount_to_integers,
)
from .xform_insert_sequence_nums_into_notes_to_sefa import (
    insert_sequence_nums_into_notes_to_sefa,
)
from .xform_number_of_findings_need_to_be_integers import (
    convert_number_of_findings_to_integers,
)
from .xform_loan_balance_need_to_be_integers import (
    convert_loan_balance_to_integers_or_na,
)

# from .xform_filter_seq_numbers_where_there_are_no_values import filter_seq_numbers_where_there_are_no_values
# from .xform_make_sure_notes_to_sefa_are_just_strings import make_sure_notes_to_sefa_are_just_strings
from .xform_trim_null_from_content_fields_in_notes_to_sefa import (
    trim_null_from_content_fields_in_notes_to_sefa,
)

from .xform_all_fields_to_stripped_string import convert_to_stripped_string

from .xform_rename_additional_notes_sheet import (
    rename_additional_notes_sheet_to_form_sheet,
)

from .xform_add_transform_for_cfda_key import generate_cfda_keys
from .xform_uniform_cluster_names import regenerate_uniform_cluster_names
from .xform_reformat_prior_references import reformat_prior_references
from .xform_reformat_award_references import reformat_award_reference
from .xform_reformat_agency_prefix import reformat_federal_agency_prefix

logger = logging.getLogger(__name__)


def run_all_transforms(ir, list_of_xforms):
    new_ir = deepcopy(ir)
    for fun in list_of_xforms:
        new_ir = fun(new_ir)
    return new_ir


def run_all_notes_to_sefa_transforms(ir):
    return run_all_transforms(ir, notes_to_sefa_transforms)


def run_all_additional_eins_transforms(ir):
    return run_all_transforms(ir, general_transforms)


def run_all_federal_awards_transforms(ir):
    return run_all_transforms(ir, federal_awards_transforms)


def run_all_additional_ueis_transforms(ir):
    return run_all_transforms(ir, general_transforms)


def run_all_audit_findings_text_transforms(ir):
    return run_all_transforms(ir, general_transforms)


def run_all_audit_findings_transforms(ir):
    return run_all_transforms(ir, audit_findings_transforms)


def run_all_corrective_action_plan_transforms(ir):
    return run_all_transforms(ir, general_transforms)


def run_all_secondary_auditors_transforms(ir):
    return run_all_transforms(ir, general_transforms)


general_transforms = [
    convert_to_stripped_string,
    remove_equals_and_quotes,
]

notes_to_sefa_transforms = general_transforms + [
    trim_null_from_content_fields_in_notes_to_sefa,
    rename_additional_notes_sheet_to_form_sheet,
    insert_sequence_nums_into_notes_to_sefa,
]

federal_awards_transforms = general_transforms + [
    convert_amount_expended_to_integers,
    convert_cluster_total_to_integers,
    convert_federal_program_total_to_integers,
    convert_total_amount_expended_to_integers,
    convert_subrecipient_amount_to_integers,
    convert_total_amount_expended_to_integers,
    convert_number_of_findings_to_integers,
    convert_loan_balance_to_integers_or_na,
    convert_federal_awards_cluster_name_to_uppercase,
    regenerate_uniform_cluster_names,
    reformat_federal_agency_prefix,
    generate_cfda_keys,
    resize_award_reference,
]

audit_findings_transforms = general_transforms + [
    reformat_award_reference,
    reformat_prior_references,
    resize_award_reference,
]
