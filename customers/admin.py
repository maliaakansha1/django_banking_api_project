from django.contrib import admin
from .models import User, KYC


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "phone_number",
        "created_at",
    )


@admin.register(KYC)
class KYCAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "aadhaar_number",
        "pan_number",
        "status",
        "submitted_at",
        "verified_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__username",
        "aadhaar_number",
        "pan_number",
    )