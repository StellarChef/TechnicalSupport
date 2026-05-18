from rest_framework import serializers

from .models import Case, CaseHistoryEvent, CasePhoto


# ── Request serializery ────────────────────────────────────────────────────
class VerifyCaseRequestSerializer(serializers.Serializer):
    """Wejście dla `POST /api/verify-case/` — wynik surowy z pipelinu (debug/preview)."""

    issue_topic = serializers.CharField(max_length=200)
    photos = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    damage_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


class CreateCaseRequestSerializer(serializers.Serializer):
    """Wejście dla `POST /api/cases/create/` — pełny pipeline + zbudowanie case'a."""

    title = serializers.CharField(max_length=200)
    photos = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        allow_empty=True,
        default=list,
    )
    damage_description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


# ── Response serializery (kształt zgodny z frontowym obiektem `case`) ──────
class CasePhotoSerializer(serializers.ModelSerializer):
    """Mapuje `CasePhoto` na `{id, url, isMain}`. URL z ImageField nadpisuje
    surowy `url` jeśli zdjęcie zostało wgrane (zamiast linkowane z zewnątrz)."""

    id = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    isMain = serializers.BooleanField(source="is_main")

    class Meta:
        model = CasePhoto
        fields = ["id", "url", "isMain"]

    def get_id(self, obj: CasePhoto) -> str:
        return f"photo_{obj.pk:02d}"

    def get_url(self, obj: CasePhoto) -> str:
        if obj.image:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(obj.image.url)
                if request
                else obj.image.url
            )
        return obj.url


class CaseHistoryEventSerializer(serializers.ModelSerializer):
    """Mapuje wpis z osi czasu na `{type, label, createdAt, createdBy}`."""

    type = serializers.CharField(source="event_type")
    createdAt = serializers.DateTimeField(source="created_at")
    createdBy = serializers.CharField(source="created_by")

    class Meta:
        model = CaseHistoryEvent
        fields = ["type", "label", "createdAt", "createdBy"]


class CaseSerializer(serializers.ModelSerializer):
    """Pełna serializacja `Case` w kształcie oczekiwanym przez frontend.

    - `id` mapuje na `case_id` (biznesowy "CASE-2026-XXXX"), nie PK auto-increment.
    - Pola `ai_*` zgrupowane w `aiClassification`.
    - Pola `cost_*` zgrupowane w `cost` (z policzonym `total`).
    - Pola `mail_*` zgrupowane w `mail` (zwraca `null` dla braku szablonu).
    - `photos` i `history` jako zagnieżdżone listy (po related_name z modeli).
    """

    # Skalary z prostym mapowaniem snake_case → camelCase
    id = serializers.CharField(source="case_id", read_only=True)
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    damageDescription = serializers.CharField(source="damage_description")
    repairDescription = serializers.CharField(source="repair_description")

    # Zagnieżdżone struktury
    photos = CasePhotoSerializer(many=True, read_only=True)
    history = CaseHistoryEventSerializer(many=True, read_only=True)
    aiClassification = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    mail = serializers.SerializerMethodField()
    # `approved` to BooleanField na modelu — DRF auto-serializuje, bez override.

    class Meta:
        model = Case
        fields = [
            "id",
            "title",
            "createdAt",
            "approved",
            "damageDescription",
            "repairDescription",
            "photos",
            "aiClassification",
            "responsibility",
            "cost",
            "mail",
            "history",
        ]

    def get_aiClassification(self, obj: Case) -> dict:
        return {
            "category": obj.ai_category,
            "damageType": obj.ai_damage_type,
            "confidence": obj.ai_confidence,
            "suggestedResponsibility": obj.ai_suggested_responsibility or None,
            "suggestedRepair": obj.ai_suggested_repair,
            "suggestedLaborCost": (
                float(obj.ai_suggested_labor_cost)
                if obj.ai_suggested_labor_cost is not None
                else None
            ),
            "suggestedMaterialCost": (
                float(obj.ai_suggested_material_cost)
                if obj.ai_suggested_material_cost is not None
                else None
            ),
        }

    def get_cost(self, obj: Case) -> dict:
        labor = float(obj.cost_labor or 0)
        materials = float(obj.cost_materials or 0)
        return {
            "labor": labor,
            "materials": materials,
            "total": labor + materials,
            "currency": obj.cost_currency,
        }

    def get_mail(self, obj: Case) -> dict:
        return {
            "shouldGenerate": obj.mail_should_generate,
            "template": obj.mail_template or None,
        }
