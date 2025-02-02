import re

from django.conf import settings

from census_historical_migration.invalid_migration_tags import INVALID_MIGRATION_TAGS
from census_historical_migration.invalid_record import InvalidRecord
from census_historical_migration.report_type_flag import AceFlag
from ..transforms.xform_string_to_int import string_to_int
from ..transforms.xform_string_to_bool import string_to_bool
from ..transforms.xform_string_to_string import string_to_string
from ..exception_utils import DataMigrationError
from ..workbooklib.excel_creation_utils import get_audits, track_invalid_records
from ..base_field_maps import FormFieldMap, FormFieldInDissem
from ..sac_general_lib.utils import (
    create_json_from_db_object,
    is_single_word,
)
import audit.validators
from ..change_record import InspectionRecord, CensusRecord, GsaFacRecord
from audit.utils import Util


def xform_apply_default_thresholds(value):
    """Applies default threshold when value is None."""
    # Transformation to be documented.
    str_value = string_to_string(value)
    if str_value == "":
        return settings.GSA_MIGRATION_INT
    return string_to_int(str_value)


mappings = [
    FormFieldMap(
        "dollar_threshold",
        "DOLLARTHRESHOLD",
        FormFieldInDissem,
        None,
        xform_apply_default_thresholds,
    ),
    FormFieldMap(
        "is_going_concern_included", "GOINGCONCERN", FormFieldInDissem, None, bool
    ),
    FormFieldMap(
        "is_internal_control_deficiency_disclosed",
        "MATERIALWEAKNESS",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap(
        "is_internal_control_material_weakness_disclosed",
        "MATERIALWEAKNESS_MP",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap(
        "is_material_noncompliance_disclosed",
        "MATERIALNONCOMPLIANCE",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap(
        "is_aicpa_audit_guide_included",
        "REPORTABLECONDITION",
        FormFieldInDissem,
        None,
        bool,
    ),
    FormFieldMap("is_low_risk_auditee", "LOWRISK", FormFieldInDissem, None, bool),
    FormFieldMap("agencies", "PYSCHEDULE", "agencies_with_prior_findings", [], list),
]


def _get_agency_prefixes(dbkey, year):
    """Returns the agency prefixes for a given dbkey and audit year."""
    agencies = set()
    audits = get_audits(dbkey, year)

    for audit_detail in audits:
        prefix = (
            string_to_string(audit_detail.CFDA_PREFIX)
            if audit_detail.CFDA_PREFIX
            else string_to_string(audit_detail.CFDA).split(".")[0]
        )
        agencies.add(prefix)

    return agencies


def xform_framework_basis(basis):
    """Transforms the framework basis from Census format to FAC format.
    For context, see ticket #2912.
    """
    # Transformation recorded (see xform_build_sp_framework_gaap_results).
    basis = string_to_string(basis)
    if is_single_word(basis):
        mappings = {
            r"cash": "cash_basis",
            r"contractual": "contractual_basis",
            r"regulatory": "regulatory_basis",
            r"tax": "tax_basis",
            r"other": "other_basis",
        }
        # Check each pattern in the mappings with case-insensitive search
        for pattern, value in mappings.items():
            if re.search(pattern, basis, re.IGNORECASE):
                return value

    raise DataMigrationError(
        f"Could not find a match for historic framework basis: '{basis}'",
        "invalid_basis",
    )


def xform_census_keys_to_fac_options(census_keys, fac_options):
    """Maps the census keys to FAC options.
    For context, see ticket #2912.
    """
    # Transformation recorded (see xform_build_sp_framework_gaap_results).
    if "U" in census_keys:
        fac_options.append("unmodified_opinion")
    if "Q" in census_keys:
        fac_options.append("qualified_opinion")
    if "A" in census_keys:
        fac_options.append("adverse_opinion")
    if "D" in census_keys:
        fac_options.append("disclaimer_of_opinion")


def xform_build_sp_framework_gaap_results(audit_header):
    """Returns the SP Framework and GAAP results for a given audit header."""
    # Transformation recorded.
    sp_framework_gaap_data = string_to_string(audit_header.TYPEREPORT_FS).upper()
    if not sp_framework_gaap_data:
        raise DataMigrationError(
            f"GAAP details are missing for DBKEY: {audit_header.DBKEY}",
            "missing_gaap",
        )

    sp_framework_gaap_results = {}
    sp_framework_gaap_results["gaap_results"] = []
    xform_census_keys_to_fac_options(
        sp_framework_gaap_data, sp_framework_gaap_results["gaap_results"]
    )

    if "S" in sp_framework_gaap_data:
        sp_framework_gaap_results["gaap_results"].append("not_gaap")
        sp_framework_gaap_results["is_sp_framework_required"] = string_to_bool(
            audit_header.SP_FRAMEWORK_REQUIRED
        )
        sp_framework_gaap_results["sp_framework_opinions"] = []
        sp_framework_opinions = string_to_string(
            audit_header.TYPEREPORT_SP_FRAMEWORK
        ).upper()
        xform_census_keys_to_fac_options(
            sp_framework_opinions, sp_framework_gaap_results["sp_framework_opinions"]
        )
        sp_framework_gaap_results["sp_framework_basis"] = []
        basis = xform_framework_basis(audit_header.SP_FRAMEWORK)
        sp_framework_gaap_results["sp_framework_basis"].append(basis)

    track_transformations(sp_framework_gaap_results, audit_header)

    return sp_framework_gaap_results


def track_transformations(sp_framework_gaap_results, audit_header):
    """Tracks all transformations related to the special framework data."""

    if sp_framework_gaap_results["gaap_results"]:
        census_data = [
            CensusRecord(
                column="TYPEREPORT_FS",
                value=audit_header.TYPEREPORT_FS,
            ).to_dict(),
        ]
        gsa_fac_data = GsaFacRecord(
            field="gaap_results",
            value=Util.json_array_to_str(sp_framework_gaap_results["gaap_results"]),
        ).to_dict()
        InspectionRecord.append_general_changes(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": [
                    "xform_build_sp_framework_gaap_results",
                    "xform_census_keys_to_fac_options",
                ],
            }
        )

    if (
        "is_sp_framework_required" in sp_framework_gaap_results
        and sp_framework_gaap_results["is_sp_framework_required"]
        != settings.GSA_MIGRATION
    ):
        census_data = [
            CensusRecord(
                column="TYPEREPORT_FS",
                value=audit_header.TYPEREPORT_FS,
            ).to_dict(),
            CensusRecord(
                column="SP_FRAMEWORK_REQUIRED",
                value=audit_header.SP_FRAMEWORK_REQUIRED,
            ).to_dict(),
        ]
        gsa_fac_data = GsaFacRecord(
            field="is_sp_framework_required",
            value=Util.optional_bool(
                sp_framework_gaap_results["is_sp_framework_required"]
            ),
        ).to_dict()
        InspectionRecord.append_general_changes(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": ["xform_build_sp_framework_gaap_results"],
            }
        )

    if "sp_framework_opinions" in sp_framework_gaap_results:
        census_data = [
            CensusRecord(
                column="TYPEREPORT_FS",
                value=audit_header.TYPEREPORT_FS,
            ).to_dict(),
            CensusRecord(
                column="TYPEREPORT_SP_FRAMEWORK",
                value=audit_header.TYPEREPORT_SP_FRAMEWORK,
            ).to_dict(),
        ]
        gsa_fac_data = GsaFacRecord(
            field="sp_framework_opinions",
            value=Util.json_array_to_str(
                sp_framework_gaap_results["sp_framework_opinions"]
            ),
        ).to_dict()
        InspectionRecord.append_general_changes(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": [
                    "xform_build_sp_framework_gaap_results",
                    "xform_census_keys_to_fac_options",
                ],
            }
        )

    if "sp_framework_basis" in sp_framework_gaap_results:
        census_data = [
            CensusRecord(
                column="TYPEREPORT_FS",
                value=audit_header.TYPEREPORT_FS,
            ).to_dict(),
            CensusRecord(
                column="SP_FRAMEWORK",
                value=audit_header.SP_FRAMEWORK,
            ).to_dict(),
        ]
        gsa_fac_data = GsaFacRecord(
            field="sp_framework_basis",
            value=Util.json_array_to_str(
                sp_framework_gaap_results["sp_framework_basis"]
            ),
        ).to_dict()
        InspectionRecord.append_general_changes(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": [
                    "xform_build_sp_framework_gaap_results",
                    "xform_framework_basis",
                ],
            }
        )


def xform_sp_framework_required(audit_header):
    if (
        "S" in string_to_string(audit_header.TYPEREPORT_FS)
        and string_to_string(audit_header.SP_FRAMEWORK_REQUIRED) == ""
    ):
        census_data = [
            CensusRecord(
                column="TYPEREPORT_FS",
                value=audit_header.TYPEREPORT_FS,
            ).to_dict(),
            CensusRecord(
                column="SP_FRAMEWORK_REQUIRED",
                value=audit_header.SP_FRAMEWORK_REQUIRED,
            ).to_dict(),
        ]
        gsa_fac_data = GsaFacRecord(
            field="is_sp_framework_required", value=settings.GSA_MIGRATION
        ).to_dict()
        InspectionRecord.append_general_changes(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": [
                    "xform_sp_framework_required",
                ],
            }
        )
        audit_header.SP_FRAMEWORK_REQUIRED = settings.GSA_MIGRATION


def xform_lowrisk(audit_header):
    if string_to_string(audit_header.LOWRISK) == "":
        census_data = [
            CensusRecord(
                column="LOWRISK",
                value=audit_header.LOWRISK,
            ).to_dict(),
        ]
        gsa_fac_data = GsaFacRecord(
            field="is_low_risk_auditee", value=settings.GSA_MIGRATION
        ).to_dict()
        InspectionRecord.append_general_changes(
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": [
                    "xform_lowrisk",
                ],
            }
        )
        audit_header.LOWRISK = settings.GSA_MIGRATION


def audit_information(audit_header):
    """Generates audit information JSON."""
    if AceFlag.get_ace_report_flag():
        audit_info = ace_audit_information(audit_header)
    else:
        xform_sp_framework_required(audit_header)
        xform_lowrisk(audit_header)
        results = xform_build_sp_framework_gaap_results(audit_header)
        audit_info = create_json_from_db_object(audit_header, mappings)
        audit_info = {
            key: results.get(key, audit_info.get(key))
            for key in set(audit_info) | set(results)
        }

    agencies_prefixes = _get_agency_prefixes(audit_header.DBKEY, audit_header.AUDITYEAR)
    audit_info["agencies"] = list(agencies_prefixes)

    audit.validators.validate_audit_information_json(audit_info)

    return audit_info


def ace_audit_information(audit_header):
    """Constructs the audit information JSON object for an ACE report."""
    actual = create_json_from_db_object(audit_header, mappings)
    default = {
        "dollar_threshold": settings.GSA_MIGRATION_INT,
        "gaap_results": [settings.GSA_MIGRATION],
        "is_going_concern_included": settings.GSA_MIGRATION,
        "is_internal_control_deficiency_disclosed": settings.GSA_MIGRATION,
        "is_internal_control_material_weakness_disclosed": settings.GSA_MIGRATION,
        "is_material_noncompliance_disclosed": settings.GSA_MIGRATION,
        "is_aicpa_audit_guide_included": settings.GSA_MIGRATION,
        "is_low_risk_auditee": settings.GSA_MIGRATION,
        "agencies": [settings.GSA_MIGRATION],
    }
    if actual:
        for key, value in actual.items():
            if value:
                default[key] = value
    # Tracking invalid records
    invalid_records = []
    for mapping in mappings:
        in_dissem = (
            mapping.in_dissem
            if mapping.in_dissem != FormFieldInDissem
            else mapping.in_form
        )
        track_invalid_records(
            [
                (mapping.in_db, getattr(audit_header, mapping.in_db)),
            ],
            in_dissem,
            default[mapping.in_form],
            invalid_records,
        )
    if invalid_records:
        InvalidRecord.append_invalid_migration_tag(
            INVALID_MIGRATION_TAGS.ACE_AUDIT_REPORT,
        )

    return default
