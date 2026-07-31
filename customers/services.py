from .models import KYC
from django.utils import timezone

def submit_kyc(
    user,
    aadhaar_number,
    pan_number,
    address,
):

    if KYC.objects.filter(
        user=user,
    ).exists():

        raise ValueError(
            "KYC has already been submitted."
        )

    return KYC.objects.create(
        user=user,
        aadhaar_number=aadhaar_number,
        pan_number=pan_number,
        address=address,
    )
    
def verify_kyc(
    kyc,
    admin_user,
):

    kyc.status = KYC.VERIFIED
    kyc.verified_by = admin_user
    kyc.verified_at = timezone.now()

    kyc.save()

    return kyc



def reject_kyc(
    kyc,
):

    kyc.status = KYC.REJECTED

    kyc.save()

    return kyc