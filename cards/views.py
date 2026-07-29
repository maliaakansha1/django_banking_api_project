from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from accounts.models import Account
from .models import Card

from .serializers import CardSerializer, IssueCardSerializer,UpdateTransactionLimitSerializer
from .services import issue_card,toggle_card_status,update_transaction_limit



class IssueCardView(APIView):

    permission_classes = [IsAuthenticated]

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

            return Response(
                {
                    "message": "Account not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            
            card = issue_card(
            account=account,
        )
        except ValueError as e:

            return Response(
                {
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CardSerializer(card).data,
            status=status.HTTP_201_CREATED,
        )
        
        
        
        
class ToggleCardStatusView(APIView):

    permission_classes = [IsAuthenticated]

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

        try:

            card = Card.objects.get(
                id=card_id,
                account__user=request.user,
            )

        except Card.DoesNotExist:

            return Response(
                {
                    "message": "Card not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        card = toggle_card_status(
            card=card,
        )

        return Response(
            {
                "message": (
                    "Card status updated successfully."
                ),
                "card": CardSerializer(card).data,
            },
            status=status.HTTP_200_OK,
        )
        
        
        
        
class UpdateTransactionLimitView(APIView):

    permission_classes = [IsAuthenticated]

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

        try:

            card = Card.objects.get(
                id=card_id,
                account__user=request.user,
            )

        except Card.DoesNotExist:

            return Response(
                {
                    "message": "Card not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        card = update_transaction_limit(
            card=card,
            transaction_limit=serializer.validated_data[
                "transaction_limit"
            ],
        )

        return Response(
            {
                "message": (
                    "Transaction limit updated successfully."
                ),
                "card": CardSerializer(card).data,
            },
            status=status.HTTP_200_OK,
        )