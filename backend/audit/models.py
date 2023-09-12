import calendar
from datetime import datetime, timezone
from itertools import chain
import json
import logging

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

from django.utils.translation import gettext_lazy as _

from django_fsm import FSMField, RETURN_VALUE, transition

import audit.cross_validation
from .validators import (
    validate_additional_ueis_json,
    validate_additional_eins_json,
    validate_corrective_action_plan_json,
    validate_excel_file,
    validate_federal_award_json,
    validate_findings_text_json,
    validate_findings_uniform_guidance_json,
    validate_general_information_json,
    validate_secondary_auditors_json,
    validate_notes_to_sefa_json,
    validate_single_audit_report_file,
    validate_auditor_certification_json,
    validate_auditee_certification_json,
    validate_tribal_data_consent_json,
    validate_audit_information_json,
    validate_component_page_numbers,
)

User = get_user_model()

logger = logging.getLogger(__name__)


class SingleAuditChecklistManager(models.Manager):
    """Manager for SAC"""

    def create(self, **obj_data):
        """
        Custom create method so that we can add derived fields.

        Currently only used for report_id, a 17-character value consisting of:
            -   Four-digit year of start of audit period.
            -   Three-character all-caps month abbrevation (start of audit period)
            -   10-digit numeric monotonically increasing, but starting from
                0001000001 because the Census numbers are six-digit values. The
                formula for creating this is basically "how many non-legacy
                entries there are in the system plus 1,000,000".
        """

        # remove event_user & event_type keys so that they're not passed into super().create below
        event_user = obj_data.pop("event_user", None)
        event_type = obj_data.pop("event_type", None)

        fiscal_start = obj_data["general_information"]["auditee_fiscal_period_start"]
        year = fiscal_start[:4]
        month = calendar.month_abbr[int(fiscal_start[5:7])].upper()
        count = SingleAuditChecklist.objects.count() + 1_000_001
        report_id = f"{year}{month}{str(count).zfill(10)}"
        updated = obj_data | {"report_id": report_id}

        result = super().create(**updated)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=result,
                user=event_user,
                event=event_type,
            )

        return result


def camel_to_snake(raw: str) -> str:
    """Convert camel case to snake_case."""
    text = f"{raw[0].lower()}{raw[1:]}"
    return "".join(c if c.islower() else f"_{c.lower()}" for c in text)


def json_property_mixin_generator(name, fname=None, toplevel=None, classname=None):
    """Generates a mixin class named classname, using the top-level fields
    in the properties field in the file named fname, accessing those fields
    in the JSON field named toplevel.
    If the optional arguments aren't provided, generate them from name."""
    filename = fname or f"{name}.schema.json"
    toplevelproperty = toplevel or camel_to_snake(name)
    mixinname = classname or f"{name}Mixin"

    def _wrapper(key):
        def inner(self):
            try:
                return getattr(self, toplevelproperty)[key]
            except KeyError:
                logger.warning("Key %s not found in SAC", key)
            except TypeError:
                logger.warning("Type error trying to get %s from SAC %s", key, self)
            return None

        return inner

    schemadir = settings.SECTION_SCHEMA_DIR
    schemafile = schemadir / filename
    schema = json.loads(schemafile.read_text())
    attrdict = {k: property(_wrapper(k)) for k in schema["properties"]}
    return type(mixinname, (), attrdict)


GeneralInformationMixin = json_property_mixin_generator("GeneralInformation")


class LateChangeError(Exception):
    pass


class SingleAuditChecklist(models.Model, GeneralInformationMixin):  # type: ignore
    """
    Monolithic Single Audit Checklist.
    """

    # Class management machinery:
    class Meta:
        """We need to set the name for the admin view."""

        verbose_name = "SF-SAC"
        verbose_name_plural = "SF-SACs"

    objects = SingleAuditChecklistManager()

    # Method overrides:
    def __str__(self):
        return f"#{self.id}--{self.report_id}--{self.auditee_uei}"

    def save(self, *args, **kwargs):
        """
        Call _reject_late_changes() to verify that a submission that's no longer
        in progress isn't being altered; skip this if we know this submission is
        in progress.
        """
        if self.submission_status != self.STATUS.IN_PROGRESS:
            try:
                self._reject_late_changes()
            except LateChangeError as err:
                raise LateChangeError from err

        event_user = kwargs.get("event_user")
        event_type = kwargs.get("event_type")
        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self,
                user=event_user,
                event=event_type,
            )

        return super().save()

    def _reject_late_changes(self):
        """
        This should only be called if status isn't STATUS.IN_PROGRESS.
        If there have been relevant changes, raise an AssertionError.
        Here, "relevant" means anything other than fields related to the status
        transition change itself.
        """
        try:
            prior_obj = SingleAuditChecklist.objects.get(pk=self.pk)
        except SingleAuditChecklist.DoesNotExist:
            # No prior instance exists, so it's a new submission.
            return True

        current = audit.cross_validation.sac_validation_shape(self)
        prior = audit.cross_validation.sac_validation_shape(prior_obj)
        if current["sf_sac_sections"] != prior["sf_sac_sections"]:
            raise LateChangeError

        meta_fields = ("submitted_by", "date_created", "report_id", "audit_type")
        for field in meta_fields:
            if current["sf_sac_meta"][field] != prior["sf_sac_meta"][field]:
                raise LateChangeError

        return True

    # Constants:
    class STATUS:
        """The states that a submission can be in."""

        IN_PROGRESS = "in_progress"
        READY_FOR_CERTIFICATION = "ready_for_certification"
        AUDITOR_CERTIFIED = "auditor_certified"
        AUDITEE_CERTIFIED = "auditee_certified"
        CERTIFIED = "certified"
        SUBMITTED = "submitted"

    STATUS_CHOICES = (
        (STATUS.IN_PROGRESS, "In Progress"),
        (STATUS.READY_FOR_CERTIFICATION, "Ready for Certification"),
        (STATUS.AUDITOR_CERTIFIED, "Auditor Certified"),
        (STATUS.AUDITEE_CERTIFIED, "Auditee Certified"),
        (STATUS.CERTIFIED, "Certified"),
        (STATUS.SUBMITTED, "Submitted"),
    )

    USER_PROVIDED_ORGANIZATION_TYPE_CODE = (
        ("state", _("State")),
        ("local", _("Local Government")),
        ("tribal", _("Indian Tribe or Tribal Organization")),
        ("higher-ed", _("Institution of higher education (IHE)")),
        ("non-profit", _("Non-profit")),
        ("unknown", _("Unknown")),
        ("none", _("None of these (for example, for-profit")),
    )

    AUDIT_TYPE_CODES = (
        ("single-audit", _("Single Audit")),
        ("program-specific", _("Program-Specific Audit")),
    )

    AUDIT_PERIOD = (
        ("annual", _("Annual")),
        ("biennial", _("Biennial")),
        ("other", _("Other")),
    )

    # 0. Meta data
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    submission_status = FSMField(default=STATUS.IN_PROGRESS, choices=STATUS_CHOICES)
    data_source = models.CharField(default="GSA")

    # implement an array of tuples as two arrays since we can only have simple fields inside an array
    transition_name = ArrayField(
        models.CharField(max_length=40, choices=STATUS_CHOICES),
        default=list,
        size=None,
        blank=True,
        null=True,
    )
    transition_date = ArrayField(
        models.DateTimeField(),
        default=list,
        size=None,
        blank=True,
        null=True,
    )

    report_id = models.CharField(max_length=17, unique=True)

    # Q2 Type of Uniform Guidance Audit
    audit_type = models.CharField(
        max_length=20, choices=AUDIT_TYPE_CODES, blank=True, null=True
    )

    # General Information
    # The general information fields are currently specified in two places:
    #   - report_submission.forms.GeneralInformationForm
    #   - schemas.sections.GeneralInformation.schema.json
    general_information = models.JSONField(
        blank=True, null=True, validators=[validate_general_information_json]
    )

    audit_information = models.JSONField(
        blank=True, null=True, validators=[validate_audit_information_json]
    )

    # Federal Awards:
    federal_awards = models.JSONField(
        blank=True, null=True, validators=[validate_federal_award_json]
    )

    # Corrective Action Plan:
    corrective_action_plan = models.JSONField(
        blank=True, null=True, validators=[validate_corrective_action_plan_json]
    )

    # Findings Text:
    findings_text = models.JSONField(
        blank=True, null=True, validators=[validate_findings_text_json]
    )

    # Findings Uniform Guidance:
    findings_uniform_guidance = models.JSONField(
        blank=True, null=True, validators=[validate_findings_uniform_guidance_json]
    )

    # Additional UEIs:
    additional_ueis = models.JSONField(
        blank=True, null=True, validators=[validate_additional_ueis_json]
    )

    # Additional EINs:
    additional_eins = models.JSONField(
        blank=True, null=True, validators=[validate_additional_eins_json]
    )

    # Secondary Auditors:
    secondary_auditors = models.JSONField(
        blank=True, null=True, validators=[validate_secondary_auditors_json]
    )

    # Notes to SEFA:
    notes_to_sefa = models.JSONField(
        blank=True, null=True, validators=[validate_notes_to_sefa_json]
    )

    auditor_certification = models.JSONField(
        blank=True, null=True, validators=[validate_auditor_certification_json]
    )

    auditee_certification = models.JSONField(
        blank=True, null=True, validators=[validate_auditee_certification_json]
    )

    tribal_data_consent = models.JSONField(
        blank=True, null=True, validators=[validate_tribal_data_consent_json]
    )

    cognizant_agency = models.TextField(null=True)

    oversight_agency = models.TextField(
        null=True,
    )

    def validate_full(self):
        """
        Full validation, intended for use when the user indicates that the
        submission is finished.

        Currently a stub, but eventually will call each of the individual
        section validation routines and then validate_cross.
        """

        validation_methods = []
        errors = [f(self) for f in validation_methods]

        if errors:
            return {"errors": errors}

        return self.validate_cross()

    def validate_cross(self):
        """
        This method should NOT be run as part of full_clean(), because we want
        to be able to save in-progress submissions.

        A stub method to represent the cross-sheet, “full” validation that we
        do once all the individual sections are complete and valid in
        themselves.
        """
        shaped_sac = audit.cross_validation.sac_validation_shape(self)
        try:
            sar = SingleAuditReportFile.objects.filter(sac_id=self.id).latest(
                "date_created"
            )
        except SingleAuditReportFile.DoesNotExist:
            sar = None
        validation_functions = audit.cross_validation.functions
        errors = list(
            chain.from_iterable(
                [func(shaped_sac, sar=sar) for func in validation_functions]
            )
        )
        if errors:
            return {"errors": errors, "data": shaped_sac}
        return {}

    @transition(
        field="submission_status",
        source=STATUS.IN_PROGRESS,
        target=RETURN_VALUE(STATUS.IN_PROGRESS, STATUS.READY_FOR_CERTIFICATION),
    )
    def transition_to_ready_for_certification(self):
        """
        Pretend we're doing multi-sheet validation here.
        This probably won't be the first time this validation is done;
        there's likely to be a step in one of the views that does cross-sheet
        validation and reports back to the user.
        """
        errors = self.validate_full()
        if not errors:
            self.transition_name.append(
                SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION
            )
            self.transition_date.append(datetime.now(timezone.utc))
            return SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION
        return SingleAuditChecklist.STATUS.IN_PROGRESS

    @transition(
        field="submission_status",
        source=STATUS.READY_FOR_CERTIFICATION,
        target=STATUS.AUDITOR_CERTIFIED,
    )
    def transition_to_auditor_certified(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will done at the view level.
        """
        self.transition_name.append(SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED)
        self.transition_date.append(datetime.now(timezone.utc))

    @transition(
        field="submission_status",
        source=STATUS.AUDITOR_CERTIFIED,
        target=STATUS.AUDITEE_CERTIFIED,
    )
    def transition_to_auditee_certified(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will done at the view level.
        """
        self.transition_name.append(SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED)
        self.transition_date.append(datetime.now(timezone.utc))

    @transition(
        field="submission_status",
        source=STATUS.AUDITEE_CERTIFIED,
        target=STATUS.SUBMITTED,
    )
    def transition_to_submitted(self):
        """
        The permission checks verifying that the user attempting to do this has
        the appropriate privileges will done at the view level.
        """

        from audit.intake_to_dissemination import IntakeToDissemination
        from audit.cog_over import cog_over

        self.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
        self.transition_date.append(datetime.now(timezone.utc))
        if self.general_information:
            # cog / over assignment
            self.cognizant_agency, self.oversight_agency = cog_over(self)
            intake_to_dissem = IntakeToDissemination(self)
            intake_to_dissem.load_all()
            # FIXME MSHD: Handle exceptions raised by the save methods
            intake_to_dissem.save_dissemination_objects()

    @transition(
        field="submission_status",
        source=[
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ],
        target=STATUS.SUBMITTED,
    )
    def transition_to_in_progress(self):
        """
        Any edit to a submission in the following states should result in it
        moving back to STATUS.IN_PROGRESS:

        +   STATUS.READY_FOR_CERTIFICATION
        +   STATUS.AUDITOR_CERTIFIED
        +   STATUS.AUDITEE_CERTIFIED
        +   STATUS.CERTIFIED

        For the moment we're not trying anything fancy like catching changes at
        the model level, and will again leave it up to the views to track that
        changes have been made at that point.
        """
        self.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
        self.transition_date.append(datetime.now(timezone.utc))

    @property
    def is_auditee_certified(self):
        return self.submission_status in [
            SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
            SingleAuditChecklist.STATUS.CERTIFIED,
            SingleAuditChecklist.STATUS.SUBMITTED,
        ]

    @property
    def is_auditor_certified(self):
        return self.submission_status in [
            SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
            SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
            SingleAuditChecklist.STATUS.CERTIFIED,
            SingleAuditChecklist.STATUS.SUBMITTED,
        ]

    @property
    def is_submitted(self):
        return self.submission_status in [SingleAuditChecklist.STATUS.SUBMITTED]

    @property
    def is_public(self):
        return self.general_information["user_provided_organization_type"] != "tribal"

    def get_transition_date(self, status):
        index = self.transition_name.index(status)
        if index >= 0:
            return self.transition_date[index]
        return None

    def _general_info_get(self, key):
        try:
            return self.general_information[key]
        except KeyError:
            pass
        except TypeError:
            pass
        return None


class AccessManager(models.Manager):
    """Custom manager for Access."""

    def create(self, **obj_data):
        """
        Check for existing users and add them at access creation time.
        Not doing this would mean that users logged in at time of Access
        instance creation would have to log out and in again to get the new
        access.
        """

        # remove event_user & event_type keys so that they're not passed into super().create below
        event_user = obj_data.pop("event_user", None)
        event_type = obj_data.pop("event_type", None)

        if obj_data["email"]:
            try:
                acc_user = User.objects.get(email=obj_data["email"])
            except User.DoesNotExist:
                acc_user = None
            if acc_user:
                obj_data["user"] = acc_user
        result = super().create(**obj_data)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=result.sac,
                user=event_user,
                event=event_type,
            )

        return result


class Access(models.Model):
    """
    Email addresses which have been granted access to SAC instances.
    An email address may be associated with a User ID if an FAC account exists.
    """

    objects = AccessManager()

    ROLES = (
        ("certifying_auditee_contact", _("Auditee Certifying Official")),
        ("certifying_auditor_contact", _("Auditor Certifying Official")),
        ("editor", _("Audit Editor")),
    )
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    role = models.CharField(
        choices=ROLES,
        help_text="Access type granted to this user",
        max_length=50,
    )
    fullname = models.CharField(blank=True)
    email = models.EmailField()
    user = models.ForeignKey(
        User,
        null=True,
        help_text="User ID associated with this email address, empty if no FAC account exists",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.email} as {self.get_role_display()}"

    class Meta:
        verbose_name_plural = "accesses"

        constraints = [
            # a SAC cannot have multiple certifying auditees
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="certifying_auditee_contact"),
                name="%(app_label)s_$(class)s_single_certifying_auditee",
            ),
            # a SAC cannot have multiple certifying auditors
            models.UniqueConstraint(
                fields=["sac"],
                condition=Q(role="certifying_auditor_contact"),
                name="%(app_label)s_%(class)s_single_certifying_auditor",
            ),
        ]


def excel_file_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id and form_section--not the user-provided filename.
    """
    return f"excel/{instance.sac.report_id}--{instance.form_section}.xlsx"


class ExcelFile(models.Model):
    """
    Data model to track uploaded Excel files and associate them with SingleAuditChecklists
    """

    file = models.FileField(upload_to=excel_file_path, validators=[validate_excel_file])
    filename = models.CharField(max_length=255)
    form_section = models.CharField(max_length=255)
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.sac.submission_status != SingleAuditChecklist.STATUS.IN_PROGRESS:
            raise LateChangeError("Attemtped Excel file upload")

        self.filename = f"{self.sac.report_id}--{self.form_section}.xlsx"

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self.sac, user=event_user, event=event_type
            )

        super().save(*args, **kwargs)


def single_audit_report_path(instance, _filename):
    """
    We want the actual filename in the filesystem to be unique and determined
    by report_id, not the user-provided filename.
    """
    base_path = "singleauditreport"
    report_id = instance.sac.report_id
    return f"{base_path}/{report_id}.pdf"


class SingleAuditReportFile(models.Model):
    """
    Data model to track uploaded Single Audit report PDFs and associate them with SingleAuditChecklists
    """

    file = models.FileField(
        upload_to=single_audit_report_path,
        validators=[validate_single_audit_report_file],
    )
    filename = models.CharField(max_length=255)
    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    component_page_numbers = models.JSONField(
        blank=True, null=True, validators=[validate_component_page_numbers]
    )

    def save(self, *args, **kwargs):
        report_id = SingleAuditChecklist.objects.get(id=self.sac.id).report_id
        self.filename = f"{report_id}.pdf"
        if self.sac.submission_status != self.sac.STATUS.IN_PROGRESS:
            raise LateChangeError("Attempted PDF upload")

        event_user = kwargs.pop("event_user", None)
        event_type = kwargs.pop("event_type", None)

        if event_user and event_type:
            SubmissionEvent.objects.create(
                sac=self.sac, user=event_user, event=event_type
            )

        super().save(*args, **kwargs)


class CognizantBaseline(models.Model):
    dbkey = models.IntegerField(
        "Identifier for a submission along with audit_year in C-FAC",
        null=True,
    )
    audit_year = models.IntegerField(
        "Audit year from fy_start_date",
        null=True,
    )
    ein = models.CharField(
        "Primary Employer Identification Number",
        null=True,
        max_length=30,
    )
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        null=True,
    )

    class Meta:
        unique_together = (("dbkey", "audit_year"),)


class SubmissionEvent(models.Model):
    class EventType:
        ACCESS_GRANTED = "access-granted"
        ADDITIONAL_EINS_UPDATED = "additional-eins-updated"
        ADDITIONAL_UEIS_UPDATED = "additional-ueis-updated"
        AUDIT_INFORMATION_UPDATED = "audit-information-updated"
        AUDIT_REPORT_PDF_UPDATED = "audit-report-pdf-updated"
        AUDITEE_CERTIFICATION_COMPLETED = "auditee-certification-completed"
        AUDITOR_CERTIFICATION_COMPLETED = "auditor-certification-completed"
        CORRECTIVE_ACTION_PLAN_UPDATED = "corrective-action-plan-updated"
        CREATED = "created"
        FEDERAL_AWARDS_UPDATED = "federal-awards-updated"
        FEDERAL_AWARDS_AUDIT_FINDINGS_UPDATED = "federal-awards-audit-findings-updated"
        FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED = (
            "federal-awards-audit-findings-text-updated"
        )
        FINDINGS_UNIFORM_GUIDANCE_UPDATED = "findings-uniform-guidance-updated"
        GENERAL_INFORMATION_UPDATED = "general-information-updated"
        LOCKED_FOR_CERTIFICATION = "locked-for-certification"
        NOTES_TO_SEFA_UPDATED = "notes-to-sefa-updated"
        SECONDARY_AUDITORS_UPDATED = "secondary-auditors-updated"
        SUBMITTED = "submitted"

    EVENT_TYPES = (
        (EventType.ACCESS_GRANTED, _("Access granted")),
        (EventType.ADDITIONAL_EINS_UPDATED, _("Additional EINs updated")),
        (EventType.ADDITIONAL_UEIS_UPDATED, _("Additional UEIs updated")),
        (EventType.AUDIT_INFORMATION_UPDATED, _("Audit information updated")),
        (EventType.AUDIT_REPORT_PDF_UPDATED, _("Audit report PDF updated")),
        (
            EventType.AUDITEE_CERTIFICATION_COMPLETED,
            _("Auditee certification completed"),
        ),
        (
            EventType.AUDITOR_CERTIFICATION_COMPLETED,
            _("Auditor certification completed"),
        ),
        (EventType.CORRECTIVE_ACTION_PLAN_UPDATED, _("Corrective action plan updated")),
        (EventType.CREATED, _("Created")),
        (EventType.FEDERAL_AWARDS_UPDATED, _("Federal awards updated")),
        (
            EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_UPDATED,
            _("Federal awards audit findings updated"),
        ),
        (
            EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED,
            _("Federal awards audit findings text updated"),
        ),
        (
            EventType.FINDINGS_UNIFORM_GUIDANCE_UPDATED,
            _("Findings uniform guidance updated"),
        ),
        (EventType.GENERAL_INFORMATION_UPDATED, _("General information updated")),
        (EventType.LOCKED_FOR_CERTIFICATION, _("Locked for certification")),
        (EventType.NOTES_TO_SEFA_UPDATED, _("Notes to SEFA updated")),
        (EventType.SECONDARY_AUDITORS_UPDATED, _("Secondary auditors updated")),
        (EventType.SUBMITTED, _("Submitted to the FAC for processing")),
    )

    sac = models.ForeignKey(SingleAuditChecklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(choices=EVENT_TYPES)
