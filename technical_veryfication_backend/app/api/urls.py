from django.urls import path

from .views import (
    ApproveCaseView,
    CaseListView,
    CorrectCaseView,
    CreateCaseView,
    PhotoUploadView,
    ReverifyCaseView,
    VerifyCaseView,
)

urlpatterns = [
    path("verify-case/", VerifyCaseView.as_view(), name="verify-case"),
    path("cases/", CaseListView.as_view(), name="cases-list"),
    path("cases/create/", CreateCaseView.as_view(), name="cases-create"),
    path("cases/<str:case_id>/approve/", ApproveCaseView.as_view(), name="cases-approve"),
    path("cases/<str:case_id>/correct/", CorrectCaseView.as_view(), name="cases-correct"),
    path("cases/<str:case_id>/reverify/", ReverifyCaseView.as_view(), name="cases-reverify"),
    path("upload-photo/", PhotoUploadView.as_view(), name="upload-photo"),
]
