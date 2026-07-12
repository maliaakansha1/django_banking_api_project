from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .serializers import AccountSerializer


from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
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