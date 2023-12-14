from ..transforms.xform_string_to_string import (
    string_to_string,
)
from ..workbooklib.excel_creation_utils import (
    map_simple_columns,
    generate_dissemination_test_table,
    set_workbook_uei,
)
from ..base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECEINS as Eins
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def xform_remove_trailing_decimal_zero(value):
    """
    Removes trailing .0 from a EIN strings.
    Raises an exception if the decimal part is not 0.
    """
    trimmed_ein = string_to_string(value)

    if "." in trimmed_ein:
        whole, decimal = trimmed_ein.split(".")
        if decimal == "0":
            return whole
        else:
            raise ValueError(
                f"additional_ein has non zero decimal value: {trimmed_ein}"
            )

    return trimmed_ein


mappings = [
    SheetFieldMap(
        "additional_ein",
        "EIN",
        WorkbookFieldInDissem,
        None,
        xform_remove_trailing_decimal_zero,
    ),
]


def _get_eins(dbkey, year):
    return Eins.objects.filter(DBKEY=dbkey, AUDITYEAR=year)


def generate_additional_eins(audit_header, outfile):
    """
    Generates additional eins workbook for a given audit header.
    """
    logger.info(
        f"--- generate additional eins {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )
    uei = string_to_string(audit_header.UEI)
    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.ADDITIONAL_EINS])
    set_workbook_uei(wb, uei)
    addl_eins = _get_eins(audit_header.DBKEY, audit_header.AUDITYEAR)
    map_simple_columns(wb, mappings, addl_eins)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        audit_header, "additional_eins", mappings, addl_eins
    )
    table["singletons"]["auditee_uei"] = uei
    return (wb, table)
