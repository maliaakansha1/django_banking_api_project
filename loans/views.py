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
from .services import foreclose_loan
from .serializers import LoanForeclosureSerializer
from .serializers import LoanHistorySerializer
from customers.permissions import IsKYCVerified

@extend_schema(
    tags=["Loans"],
)
class LoanApplicationView(APIView):

    # permission_classes = [
    #     IsAuthenticated,IsKYCVerified
    # ]
    def get_permissions(self):

        if self.request.method == "POST":
            return [
                IsAuthenticated(),
                IsKYCVerified(),
            ]

        return [
            IsAuthenticated(),
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




@extend_schema(
    request=LoanForeclosureSerializer,
    responses={
        200: OpenApiExample(
            "Success",
            value={
                "message": "Loan foreclosed successfully."
            },
        ),
    },
)
class LoanForeclosureView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(
        self,
        request,
        loan_id,
    ):

        loan = get_object_or_404(
            Loan,
            id=loan_id,
            customer=request.user,
        )

        try:

            foreclose_loan(
                loan=loan,
            )

            return Response(
                {
                    "message": "Loan foreclosed successfully."
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:

            return Response(
                {
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            
            
            
            
class LoanHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Loans"],
        summary="Loan History",
        description=(
            "Displays the authenticated customer's loan details "
            "along with the complete EMI schedule and remaining balance."
        ),
        responses={
            200: LoanHistorySerializer,
        },
    )
    def get(self, request, loan_id):

        try:

            loan = Loan.objects.get(
                id=loan_id,
                customer=request.user,
            )

        except Loan.DoesNotExist:

            return Response(
                {
                    "message": "Loan not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LoanHistorySerializer(
            loan
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )