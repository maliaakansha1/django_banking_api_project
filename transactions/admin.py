from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):

    list_display = (
        "reference_number",
        "account",
        "transaction_type",
        "amount",
        "balance_after_transaction",
        "created_at",
    )

    search_fields = (
        "reference_number",
        "account__account_number",
    )

    list_filter = (
        "transaction_type",
        "created_at",
    )

    ordering = (
        "-created_at",
    )