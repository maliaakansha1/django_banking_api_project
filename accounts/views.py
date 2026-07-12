from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView
from .models import Account
from .serializers import AccountSerializer

from .serializers import AccountSerializer


from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    OpenApiTypes,
)

@extend_schema(
    summary="Create Bank Account",
    description="""
Creates a new bank account for the authenticated user.

• Savings Account → Minimum Deposit ₹500
• Current Account → Minimum Deposit ₹1000

Account Number is generated automatically.
""",
    request=AccountSerializer,
    responses={201: AccountSerializer},
    examples=[
        OpenApiExample(
            "Savings Account",
            value={
                "account_type": "SAVINGS",
                "initial_deposit": "5000"
            },
        ),
        OpenApiExample(
            "Current Account",
            value={
                "account_type": "CURRENT",
                "initial_deposit": "10000"
            },
        ),
    ],
)
class CreateAccountView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = AccountSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():

            account = serializer.save()

            return Response(
                AccountSerializer(account).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
        
@extend_schema(
    tags=["Account Management"],
    summary="List My Accounts",
    description="""
Returns all bank accounts belonging to the authenticated user.

Supports pagination and filtering.
""",
    parameters=[
        OpenApiParameter(
            name="account_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter accounts by type (SAVINGS or CURRENT)",
        ),
    ],
    responses=AccountSerializer(many=True),
)
class AccountListView(ListAPIView):

    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        queryset = Account.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

        account_type = self.request.query_params.get("account_type")

        if account_type:
            queryset = queryset.filter(
                account_type=account_type.upper()
            )

        return queryset