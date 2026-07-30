from rest_framework import serializers

from .models import Card


class CardSerializer(serializers.ModelSerializer):

    masked_card_number = serializers.SerializerMethodField()

    expiry = serializers.SerializerMethodField()
    account_number = serializers.CharField(
        source="account.account_number",
        read_only=True,
    )

    account_type = serializers.CharField(
        source="account.account_type",
        read_only=True,
    )

    class Meta:

        model = Card

        fields = [
            "id",
            "card_holder_name",
            "masked_card_number",
            "expiry",
            "card_type",
            "account_number",
            "account_type",
            "status",
            "transaction_limit",
        ]

    def get_masked_card_number(
        self,
        obj,
    ):

        return (
            "*" * 12
            + obj.card_number[-4:]
        )

    def get_expiry(
        self,
        obj,
    ):

        return obj.expiry_date.strftime(
            "%m/%y"
        )
        
class IssueCardSerializer(serializers.Serializer):

    account_number = serializers.CharField(
        max_length=20,
        help_text="Enter your account number.",
    )
    
class UpdateTransactionLimitSerializer(
    serializers.Serializer,
):

    transaction_limit = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=1,
        help_text=(
            "Maximum amount allowed "
            "per card transaction."
        ),
    )
    
    
    
class CardTransactionSerializer(
    serializers.Serializer,
):

    card_number = serializers.CharField(
        max_length=16,
        help_text="16-digit debit card number.",
    )

    cvv = serializers.CharField(
        max_length=3,
        help_text="3-digit CVV.",
    )

    expiry_date = serializers.DateField(
        help_text="Card expiry date.",
    )

    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=1,
        help_text="Transaction amount.",
    )