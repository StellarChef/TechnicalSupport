from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CostEstimationRequestSerializer,
    CreateCaseRequestSerializer,
    VerificationRequestSerializer,
)
from prompts.prompt_helpers import PromptService


class VerifyCaseView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        issue_topic = serializer.validated_data["issue_topic"]
        photos = serializer.validated_data.get("photos", [])
        damage_description = serializer.validated_data.get("damage_description", "")
        use_ai = serializer.validated_data.get("use_ai", True)

        prompt_text = PromptService.build_verification_prompt(issue_topic, photos)
        verification_result = PromptService.process_verification_with_ai(
            issue_topic=issue_topic,
            photos=photos,
            damage_description=damage_description,
            use_ai=use_ai,
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
        use_ai = serializer.validated_data.get("use_ai", True)

        prompt_text = PromptService.build_cost_estimation_prompt(
            input_data, search_results
        )
        cost_result = PromptService.process_cost_estimation_with_ai(
            input_data, search_results, use_ai=use_ai
        )

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
        use_ai = serializer.validated_data.get("use_ai", True)
        search_results = request.data.get("search_results", "")

        verification_result = PromptService.process_verification_with_ai(
            issue_topic=issue_topic,
            photos=photos,
            damage_description=damage_description,
            use_ai=use_ai,
        )
        cost_result = PromptService.process_cost_estimation_with_ai(
            verification_result, search_results, use_ai=use_ai
        )

        return Response(
            {
                "verification_result": verification_result,
                "cost_estimation": cost_result,
            },
            status=status.HTTP_200_OK,
        )


class CreateCaseView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateCaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data["title"]
        photos = serializer.validated_data.get("photos", [])
        damage_description = serializer.validated_data.get("damage_description", "")
        search_results = serializer.validated_data.get("search_results", "")
        use_ai = serializer.validated_data.get("use_ai", True)

        # Process verification
        verification_result = PromptService.process_verification_with_ai(
            issue_topic=title,
            photos=photos,
            damage_description=damage_description,
            use_ai=use_ai,
        )

        # Process cost estimation
        cost_result = PromptService.process_cost_estimation_with_ai(
            verification_result, search_results, use_ai=use_ai
        )

        # Generate case ID
        import uuid
        from datetime import datetime

        case_id = f"CASE-{datetime.now().year}-{str(uuid.uuid4())[:4].upper()}"

        # Build complete case object
        case = {
            "id": case_id,
            "title": title,
            "createdAt": datetime.now().isoformat() + "Z",
            "status": "ai_review",
            "damageDescription": verification_result.get(
                "damage_description", damage_description or title
            ),
            "repairDescription": verification_result.get("repair_steps", ""),
            "photos": [
                {
                    "id": f"photo_{i+1:02d}",
                    "url": photo_url,
                    "isMain": i == 0,
                }
                for i, photo_url in enumerate(photos)
            ],
            "aiClassification": {
                "category": "Nieokreślona",  # Could be inferred from verification
                "damageType": verification_result.get("detected_element", ""),
                "confidence": verification_result.get("confidence_percentage", 0) / 100,
                "suggestedResponsibility": cost_result.get(
                    "responsibility", "unresolved"
                ),
                "suggestedRepair": verification_result.get("repair_steps", ""),
                "suggestedLaborCost": cost_result.get("cost_breakdown", {}).get(
                    "labor", 0
                ),
                "suggestedMaterialCost": cost_result.get("cost_breakdown", {}).get(
                    "materials", 0
                ),
            },
            "responsibility": cost_result.get("responsibility", "unresolved"),
            "cost": {
                "labor": cost_result.get("cost_breakdown", {}).get("labor", 0),
                "materials": cost_result.get("cost_breakdown", {}).get("materials", 0),
                "total": cost_result.get("final_cost_pln", 0),
                "currency": "PLN",
            },
            "mail": {
                "shouldGenerate": cost_result.get("responsibility")
                in ["owner", "tenant"],
                "template": (
                    "owner_repair_notice"
                    if cost_result.get("responsibility") == "owner"
                    else "tenant_repair_notice"
                ),
                "status": "draft",
            },
            "feedback": {
                "aiHelpful": None,
                "rating": None,
                "comment": None,
            },
            "history": [
                {
                    "type": "created",
                    "label": "Utworzono zgłoszenie",
                    "createdAt": datetime.now().isoformat() + "Z",
                    "createdBy": "System",
                },
                {
                    "type": "ai_classified",
                    "label": "AI sklasyfikowało zgłoszenie",
                    "createdAt": (
                        datetime.now().replace(second=datetime.now().second + 2)
                    ).isoformat()
                    + "Z",
                    "createdBy": "AI",
                },
            ],
        }

        return Response(
            {
                "case": case,
                "verification_result": verification_result,
                "cost_estimation": cost_result,
            },
            status=status.HTTP_201_CREATED,
        )
