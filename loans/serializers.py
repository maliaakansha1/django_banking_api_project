from decimal import Decimal

from rest_framework import serializers

from .models import Loan


class LoanApplicationSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Loan

        fields = [
            "id",
            "loan_type",
            "loan_amount",
            "interest_rate",
            "tenure_months",
            "status",
        ]

        read_only_fields = [
            "id",
            "status",
        ]

    def validate_loan_amount(
        self,
        value,
    ):

        if value <= Decimal("0"):
            raise serializers.ValidationError(
                "Loan amount must be greater than zero."
            )

        if value > Decimal("1000000"):
            raise serializers.ValidationError(
                "Maximum loan amount is ₹10,00,000."
            )

        return value

    def validate_tenure_months(
        self,
        value,
    ):

        if value < 6:
            raise serializers.ValidationError(
                "Minimum tenure is 6 months."
            )

        if value > 360:
            raise serializers.ValidationError(
                "Maximum tenure is 360 months."
            )

        return value