import json
from audit.models import SingleAuditChecklist
from .excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    model_to_dict,
    templates,
    set_uei,
    insert_version_and_sheet_name,
    set_single_cell_range,
    map_simple_columns,
    generate_dissemination_test_table,
    set_range,
)
from django.db.models import Q


from config import settings
from .transformers import clean_cfda, get_extra_cfda_attrinutes

from c2g.models import (
    ELECAUDITS as Cfda,
    ELECPASSTHROUGH as PassThrough,
)

import openpyxl as pyxl

# import json
import re

import logging

logger = logging.getLogger(__name__)


class FederalAward:
    def __init__(self, cfda: Cfda, seq):
        self.dict_instance = {}

        cfda.LOANBALANCE = self.normalize_number(cfda.LOANBALANCE)
        cfda.AMOUNT = self.normalize_number(cfda.AMOUNT)
        cfda.FINDINGSCOUNT = self.normalize_number(cfda.FINDINGSCOUNT)
        cfda.AWARDIDENTIFICATION = self.normalize_addl_award_id(
            cfda.AWARDIDENTIFICATION, cfda.CFDA, cfda.DBKEY
        )
        cfda.STATECLUSTERNAME = (
            cfda.STATECLUSTERNAME if "STATE CLUSTER" == cfda.CLUSTERNAME else ""
        )

        self.dict_instance["program_name"] = cfda.FEDERALPROGRAMNAME
        self.dict_instance["state_cluster_name"] = cfda.STATECLUSTERNAME
        self.dict_instance["federal_program_total"] = cfda.PROGRAMTOTAL
        self.dict_instance["cluster_total"] = cfda.CLUSTERTOTAL
        self.dict_instance["is_guaranteed"] = cfda.LOANS
        self.dict_instance["loan_balance_at_audit_period_end"] = cfda.LOANBALANCE
        self.dict_instance["is_direct"] = cfda.DIRECT
        self.dict_instance["is_passed"] = cfda.PASSTHROUGHAWARD
        self.dict_instance["subrecipient_amount"] = cfda.PASSTHROUGHAMOUNT
        self.dict_instance["is_major"] = cfda.MAJORPROGRAM
        self.dict_instance["amount_expended"] = cfda.AMOUNT
        self.dict_instance["program"] = {
            "number_of_audit_findings": int(cfda.FINDINGSCOUNT)
        }

        self.dict_instance["award_reference"] = f"AWARD-{seq+1:04}"

    def normalize_number(self, number: str):
        if number in ["N/A", "", None]:
            return "0"
        if self.is_positive(number):
            return number
        return "0"

    def is_positive(self, s):
        try:
            value = int(s)
            return value >= 0
        except ValueError:
            return False

    def normalize_addl_award_id(self, award_id: str, cfda_id: str, dbkey):
        if "u" in cfda_id.lower() or "rd" in cfda_id.lower():
            if not award_id or len(award_id) == 0:
                return f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
            return award_id
        return ""

    def get_dict(self):
        return self.dict_instance


def if_zero_empty(v):
    if int(v) == 0:
        return ""
    else:
        return int(v)


mappings = [
    FieldMap(
        "program_name", "federalprogramname".upper(), "federal_program_name", None, str
    ),
    FieldMap(
        "state_cluster_name",
        "stateclustername".upper(),
        WorkbookFieldInDissem,
        None,
        str,
    ),
    FieldMap(
        "federal_program_total", "programtotal".upper(), WorkbookFieldInDissem, 0, int
    ),
    FieldMap("cluster_total", "clustertotal".upper(), WorkbookFieldInDissem, 0, int),
    FieldMap("is_guaranteed", "loans".upper(), "is_loan", None, str),
    FieldMap(
        "loan_balance_at_audit_period_end",
        "loanbalance".upper(),
        "loan_balance",
        None,
        int,
    ),
    FieldMap("is_direct", "direct".upper(), WorkbookFieldInDissem, None, str),
    FieldMap(
        "is_passed", "passthroughaward".upper(), "is_passthrough_award", None, str
    ),
    FieldMap(
        "subrecipient_amount",
        "passthroughamount".upper(),
        "passthrough_amount",
        None,
        if_zero_empty,
    ),
    FieldMap("is_major", "majorprogram".upper(), WorkbookFieldInDissem, None, str),
    FieldMap(
        "audit_report_type", "typereport_mp".upper(), "audit_report_type", None, str
    ),
    FieldMap(
        "number_of_audit_findings", "findingscount".upper(), "findings_count", 0, int
    ),
    FieldMap("amount_expended", "amount".upper(), WorkbookFieldInDissem, 0, int),
]


def get_list_index(all, index):
    counter = 0
    for o in list(all):
        if o.ID == index:
            return counter
        else:
            counter += 1
    return -1


def int_or_na(o):
    if o == "N/A":
        return o
    elif isinstance(o, int):
        return int(o)
    else:
        return "N/A"


def _generate_cluster_names(cfdas, valid_json):
    cluster_names = []
    other_cluster_names = []
    cfda: Cfda
    for cfda in cfdas:
        if not cfda.CLUSTERNAME or len(cfda.CLUSTERNAME) == 0:
            cluster_names.append("N/A")
            other_cluster_names.append("")
        elif cfda.CLUSTERNAME in valid_json["cluster_names"]:
            cluster_names.append(cfda.CLUSTERNAME)
            other_cluster_names.append("")
        else:
            logger.debug(f"Cluster {cfda.CLUSTERNAME} not in the list. Replacing.")
            cluster_names.append("OTHER CLUSTER NOT LISTED ABOVE")
            other_cluster_names.append(f"{cfda.CLUSTERNAME}")

    return (cluster_names, other_cluster_names)


def _fix_addl_award_identification(cfdas, audit_year, dbkey):
    addls = ["" for _ in list(range(0, len(cfdas)))]
    cfda: Cfda
    for cfda in Cfda.objects.filter(
        Q(DBKEY=dbkey)
        & Q(AUDITYEAR=audit_year)
        & (
            Q(CFDA__icontains="%U%")
            | Q(CFDA__icontains="%u%")
            | Q(CFDA__icontains="%rd%")
            | Q(CFDA__icontains="%RD%")
        )
    ).order_by("ID"):
        if cfda.AWARDIDENTIFICATION is None or len(cfda.AWARDIDENTIFICATION) < 1:
            addls[
                get_list_index(cfdas, cfda.id)
            ] = f"ADDITIONAL AWARD INFO - DBKEY {dbkey}"
        else:
            addls[get_list_index(cfdas, cfda.id)] = cfda.AWARDIDENTIFICATION
    return addls


def _fix_pfixes(cfdas):
    # Map things with transformations
    prefixes = map(lambda v: (v.CFDA).split(".")[0], cfdas)
    # prefixes = map(lambda v: f'0{v}' if int(v) < 10 else v, prefixes)
    # Truncate any nastiness in the CFDA extensions to three characters.
    extensions = map(lambda v: ((v.CFDA).split(".")[1])[:3].upper(), cfdas)
    extensions = map(
        lambda v: v
        if re.search("^(RD|RD[0-9]|[0-9]{3}[A-Za-z]{0,1}|U[0-9]{2})$", v)
        else "000",
        extensions,
    )
    return (prefixes, extensions, map(lambda v: v.CFDA, cfdas))


def _fix_passthroughs(cfdas, audit_year, dbkey):
    passthrough_names = ["" for x in list(range(0, len(cfdas)))]
    passthrough_ids = ["" for x in list(range(0, len(cfdas)))]
    cfda: Cfda
    for cfda in Cfda.objects.filter(Q(DBKEY=dbkey) & Q(AUDITYEAR=audit_year)).order_by(
        "ID"
    ):
        pnq = PassThrough()
        if cfda.DIRECT == "Y":
            pnq.PASSTHROUGHNAME = ""
            pnq.PASSTHROUGHID = ""
        if cfda.DIRECT == "N":
            try:
                pnq = PassThrough.objects.get(
                    DBKEY=dbkey, AUDITYEAR=audit_year, ELECAUDITSID=cfda.ELECAUDITSID
                )

            except Exception as e:
                print(e)
                pnq.passthroughname = "EXCEPTIONAL PASSTHROUGH NAME"
                pnq.passthroughid = "EXCEPTIONAL PASSTHROUGH ID"

        name = pnq.PASSTHROUGHNAME
        if name is None:
            name = ""
        name = name.rstrip()
        if name == "" and cfda.DIRECT == "N":
            passthrough_names[
                get_list_index(cfdas, cfda.ID)
            ] = "NO PASSTHROUGH NAME PROVIDED"
        else:
            passthrough_names[get_list_index(cfdas, cfda.ID)] = name

        ID = pnq.ID
        if ID is None:
            ID = ""
        ID = ID.rstrip()
        if ID == "" and cfda.DIRECT == "N":
            passthrough_ids[
                get_list_index(cfdas, cfda.ID)
            ] = "NO PASSTHROUGH ID PROVIDED"
        else:
            passthrough_ids[get_list_index(cfdas, cfda.ID)] = pnq.PASSTHROUGHID

    return (passthrough_names, passthrough_ids)


def federal_awards_to_json(sac: SingleAuditChecklist, dbkey, audit_year):
    json_str: str = '{"FederalAwards" : {"federal_awards":['
    cfdas = Cfda.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    cfda: Cfda
    for i in range(len(cfdas)):
        cfda = cfdas[i]
        award = FederalAward(cfda, i)
        if i > 0:
            json_str += ","
        json_str += json.dumps(award.get_dict())
    json_str += "]}}"
    json_obj = json.loads(json_str)
    sac.federal_awards = json_obj


def generate_federal_awards(sac, dbkey, audit_year, outfile):
    logger.info(f"--- generate federal awards {dbkey} {audit_year} ---")
    wb = pyxl.load_workbook(templates["FederalAwards"])
    # In sheet : in DB

    set_uei(sac, wb)
    insert_version_and_sheet_name(wb, "federal-awards-workbook")

    cfdas = Cfda.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    cfda: Cfda
    for cfda in cfdas:
        clean_cfda(cfda)
    map_simple_columns(wb, mappings, cfdas)

    cluster_names = get_extra_cfda_attrinutes("cluster_names")
    set_range(wb, "cluster_name", cluster_names)
    other_cluster_names = get_extra_cfda_attrinutes("cluster_names")
    set_range(wb, "other_cluster_name", other_cluster_names)
    prefixes = get_extra_cfda_attrinutes("prefixes")
    set_range(wb, "federal_agency_prefix", prefixes)
    extensions = get_extra_cfda_attrinutes("extensions")
    set_range(wb, "three_digit_extension", extensions)
    award_references = [f"AWARD-{n+1:04}" for n in range(len(cfdas))]
    set_range(wb, "award_reference", award_references, default="Empty")
    addls = [cfda.AWARDIDENTIFICATION for cfda in cfdas]
    set_range(wb, "additional_award_identification", addls)
    total = sum([int(cfda.AMOUNT) for cfda in cfdas])
    set_single_cell_range(wb, "total_amount_expended", total)
    # state_cluster_names = [cfda.STATECLUSTERNAME for cfda in cfdas]
    # set_range(wb, "state_cluster_name", state_cluster_names)

    """
    # Fix the additional award identification. If they had a "U", we want
    # to see something in the addl. column.
    addls = _fix_addl_award_identification(cfdas, audit_year, dbkey)
    set_range(wb, "additional_award_identification", addls)

    (prefixes, extensions, full_cfdas) = _fix_pfixes(cfdas)

    # We need a `cfda_key` as a magic column for the summation logic to work/be checked.
    set_range(wb, "cfda_key", full_cfdas, conversion_fun=str)

    (passthrough_names, passthrough_ids) = _fix_passthroughs(cfdas, audit_year, dbkey)
    set_range(wb, "passthrough_name", passthrough_names)
    set_range(wb, "passthrough_identifying_number", passthrough_ids)

    # The award numbers!
    award_references = [f"AWARD-{n+1:04}" for n in range(len(cfdas))]

    set_range(wb, "award_reference", award_references, default="Empty")

    # Total amount expended must be calculated and inserted
    total = 0
    for cfda in cfdas:
        total += int(cfda.AMOUNT)
    set_single_cell_range(wb, "total_amount_expended", total)

    # loansatend = list()
    # cfda: Cfda
    # for cfda in Cfda.objects.filter(Q(DBKEY=dbkey) & Q(AUDITYEAR=audit_year)).order_by(
    #     "ID"
    # ):
    #     if cfda.LOANS == "Y":
    #         if cfda.LOANBALANCE is None:
    #             # loansatend.append("N/A")
    #             loansatend.append(1)
    #         else:
    #             loansatend.append(cfda.LOANBALANCE)
    #     else:
    #         loansatend.append("")
    # # set_range(wb, "loan_balance_at_audit_period_end", loansatend, type=int_or_na)
    # set_range(wb, "loan_balance_at_audit_period_end", loansatend, conversion_fun=int)
    """
    wb.save(outfile)

    table = generate_dissemination_test_table(
        sac, "federal_awards", audit_year, dbkey, mappings, cfdas
    )
    # award_counter = 1
    # prefix
    for obj, pfix, ext, refs, addl, cn, ocn in zip(
        table["rows"],
        prefixes,
        extensions,
        award_references,
        addls,
        cluster_names,
        other_cluster_names,
    ):
        obj["fields"].append("federal_agency_prefix")
        obj["values"].append(pfix)
        obj["fields"].append("three_digit_extension")
        obj["values"].append(ext)
        # Sneak in the award number here
        obj["fields"].append("award_reference")
        obj["values"].append(refs)
        obj["fields"].append("additional_award_identification")
        obj["values"].append(addl)
        obj["fields"].append("cluster_name")
        obj["values"].append(cn)
        obj["fields"].append("other_cluster_name")
        obj["fields"].append(ocn)

    table["singletons"]["auditee_uei"] = sac.auditee_uei
    table["singletons"]["total_amount_expended"] = total

    return (wb, table)
