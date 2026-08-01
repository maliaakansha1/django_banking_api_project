from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle


class LoginRateThrottle(UserRateThrottle):
    scope = "login"


class TransferRateThrottle(UserRateThrottle):
    scope = "transfer"

class DepositRateThrottle(UserRateThrottle):
    scope = "deposit"

class KYCRateThrottle(UserRateThrottle):
    scope = "kyc"