from django.urls import path

from .views import LoanApplicationView, LoanApprovalView


urlpatterns = [
    path(
        "",
        LoanApplicationView.as_view(),
        name="loan-list-create",
    ),
    path(
        "<int:loan_id>/status/",
        LoanApprovalView.as_view(),
        name="loan-status",
    ),
]