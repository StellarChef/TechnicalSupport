"""
Endpoints:
  POST /api/verify-case/   — uruchamia pipeline i zwraca SUROWY wynik (preview/debug)
  POST /api/cases/create/  — uruchamia pipeline i zwraca OBIEKT CASE w kształcie frontu

Brak jeszcze persystencji w DB — to dorobimy w kolejnym kroku
(migracje + zapis do modeli `Case`, `CasePhoto`, `CaseHistoryEvent`).
"""

from __future__ import annotations

import base64
import mimetypes
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from prompts.prompt_service import PromptService, VerificationResult
from .models import Case, CaseHistoryEvent, CasePhoto, KnowledgeBaseEntry

from .serializers import (
    CreateCaseRequestSerializer,
    VerifyCaseRequestSerializer,
    CaseSerializer,
)

# Ile wpisów KB wstrzykujemy do pipelinu — kompromis między jakością a kosztem tokenów.
KB_CONTEXT_LIMIT = 5

# Wyświetlana nazwa "wykonawcy" akcji koordynatora. Do podmiany gdy wejdzie auth.
COORDINATOR_NAME = "Maciej"


# ── Helpers ────────────────────────────────────────────────────────────────
def _now_iso() -> str:
    """ISO 8601 w UTC z sufiksem 'Z' (kompatybilne z frontowymi createdAt)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _next_case_id() -> str:
    """`CASE-{rok}-{4 hex znaki}`. Tymczasowo — bez DB, krótki uuid jako sufiks.
    Po dorobieniu persystencji zamienić na sekwencję z bazy."""
    year = datetime.now(timezone.utc).year
    suffix = uuid.uuid4().hex[:4].upper()
    return f"CASE-{year}-{suffix}"


def _mail_payload(responsibility: str) -> dict:
    """Mail nie jest potrzebny gdy płaci najemca. Dla właściciela / sytuacji
    nierozstrzygniętej generujemy szkic odpowiedniego szablonu."""
    if responsibility == "tenant":
        return {"shouldGenerate": False, "template": None}
    if responsibility == "owner":
        return {"shouldGenerate": True, "template": "owner_repair_notice"}
    return {"shouldGenerate": True, "template": "issue_verification_request"}


def _resolve_photo_to_data_url(url: str) -> str | None:
    """Zamienia URL z naszego MEDIA na `data:image/...;base64,...`.

    OpenAI Vision potrzebuje albo publicznie dostępnego URL-a, albo dataURL.
    Nasze pliki w `MEDIA_ROOT` siedzą na localhost/wewnętrznej sieci dockera —
    OpenAI tam nie dotrze. Więc czytamy bytes z dysku i kodujemy base64.
    Zwracamy `None` gdy URL nie wskazuje na nasze media / plik nie istnieje
    / typ MIME nie jest obrazem — wtedy zdjęcie po prostu pomijamy."""
    if not url:
        return None
    if url.startswith("data:"):
        return url

    media_marker = settings.MEDIA_URL or "/media/"
    if media_marker not in url:
        # URL spoza naszego serwera — nie pobieramy, pomijamy.
        return None

    relative = url.split(media_marker, 1)[1].lstrip("/")
    path = Path(settings.MEDIA_ROOT) / relative
    if not path.exists() or not path.is_file():
        return None

    mime, _ = mimetypes.guess_type(str(path))
    if not mime or not mime.startswith("image/"):
        return None

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _resolve_photos(urls: list[str]) -> list[str]:
    """Z listy URL-i zwraca listę dataURL-i (pomijając te, których nie da się
    rozwiązać). Pipeline dostanie tylko te zdjęcia które realnie umie zobaczyć."""
    resolved = []
    for url in urls:
        data_url = _resolve_photo_to_data_url(url)
        if data_url:
            resolved.append(data_url)
    return resolved


def _build_kb_context(limit: int = KB_CONTEXT_LIMIT) -> str:
    """Składa krótki blok tekstu z ostatnich wpisów KB do wstrzyknięcia w prompt.
    Pusty string gdy KB pusta — wtedy `_kb_block` w pipelinie zwróci ''."""
    entries = KnowledgeBaseEntry.objects.all()[:limit]
    if not entries:
        return ""
    blocks = []
    for entry in entries:
        note = (
            f" | nota koordynatora: {entry.coordinator_note}"
            if entry.coordinator_note
            else ""
        )
        blocks.append(
            f"- Element: {entry.detected_element} | "
            f"przyczyna: {entry.damage_cause} | "
            f"odpowiedzialność: {entry.responsibility or 'nieznana'} | "
            f"koszt: {entry.cost_total} {entry.cost_currency}{note}"
        )
    return "\n".join(blocks)


def _save_case(title: str, photos: list[str], result: VerificationResult) -> Case:
    mail = _mail_payload(result.responsibility)
    case = Case.objects.create(
        case_id=_next_case_id(),
        title=title,
        damage_description=result.damage_description,
        repair_description=result.repair_steps,
        ai_category=result.damage_cause,
        ai_damage_type=result.detected_element,
        ai_confidence=result.confidence_percentage / 100,
        ai_suggested_responsibility=result.responsibility,
        ai_suggested_repair=result.repair_steps,
        ai_suggested_labor_cost=result.cost.labor,
        ai_suggested_material_cost=result.cost.materials,
        responsibility=result.responsibility,
        cost_labor=result.cost.labor,
        cost_materials=result.cost.materials,
        cost_currency=result.cost.currency,
        mail_should_generate=mail["shouldGenerate"],
        mail_template=mail["template"] or "",
    )
    for i, url in enumerate(photos):
        CasePhoto.objects.create(case=case, url=url, is_main=(i == 0))
    now = datetime.now(timezone.utc)
    CaseHistoryEvent.objects.create(
        case=case,
        created_at=now,
        event_type="created",
        created_by="System",
        label="Utworzono zgłoszenie",
    )
    CaseHistoryEvent.objects.create(
        case=case,
        event_type="ai_classified",
        label="AI sklasyfikowało zgłoszenie",
        created_at=now + timedelta(seconds=2),
        created_by="AI",
    )
    return case


# ── Views ──────────────────────────────────────────────────────────────────
class VerifyCaseView(APIView):
    """Uruchamia pipeline i zwraca surowy `VerificationResult` (debug/preview)."""

    def post(self, request, *args, **kwargs):
        serializer = VerifyCaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        result = PromptService().run(
            issue_topic=data["issue_topic"],
            photos=data.get("photos", []),
            damage_description_hint=data.get("damage_description", ""),
        )
        return Response(result.model_dump(), status=status.HTTP_200_OK)


class CreateCaseView(APIView):
    """Pełny pipeline + zbudowanie obiektu case w kształcie frontu.
    Wciąga kontekst z KB, żeby AI uczyło się z poprzednio zatwierdzonych spraw."""

    def post(self, request, *args, **kwargs):
        serializer = CreateCaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        photo_urls = data.get("photos", [])
        result = PromptService().run(
            issue_topic=data["title"],
            photos=_resolve_photos(photo_urls),
            damage_description_hint=data.get("damage_description", ""),
            kb_context=_build_kb_context(),
        )
        case = _save_case(
            title=data["title"],
            photos=photo_urls,
            result=result,
        )

        return Response(
            {
                "case": CaseSerializer(case, context={"request": request}).data,
                "verification_result": result.model_dump(),
            },
            status=status.HTTP_201_CREATED,
        )


class ApproveCaseView(APIView):
    """POST /api/cases/<case_id>/approve/

    Zatwierdza sprawę: flip `approved=True`, zapis snapshotu do KB
    (pamięć trwała dla kolejnych weryfikacji), wpis do historii.
    Body (opcjonalne): `{"comment": "..."}` — nota koordynatora trafia do KB.
    """

    def post(self, request, case_id, *args, **kwargs):
        case = get_object_or_404(Case, case_id=case_id)
        comment = request.data.get("comment", "")

        if case.approved:
            return Response(
                {"error": "Sprawa już zatwierdzona."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.approved = True
        case.save(update_fields=["approved", "updated_at"])

        KnowledgeBaseEntry.objects.create(
            source_case=case,
            detected_element=case.ai_damage_type,
            damage_cause=case.ai_category,
            damage_description=case.damage_description,
            repair_steps=case.repair_description,
            cost_total=(case.cost_labor or 0) + (case.cost_materials or 0),
            cost_currency=case.cost_currency,
            responsibility=case.responsibility,
            coordinator_note=comment,
        )

        CaseHistoryEvent.objects.create(
            case=case,
            event_type="approved",
            label="Zatwierdzono sprawę — dodano do bazy wiedzy",
            created_at=datetime.now(timezone.utc),
            created_by=COORDINATOR_NAME,
        )

        return Response(
            CaseSerializer(case, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class CorrectCaseView(APIView):
    """POST /api/cases/<case_id>/correct/

    Ręczna korekta klasyfikacji AI przez koordynatora. Wszystkie pola opcjonalne
    — aktualizujemy tylko te, które przyszły w body.
    Body (wszystkie opcjonalne):
        {
          "category": "Uszkodzenie mechaniczne",
          "damage_type": "deska klozetowa",
          "responsibility": "tenant" | "owner" | "unresolved",
          "labor_cost": 120,
          "material_cost": 80,
          "comment": "Wyraźne pęknięcie na środku — to nie zużycie."
        }
    Po zmianie `responsibility` przeliczamy też `mail_should_generate`/`template`.
    """

    RESPONSIBILITY_CHOICES = {"owner", "tenant", "unresolved"}

    def post(self, request, case_id, *args, **kwargs):
        case = get_object_or_404(Case, case_id=case_id)
        body = request.data

        updated_fields = []

        if "category" in body:
            case.ai_category = body["category"] or ""
            updated_fields.append("ai_category")

        if "damage_type" in body:
            case.ai_damage_type = body["damage_type"] or ""
            updated_fields.append("ai_damage_type")

        if "responsibility" in body:
            resp = body["responsibility"]
            if resp not in self.RESPONSIBILITY_CHOICES:
                return Response(
                    {"error": f"responsibility musi być jedną z: {sorted(self.RESPONSIBILITY_CHOICES)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            case.responsibility = resp
            updated_fields.append("responsibility")
            # Zmiana strony kosztowej → przelicz mail.
            mail = _mail_payload(resp)
            case.mail_should_generate = mail["shouldGenerate"]
            case.mail_template = mail["template"] or ""
            updated_fields += ["mail_should_generate", "mail_template"]

        if "labor_cost" in body:
            case.cost_labor = body["labor_cost"] or 0
            updated_fields.append("cost_labor")

        if "material_cost" in body:
            case.cost_materials = body["material_cost"] or 0
            updated_fields.append("cost_materials")

        if not updated_fields:
            return Response(
                {"error": "Brak zmian do zapisania."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.save(update_fields=updated_fields + ["updated_at"])

        # Zapis eventu z notatką (jeśli była).
        comment = (body.get("comment") or "").strip()
        snippet = comment if len(comment) <= 80 else comment[:77] + "..."
        label = f"Korekta koordynatora: {snippet}" if snippet else "Korekta koordynatora"
        CaseHistoryEvent.objects.create(
            case=case,
            event_type="corrected",
            label=label,
            created_at=datetime.now(timezone.utc),
            created_by=COORDINATOR_NAME,
        )

        return Response(
            CaseSerializer(case, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class ReverifyCaseView(APIView):
    """POST /api/cases/<case_id>/reverify/

    Uruchamia pipeline ponownie na istniejącej sprawie, dorzucając
    `additional_info` do hintu. Aktualizuje pola AI/cost in-place i
    dopisuje event historii. Nie zmienia `approved`.
    Body: `{"additional_info": "..."}` (wymagane, niepuste).
    """

    def post(self, request, case_id, *args, **kwargs):
        case = get_object_or_404(Case, case_id=case_id)
        additional_info = (request.data.get("additional_info") or "").strip()

        if not additional_info:
            return Response(
                {"error": "Brak dodatkowej informacji."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sklej oryginalny opis z nową informacją od koordynatora.
        original = (case.damage_description or "").strip()
        combined_hint = (
            f"{original}\n\nDodatkowa informacja od koordynatora: {additional_info}"
            if original
            else f"Dodatkowa informacja od koordynatora: {additional_info}"
        )

        # Zdjęcia: weź zewnętrzny `url` jeśli jest, w przeciwnym razie ścieżkę z `image`.
        photo_urls = [
            p.url or (p.image.url if p.image else "")
            for p in case.photos.all()
            if p.url or p.image
        ]

        result = PromptService().run(
            issue_topic=case.title,
            photos=_resolve_photos(photo_urls),
            damage_description_hint=combined_hint,
            kb_context=_build_kb_context(),
        )

        mail = _mail_payload(result.responsibility)
        case.damage_description = result.damage_description
        case.repair_description = result.repair_steps
        case.ai_category = result.damage_cause
        case.ai_damage_type = result.detected_element
        case.ai_confidence = result.confidence_percentage / 100
        case.ai_suggested_responsibility = result.responsibility
        case.ai_suggested_repair = result.repair_steps
        case.ai_suggested_labor_cost = result.cost.labor
        case.ai_suggested_material_cost = result.cost.materials
        case.responsibility = result.responsibility
        case.cost_labor = result.cost.labor
        case.cost_materials = result.cost.materials
        case.cost_currency = result.cost.currency
        case.mail_should_generate = mail["shouldGenerate"]
        case.mail_template = mail["template"] or ""
        case.save()

        # Skróć info do labela żeby nie rozwalać layoutu osi czasu w UI.
        snippet = additional_info if len(additional_info) <= 80 else additional_info[:77] + "..."
        CaseHistoryEvent.objects.create(
            case=case,
            event_type="reverified",
            label=f"Ponowna weryfikacja AI: {snippet}",
            created_at=datetime.now(timezone.utc),
            created_by=COORDINATOR_NAME,
        )

        return Response(
            CaseSerializer(case, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )


class CaseListView(APIView):

    def get(self, request, *args, **kwargs):
        cases: list = Case.objects.all()
        serializer = CaseSerializer(cases, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PhotoUploadView(APIView):
    """POST /api/upload-photo/  — multipart upload zdjęcia.

    Zapisuje plik bezpośrednio do MEDIA_ROOT/cases/ przez `default_storage`
    (BEZ tworzenia wiersza w `CasePhoto` — bo `case` jest wymaganym FK i nie
    wiemy jeszcze do której sprawy zdjęcie należy). Zwraca absolutny URL,
    który frontend wkleja do listy `photos` przy `POST /api/cases/create/`.
    Wiersz `CasePhoto(url=...)` powstaje dopiero w `_save_case`.
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        from django.core.files.storage import default_storage

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "Brak pliku (oczekiwane pole 'file')."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # default_storage automatycznie unika kolizji nazw (dopisuje _<hash>).
        saved_path = default_storage.save(f"cases/{file.name}", file)
        url = request.build_absolute_uri(default_storage.url(saved_path))
        return Response({"url": url}, status=status.HTTP_201_CREATED)
