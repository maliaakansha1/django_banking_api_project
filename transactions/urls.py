from django.urls import path

from .views import DepositView,WithdrawalView

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
]