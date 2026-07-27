from django.urls import path

from .views import IssueCardView

urlpatterns = [

    path(
        "issue/",
        IssueCardView.as_view(),
        name="issue-card",
    ),

]