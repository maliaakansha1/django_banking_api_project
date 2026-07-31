from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, ProfileView, RegisterView, RejectKYCView,SubmitKYCView, VerifyKYCView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    # path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("submit-kyc/", SubmitKYCView.as_view(), name="submit-kyc"),
    path(
    "kyc/<int:kyc_id>/verify/",
    VerifyKYCView.as_view(),
    name="verify-kyc",
),

path(
    "kyc/<int:kyc_id>/reject/",
    RejectKYCView.as_view(),
    name="reject-kyc",
),
]