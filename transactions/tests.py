from django.test import TestCase

# Create your tests here.
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import User
from customers.manage_token import generate_token, store_token

from accounts.models import Account


class TransactionTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="akku",
            email="akku@gmail.com",
            password="akku123",
            phone_number="9876543210",
        )

        token = generate_token(self.user)
        store_token(self.user, token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.account = Account.objects.create(
            user=self.user,
            account_type=Account.SAVINGS,
            balance=Decimal("5000"),
        )

    # -----------------------------
    # Deposit Tests
    # -----------------------------

    def test_successful_deposit(self):

        response = self.client.post(
            "/api/transactions/deposit/",
            {
                "account_number": self.account.account_number,
                "amount": "1000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.account.refresh_from_db()

        self.assertEqual(
            self.account.balance,
            Decimal("6000"),
        )

    def test_deposit_invalid_account(self):

        response = self.client.post(
            "/api/transactions/deposit/",
            {
                "account_number": "999999999999",
                "amount": "500",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_deposit_invalid_amount(self):

        response = self.client.post(
            "/api/transactions/deposit/",
            {
                "account_number": self.account.account_number,
                "amount": "-100",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # -----------------------------
    # Withdrawal Tests
    # -----------------------------

    def test_successful_withdrawal(self):

        response = self.client.post(
            "/api/transactions/withdraw/",
            {
                "account_number": self.account.account_number,
                "amount": "1000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.account.refresh_from_db()

        self.assertEqual(
            self.account.balance,
            Decimal("4000"),
        )

    def test_withdraw_insufficient_balance(self):

        response = self.client.post(
            "/api/transactions/withdraw/",
            {
                "account_number": self.account.account_number,
                "amount": "10000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_withdraw_invalid_account(self):

        response = self.client.post(
            "/api/transactions/withdraw/",
            {
                "account_number": "999999999999",
                "amount": "500",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_withdraw_invalid_amount(self):

        response = self.client.post(
            "/api/transactions/withdraw/",
            {
                "account_number": self.account.account_number,
                "amount": "-100",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )