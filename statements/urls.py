from django.urls import path

from .views import StatementDownloadView, StatementRequestView,StatementStatusView


urlpatterns = [
    path(
        "",
        StatementRequestView.as_view(),
        name="statement-request",
    ),
    path(
    "<int:id>/status/",
    StatementStatusView.as_view(),
    name="statement-status",
),
    path(
    "<int:id>/download/",
    StatementDownloadView.as_view(),
    name="statement-download",
),
]