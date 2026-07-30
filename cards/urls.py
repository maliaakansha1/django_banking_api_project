from django.urls import path

from .views import IssueCardView,ToggleCardStatusView,UpdateTransactionLimitView,CardTransactionView

urlpatterns = [

    path(
        "issue/",
        IssueCardView.as_view(),
        name="issue-card",
    ),
    path(
        "<int:card_id>/toggle-status/",
        ToggleCardStatusView.as_view(),
        name="toggle-card-status",
    ),

    path(
        "<int:card_id>/transaction-limit/",
        UpdateTransactionLimitView.as_view(),
        name="update-transaction-limit",
    ),
    path(
    "Cardtransaction/",
    CardTransactionView.as_view(),
    name="card-transaction",
),

]