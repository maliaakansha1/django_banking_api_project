from django.contrib import admin

from .models import Loan, EMI


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "loan_type",
        "loan_amount",
        "status",
    )


@admin.register(EMI)
class EMIAdmin(admin.ModelAdmin):

    list_display = (
        "loan",
        "emi_number",
        "due_date",
        "emi_amount",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "loan__customer__username",
    )