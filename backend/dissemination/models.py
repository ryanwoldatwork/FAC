from django.db import models
from django.utils import timezone

from . import docs

from .hist_models import census_2019, census_2022  # noqa: F401

BIGINT_MAX_DIGITS = 25

REPORT_ID_FK_HELP_TEXT = "GSAFAC generated identifier"


class FindingText(models.Model):
    """Specific findings details. References General"""

    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    finding_ref_number = models.TextField(
        "Finding Reference Number - FK",
        help_text=docs.finding_ref_nums_findingstext,
    )
    contains_chart_or_table = models.TextField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        help_text=docs.charts_tables_findingstext,
    )
    finding_text = models.TextField(
        "Content of the finding text",
        help_text=docs.text_findingstext,
    )


class AdditionalUei(models.Model):
    """Additional UEIs for this audit."""

    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    additional_uei = models.TextField()


class AdditionalEin(models.Model):
    """Additional EINs for this audit."""

    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    additional_ein = models.TextField()


class Finding(models.Model):
    """A finding from the audit. References FederalAward and FindingText"""

    award_reference = models.TextField(
        "Order that the award line was reported in Award",
    )
    reference_number = models.TextField(
        "Findings Reference Numbers",
        help_text=docs.finding_ref_nums_findings,
    )
    is_material_weakness = models.TextField(
        "Material Weakness finding",
        help_text=docs.material_weakness_findings,
    )
    is_modified_opinion = models.TextField(
        "Modified Opinion finding", help_text=docs.modified_opinion
    )
    is_other_findings = models.TextField(
        "Other findings", help_text=docs.other_findings
    )
    is_other_matters = models.TextField(
        "Other non-compliance", help_text=docs.other_non_compliance
    )
    is_questioned_costs = models.TextField(
        "Questioned Costs", help_text=docs.questioned_costs_findings
    )
    is_repeat_finding = models.TextField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        help_text=docs.repeat_finding,
    )
    is_significant_deficiency = models.TextField(
        "Significant Deficiency finding",
        help_text=docs.significant_deficiency_findings,
    )
    prior_finding_ref_numbers = models.TextField(
        "Audit finding reference numbers from the immediate prior audit",
        help_text=docs.prior_finding_ref_nums,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    # each element in the list is a FK to Finding
    type_requirement = models.TextField(
        "Type Requirement Failure",
        help_text=docs.type_requirement_findings,
    )

class OversightSearch(models.Model):
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    federal_agency_prefix = models.TextField(
        "2-char code refers to an agency",
    )
    federal_award_extension = models.TextField(
        "3-digit extn for a program defined by the agency",
    )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)",
        help_text=docs.findings_count,
    )
    is_direct = models.TextField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        help_text=docs.direct,
    )
    is_direct = models.TextField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        help_text=docs.direct,
    )
    is_major = models.TextField(
        "Indicate whether or not the Federal program is a major program",
        help_text=docs.major_program,
    )
    is_material_weakness = models.TextField(
        "Material Weakness finding",
        help_text=docs.material_weakness_findings,
    )
    is_modified_opinion = models.TextField(
        "Modified Opinion finding", help_text=docs.modified_opinion
    )
    is_other_findings = models.TextField(
        "Other findings", help_text=docs.other_findings
    )
    is_other_matters = models.TextField(
        "Other non-compliance", help_text=docs.other_non_compliance
    )
    is_questioned_costs = models.TextField(
        "Questioned Costs", help_text=docs.questioned_costs_findings
    )
    is_repeat_finding = models.TextField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        help_text=docs.repeat_finding,
    )
    is_significant_deficiency = models.TextField(
        "Significant Deficiency finding",
        help_text=docs.significant_deficiency_findings,
    )



class FederalAward(models.Model):
    """Information about the federal award section of the form. References General"""

    # 20240125 - These are indices that would be used in our ALN search/annotation.
    # class Meta:
    #     indexes = [
    #         models.Index(fields=["report_id",]),
    #         # This is possibly redundant with the pairwise index?
    #         models.Index(fields=["federal_agency_prefix",]),
    #         models.Index(fields=["federal_agency_prefix", "federal_award_extension"]),
    #         models.Index(fields=[
    #             "report_id",
    #             "federal_agency_prefix",
    #             "findings_count"
    #             ]),
    #     ]

    additional_award_identification = models.TextField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        help_text=docs.award_identification,
    )
    amount_expended = models.BigIntegerField(
        "Amount Expended for the Federal Program",
        help_text=docs.amount,
    )
    award_reference = models.TextField(
        "Order that the award line was reported",
    )
    cluster_name = models.TextField(
        "The name of the cluster",
        help_text=docs.cluster_name,
    )
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name",
        help_text=docs.cluster_total,
    )
    federal_agency_prefix = models.TextField(
        "2-char code refers to an agency",
    )
    federal_award_extension = models.TextField(
        "3-digit extn for a program defined by the agency",
    )
    federal_program_name = models.TextField(
        "Name of Federal Program",
        help_text=docs.federal_program_name,
    )
    federal_program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension",
        help_text=docs.program_total,
    )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)",
        help_text=docs.findings_count,
    )
    is_direct = models.TextField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        help_text=docs.direct,
    )
    is_loan = models.TextField(
        "Indicate whether or not the program is a Loan or Loan Guarantee (only available for audit years 2013 and beyond)",
        help_text=docs.loans,
    )
    is_major = models.TextField(
        "Indicate whether or not the Federal program is a major program",
        help_text=docs.major_program,
    )
    is_passthrough_award = models.TextField(
        "Indicates whether or not funds were passed through to any subrecipients for the Federal program",
        help_text=docs.passthrough_award,
    )
    loan_balance = models.TextField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        help_text=docs.loan_balance,
    )
    audit_report_type = models.TextField(
        "Type of Report Issued on the Major Program Compliance",
        help_text=docs.type_report_major_program_cfdainfo,
    )
    other_cluster_name = models.TextField(
        "The name of the cluster (if not listed in the Compliance Supplement)",
        help_text=docs.other_cluster_name,
    )
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients",
        help_text=docs.passthrough_amount,
        null=True,
    )
    state_cluster_name = models.TextField(
        "The name of the state cluster",
        help_text=docs.state_cluster_name,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )


class CapText(models.Model):
    """Corrective action plan text. Referebces General"""

    contains_chart_or_table = models.TextField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        help_text=docs.charts_tables_captext,
    )
    finding_ref_number = models.TextField(
        "Audit Finding Reference Number",
        help_text=docs.finding_ref_nums_captext,
    )
    planned_action = models.TextField(
        "Content of the Corrective Action Plan (CAP)",
        help_text=docs.text_captext,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )


class Note(models.Model):
    """Note to Schedule of Expenditures of Federal Awards (SEFA)"""

    accounting_policies = models.TextField(
        "A description of the significant accounting policies used in preparing the SEFA (2 CFR 200.510(b)(6))",
    )
    is_minimis_rate_used = models.TextField("'Yes', 'No', or 'Both' (2 CFR 200.414(f))")
    rate_explained = models.TextField("Explanation for minimis rate")
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    content = models.TextField("Content of the Note", help_text=docs.content)
    note_title = models.TextField("Note title", help_text=docs.title)
    contains_chart_or_table = models.TextField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        help_text=docs.charts_tables_note,
    )


class Passthrough(models.Model):
    """The pass-through entity information, when it is not a direct federal award"""

    award_reference = models.TextField(
        "Order that the award line was reported",
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    passthrough_id = models.TextField(
        "Identifying Number Assigned by the Pass-through Entity",
        help_text=docs.passthrough_id,
    )
    passthrough_name = models.TextField(
        "Name of Pass-through Entity",
        help_text=docs.passthrough_name,
    )


class General(models.Model):
    # Relational fields
    # null = True for these so we can load in phases, may want to tighten validation later
    # 20240125 - These are indices that would be used in our ALN search/annotation.
    # class Meta:
    #     indexes = [
    #         models.Index(fields=["report_id",]),
    #         models.Index(fields=["fac_accepted_date",]),

    #     ]

    report_id = models.TextField(
        "Report ID",
        help_text=REPORT_ID_FK_HELP_TEXT,
        unique=True,
    )
    auditee_certify_name = models.TextField(
        "Name of Auditee Certifying Official",
        help_text=docs.auditee_certify_name,
    )
    auditee_certify_title = models.TextField(
        "Title of Auditee Certifying Official",
        help_text=docs.auditee_certify_title,
    )
    auditor_certify_name = models.TextField(
        "Name of Auditor Certifying Official",
        help_text=docs.auditor_certify_name,
    )
    auditor_certify_title = models.TextField(
        "Title of Auditor Certifying Official",
        help_text=docs.auditor_certify_title,
    )
    auditee_contact_name = models.TextField(
        "Name of Auditee Contact",
        help_text=docs.auditee_contact,
    )
    auditee_email = models.TextField(
        "Auditee Email address",
        help_text=docs.auditee_email,
    )
    auditee_name = models.TextField("Name of the Auditee", help_text=docs.auditee_name)
    auditee_phone = models.TextField(
        "Auditee Phone Number", help_text=docs.auditee_phone
    )
    auditee_contact_title = models.TextField(
        "Title of Auditee Contact",
        help_text=docs.auditee_title,
    )
    auditee_address_line_1 = models.TextField(
        "Auditee Street Address", help_text=docs.street1
    )
    auditee_city = models.TextField("Auditee City", help_text=docs.city)
    auditee_state = models.TextField("Auditee State", help_text=docs.state)
    auditee_ein = models.TextField(
        "Primary Employer Identification Number",
    )

    auditee_uei = models.TextField("Auditee UEI", help_text=docs.uei_general)

    is_additional_ueis = models.TextField()

    auditee_zip = models.TextField(
        "Auditee Zip Code",
        help_text=docs.zip_code,
    )
    auditor_phone = models.TextField("CPA phone number", help_text=docs.auditor_phone)

    auditor_state = models.TextField("CPA State", help_text=docs.auditor_state)
    auditor_city = models.TextField("CPA City", help_text=docs.auditor_city)
    auditor_contact_title = models.TextField(
        "Title of CPA Contact",
        help_text=docs.auditor_title,
    )
    auditor_address_line_1 = models.TextField(
        "CPA Street Address",
        help_text=docs.auditor_street1,
    )
    auditor_zip = models.TextField(
        "CPA Zip Code",
        help_text=docs.auditor_zip_code,
    )
    auditor_country = models.TextField("CPA Country", help_text=docs.auditor_country)
    auditor_contact_name = models.TextField(
        "Name of CPA Contact",
        help_text=docs.auditor_contact,
    )
    auditor_email = models.TextField(
        "CPA mail address (optional)",
        help_text=docs.auditor_email,
    )
    auditor_firm_name = models.TextField(
        "CPA Firm Name", help_text=docs.auditor_firm_name
    )
    # Once loaded, would like to add these as regular addresses and just change this to a country field
    auditor_foreign_address = models.TextField(
        "CPA Address - if international",
        help_text=docs.auditor_foreign,
    )
    auditor_ein = models.TextField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        help_text=docs.auditor_ein,
    )

    # Agency
    cognizant_agency = models.TextField(
        "Two digit Federal agency prefix of the cognizant agency",
        help_text=docs.cognizant_agency,
        null=True,
    )
    oversight_agency = models.TextField(
        "Two digit Federal agency prefix of the oversight agency",
        help_text=docs.oversight_agency,
        null=True,
    )

    # Dates
    date_created = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        help_text=docs.initial_date_received,
    )
    ready_for_certification_date = models.DateField(
        "The date at which the audit transitioned to 'ready for certification'",
    )
    auditor_certified_date = models.DateField(
        "The date at which the audit transitioned to 'auditor certified'",
    )
    auditee_certified_date = models.DateField(
        "The date at which the audit transitioned to 'auditee certified'",
    )
    submitted_date = models.DateField(
        "The date at which the audit transitioned to 'submitted'",
    )
    fac_accepted_date = models.DateField(
        "The date at which the audit transitioned to 'accepted'",
    )
    # auditor_signature_date = models.DateField(
    #     "The date on which the auditor signed the audit",
    # )
    # auditee_signature_date = models.DateField(
    #     "The date on which the auditee signed the audit",
    # )
    fy_end_date = models.DateField("Fiscal Year End Date", help_text=docs.fy_end_date)
    fy_start_date = models.DateField(
        "Fiscal Year Start Date", help_text=docs.fy_start_date
    )
    audit_year = models.TextField(
        "Audit year from fy_start_date.",
        help_text=docs.audit_year_general,
    )

    audit_type = models.TextField(
        "Type of Audit",
        help_text=docs.audit_type,
    )

    # Audit Info
    gaap_results = models.TextField(
        "GAAP Results by Auditor",
    )  # Concatenation of choices
    sp_framework_basis = models.TextField(
        "Special Purpose Framework that was used as the basis of accounting",
        help_text=docs.sp_framework,
    )
    is_sp_framework_required = models.TextField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        help_text=docs.sp_framework_required,
    )
    sp_framework_opinions = models.TextField(
        "The auditor's opinion on the special purpose framework",
        help_text=docs.type_report_special_purpose_framework,
    )
    is_going_concern_included = models.TextField(
        "Whether or not the audit contained a going concern paragraph on financial statements",
        help_text=docs.going_concern,
    )
    is_internal_control_deficiency_disclosed = models.TextField(
        "Whether or not the audit disclosed a significant deficiency on financial statements",
        help_text=docs.significant_deficiency_general,
    )
    is_internal_control_material_weakness_disclosed = models.TextField(
        help_text=docs.material_weakness_general
    )
    is_material_noncompliance_disclosed = models.TextField(
        "Whether or not the audit disclosed a material noncompliance on financial statements",
        help_text=docs.material_noncompliance,
    )
    # is_duplicate_reports = models.BooleanField(
    #     "Whether or not the financial statements include departments that have separate expenditures not included in this audit",
    #     null=True,
    #     help_text=docs.dup_reports,
    # )  # is_aicpa_audit_guide_included
    is_aicpa_audit_guide_included = models.TextField()
    dollar_threshold = models.BigIntegerField(
        "Dollar Threshold to distinguish between Type A and Type B programs.",
        help_text=docs.dollar_threshold,
    )
    is_low_risk_auditee = models.TextField(
        "Indicate whether or not the auditee qualified as a low-risk auditee",
        help_text=docs.low_risk,
    )
    agencies_with_prior_findings = models.TextField(
        "List of agencues with prior findings",
    )  # Concatenation of agency codes
    # End of Audit Info

    entity_type = models.TextField(
        "Self reported type of entity (i.e., States, Local Governments, Indian Tribes, Institutions of Higher Education, NonProfit)",
        help_text=docs.entity_type,
    )
    number_months = models.TextField(
        "Number of Months Covered by the 'Other' Audit Period",
        help_text=docs.number_months,
    )
    audit_period_covered = models.TextField(
        "Audit Period Covered by Audit", help_text=docs.period_covered
    )
    total_amount_expended = models.BigIntegerField(
        "Total Federal Expenditures",
        help_text=docs.total_fed_expenditures,
    )

    type_audit_code = models.TextField(
        "Determines if audit is A133 or UG",
    )

    is_public = models.BooleanField(
        "True for public records, False for non-public records", default=False
    )
    # Choices are: GSA, Census, or TESTDATA
    data_source = models.TextField("Data origin; GSA, Census, or TESTDATA")
    # FIXME This looks like audit_report_type in FederalAwards, must be verified
    #  and removed if needed.
    # type_report_major_program = models.TextField(
    #     "Type of Report Issued on the Major Program Compliance",
    #     null=True,
    #     help_text=docs.type_report_major_program_general,
    # )

    class Meta:
        unique_together = (("report_id",),)

    def __str__(self):
        return (
            f"report_id:{self.report_id} UEI:{self.auditee_uei}, AY:{self.audit_year}"
        )


class SecondaryAuditor(models.Model):
    address_city = models.TextField(
        "CPA City",
        help_text=docs.auditor_city,
    )
    address_state = models.TextField(
        "CPA State",
        help_text=docs.auditor_state,
    )
    address_street = models.TextField(
        "CPA Street Address",
        help_text=docs.auditor_street1,
    )
    address_zipcode = models.TextField(
        "CPA Zip Code",
        help_text=docs.auditor_zip_code,
    )
    auditor_ein = models.TextField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        help_text=docs.auditor_ein,
    )
    auditor_name = models.TextField(
        "CPA Firm Name",
        help_text=docs.auditor_firm_name,
    )
    contact_email = models.TextField(
        "CPA mail address (optional)",
        help_text=docs.auditor_email,
    )
    contact_name = models.TextField(
        "Name of CPA Contact",
    )
    contact_phone = models.TextField(
        "CPA phone number",
        help_text=docs.auditor_phone,
    )
    contact_title = models.TextField(
        "Title of CPA Contact",
        help_text=docs.auditor_title,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )


class OneTimeAccess(models.Model):
    uuid = models.UUIDField()
    timestamp = models.DateTimeField(
        auto_now_add=True,
    )
    api_key_id = models.TextField(
        "API key Id for the user",
    )
    report_id = models.TextField(
        "Report ID",
        help_text=REPORT_ID_FK_HELP_TEXT,
    )


class MigrationInspectionRecord(models.Model):
    audit_year = models.TextField(blank=True, null=True)
    dbkey = models.TextField(blank=True, null=True)
    report_id = models.TextField(blank=True, null=True)
    run_datetime = models.DateTimeField(default=timezone.now)
    finding_text = models.JSONField(blank=True, null=True)
    additional_uei = models.JSONField(blank=True, null=True)
    additional_ein = models.JSONField(blank=True, null=True)
    finding = models.JSONField(blank=True, null=True)
    federal_award = models.JSONField(blank=True, null=True)
    cap_text = models.JSONField(blank=True, null=True)
    note = models.JSONField(blank=True, null=True)
    passthrough = models.JSONField(blank=True, null=True)
    general = models.JSONField(blank=True, null=True)
    secondary_auditor = models.JSONField(blank=True, null=True)
