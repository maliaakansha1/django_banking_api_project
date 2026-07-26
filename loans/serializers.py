from decimal import Decimal

from rest_framework import serializers

from .models import Loan
from django.db.models import Sum


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

class LoanForeclosureSerializer(serializers.Serializer):
    """
    Empty serializer used for Swagger documentation.
    """

    pass

from rest_framework import serializers
from .models import Loan, EMI





class EMISerializer(serializers.ModelSerializer):

    class Meta:

        model = EMI

        fields = [
            "emi_number",
            "due_date",
            "emi_amount",
            "principal_amount",
            "interest_amount",
            "penalty_amount",
            "remaining_balance",
            "status",
        ]
        
class LoanHistorySerializer(serializers.ModelSerializer):

    emi_schedule = serializers.SerializerMethodField()

    remaining_balance = serializers.SerializerMethodField()
    outstanding_amount = serializers.SerializerMethodField()
    next_emi = serializers.SerializerMethodField()
    
    total_penalty = serializers.SerializerMethodField()

    total_emis = serializers.SerializerMethodField()

    paid_emis = serializers.SerializerMethodField()

    pending_emis = serializers.SerializerMethodField()

    failed_emis = serializers.SerializerMethodField()

    cancelled_emis = serializers.SerializerMethodField()

    class Meta:

        model = Loan

        fields = [
            "id",
            "loan_type",
            "loan_amount",
            "interest_rate",
            "tenure_months",
            "status",
            "remaining_balance",
            "emi_schedule",
            "total_penalty",
            "total_emis",
            "paid_emis",
            "pending_emis",
            "failed_emis",
            "cancelled_emis",
            "outstanding_amount",
            "next_emi",
        ]

    def get_emi_schedule(self, obj):

        emis = (
            EMI.objects.filter(
                loan=obj
            )
            .order_by("emi_number")
        )

        return EMISerializer(
            emis,
            many=True,
        ).data

    def get_remaining_balance(self, obj):

        emi = (
            EMI.objects.filter(
                loan=obj,
                status__in=[
                    EMI.PENDING,
                    EMI.FAILED,
                ],
            )
            .order_by("emi_number")
            .first()
        )

        if emi:

            return emi.remaining_balance

        return 0
    
    def get_outstanding_amount(self, obj):

      emi = (
        EMI.objects.filter(
            loan=obj,
            status__in=[
                EMI.PENDING,
                EMI.FAILED,
            ],
        )
        .order_by("emi_number")
        .first()
    )

      remaining_balance = (
        emi.remaining_balance
        if emi
        else 0
    )

      total_penalty = (
        EMI.objects.filter(
            loan=obj,
        )
        .aggregate(
            total=Sum("penalty_amount")
        )["total"]
        or 0
    )

      return remaining_balance + total_penalty
  
    def get_next_emi(self, obj):

      emi = (
        EMI.objects.filter(
            loan=obj,
            status__in=[
                EMI.FAILED,
                EMI.PENDING,
            ],
        )
        .order_by(
            "due_date",
            "emi_number",
        )
        .first()
    )

      if emi is None:

        return None

      return EMISerializer(
        emi
       ).data
      
      
    def get_total_penalty(self, obj):

      return (
        EMI.objects.filter(
            loan=obj
        ).aggregate(
            total=Sum("penalty_amount")
        )["total"] or 0
    )


    def get_total_emis(self, obj):

      return EMI.objects.filter(
        loan=obj
    ).count()


    def get_paid_emis(self, obj):

       return EMI.objects.filter(
        loan=obj,
        status=EMI.PAID,
    ).count()


    def get_pending_emis(self, obj):

      return EMI.objects.filter(
        loan=obj,
        status=EMI.PENDING,
    ).count()


    def get_failed_emis(self, obj):

      return EMI.objects.filter(
        loan=obj,
        status=EMI.FAILED,
    ).count()


    def get_cancelled_emis(self, obj):

      return EMI.objects.filter(
        loan=obj,
        status=EMI.CANCELLED,
    ).count()