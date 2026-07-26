from django.urls import path

from .views import LoanApplicationView, LoanApprovalView
from .views import LoanForeclosureView,LoanHistoryView

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
    path(
          "loans/<int:loan_id>/foreclose/",
              LoanForeclosureView.as_view(),
            name="loan-foreclosure",
),
    path(
        "loans/<int:loan_id>/history/",
         LoanHistoryView.as_view(),
         name="loan-history",
),
    
]