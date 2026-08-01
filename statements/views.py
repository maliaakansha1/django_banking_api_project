from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import StatementRequestSerializer
from .tasks import generate_statement
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from rest_framework.generics import RetrieveAPIView

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import StatementRequest
from utils.responses import success_response, error_response

from .serializers import (
    StatementStatusSerializer,
)

tags=["Statements"]

@extend_schema(
    request=StatementRequestSerializer,
    responses={
        201: OpenApiResponse(
            description="Statement request submitted successfully."
        ),
    },
)


class StatementRequestView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = StatementRequestSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        statement_request = serializer.save()

        generate_statement.delay(
            statement_request.id
        )

        return success_response(
            data={
                "message": "Statement request submitted successfully.",
                "request_id": statement_request.id,
                "status": statement_request.status,
            },
            status=status.HTTP_201_CREATED,
        )
        
        


class StatementStatusView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Check Statement Status",
        description=(
            "Returns the current processing status of a statement request. "
            "If completed, the response includes the download URL."
        ),
        responses={
            200: StatementStatusSerializer,
        },
    )
    def get(
        self,
        request,
        id,
    ):

        statement = get_object_or_404(
            StatementRequest,
            id=id,
            user=request.user,
        )

        serializer = StatementStatusSerializer(
            statement,
            context={
               "request": request,
    },
        )

        return success_response(
            data=serializer.data,
            status=status.HTTP_200_OK,
        )
        
class StatementDownloadView(APIView):

    @extend_schema(
        summary="Download Account Statement",
        description=(
            "Downloads the generated PDF statement for the authenticated user."
        ),
        responses={
            200: {
                "description": "PDF File"
            }
        },
    )
    def get(
        self,
        request,
        id,
    ):

        statement = get_object_or_404(
            StatementRequest,
            id=id,
            user=request.user,
        )

        if not statement.statement_file:

            return error_response(
                error="Statement has not been generated yet.",
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            statement.statement_file.open(
                "rb"
            ),
            as_attachment=True,
            filename=(
                statement.statement_file.name
                .split("/")[-1]
            ),
        )