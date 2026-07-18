from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Beneficiary


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "beneficiary_account",
        "created_at",
    )

    search_fields = (
        "user__username",
        "beneficiary_account__account_number",
    )