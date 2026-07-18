from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Account
from beneficiaries.models import Beneficiary
from customers.models import User
from customers.manage_token import (
    generate_token,
    store_token,
)


class BeneficiaryTests(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="aakansha",
            email="aakansha@gmail.com",
            password="admin123",
            phone_number="9876543210",
        )

        self.other_user = User.objects.create_user(
            username="rahul",
            email="rahul@gmail.com",
            password="admin123",
            phone_number="9999999999",
        )

        token = generate_token(self.user)
        store_token(self.user, token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        self.other_account = Account.objects.create(
            user=self.other_user,
            account_type=Account.SAVINGS,
            balance=5000,
        )

    def test_add_beneficiary(self):

        response = self.client.post(
            "/api/beneficiaries/",
            {
                "account_number": self.other_account.account_number,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Beneficiary.objects.count(),
            1,
        )

    def test_list_beneficiaries(self):

        Beneficiary.objects.create(
            user=self.user,
            beneficiary_account=self.other_account,
        )

        response = self.client.get(
            "/api/beneficiaries/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_delete_beneficiary(self):

        beneficiary = Beneficiary.objects.create(
            user=self.user,
            beneficiary_account=self.other_account,
        )

        response = self.client.delete(
            f"/api/beneficiaries/{beneficiary.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            Beneficiary.objects.count(),
            0,
        )