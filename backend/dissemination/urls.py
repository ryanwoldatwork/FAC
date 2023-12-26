from django.urls import path

from dissemination import views

app_name = "dissemination"

urlpatterns = [
    path(
        "workbook/xlsx/<str:file_type>/<str:report_id>",
        views.XlsxDownloadView.as_view(),
        name="XlsxDownload",
    ),
    path(
        "report/pdf/<str:report_id>",
        views.PdfDownloadView.as_view(),
        name="PdfDownload",
    ),
    path(
        "summary-report/xlsx/<str:report_id>",
        views.SingleSummaryReportDownloadView.as_view(),
        name="SummaryReportDownload",
    ),
    path(
        "summary-report/xlsx",
        views.MultipleSummaryReportDownloadView.as_view(),
        name="MultipleSummaryReportDownload",
    ),
    path("search/", views.Search.as_view(), name="Search"),
    path("summary/<str:report_id>", views.AuditSummaryView.as_view(), name="Summary"),
]
