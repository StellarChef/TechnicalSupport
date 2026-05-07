from django.urls import path

from .views import (
    CaseClassificationView,
    CostEstimationView,
    CreateCaseView,
    VerifyCaseView,
)

urlpatterns = [
    path("verify-case/", VerifyCaseView.as_view(), name="verify-case"),
    path("estimate-cost/", CostEstimationView.as_view(), name="estimate-cost"),
    path("classify-case/", CaseClassificationView.as_view(), name="classify-case"),
    path("create-case/", CreateCaseView.as_view(), name="create-case"),
]
