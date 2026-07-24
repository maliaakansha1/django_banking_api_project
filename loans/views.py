from django.shortcuts import render
from drf_spectacular.utils import OpenApiExample, extend_schema
# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoanApplicationSerializer
from .services import apply_loan

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser

from .models import Loan
from .services import update_loan_status,list_loans


@extend_schema(
    tags=["Loans"],
)
class LoanApplicationView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @extend_schema(
        summary="View My Loans",
        description="Returns all loans of the logged-in customer.",
        responses=LoanApplicationSerializer(many=True),
    )
    def get(
        self,
        request,
    ):

        loans = list_loans(
            user=request.user,
        )

        serializer = LoanApplicationSerializer(
            loans,
            many=True,
        )

        return Response(
            serializer.data,
        )

    @extend_schema(
        summary="Apply for Loan",
        description="Allows an authenticated customer to apply for a new loan.",
        request=LoanApplicationSerializer,
        responses={
            201: LoanApplicationSerializer,
        },
    )
    def post(
        self,
        request,
    ):

        serializer = LoanApplicationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        loan = apply_loan(
            user=request.user,
            loan_type=serializer.validated_data["loan_type"],
            loan_amount=serializer.validated_data["loan_amount"],
            interest_rate=serializer.validated_data["interest_rate"],
            tenure_months=serializer.validated_data["tenure_months"],
        )

        return Response(
            LoanApplicationSerializer(loan).data,
            status=status.HTTP_201_CREATED,
        )
        
class LoanApprovalView(APIView):

    permission_classes = [
        IsAdminUser,
    ]
    @extend_schema(
        summary="Approve or Reject Loan",
        description=(
            "Allows an administrator to approve or reject a "
            "loan application. Only loans with PENDING status "
            "can be updated."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": [
                            "APPROVED",
                            "REJECTED",
                        ],
                    },
                },
                "required": ["status"],
            },
        },
        responses={
            200: LoanApplicationSerializer,
            400: None,
            403: None,
            404: None,
        },
        examples=[
            OpenApiExample(
                "Approve Loan",
                value={
                    "status": "APPROVED",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Reject Loan",
                value={
                    "status": "REJECTED",
                },
                request_only=True,
            ),
        ],
    )
    def patch(
        self,
        request,
        loan_id,
    ):

        loan = get_object_or_404(
            Loan,
            id=loan_id,
        )

        status = request.data.get("status")

        if status not in [
            Loan.APPROVED,
            Loan.REJECTED,
        ]:
            return Response(
                {
                    "error": "Invalid status."
                },
                status=400,
            )

        try:

            loan = update_loan_status(
                loan=loan,
                status=status,
            )

        except ValueError as e:

            return Response(
                {
                    "error": str(e)
                },
                status=400,
            )

        return Response(
            LoanApplicationSerializer(loan).data
        )