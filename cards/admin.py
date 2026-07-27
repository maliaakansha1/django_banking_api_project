from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):

    list_display = (
        "card_holder_name",
        "masked_card_number",
        "account_number",
        "account_type",
        "status",
        "expiry_date",
    )

    search_fields = (
        "card_holder_name",
        "card_number",
        "account__account_number",
    )

    list_filter = (
        "status",
        "card_type",
    )

    def masked_card_number(self, obj):

        return "************" + obj.card_number[-4:]

    masked_card_number.short_description = "Card Number"

    def account_number(self, obj):

        return obj.account.account_number

    account_number.short_description = "Account Number"

    def account_type(self, obj):

        return obj.account.account_type

    account_type.short_description = "Account Type"