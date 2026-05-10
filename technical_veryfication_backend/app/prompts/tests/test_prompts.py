"""
Tester promptów AI — uruchamia 4 scenariusze i zapisuje wyniki do tests/test_results.json.
Uruchomienie: python -m prompts.tests.test_prompts
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests as http

from prompts.prompt_helpers import PromptService

TESTS_DIR = Path(__file__).parent


@dataclass
class TestCase:
    name: str
    issue_topic: str
    photos: List[str]
    damage_description: str = ""
    expected_damage_cause: str = ""
    expected_responsibility: str = ""
    search_results: str = ""


TEST_CASES: List[TestCase] = [
    TestCase(
        name="Bateria przeciekająca",
        issue_topic="Uszkodzona bateria w łazience",
        photos=["https://example.com/battery-leak.jpg"],
        damage_description="Bateria łazienkowa przecieka przy podstawie.",
        expected_damage_cause="Uszkodzenie amortyzacyjne",
        expected_responsibility="owner",
        search_results="Naprawa baterii łazienkowej kosztuje około 250-350 PLN",
    ),
    TestCase(
        name="Pęknięta szyba",
        issue_topic="Pęknięta szyba balkonowa",
        photos=["https://example.com/cracked-glass.jpg"],
        damage_description="Pęknięcie w dolnej części tafli szyby balkonowej.",
        expected_damage_cause="Uszkodzenie mechaniczne",
        expected_responsibility="tenant",
        search_results="Wymiana szyby balkonowej kosztuje 600-800 PLN",
    ),
    TestCase(
        name="Zatkany odpływ",
        issue_topic="Zatkany odpływ w kuchni",
        photos=["https://example.com/clogged-drain.jpg"],
        damage_description="Odpływ w zlewie kuchennym zatkany, woda spływa wolno.",
        expected_damage_cause="Uszkodzenie amortyzacyjne",
        expected_responsibility="owner",
        search_results="Udrożnienie odpływu kuchennego kosztuje 150-250 PLN",
    ),
    TestCase(
        name="Wyrwany zawias",
        issue_topic="Wyrwany zawias drzwiowy",
        photos=["https://example.com/broken-hinge.jpg"],
        damage_description="Zawias drzwiowy wyrwany z futryny.",
        expected_damage_cause="Uszkodzenie mechaniczne",
        expected_responsibility="tenant",
        search_results="Naprawa zawiasu drzwiowego kosztuje 80-150 PLN",
    ),
]


def run_tests(save: bool = True) -> List[Dict[str, Any]]:
    results = []

    for i, tc in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {tc.name}")
        t0 = time.time()

        verification = PromptService.process_verification(
            issue_topic=tc.issue_topic,
            photos=tc.photos,
            damage_description=tc.damage_description,
        )
        cost = PromptService.process_cost_estimation(verification, tc.search_results)
        elapsed = round(time.time() - t0, 2)

        actual_cause = verification.get("damage_cause", "")
        actual_resp = cost.get("responsibility", "")
        cause_ok = tc.expected_damage_cause.lower() in actual_cause.lower()
        resp_ok = tc.expected_responsibility == actual_resp

        print(f"  Przyczyna : {actual_cause} ({'OK' if cause_ok else 'FAIL, oczekiwano: ' + tc.expected_damage_cause})")
        print(f"  Odpow.    : {actual_resp} ({'OK' if resp_ok else 'FAIL, oczekiwano: ' + tc.expected_responsibility})")
        print(f"  Koszt     : {cost.get('final_cost_pln')} PLN  ({elapsed}s)")

        results.append({
            "test": tc.name,
            "passed": cause_ok and resp_ok,
            "elapsed_s": elapsed,
            "verification": verification,
            "cost": cost,
            "timestamp": datetime.now().isoformat(),
        })

    if save:
        out = TESTS_DIR / "test_results.json"
        out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nWyniki zapisane: {out}")

    passed = sum(1 for r in results if r["passed"])
    print(f"\n=== {passed}/{len(results)} testów zaliczonych ===")
    return results


def send_to_api(payload: Dict[str, Any], url: str = "http://localhost:8000/api/create-case/") -> Optional[Dict]:
    """Wysyła payload do endpointu API i zwraca odpowiedź JSON."""
    try:
        resp = http.post(url, json=payload, timeout=30)
        if resp.status_code == 201:
            print("API OK:", resp.status_code)
            return resp.json()
        print(f"API ERROR {resp.status_code}: {resp.text[:200]}")
        return None
    except http.exceptions.RequestException as e:
        print(f"Połączenie nieudane: {e}")
        return None


if __name__ == "__main__":
    run_tests()
