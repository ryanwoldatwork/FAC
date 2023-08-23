import logging
from datetime import datetime

from dissemination.models import (
    FindingText,
    Finding,
    FederalAward,
    CapText,
    Note,
    Revision,
    Passthrough,
    General,
    SecondaryAuditor,
    AdditionalUei,
    AdditionalEin,
)
from audit.models import SingleAuditChecklist

logger = logging.getLogger(__name__)


class ETL(object):
    def __init__(self, sac: SingleAuditChecklist) -> None:
        self.single_audit_checklist = sac
        self.report_id = sac.report_id
        audit_date = sac.general_information.get(
            "auditee_fiscal_period_start", datetime.now
        )
        self.audit_year = int(audit_date.split("-")[0])

    def load_all(self):
        load_methods = (
            self.load_general,
            self.load_secondary_auditor,
            self.load_federal_award,
            self.load_findings,
            self.load_passthrough,
            self.load_finding_texts,
            self.load_captext,
            self.load_note,
            self.load_additional_uei,
            self.load_additional_ein,
            self.load_audit_info,
        )
        for load_method in load_methods:
            try:
                load_method()
            except KeyError as key_error:
                logger.warning(
                    f"{type(key_error).__name__} in {load_method.__name__}: {key_error}"
                )

    def load_finding_texts(self):
        findings_text = self.single_audit_checklist.findings_text

        if not findings_text:
            logger.warning("No finding texts found to load")
            return

        findings_text_entries = findings_text["FindingsText"]["findings_text_entries"]
        for entry in findings_text_entries:
            finding_text_ = FindingText(
                report_id=self.report_id,
                finding_ref_number=entry.get("reference_number", ""),
                contains_chart_or_table=entry["contains_chart_or_table"] == "Y",
                finding_text=entry.get("text_of_finding", ""),
            )
            finding_text_.save()

    def load_findings(self):
        findings_uniform_guidance = (
            self.single_audit_checklist.findings_uniform_guidance
        )
        if not findings_uniform_guidance:
            logger.warning("No findings found to load")
            return

        findings_uniform_guidance_entries = findings_uniform_guidance[
            "FindingsUniformGuidance"
        ]["findings_uniform_guidance_entries"]

        for entry in findings_uniform_guidance_entries:
            findings = entry["findings"]
            program = entry["program"]
            prior_finding_ref_numbers = None
            if "prior_references" in findings:
                prior_finding_ref_numbers = findings.get("prior_references", "")

            finding = Finding(
                award_reference=program.get("award_reference", ""),
                report_id=self.report_id,
                finding_ref_number=findings.get("reference_number", ""),
                is_material_weakness=entry["material_weakness"] == "Y",
                is_modified_opinion=entry["modified_opinion"] == "Y",
                is_other_findings=entry["other_findings"] == "Y",
                is_other_non_compliance=entry["other_matters"] == "Y",
                prior_finding_ref_numbers=prior_finding_ref_numbers,
                is_questioned_costs=entry["questioned_costs"] == "Y",
                is_repeat_finding=(findings["repeat_prior_reference"] == "Y"),
                is_significant_deficiency=(entry["significant_deficiency"] == "Y"),
                type_requirement=program.get("compliance_requirement", ""),
            )
            finding.save()

    def conditional_lookup(self, dict, key, default):
        if key in dict:
            return dict[key]
        else:
            return default

    def load_federal_award(self):
        federal_awards = self.single_audit_checklist.federal_awards
        general = self._get_general()
        if not general:
            logger.error(
                f"""
                General must be loaded before FederalAward.
                report_id = {self.single_audit_checklist.report_id}"
                """
            )
            return
        general.total_amount_expended = federal_awards["FederalAwards"].get(
            "total_amount_expended"
        )
        general.save()

        for entry in federal_awards["FederalAwards"]["federal_awards"]:
            program = entry["program"]
            loan = entry["loan_or_loan_guarantee"]
            is_direct = entry["direct_or_indirect_award"]["is_direct"] == "Y"
            is_passthrough = entry["subrecipients"]["is_passed"] == "Y"
            cluster = entry["cluster"]
            subrecipient_amount = entry["subrecipients"].get("subrecipient_amount")
            state_cluster_name = cluster.get("state_cluster_name", "")
            other_cluster_name = cluster.get("other_cluster_name", "")
            additional_award_identification = self.conditional_lookup(
                program, "additional_award_identification", ""
            )
            federal_award = FederalAward(
                report_id=self.report_id,
                award_reference=entry.get("award_reference", ""),
                federal_agency_prefix=program["federal_agency_prefix"],
                federal_award_extension=program["three_digit_extension"],
                additional_award_identification=additional_award_identification,
                federal_program_name=program.get("program_name", ""),
                amount_expended=program["amount_expended"],
                cluster_name=cluster.get("cluster_name", ""),
                other_cluster_name=other_cluster_name,
                state_cluster_name=state_cluster_name,
                cluster_total=cluster["cluster_total"],
                federal_program_total=program["federal_program_total"],
                is_loan=loan["is_guaranteed"] == "Y",
                loan_balance=self.conditional_lookup(
                    loan, "loan_balance_at_audit_period_end", 0
                ),
                is_direct=is_direct,
                is_major=program["is_major"] == "Y" if "is_major" in program else False,
                mp_audit_report_type=self.conditional_lookup(
                    program, "audit_report_type", ""
                ),
                findings_count=program["number_of_audit_findings"],
                is_passthrough_award=is_passthrough,
                passthrough_amount=subrecipient_amount,
            )
            federal_award.save()

    def load_captext(self):
        corrective_action_plan = self.single_audit_checklist.corrective_action_plan
        if (
            "corrective_action_plan_entries"
            in corrective_action_plan["CorrectiveActionPlan"]
        ):
            corrective_action_plan_entries = corrective_action_plan[
                "CorrectiveActionPlan"
            ]["corrective_action_plan_entries"]
            for entry in corrective_action_plan_entries:
                cap_text = CapText(
                    report_id=self.report_id,
                    finding_ref_number=entry.get("reference_number", ""),
                    contains_chart_or_table=entry["contains_chart_or_table"] == "Y",
                    planned_action=entry.get("planned_action", ""),
                )
                cap_text.save()

    def load_note(self):
        if (
            self.single_audit_checklist.notes_to_sefa is not None
        ) and "NotesToSefa" in self.single_audit_checklist.notes_to_sefa:
            notes_to_sefa = self.single_audit_checklist.notes_to_sefa["NotesToSefa"]
            if notes_to_sefa:
                accounting_policies = notes_to_sefa.get("accounting_policies", "")
                is_minimis_rate_used = notes_to_sefa["is_minimis_rate_used"] == "Y"
                rate_explained = notes_to_sefa["rate_explained"]
                if "notes_to_sefa_entries" in notes_to_sefa:
                    entries = notes_to_sefa["notes_to_sefa_entries"]
                    if not entries:
                        note = Note(
                            report_id=self.report_id,
                            accounting_policies=accounting_policies,
                            is_minimis_rate_used=is_minimis_rate_used,
                            rate_explained=rate_explained,
                        )
                        note.save()
                    else:
                        for entry in entries:
                            note = Note(
                                report_id=self.report_id,
                                content=entry.get("note_content", ""),
                                note_title=entry.get("note_title", ""),
                                accounting_policies=accounting_policies,
                                is_minimis_rate_used=is_minimis_rate_used,
                                rate_explained=rate_explained,
                            )
                            note.save()

    def load_revision(self):
        revision = Revision(
            findings=None,  # TODO: Where does this come from?
            revision_id=None,  # TODO: Where does this come from?
            federal_awards=None,  # TODO: Where does this come from?
            general_info_explain=None,  # TODO: Where does this come from?
            federal_awards_explain=None,  # TODO: Where does this come from?
            notes_to_sefa_explain=None,  # TODO: Where does this come from?
            audit_info_explain=None,  # TODO: Where does this come from?
            findings_explain=None,  # TODO: Where does this come from?
            findings_text_explain=None,  # TODO: Where does this come from?
            cap_explain=None,  # TODO: Where does this come from?
            other_explain=None,  # TODO: Where does this come from?
            audit_info=None,  # TODO: Where does this come from?
            notes_to_sefa=None,  # TODO: Where does this come from?
            findings_tex=None,  # TODO: Where does this come from?
            cap=None,  # TODO: Where does this come from?
            other=None,  # TODO: Where does this come from?
            general_info=None,  # TODO: Where does this come from?
            audit_year=self.audit_year,
            report_id=self.report_id,
        )
        revision.save()

    def load_passthrough(self):
        federal_awards = self.single_audit_checklist.federal_awards
        for entry in federal_awards["FederalAwards"]["federal_awards"]:
            if "entities" in entry["direct_or_indirect_award"]:
                for entity in entry["direct_or_indirect_award"]["entities"]:
                    passthrough = Passthrough(
                        award_reference=entry.get("award_reference", ""),
                        report_id=self.report_id,
                        passthrough_id=entity.get("passthrough_identifying_number", ""),
                        passthrough_name=entity.get("passthrough_name", ""),
                    )
                    passthrough.save()

    def _get_dates_from_sac(self):
        return_dict = dict()
        sac = self.single_audit_checklist
        for status_choice in sac.STATUS_CHOICES:
            status = status_choice[0]
            if status in sac.transition_name:
                return_dict[status] = sac.get_transition_date(status)
            else:
                return_dict[status] = None
        return return_dict

    def load_general(self):
        general_information = self.single_audit_checklist.general_information
        dates_by_status = self._get_dates_from_sac()

        num_months = None
        if (
            ("audit_period_other_months" in general_information)
            and general_information.get("audit_period_other_months", "") != ""
            and general_information.get("audit_period_other_months", "") is not None
        ):
            num_months = int(general_information.get("audit_period_other_months", ""))

        general = General(
            report_id=self.report_id,
            auditee_certify_name="",  # TODO: Where does this come from?
            auditee_certify_title="",  # TODO: Where does this come from?
            auditee_contact_name=general_information.get("auditee_contact_name", ""),
            auditee_email=general_information.get("auditee_email", ""),
            auditee_name=general_information.get("auditee_name", ""),
            auditee_phone=general_information.get("auditee_phone", ""),
            auditee_contact_title=general_information.get("auditee_contact_title", ""),
            auditee_address_line_1=general_information.get(
                "auditee_address_line_1", ""
            ),
            auditee_city=general_information.get("auditee_city", ""),
            auditee_state=general_information.get("auditee_state", ""),
            auditee_ein=general_information.get("ein", ""),
            auditee_uei=general_information.get("auditee_uei", ""),
            additional_ueis_covered=general_information.get("multiple_eins_covered") == 'Y',
            auditee_zip=general_information.get("auditee_zip", ""),
            auditor_phone=general_information.get("auditor_phone", ""),
            auditor_state=general_information.get("auditor_state", ""),
            auditor_city=general_information.get("auditor_city", ""),
            auditor_contact_title=general_information.get("auditor_contact_title", ""),
            auditor_address_line_1=general_information.get(
                "auditor_address_line_1", ""
            ),
            auditor_zip=general_information.get("auditor_zip", ""),
            auditor_country=general_information.get("auditor_country", ""),
            auditor_contact_name=general_information.get("auditor_contact_name", ""),
            auditor_email=general_information.get("auditor_email", ""),
            auditor_firm_name=general_information.get("auditor_firm_name", ""),
            auditor_foreign_addr="",  # TODO:  What does this look like in the incoming json?
            auditor_ein=general_information.get("auditor_ein", ""),
            additional_eins_covered=general_information.get("multiple_ueis_covered") == 'Y',
            cognizant_agency=self.single_audit_checklist.cognizant_agency or "",
            oversight_agency=self.single_audit_checklist.oversight_agency or "",
            initial_date_received=self.single_audit_checklist.date_created,
            ready_for_certification_date=dates_by_status[
                self.single_audit_checklist.STATUS.READY_FOR_CERTIFICATION
            ],
            auditor_certified_date=dates_by_status[
                self.single_audit_checklist.STATUS.AUDITOR_CERTIFIED
            ],
            auditee_certified_date=dates_by_status[
                self.single_audit_checklist.STATUS.AUDITEE_CERTIFIED
            ],
            certified_date=dates_by_status[
                self.single_audit_checklist.STATUS.CERTIFIED
            ],
            submitted_date=dates_by_status[
                self.single_audit_checklist.STATUS.SUBMITTED
            ],
            auditor_signature_date=None,  # TODO: Field will be added by front end
            auditee_signature_date=None,  # TODO: Field will be added by front end
            fy_end_date=general_information.get("auditee_fiscal_period_end", ""),
            fy_start_date=general_information.get("auditee_fiscal_period_start", ""),
            audit_year=self.audit_year,
            audit_type=general_information.get("audit_type", ""),
            entity_type=general_information.get("user_provided_organization_type", ""),
            number_months=num_months,
            audit_period_covered=general_information.get("audit_period_covered", ""),
            secondary_auditors_exist=general_information.get(
                "secondary_auditors_exist"
            ) == 'Y',
            total_amount_expended=None,  # loaded from FederalAward
            type_audit_code="UG",
            is_public=self.single_audit_checklist.is_public,
            data_source=self.single_audit_checklist.data_source,
        )
        general.save()

    def load_secondary_auditor(self):
        general = self._get_general()
        if not general:
            return
        secondary_auditors = self.single_audit_checklist.secondary_auditors
        if not secondary_auditors:
            general.secondary_auditors_exist = False
            general.save()
            return
        if "secondary_auditors_entries" in secondary_auditors["SecondaryAuditors"]:
            for secondary_auditor in secondary_auditors["SecondaryAuditors"][
                "secondary_auditors_entries"
            ]:
                sec_auditor = SecondaryAuditor(
                    report_id=self.single_audit_checklist.report_id,
                    auditor_ein=secondary_auditor.get("secondary_auditor_ein", ""),
                    auditor_name=secondary_auditor.get("secondary_auditor_name", ""),
                    contact_name=secondary_auditor.get(
                        "secondary_auditor_contact_name", ""
                    ),
                    contact_title=secondary_auditor.get(
                        "secondary_auditor_contact_title", ""
                    ),
                    contact_email=secondary_auditor.get(
                        "secondary_auditor_contact_email", ""
                    ),
                    contact_phone=secondary_auditor.get(
                        "secondary_auditor_contact_phone", ""
                    ),
                    address_street=secondary_auditor.get(
                        "secondary_auditor_address_street", ""
                    ),
                    address_city=secondary_auditor.get(
                        "secondary_auditor_address_city", ""
                    ),
                    address_state=secondary_auditor.get(
                        "secondary_auditor_address_state", ""
                    ),
                    address_zipcode=secondary_auditor.get(
                        "secondary_auditor_address_zipcode", ""
                    ),
                )
                sec_auditor.save()

    def load_additional_uei(self):
        addl_ueis = self.single_audit_checklist.additional_ueis
        if not addl_ueis:
            return
        if "AdditionalUEIs" in addl_ueis:
            for uei in addl_ueis["AdditionalUEIs"]["additional_ueis_entries"]:
                AdditionalUei(
                    report_id=self.single_audit_checklist.report_id,
                    additional_uei=uei["additional_uei"],
                ).save()

    def load_additional_ein(self):
        addl_eins = self.single_audit_checklist.additional_eins
        if not addl_eins:
            return
        if "AdditionalEINs" in addl_eins:
            for ein in addl_eins["AdditionalEINs"]["additional_eins_entries"]:
                AdditionalEin(
                    report_id=self.single_audit_checklist.report_id,
                    additional_ein=ein["additional_ein"],
                ).save()

    def load_audit_info(self):
        general = self._get_general()
        if not general:
            return
        audit_information = self.single_audit_checklist.audit_information
        if not audit_information:
            logger.warning("No audit info found to load")
            return
        general.gaap_results = audit_information.get("gaap_results", "")
        general.sp_framework = audit_information.get("sp_framework_basis", "")
        general.is_sp_framework_required = (
            audit_information["is_sp_framework_required"] == "Y"
        )
        general.sp_framework_auditor_opinion = audit_information[
            "sp_framework_opinions"
        ]
        general.is_going_concern = audit_information["is_going_concern_included"] == "Y"
        general.is_significant_deficiency = (
            audit_information["is_internal_control_deficiency_disclosed"] == "Y"
        )
        general.is_material_weakness = (
            audit_information["is_internal_control_material_weakness_disclosed"] == "Y"
        )
        general.is_material_noncompliance = (
            audit_information["is_material_noncompliance_disclosed"] == "Y"
        )
        general.is_duplicate_reports = (
            audit_information["is_aicpa_audit_guide_included"] == "Y"
        )
        general.dollar_threshold = audit_information["dollar_threshold"]
        general.is_low_risk = audit_information["is_low_risk_auditee"] == "Y"
        general.agencies_with_prior_findings = audit_information["agencies"]

        general.save()

    def _get_general(self):
        general = None
        report_id = self.single_audit_checklist.report_id
        try:
            general = General.objects.get(report_id=report_id)
        except General.DoesNotExist:
            logger.error(
                f"General must be loaded before AuditInfo. report_id = {report_id}"
            )
        return general
