from census_historical_migration.workbooklib.excel_creation_utils import (
    add_hyphen_to_zip,
    get_audit_header,
    map_simple_columns,
    generate_dissemination_test_table,
    set_workbook_uei,
)
from census_historical_migration.base_field_maps import SheetFieldMap
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.models import ELECCPAS as Caps
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "secondary_auditor_address_city", "CPACITY", "address_city", None, str
    ),
    SheetFieldMap(
        "secondary_auditor_contact_name", "CPACONTACT", "contact_name", None, str
    ),
    SheetFieldMap("secondary_auditor_ein", "CPAEIN", "auditor_ein", None, str),
    SheetFieldMap(
        "secondary_auditor_contact_email", "CPAEMAIL", "contact_email", None, str
    ),
    SheetFieldMap("secondary_auditor_name", "CPAFIRMNAME", "auditor_name", None, str),
    SheetFieldMap(
        "secondary_auditor_contact_phone", "CPAPHONE", "contact_phone", None, str
    ),
    SheetFieldMap(
        "secondary_auditor_address_state", "CPASTATE", "address_state", None, str
    ),
    SheetFieldMap(
        "secondary_auditor_address_street",
        "CPASTREET1",
        "address_street",
        None,
        str,
    ),
    SheetFieldMap(
        "secondary_auditor_contact_title",
        "CPATITLE",
        "contact_title",
        None,
        str,
    ),
    SheetFieldMap(
        "secondary_auditor_address_zipcode",
        "CPAZIPCODE",
        "address_zipcode",
        None,
        add_hyphen_to_zip,
    ),
]


def _get_secondary_auditors(dbkey):
    return Caps.objects.filter(DBKEY=dbkey)


def generate_secondary_auditors(dbkey, year, outfile):
    """
    Generates secondary auditor workbook for a given dbkey.
    """
    logger.info(f"--- generate secondary auditors {dbkey} {year} ---")

    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.SECONDARY_AUDITORS]
    )

    audit_header = get_audit_header(dbkey)

    set_workbook_uei(wb, audit_header.UEI)

    secondary_auditors = _get_secondary_auditors(dbkey)

    map_simple_columns(wb, mappings, secondary_auditors)

    wb.save(outfile)

    # FIXME - MSHD: The logic below will most likely be removed, see comment in federal_awards.py
    table = generate_dissemination_test_table(
        audit_header, "secondary_auditor", dbkey, mappings, secondary_auditors
    )

    table["singletons"]["auditee_uei"] = audit_header.UEI

    return (wb, table)
