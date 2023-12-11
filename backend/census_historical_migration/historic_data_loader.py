from .models import ELECAUDITHEADER as AuditHeader
from .models import ReportMigrationStatus
from .workbooklib.end_to_end_core import run_end_to_end

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.utils import timezone


User = get_user_model()


def load_historic_data_for_year(audit_year, page_size, pages):
    """Iterates over and processes submissions for the given audit year"""
    result_log = {}
    total_count = error_count = 0
    user = create_or_get_user()
    submissions_for_year = AuditHeader.objects.filter(AUDITYEAR=audit_year).order_by(
        "ELECAUDITHEADERID"
    )
    paginator = Paginator(submissions_for_year, page_size)

    print(f"{submissions_for_year.count()} submissions found for {audit_year}")

    for page_number in pages:
        page = paginator.page(page_number)
        print(
            f"Processing page {page_number} with {page.object_list.count()} submissions."
        )

        for submission in page.object_list:
            result = {"success": [], "errors": []}
            # Migrate a single submission
            run_end_to_end(user, submission, result)

            result_log[(audit_year, submission.DBKEY)] = result
            total_count += 1

            migration_status = "SUCCESS"
            if len(result["errors"]) > 0:
                migration_status = "FAILURE"

            record_migration_status(audit_year, submission.DBKEY, migration_status)

            if len(result["errors"]) > 0:
                error_count += 1
            if total_count % 5 == 0:
                print(f"Processed = {total_count}, Errors = {error_count}")
            if error_count > 5:
                break

    print("********* Loader Summary ***************")

    for k, v in result_log.items():
        print(k, v)
        print("-------------------")

    print(f"{error_count} errors out of {total_count}")


def create_or_get_user():
    """Returns the default migration user"""
    user_email = "fac-census-migration-auditee-official@fac.gsa.gov"
    user_name = "fac-census-migration-auditee-official"
    user = None

    users = User.objects.filter(email=user_email)
    if users:
        user = users.first()
    else:
        print("Creating user", user_email, user_name)
        user = User(username=user_name, email=user_email)
        user.save()

    return user


def record_migration_status(audit_year, dbkey, status):
    ReportMigrationStatus(
        audit_year=audit_year,
        dbkey=dbkey,
        run_datetime=timezone.now(),
        migration_status=status,
    ).save()
