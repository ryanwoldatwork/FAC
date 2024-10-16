# Generated by Django 5.1.1 on 2024-10-01 15:38

import audit.models.models
import audit.validators
import django.contrib.postgres.fields
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SingleAuditChecklist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "submission_status",
                    models.CharField(
                        choices=[
                            ("in_progress", "In Progress"),
                            ("ready_for_certification", "Ready for Certification"),
                            ("auditor_certified", "Auditor Certified"),
                            ("auditee_certified", "Auditee Certified"),
                            ("certified", "Certified"),
                            ("submitted", "Submitted"),
                            ("disseminated", "Disseminated"),
                        ],
                        default="in_progress",
                    ),
                ),
                ("data_source", models.CharField(default="GSAFAC")),
                (
                    "transition_name",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("in_progress", "In Progress"),
                                ("ready_for_certification", "Ready for Certification"),
                                ("auditor_certified", "Auditor Certified"),
                                ("auditee_certified", "Auditee Certified"),
                                ("certified", "Certified"),
                                ("submitted", "Submitted"),
                                ("disseminated", "Disseminated"),
                            ],
                            max_length=40,
                        ),
                        blank=True,
                        default=list,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "transition_date",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.DateTimeField(),
                        blank=True,
                        default=list,
                        null=True,
                        size=None,
                    ),
                ),
                ("report_id", models.CharField(unique=True)),
                (
                    "audit_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("single-audit", "Single Audit"),
                            ("program-specific", "Program-Specific Audit"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "general_information",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_general_information_json],
                    ),
                ),
                (
                    "audit_information",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_audit_information_json],
                    ),
                ),
                (
                    "federal_awards",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_federal_award_json],
                    ),
                ),
                (
                    "corrective_action_plan",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[
                            audit.validators.validate_corrective_action_plan_json
                        ],
                    ),
                ),
                (
                    "findings_text",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_findings_text_json],
                    ),
                ),
                (
                    "findings_uniform_guidance",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[
                            audit.validators.validate_findings_uniform_guidance_json
                        ],
                    ),
                ),
                (
                    "additional_ueis",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_additional_ueis_json],
                    ),
                ),
                (
                    "additional_eins",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_additional_eins_json],
                    ),
                ),
                (
                    "secondary_auditors",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_secondary_auditors_json],
                    ),
                ),
                (
                    "notes_to_sefa",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_notes_to_sefa_json],
                    ),
                ),
                (
                    "auditor_certification",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[
                            audit.validators.validate_auditor_certification_json
                        ],
                    ),
                ),
                (
                    "auditee_certification",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[
                            audit.validators.validate_auditee_certification_json
                        ],
                    ),
                ),
                (
                    "tribal_data_consent",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_tribal_data_consent_json],
                    ),
                ),
                (
                    "cognizant_agency",
                    models.CharField(
                        blank=True,
                        help_text="Agency assigned to this large submission. Computed when the submisson is finalized, but may be overridden",
                        max_length=2,
                        null=True,
                        verbose_name="Cog Agency",
                    ),
                ),
                (
                    "oversight_agency",
                    models.CharField(
                        blank=True,
                        help_text="Agency assigned to this not so large submission. Computed when the submisson is finalized",
                        max_length=2,
                        null=True,
                        verbose_name="OSight Agency",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "SF-SAC",
                "verbose_name_plural": "SF-SACs",
            },
            bases=(models.Model, audit.models.models.GeneralInformationMixin),
        ),
        migrations.CreateModel(
            name="SingleAuditReportFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to=audit.models.models.single_audit_report_path,
                        validators=[audit.validators.validate_single_audit_report_file],
                    ),
                ),
                ("filename", models.CharField(max_length=255)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "component_page_numbers",
                    models.JSONField(
                        blank=True,
                        null=True,
                        validators=[audit.validators.validate_component_page_numbers],
                    ),
                ),
                (
                    "sac",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="audit.singleauditchecklist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ExcelFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to=audit.models.models.excel_file_path,
                        validators=[audit.validators.validate_excel_file],
                    ),
                ),
                ("filename", models.CharField(max_length=255)),
                ("form_section", models.CharField(max_length=255)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "sac",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="audit.singleauditchecklist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Access",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            (
                                "certifying_auditee_contact",
                                "Auditee Certifying Official",
                            ),
                            (
                                "certifying_auditor_contact",
                                "Auditor Certifying Official",
                            ),
                            ("editor", "Audit Editor"),
                        ],
                        help_text="Access type granted to this user",
                        max_length=50,
                    ),
                ),
                ("fullname", models.CharField(blank=True)),
                ("email", models.EmailField(max_length=254)),
                (
                    "sac",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="audit.singleauditchecklist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User ID associated with this email address, empty if no FAC account exists",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "accesses",
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("role", "certifying_auditee_contact")),
                        fields=("sac",),
                        name="audit_$(class)s_single_certifying_auditee",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("role", "certifying_auditor_contact")),
                        fields=("sac",),
                        name="audit_access_single_certifying_auditor",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="DeletedAccess",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            (
                                "certifying_auditee_contact",
                                "Auditee Certifying Official",
                            ),
                            (
                                "certifying_auditor_contact",
                                "Auditor Certifying Official",
                            ),
                            ("editor", "Audit Editor"),
                        ],
                        help_text="Access type granted to this user",
                        max_length=50,
                    ),
                ),
                ("fullname", models.CharField(blank=True)),
                ("email", models.EmailField(max_length=254)),
                ("removed_at", models.DateTimeField(auto_now_add=True)),
                ("removed_by_email", models.EmailField(max_length=254, null=True)),
                (
                    "removal_event",
                    models.CharField(choices=[("access-change", "Access change")]),
                ),
                (
                    "removed_by_user",
                    models.ForeignKey(
                        help_text="User ID used to delete this Access",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="access_deleted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sac",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="audit.singleauditchecklist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="User ID associated with this email address, empty if no FAC account exists",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "deleted accesses",
            },
        ),
        migrations.CreateModel(
            name="SubmissionEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "event",
                    models.CharField(
                        choices=[
                            ("access-granted", "Access granted"),
                            ("additional-eins-updated", "Additional EINs updated"),
                            ("additional-eins-deleted", "Additional EINs deleted"),
                            ("additional-ueis-updated", "Additional UEIs updated"),
                            ("additional-ueis-deleted", "Additional UEIs deleted"),
                            ("audit-information-updated", "Audit information updated"),
                            ("audit-report-pdf-updated", "Audit report PDF updated"),
                            (
                                "auditee-certification-completed",
                                "Auditee certification completed",
                            ),
                            (
                                "auditor-certification-completed",
                                "Auditor certification completed",
                            ),
                            (
                                "corrective-action-plan-updated",
                                "Corrective action plan updated",
                            ),
                            (
                                "corrective-action-plan-deleted",
                                "Corrective action plan deleted",
                            ),
                            ("created", "Created"),
                            ("federal-awards-updated", "Federal awards updated"),
                            (
                                "federal-awards-audit-findings-updated",
                                "Federal awards audit findings updated",
                            ),
                            (
                                "federal-awards-audit-findings-deleted",
                                "Federal awards audit findings deleted",
                            ),
                            (
                                "federal-awards-audit-findings-text-updated",
                                "Federal awards audit findings text updated",
                            ),
                            (
                                "federal-awards-audit-findings-text-deleted",
                                "Federal awards audit findings text deleted",
                            ),
                            (
                                "findings-uniform-guidance-updated",
                                "Findings uniform guidance updated",
                            ),
                            (
                                "findings-uniform-guidance-deleted",
                                "Findings uniform guidance deleted",
                            ),
                            (
                                "general-information-updated",
                                "General information updated",
                            ),
                            ("locked-for-certification", "Locked for certification"),
                            (
                                "unlocked-after-certification",
                                "Unlocked after certification",
                            ),
                            ("notes-to-sefa-updated", "Notes to SEFA updated"),
                            (
                                "secondary-auditors-updated",
                                "Secondary auditors updated",
                            ),
                            (
                                "secondary-auditors-deleted",
                                "Secondary auditors deleted",
                            ),
                            ("submitted", "Submitted to the FAC for processing"),
                            ("disseminated", "Copied to dissemination tables"),
                            ("tribal-consent-updated", "Tribal audit consent updated"),
                        ]
                    ),
                ),
                (
                    "sac",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="audit.singleauditchecklist",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UeiValidationWaiver",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("uei", models.TextField(verbose_name="UEI")),
                (
                    "approver_email",
                    models.TextField(
                        verbose_name="Email address of FAC staff member approving the waiver"
                    ),
                ),
                (
                    "approver_name",
                    models.TextField(
                        verbose_name="Name of FAC staff member approving the waiver"
                    ),
                ),
                (
                    "requester_email",
                    models.TextField(
                        verbose_name="Email address of NSAC/KSAML requesting the waiver"
                    ),
                ),
                (
                    "requester_name",
                    models.TextField(
                        verbose_name="Name of NSAC/KSAML requesting the waiver"
                    ),
                ),
                (
                    "justification",
                    models.TextField(
                        verbose_name="Brief plain-text justification for the waiver"
                    ),
                ),
                (
                    "expiration",
                    models.DateTimeField(
                        default=audit.models.models.one_month_from_today,
                        verbose_name="When the waiver will expire",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="When the waiver was created",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SacValidationWaiver",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="When the waiver was created",
                    ),
                ),
                (
                    "approver_email",
                    models.TextField(
                        verbose_name="Email address of FAC staff member approving the waiver"
                    ),
                ),
                (
                    "approver_name",
                    models.TextField(
                        verbose_name="Name of FAC staff member approving the waiver"
                    ),
                ),
                (
                    "requester_email",
                    models.TextField(
                        verbose_name="Email address of NSAC/KSAML requesting the waiver"
                    ),
                ),
                (
                    "requester_name",
                    models.TextField(
                        verbose_name="Name of NSAC/KSAML requesting the waiver"
                    ),
                ),
                (
                    "justification",
                    models.TextField(
                        verbose_name="Brief plain-text justification for the waiver"
                    ),
                ),
                (
                    "waiver_types",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                (
                                    "auditee_certifying_official",
                                    "No auditee certifying official is available",
                                ),
                                (
                                    "auditor_certifying_official",
                                    "No auditor certifying official is available",
                                ),
                                (
                                    "finding_reference_number",
                                    "Report has duplicate finding reference numbers",
                                ),
                            ],
                            max_length=50,
                        ),
                        default=list,
                        size=None,
                        verbose_name="The waiver type",
                    ),
                ),
                (
                    "report_id",
                    models.ForeignKey(
                        db_column="report_id",
                        help_text="The report that the waiver applies to",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="audit.singleauditchecklist",
                        to_field="report_id",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SingleAuditChecklistFlow",
            fields=[
                (
                    "singleauditchecklist_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="audit.singleauditchecklist",
                    ),
                ),
            ],
            bases=("audit.singleauditchecklist",),
        ),
    ]
