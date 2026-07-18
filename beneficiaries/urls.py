from django.urls import path

from .views import BeneficiaryDeleteView, BeneficiaryListCreateView

urlpatterns = [
    path(
        "",
        BeneficiaryListCreateView.as_view(),
        name="add-beneficiary",
    ),
    path(
        "<int:beneficiary_id>/",
        BeneficiaryDeleteView.as_view(),
        name="delete-beneficiary",
    ),

]