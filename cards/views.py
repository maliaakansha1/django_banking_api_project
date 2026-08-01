from django.shortcuts import render
from accounts.permissions import IsAccountOwner
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from accounts.models import Account
from .models import Card

from .serializers import CardSerializer, IssueCardSerializer,UpdateTransactionLimitSerializer,CardTransactionSerializer
from .services import issue_card,toggle_card_status,update_transaction_limit,simulate_card_transaction
from django.shortcuts import get_object_or_404
from customers.permissions import IsKYCVerified
from utils.responses import success_response, error_response

class IssueCardView(APIView):

    permission_classes = [IsAuthenticated,IsKYCVerified,IsAccountOwner]

    @extend_schema(
        tags=["Cards"],
        summary="Issue Debit Card",
        description=(
            "Issues a debit card for the authenticated user's account."
        ),
        request=IssueCardSerializer,
        responses={
            201: CardSerializer,
        },
    )
    def post(self, request):

        serializer = IssueCardSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        try:

            account = Account.objects.get(
                account_number=serializer.validated_data[
                    "account_number"
                ],
                user=request.user,
            )

        except Account.DoesNotExist:

            return error_response(
                error="Account not found.",
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            
            card = issue_card(
            account=account,
        )
        except ValueError as e:

            return error_response(
                error=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(
            data={
             "message": "Debit card issued successfully.",
             "card": CardSerializer(card).data,
    },
            status=status.HTTP_201_CREATED,
)
        
        
        
        
class ToggleCardStatusView(APIView):

    permission_classes = [IsAuthenticated,IsAccountOwner]

    @extend_schema(
        tags=["Cards"],
        summary="Block / Unblock Card",
        description=(
            "Blocks an active card or "
            "unblocks a blocked card."
        ),
        responses={
            200: CardSerializer,
        },
    )
    def post(
        self,
        request,
        card_id,
    ):

        card = get_object_or_404(
            Card,
            id=card_id,
        )

        self.check_object_permissions(
            request,
            card,
        )

        card = toggle_card_status(
            card=card,
        )

        return success_response(
            data={
                "message": (
                    "Card status updated successfully."
                ),
                "card": CardSerializer(card).data,
            },
            status=status.HTTP_200_OK,
        )
        
        
        
        
class UpdateTransactionLimitView(APIView):

    permission_classes = [IsAuthenticated,IsAccountOwner,IsKYCVerified]

    @extend_schema(
        tags=["Cards"],
        summary="Update Transaction Limit",
        description=(
            "Updates the maximum "
            "transaction limit of a card."
        ),
        request=UpdateTransactionLimitSerializer,
        responses={
            200: CardSerializer,
        },
    )
    def patch(
        self,
        request,
        card_id,
    ):

        serializer = (
            UpdateTransactionLimitSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        card = get_object_or_404(
               Card,
               id=card_id,
)

        self.check_object_permissions(
           request,
            card,
)

        card = update_transaction_limit(
            card=card,
            transaction_limit=serializer.validated_data[
                "transaction_limit"
            ],
        )

        return success_response(
            data={
                "message": (
                    "Transaction limit updated successfully."
                ),
                "card": CardSerializer(card).data,
            },
            status=status.HTTP_200_OK,
        )
        
        
        
        
class CardTransactionView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cards"],
        summary="Simulate Debit Card Transaction",
        description=(
            "Simulates a debit card transaction after "
            "validating card details, status, transaction "
            "limit and account balance."
        ),
        request=CardTransactionSerializer,
    )
    def post(
        self,
        request,
    ):

        serializer = CardTransactionSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        try:

            account = simulate_card_transaction(
                card_number=serializer.validated_data[
                    "card_number"
                ],
                cvv=serializer.validated_data[
                    "cvv"
                ],
                expiry_date=serializer.validated_data[
                    "expiry_date"
                ],
                amount=serializer.validated_data[
                    "amount"
                ],
            )

        except ValueError as e:

            return error_response(
                error=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )

        return success_response(
            data={
                "message": "Debit card transaction successful.",
                "transaction_type": "CARD_PAYMENT",
                "transaction_amount": serializer.validated_data[
                    "amount"
                ],
                "account_number": account.account_number,
                "remaining_balance": account.balance,
            },
            status=status.HTTP_200_OK,
        )
     