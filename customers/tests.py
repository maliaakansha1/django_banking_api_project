from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import User
from customers.manage_token import redis_client


class JWTAuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123",
            phone_number="1234567890",
        )

    def test_login_returns_token_and_stores_it(self):
        response = self.client.post(
            "/api/login/",
            {"username": "alice", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertTrue(redis_client.exists(f"user:{self.user.id}"))

    def test_profile_endpoint_accepts_valid_bearer_token(self):
        login_response = self.client.post(
            "/api/login/",
            {"username": "alice", "password": "StrongPass123"},
            format="json",
        )
        token = login_response.data["token"]

        response = self.client.get(
            "/api/profile/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], self.user.username)
