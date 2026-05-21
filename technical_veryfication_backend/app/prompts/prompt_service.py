"""
Pipeline weryfikacji usterek (LangChain).

Pięć etapów, jeden plik promptu na etap, wspólny system_prompt:

  1. detect_element     - Prompt_1: identyfikacja uszkodzonego elementu
  2. classify_damage    - Prompt_2: przyczyna (mechaniczna / amortyzacyjna)
  3. propose_repair     - Prompt_3: najtrwalsza ścieżka naprawy
  4. estimate_cost      - Prompt_4: koszt finalny (PLN, single value)
  5. aggregate          - Prompt_5: DETERMINISTYCZNY merge (bez LLM)

Wszystkie wywołania LLM używają `with_structured_output(pydantic_schema)` -
brak ręcznego parsowania JSON.

Bonus poza schematem promptów (deterministycznie): `responsibility` jest
wyprowadzane z damage_cause (mechaniczne → tenant, amortyzacyjne → landlord)
- wymagane przez front i model Django, a nie zwracane przez żaden z 5 promptów.

Klucz API: AI_API_KEY ładowany z `.env` w roocie projektu.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# ── .env loader ─────────────────────────────────────────────────────────────
# Poza Dockerem dotenv sam znajdzie `.env` w drzewie (find_dotenv).
# W kontenerze zmienne wstrzykuje compose przez `env_file` - load_dotenv()
# bez pliku to no-op, więc bezpiecznie wołać w obu środowiskach.
load_dotenv()

BASE_PROMPTS_DIR = Path(__file__).resolve().parent


# ── Schemy etapowe (output każdego LLM-calla) ───────────────────────────────
class ElementDetection(BaseModel):
    """Prompt 1 - Element Detector."""

    detected_element: str = Field(
        description="Nazwa uszkodzonego elementu (technicznie i potocznie)"
    )


class DamageClassification(BaseModel):
    """Prompt 2 - Damage Classifier."""

    damage_cause: str = Field(
        description="'Uszkodzenie mechaniczne' lub 'Uszkodzenie amortyzacyjne'"
    )
    confidence_percentage: int = Field(ge=0, le=100)
    damage_description: str = Field(description="Krótki opis stanu uszkodzenia")


class RepairProposal(BaseModel):
    """Prompt 3 - Repair Specialist (najtrwalsze rozwiązanie)."""

    repair_steps: str = Field(description="Numerowane kroki naprawy, max 50 słów")
    repair_durability: str = Field(
        description="Trwałość rozwiązania, np. 'wysoka', '3-5 lat'"
    )
    repair_difficulty: str = Field(description="niski | średni | wysoki")


class CostBreakdown(BaseModel):
    labor: float
    materials: float
    total: float
    currency: str = "PLN"


class CostEstimate(BaseModel):
    """Prompt 4 - Cost Estimator (single value, nie widełki)."""

    cost: CostBreakdown


# ── Wyjście pipelinu (po Prompt 5 - deterministyczny merge) ────────────────
class VerificationResult(BaseModel):
    damage_cause: str
    confidence_percentage: int
    detected_element: str
    damage_description: str
    repair_steps: str
    repair_durability: str
    repair_difficulty: str
    cost: CostBreakdown
    # Pole spoza promptów - wyprowadzone z damage_cause.
    responsibility: str = Field(description="tenant | owner | unresolved")


# ── Service ─────────────────────────────────────────────────────────────────
class PromptService:
    """LangChain-owy pipeline weryfikacji usterki."""

    # Defaulty czytane z .env (zmienne `AI_MODEL` i `AI_TEMPERATURE`), z fallbackiem
    # do bezpiecznych wartości deweloperskich gdy zmienne nie są ustawione.
    DEFAULT_MODEL = os.environ.get("AI_MODEL", "gpt-4o")
    DEFAULT_TEMPERATURE = float(os.environ.get("AI_TEMPERATURE", "0.1"))

    # ── Init ────────────────────────────────────────────────────────────────
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
    ):
        self.model_name = model or self.DEFAULT_MODEL
        self.temperature = (
            temperature if temperature is not None else self.DEFAULT_TEMPERATURE
        )
        # `api_key=""` świadomie wymusza tryb symulacji
        if api_key is None:
            self.api_key = os.environ.get("AI_API_KEY") or os.environ.get(
                "OPENAI_API_KEY"
            )
        else:
            self.api_key = api_key
        self._llm = None  # lazy

    # ── Public API: cały pipeline ──────────────────────────────────────────
    def run(
        self,
        issue_topic: str,
        photos: Optional[List[str]] = None,
        damage_description_hint: str = "",
        kb_context: str = "",
    ) -> VerificationResult:
        """`kb_context` - opcjonalny blok tekstu z wcześniejszymi zatwierdzonymi
        sprawami (z `KnowledgeBaseEntry`). Wstrzykiwany do promptów detect i
        classify, żeby AI uczyło się z decyzji koordynatora."""
        photos = photos or []
        detection = self.detect_element(
            issue_topic, photos, damage_description_hint, kb_context
        )
        classification = self.classify_damage(
            issue_topic, photos, detection, damage_description_hint, kb_context
        )
        repair = self.propose_repair(issue_topic, photos, detection, classification)
        cost = self.estimate_cost(issue_topic, photos, detection, classification, repair)
        return self.aggregate(detection, classification, repair, cost)

    # ── Etap 1 (z vision) ──────────────────────────────────────────────────
    def detect_element(
        self,
        issue_topic: str,
        photos: List[str],
        hint: str = "",
        kb_context: str = "",
    ) -> ElementDetection:
        if not self.api_key:
            return self._simulate_detection(issue_topic, hint)

        human = (
            f"{self._kb_block(kb_context)}"
            f"Temat usterki: {issue_topic}\n"
            f"Liczba załączonych zdjęć: {len(photos)}\n"
            f"Dodatkowy opis użytkownika: {hint or '(brak)'}"
        )
        return self._invoke(ElementDetection, "Prompt_1.txt", human, photos)

    # ── Etap 2 (z vision) ──────────────────────────────────────────────────
    def classify_damage(
        self,
        issue_topic: str,
        photos: List[str],
        detection: ElementDetection,
        hint: str = "",
        kb_context: str = "",
    ) -> DamageClassification:
        if not self.api_key:
            return self._simulate_classification(issue_topic, hint)

        human = (
            f"{self._kb_block(kb_context)}"
            f"Temat usterki: {issue_topic}\n"
            f"Liczba załączonych zdjęć: {len(photos)}\n"
            f"Dodatkowy opis użytkownika: {hint or '(brak)'}\n\n"
            f"Output z Prompt 1:\n{detection.model_dump_json(indent=2)}"
        )
        return self._invoke(DamageClassification, "Prompt_2.txt", human, photos)

    @staticmethod
    def _kb_block(kb_context: str) -> str:
        """Sklejony nagłówek z kontekstem KB albo pusty string. Pusta wartość
        ułatwia formatowanie f-stringów wyżej (bez warunków w środku)."""
        if not kb_context:
            return ""
        return (
            "Wcześniejsze zatwierdzone sprawy (kontekst od koordynatora):\n"
            f"{kb_context}\n\n"
        )

    # ── Etap 3 (z vision - naprawa dopasowana do widocznej skali) ──────────
    def propose_repair(
        self,
        issue_topic: str,
        photos: List[str],
        detection: ElementDetection,
        classification: DamageClassification,
    ) -> RepairProposal:
        if not self.api_key:
            return self._simulate_repair(classification)

        human = (
            f"Temat usterki: {issue_topic}\n"
            f"Liczba załączonych zdjęć: {len(photos)}\n\n"
            f"Output z Prompt 1:\n{detection.model_dump_json(indent=2)}\n\n"
            f"Output z Prompt 2:\n{classification.model_dump_json(indent=2)}"
        )
        return self._invoke(RepairProposal, "Prompt_3.txt", human, photos)

    # ── Etap 4 (z vision - koszt zależny od skali widocznej na zdjęciu) ────
    def estimate_cost(
        self,
        issue_topic: str,
        photos: List[str],
        detection: ElementDetection,
        classification: DamageClassification,
        repair: RepairProposal,
    ) -> CostEstimate:
        if not self.api_key:
            return self._simulate_cost(repair)

        human = (
            f"Temat usterki: {issue_topic}\n"
            f"Liczba załączonych zdjęć: {len(photos)}\n\n"
            f"Output z Prompt 1:\n{detection.model_dump_json(indent=2)}\n\n"
            f"Output z Prompt 2:\n{classification.model_dump_json(indent=2)}\n\n"
            f"Output z Prompt 3:\n{repair.model_dump_json(indent=2)}"
        )
        return self._invoke(CostEstimate, "Prompt_4.txt", human, photos)

    # ── Etap 5 - DETERMINISTYCZNY merge (bez LLM) ──────────────────────────
    @staticmethod
    def aggregate(
        detection: ElementDetection,
        classification: DamageClassification,
        repair: RepairProposal,
        cost: CostEstimate,
    ) -> VerificationResult:
        return VerificationResult(
            damage_cause=classification.damage_cause,
            confidence_percentage=classification.confidence_percentage,
            detected_element=detection.detected_element,
            damage_description=classification.damage_description,
            repair_steps=repair.repair_steps,
            repair_durability=repair.repair_durability,
            repair_difficulty=repair.repair_difficulty,
            cost=cost.cost,
            responsibility=PromptService._derive_responsibility(
                classification.damage_cause
            ),
        )

    # ── Reguła responsibility (deterministyczna, poza schematem promptów) ──
    # "owner" = właściciel (front i model Django) - odpowiednik "landlord" w domenie.
    @staticmethod
    def _derive_responsibility(damage_cause: str) -> str:
        cause = (damage_cause or "").lower()
        if "mechaniczne" in cause:
            return "tenant"
        if "amortyzacyjne" in cause:
            return "owner"
        return "unresolved"

    # ── LangChain helpers ──────────────────────────────────────────────────
    def _get_llm(self):
        if self._llm is None:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.api_key,
            )
        return self._llm

    def _invoke(
        self,
        schema: type[BaseModel],
        step_filename: str,
        human_text: str,
        photos: List[str],
    ):
        """Wywołuje LLM: SystemMessage = System_Prompt + Prompt_N, HumanMessage
        = tekst + (opcjonalnie) image_url content blocks. `photos` to lista
        dataURL-i (`data:image/jpeg;base64,...`) - view wcześniej zamienił
        URL-e z MEDIA na bytes, bo OpenAI nie dotrze do localhost. URL-e
        nie-data są przepuszczane jako-jest (na wypadek publicznych linków)."""
        from langchain_core.messages import HumanMessage, SystemMessage

        system_text = (
            self._load_text("System_Prompt.txt")
            + "\n\n---\n\n"
            + self._load_text(step_filename)
        )

        content_blocks: list = [{"type": "text", "text": human_text}]
        for image_ref in photos:
            if not image_ref:
                continue
            content_blocks.append(
                {"type": "image_url", "image_url": {"url": image_ref}}
            )

        messages = [
            SystemMessage(content=system_text),
            HumanMessage(content=content_blocks),
        ]
        structured = self._get_llm().with_structured_output(schema)
        return structured.invoke(messages)

    @staticmethod
    def _load_text(filename: str) -> str:
        # SystemMessage przyjmuje surowy tekst - escape klamer nie jest potrzebny.
        return (BASE_PROMPTS_DIR / filename).read_text(encoding="utf-8")

    # ── Symulacje (fallback bez klucza API) ────────────────────────────────
    @staticmethod
    def _simulate_detection(issue_topic: str, hint: str) -> ElementDetection:
        text = f"{issue_topic} {hint}".lower()
        if "bateria" in text:
            element = "bateria łazienkowa"
        elif "szyba" in text:
            element = "szyba balkonowa"
        elif "odpływ" in text or "syfon" in text:
            element = "odpływ / syfon kuchenny"
        elif "deska" in text:
            element = "deska klozetowa"
        else:
            element = "niezidentyfikowany element"
        return ElementDetection(detected_element=element)

    @staticmethod
    def _simulate_classification(issue_topic: str, hint: str) -> DamageClassification:
        text = f"{issue_topic} {hint}".lower()
        mech = any(w in text for w in ("pęknię", "wyrwan", "złama", "spal", "zerwa"))
        amort = any(
            w in text for w in ("przeciek", "wyciek", "zatk", "wilgoć", "zużycie")
        )
        if mech and not amort:
            cause = "Uszkodzenie mechaniczne"
        elif amort and not mech:
            cause = "Uszkodzenie amortyzacyjne"
        else:
            cause = "Uszkodzenie amortyzacyjne"
        return DamageClassification(
            damage_cause=cause,
            confidence_percentage=75,
            damage_description=(hint or issue_topic)[:200],
        )

    @staticmethod
    def _simulate_repair(classification: DamageClassification) -> RepairProposal:
        return RepairProposal(
            repair_steps=(
                "1. Zdiagnozować uszkodzony podzespół. "
                "2. Wymienić element na nowy. "
                "3. Przetestować szczelność/funkcjonalność."
            ),
            repair_durability="wysoka",
            repair_difficulty="średni",
        )

    @staticmethod
    def _simulate_cost(repair: RepairProposal) -> CostEstimate:
        total = 350
        labor = int(round(total * 0.6))
        return CostEstimate(
            cost=CostBreakdown(
                labor=labor,
                materials=total - labor,
                total=total,
                currency="PLN",
            )
        )
