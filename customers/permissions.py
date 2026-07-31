from rest_framework.permissions import BasePermission
from .models import KYC


class IsKYCVerified(BasePermission):

    message = (
        "Your KYC is not verified. "
        "Please complete KYC verification."
    )

    def has_permission(
        self,
        request,
        view,
    ):

        try:

            kyc = KYC.objects.get(
                user=request.user
            )

            return (
                kyc.status ==
                KYC.VERIFIED
            )

        except KYC.DoesNotExist:

            return False