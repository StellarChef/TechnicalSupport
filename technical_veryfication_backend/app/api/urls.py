from django.urls import path

from .views import CaseClassificationView, CostEstimationView, VerifyCaseView

urlpatterns = [
    path("verify-case/", VerifyCaseView.as_view(), name="verify-case"),
    path("estimate-cost/", CostEstimationView.as_view(), name="estimate-cost"),
    path("classify-case/", CaseClassificationView.as_view(), name="classify-case"),
]
