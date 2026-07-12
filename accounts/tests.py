from django.test import TestCase

# Create your tests here.
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import User
from customers.manage_token import generate_token, store_token
from accounts.models import Account


class CreateAccountTests(APITestCase):

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

    def test_create_savings_account(self):

        response = self.client.post(
            "/api/accounts/create/",
            {
                "account_type": "SAVINGS",
                "initial_deposit": "5000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        account = Account.objects.first()

        self.assertEqual(account.user, self.user)
        self.assertEqual(account.balance, Decimal("5000"))
        self.assertEqual(account.account_type, "SAVINGS")

    def test_savings_minimum_balance(self):

        response = self.client.post(
            "/api/accounts/create/",
            {
                "account_type": "SAVINGS",
                "initial_deposit": "200",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_current_minimum_balance(self):

        response = self.client.post(
            "/api/accounts/create/",
            {
                "account_type": "CURRENT",
                "initial_deposit": "500",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_accounts(self):

      Account.objects.create(
        user=self.user,
        account_type="SAVINGS",
        balance=Decimal("5000"),
    )

      Account.objects.create(
        user=self.user,
        account_type="CURRENT",
        balance=Decimal("3000"),
    )

      response = self.client.get("/api/accounts/")

      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(response.data["count"], 2)
      self.assertEqual(len(response.data["results"]), 2)
      
    def test_only_own_accounts(self):

      another_user = User.objects.create_user(
        username="raj",
        email="raj@gmail.com",
        password="raj123",
        phone_number="9999999999",
    )

      Account.objects.create(
        user=self.user,
        account_type="SAVINGS",
        balance=Decimal("5000"),
    )

      Account.objects.create(
        user=another_user,
        account_type="CURRENT",
        balance=Decimal("9000"),
    )

      response = self.client.get("/api/accounts/")

      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(response.data["count"], 1)

      account = response.data["results"][0]

      self.assertEqual(account["account_type"], "SAVINGS")
      
    def test_filter_savings_accounts(self):

      Account.objects.create(
        user=self.user,
        account_type="SAVINGS",
        balance=Decimal("5000"),
    )

      Account.objects.create(
        user=self.user,
        account_type="CURRENT",
        balance=Decimal("8000"),
    )

      response = self.client.get(
        "/api/accounts/?account_type=SAVINGS"
    )

      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(response.data["count"], 1)

      account = response.data["results"][0]

      self.assertEqual(account["account_type"], "SAVINGS")
      
    def test_filter_current_accounts(self):

      Account.objects.create(
        user=self.user,
        account_type="SAVINGS",
        balance=Decimal("5000"),
    )

      Account.objects.create(
        user=self.user,
        account_type="CURRENT",
        balance=Decimal("8000"),
    )

      response = self.client.get(
        "/api/accounts/?account_type=CURRENT"
    )

      self.assertEqual(response.status_code, status.HTTP_200_OK)
      self.assertEqual(response.data["count"], 1)

      account = response.data["results"][0]

      self.assertEqual(account["account_type"], "CURRENT")
      
    def test_account_list_requires_authentication(self):

      self.client.credentials()

      response = self.client.get("/api/accounts/")

      self.assertEqual(
        response.status_code,
        status.HTTP_401_UNAUTHORIZED,
    )