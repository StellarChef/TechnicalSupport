from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CostEstimationRequestSerializer, VerificationRequestSerializer
from prompts.prompt_helpers import PromptService


class VerifyCaseView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        issue_topic = serializer.validated_data["issue_topic"]
        photos = serializer.validated_data.get("photos", [])
        damage_description = serializer.validated_data.get("damage_description", "")

        prompt_text = PromptService.build_verification_prompt(issue_topic, photos)
        verification_result = PromptService.process_verification(
            issue_topic=issue_topic,
            photos=photos,
            damage_description=damage_description,
        )

        return Response(
            {
                "prompt": prompt_text,
                "verification_result": verification_result,
            },
            status=status.HTTP_200_OK,
        )


class CostEstimationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CostEstimationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_data = serializer.validated_data["input_data"]
        search_results = serializer.validated_data.get("search_results", "")

        prompt_text = PromptService.build_cost_estimation_prompt(
            input_data, search_results
        )
        cost_result = PromptService.process_cost_estimation(input_data, search_results)

        return Response(
            {
                "prompt": prompt_text,
                "cost_estimation": cost_result,
            },
            status=status.HTTP_200_OK,
        )


class CaseClassificationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        issue_topic = serializer.validated_data["issue_topic"]
        photos = serializer.validated_data.get("photos", [])
        damage_description = serializer.validated_data.get("damage_description", "")
        search_results = request.data.get("search_results", "")

        verification_result = PromptService.process_verification(
            issue_topic=issue_topic,
            photos=photos,
            damage_description=damage_description,
        )
        cost_result = PromptService.process_cost_estimation(
            verification_result, search_results
        )

        return Response(
            {
                "verification_result": verification_result,
                "cost_estimation": cost_result,
            },
            status=status.HTTP_200_OK,
        )
