from django.urls import path

from .views import CreateAccountView,AccountListView


urlpatterns = [
    path("create/", CreateAccountView.as_view(), name="create-account"),
    path("", AccountListView.as_view(), name="account-list"),
]