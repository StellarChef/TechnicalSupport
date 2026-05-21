"""
Tester pipelinu PromptService - uruchamia scenariusze i zapisuje wyniki
do tests/test_results.json.

Domyślnie idzie w trybie SYMULACJI (bez wywołań API, szybko, deterministycznie).
Aby uderzyć w realne API:
    python -m prompts.tests.test_prompts --api

Aby wysłać wyniki na lokalny endpoint Django (po podniesieniu serwera):
    python -m prompts.tests.test_prompts --send-to-api
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests as http

# Pozwól odpalać plik bezpośrednio (poza Djangiem)
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from prompts.prompt_service import PromptService, VerificationResult

TESTS_DIR = Path(__file__).parent


@dataclass
class TestCase:
    name: str
    issue_topic: str
    photos: List[str]
    damage_description: str = ""
    expected_damage_cause: str = ""  # częściowy match (lowercase), np. "mechaniczne"
    expected_responsibility: str = ""  # tenant | owner | unresolved


TEST_CASES: List[TestCase] = [
    TestCase(
        name="Bateria przeciekająca",
        issue_topic="Uszkodzona bateria w łazience",
        photos=["https://example.com/battery-leak.jpg"],
        damage_description="Bateria łazienkowa przecieka przy podstawie.",
        expected_damage_cause="amortyzacyjne",
        expected_responsibility="owner",
    ),
    TestCase(
        name="Pęknięta szyba",
        issue_topic="Pęknięta szyba balkonowa",
        photos=["https://example.com/cracked-glass.jpg"],
        damage_description="Pęknięcie w dolnej części tafli szyby balkonowej.",
        expected_damage_cause="mechaniczne",
        expected_responsibility="tenant",
    ),
    TestCase(
        name="Zatkany odpływ",
        issue_topic="Zatkany odpływ w kuchni",
        photos=["https://example.com/clogged-drain.jpg"],
        damage_description="Odpływ w zlewie kuchennym zatkany, woda spływa wolno.",
        expected_damage_cause="amortyzacyjne",
        expected_responsibility="owner",
    ),
    TestCase(
        name="Wyrwany zawias",
        issue_topic="Wyrwany zawias drzwiowy",
        photos=["https://example.com/broken-hinge.jpg"],
        damage_description="Zawias drzwiowy wyrwany z futryny.",
        expected_damage_cause="mechaniczne",
        expected_responsibility="tenant",
    ),
]


def run_tests(use_api: bool = False, save: bool = True) -> List[Dict[str, Any]]:
    mode = "REAL API" if use_api else "SIMULATION"
    print(f"=== Tryb: {mode} ===\n")

    # api_key="" wymusza symulację; None → wczyta z .env
    service = PromptService(api_key=None if use_api else "")

    results: List[Dict[str, Any]] = []

    for i, tc in enumerate(TEST_CASES, 1):
        print(f"[{i}/{len(TEST_CASES)}] {tc.name}")
        t0 = time.time()

        result: VerificationResult = service.run(
            issue_topic=tc.issue_topic,
            photos=tc.photos,
            damage_description_hint=tc.damage_description,
        )
        elapsed = round(time.time() - t0, 2)

        cause_ok = tc.expected_damage_cause.lower() in result.damage_cause.lower()
        resp_ok = tc.expected_responsibility == result.responsibility

        cause_tag = "OK" if cause_ok else f"FAIL (oczekiwano: {tc.expected_damage_cause})"
        resp_tag = "OK" if resp_ok else f"FAIL (oczekiwano: {tc.expected_responsibility})"

        print(f"  Element     : {result.detected_element}")
        print(f"  Przyczyna   : {result.damage_cause} [{cause_tag}]")
        print(f"  Pewność     : {result.confidence_percentage}%")
        print(f"  Odpow.      : {result.responsibility} [{resp_tag}]")
        print(f"  Koszt total : {result.cost.total} {result.cost.currency}")
        print(f"  Czas        : {elapsed}s\n")

        results.append(
            {
                "test": tc.name,
                "passed": cause_ok and resp_ok,
                "elapsed_s": elapsed,
                "result": result.model_dump(),
                "timestamp": datetime.now().isoformat(),
            }
        )

    if save:
        out = TESTS_DIR / "test_results.json"
        out.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Wyniki zapisane: {out}")

    passed = sum(1 for r in results if r["passed"])
    print(f"\n=== {passed}/{len(results)} testów zaliczonych ===")
    return results


def send_to_api(
    payload: Dict[str, Any],
    url: str = "http://localhost:8000/api/cases/create/",
) -> Optional[Dict]:
    """Wysyła payload do `POST /api/cases/create/` i zwraca odpowiedź JSON."""
    try:
        resp = http.post(url, json=payload, timeout=60)
        if resp.status_code == 201:
            print(f"API OK ({resp.status_code})")
            return resp.json()
        print(f"API ERROR {resp.status_code}: {resp.text[:200]}")
        return None
    except http.exceptions.RequestException as e:
        print(f"Połączenie nieudane: {e}")
        return None


def _send_all_to_api():
    for tc in TEST_CASES:
        print(f"\n→ POST {tc.name}")
        send_to_api(
            {
                "title": tc.issue_topic,
                "photos": tc.photos,
                "damage_description": tc.damage_description,
            }
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tester PromptService")
    parser.add_argument(
        "--api",
        action="store_true",
        help="Uderzaj w realne OpenAI API zamiast w symulację",
    )
    parser.add_argument(
        "--send-to-api",
        action="store_true",
        help="Wyślij testowe payloady na lokalny endpoint Django",
    )
    args = parser.parse_args()

    if args.send_to_api:
        _send_all_to_api()
    else:
        run_tests(use_api=args.api)
