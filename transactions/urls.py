from django.urls import path

from .views import DepositView,WithdrawalView,TransferView

urlpatterns = [
    path(
        "deposit/",
        DepositView.as_view(),
        name="deposit-money",
    ),
    path(
       "withdraw/",
        WithdrawalView.as_view(),
       name="withdraw-money",
),
    path(
        "transfer/",
        TransferView.as_view(),
        name="transfer",
    ),
]