from rest_framework.permissions import BasePermission
class IsAccountOwner(BasePermission):
    """
    Allows access only to the owner of the object.
    """

    message = (
        "You do not have permission to access this resource."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if hasattr(obj, "user"):
            return obj.user == request.user

        if hasattr(obj, "customer"):
            return obj.customer == request.user

        if hasattr(obj, "account"):
            return obj.account.user == request.user

        if hasattr(obj, "loan"):
            return obj.loan.customer == request.user

        return False