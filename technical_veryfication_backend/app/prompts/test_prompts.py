"""
Test Prompts Module

Moduł do testowania i eksperymentowania z promptami AI.
Pozwala na porównywanie różnych wersji promptów i ich wyników.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from .prompt_helpers import PromptService


@dataclass
class TestCase:
    """Reprezentuje pojedynczy przypadek testowy"""

    name: str
    issue_topic: str
    photos: List[str]
    damage_description: str = ""
    expected_damage_cause: str = ""
    expected_responsibility: str = ""
    search_results: str = ""


@dataclass
class TestResult:
    """Wynik pojedynczego testu"""

    test_case: TestCase
    verification_result: Dict[str, Any]
    cost_result: Dict[str, Any]
    full_case: Dict[str, Any]
    execution_time: float
    timestamp: str


class PromptTester:
    """Klasa do testowania promptów i porównywania wyników"""

    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.results: List[TestResult] = []

    @staticmethod
    def _load_test_cases() -> List[TestCase]:
        """Ładuje przykładowe przypadki testowe"""
        return [
            TestCase(
                name="Bateria przeciekająca",
                issue_topic="Uszkodzona bateria w łazience",
                photos=["https://example.com/battery-leak.jpg"],
                damage_description="Bateria łazienkowa przecieka przy podstawie i powoduje zalewanie blatu.",
                expected_damage_cause="Uszkodzenie amortyzacyjne",
                expected_responsibility="landlord",
                search_results="Naprawa baterii łazienkowej kosztuje około 250-350 PLN",
            ),
            TestCase(
                name="Pęknięta szyba",
                issue_topic="Pęknięta szyba balkonowa",
                photos=["https://example.com/cracked-glass.jpg"],
                damage_description="Na szybie balkonowej widoczne jest pęknięcie w dolnej części tafli.",
                expected_damage_cause="Uszkodzenie mechaniczne",
                expected_responsibility="tenant",
                search_results="Wymiana szyby balkonowej kosztuje 600-800 PLN",
            ),
            TestCase(
                name="Zatkany odpływ",
                issue_topic="Zatkany odpływ w kuchni",
                photos=["https://example.com/clogged-drain.jpg"],
                damage_description="Odpływ w zlewie kuchennym jest zatkany i woda spływa bardzo wolno.",
                expected_damage_cause="Uszkodzenie amortyzacyjne",
                expected_responsibility="landlord",
                search_results="Udrożnienie odpływu kuchennego kosztuje 150-250 PLN",
            ),
            TestCase(
                name="Wyrwany zawias",
                issue_topic="Wyrwany zawias drzwiowy",
                photos=["https://example.com/broken-hinge.jpg"],
                damage_description="Zawias drzwiowy został wyrwany z futryny.",
                expected_damage_cause="Uszkodzenie mechaniczne",
                expected_responsibility="tenant",
                search_results="Naprawa zawiasu drzwiowego kosztuje 80-150 PLN",
            ),
        ]

    def run_single_test(self, test_case: TestCase) -> TestResult:
        """Uruchamia pojedynczy test case"""
        start_time = time.time()

        # Krok 1: Weryfikacja uszkodzeń
        verification_result = PromptService.process_verification(
            issue_topic=test_case.issue_topic,
            photos=test_case.photos,
            damage_description=test_case.damage_description,
        )

        # Krok 2: Estymacja kosztów
        cost_result = PromptService.process_cost_estimation(
            verification_result, test_case.search_results
        )

        # Krok 3: Tworzenie pełnego case
        full_case = self._create_full_case(test_case, verification_result, cost_result)

        execution_time = time.time() - start_time

        result = TestResult(
            test_case=test_case,
            verification_result=verification_result,
            cost_result=cost_result,
            full_case=full_case,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat(),
        )

        return result

    def run_all_tests(self) -> List[TestResult]:
        """Uruchamia wszystkie test cases"""
        self.results = []
        print("🚀 Rozpoczynam testowanie promptów...\n")

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"📋 Test {i}/{len(self.test_cases)}: {test_case.name}")
            result = self.run_single_test(test_case)
            self.results.append(result)

            # Wyświetl podsumowanie
            self._print_test_summary(result)
            print("-" * 60)

        print(f"✅ Zakończono testowanie {len(self.results)} przypadków")
        return self.results

    def _create_full_case(
        self,
        test_case: TestCase,
        verification: Dict[str, Any],
        cost_estimation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Tworzy pełny obiekt case na podstawie wyników"""
        import uuid

        case_id = f"TEST-{datetime.now().year}-{str(uuid.uuid4())[:4].upper()}"

        return {
            "id": case_id,
            "title": test_case.issue_topic,
            "createdAt": datetime.now().isoformat() + "Z",
            "status": "ai_review",
            "damageDescription": verification.get(
                "damage_description", test_case.damage_description
            ),
            "repairDescription": verification.get("repair_steps", ""),
            "photos": [
                {
                    "id": f"photo_{i+1:02d}",
                    "url": photo_url,
                    "isMain": i == 0,
                }
                for i, photo_url in enumerate(test_case.photos)
            ],
            "aiClassification": {
                "category": "Nieokreślona",
                "damageType": verification.get("detected_element", ""),
                "confidence": verification.get("confidence_percentage", 0) / 100,
                "suggestedResponsibility": cost_estimation.get(
                    "responsibility", "unresolved"
                ),
                "suggestedRepair": verification.get("repair_steps", ""),
                "suggestedLaborCost": cost_estimation.get("cost_breakdown", {}).get(
                    "labor", 0
                ),
                "suggestedMaterialCost": cost_estimation.get("cost_breakdown", {}).get(
                    "materials", 0
                ),
            },
            "responsibility": cost_estimation.get("responsibility", "unresolved"),
            "cost": {
                "labor": cost_estimation.get("cost_breakdown", {}).get("labor", 0),
                "materials": cost_estimation.get("cost_breakdown", {}).get(
                    "materials", 0
                ),
                "total": cost_estimation.get("final_cost_pln", 0),
                "currency": "PLN",
            },
            "mail": {
                "shouldGenerate": cost_estimation.get("responsibility")
                in ["owner", "tenant"],
                "template": (
                    "owner_repair_notice"
                    if cost_estimation.get("responsibility") == "owner"
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
                    "label": "Utworzono zgłoszenie testowe",
                    "createdAt": datetime.now().isoformat() + "Z",
                    "createdBy": "Test System",
                },
                {
                    "type": "ai_classified",
                    "label": "AI przetestowało zgłoszenie",
                    "createdAt": (
                        datetime.now().replace(second=datetime.now().second + 1)
                    ).isoformat()
                    + "Z",
                    "createdBy": "AI Test",
                },
            ],
        }

    def _print_test_summary(self, result: TestResult):
        """Wyświetla podsumowanie pojedynczego testu"""
        print(f"⏱️  Czas wykonania: {result.execution_time:.2f}s")
        print(
            f"🔍 Przyczyna uszkodzenia: {result.verification_result.get('damage_cause', 'N/A')}"
        )
        print(f"👤 Odpowiedzialność: {result.cost_result.get('responsibility', 'N/A')}")
        print(f"💰 Szacowany koszt: {result.cost_result.get('final_cost_pln', 0)} PLN")
        print(
            f"📊 Pewność diagnozy: {result.verification_result.get('confidence_percentage', 0)}%"
        )

        # Sprawdź zgodność z oczekiwaniami
        expected_cause = result.test_case.expected_damage_cause
        actual_cause = result.verification_result.get("damage_cause", "")
        if expected_cause and expected_cause.lower() in actual_cause.lower():
            print("✅ Przyczyna uszkodzenia zgodna z oczekiwaniami")
        elif expected_cause:
            print(f"❌ Przyczyna niezgodna - oczekiwano: {expected_cause}")

        expected_resp = result.test_case.expected_responsibility
        actual_resp = result.cost_result.get("responsibility", "")
        if expected_resp and expected_resp == actual_resp:
            print("✅ Odpowiedzialność zgodna z oczekiwaniami")
        elif expected_resp:
            print(f"❌ Odpowiedzialność niezgodna - oczekiwano: {expected_resp}")

    def save_results_to_file(self, filename: str = "test_results.json"):
        """Zapisuje wyniki testów do pliku JSON"""
        results_data = []
        for result in self.results:
            results_data.append(
                {
                    "test_case": {
                        "name": result.test_case.name,
                        "issue_topic": result.test_case.issue_topic,
                        "expected_damage_cause": result.test_case.expected_damage_cause,
                        "expected_responsibility": result.test_case.expected_responsibility,
                    },
                    "verification_result": result.verification_result,
                    "cost_result": result.cost_result,
                    "execution_time": result.execution_time,
                    "timestamp": result.timestamp,
                }
            )

        output_path = Path(__file__).parent / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)

        print(f"💾 Wyniki zapisane do: {output_path}")

    def compare_prompt_versions(
        self, version1_results: List[TestResult], version2_results: List[TestResult]
    ):
        """Porównuje wyniki dwóch wersji promptów"""
        if len(version1_results) != len(version2_results):
            print("❌ Różna liczba wyników do porównania")
            return

        print("📊 PORÓWNANIE WYNIKÓW:")
        print("=" * 60)

        total_accuracy_v1 = 0
        total_accuracy_v2 = 0

        for i, (r1, r2) in enumerate(zip(version1_results, version2_results)):
            print(f"\n🔍 Test {i+1}: {r1.test_case.name}")

            # Porównaj przyczyny uszkodzeń
            cause1 = r1.verification_result.get("damage_cause", "")
            cause2 = r2.verification_result.get("damage_cause", "")
            expected = r1.test_case.expected_damage_cause

            acc1 = 1 if expected.lower() in cause1.lower() else 0
            acc2 = 1 if expected.lower() in cause2.lower() else 0

            print(f"  Przyczyna V1: {cause1} ({'✅' if acc1 else '❌'})")
            print(f"  Przyczyna V2: {cause2} ({'✅' if acc2 else '❌'})")

            # Porównaj odpowiedzialność
            resp1 = r1.cost_result.get("responsibility", "")
            resp2 = r2.cost_result.get("responsibility", "")
            expected_resp = r1.test_case.expected_responsibility

            resp_acc1 = 1 if expected_resp == resp1 else 0
            resp_acc2 = 1 if expected_resp == resp2 else 0

            print(f"  Odpowiedzialność V1: {resp1} ({'✅' if resp_acc1 else '❌'})")
            print(f"  Odpowiedzialność V2: {resp2} ({'✅' if resp_acc2 else '❌'})")

            total_accuracy_v1 += acc1 + resp_acc1
            total_accuracy_v2 += acc2 + resp_acc2

        max_score = (
            len(version1_results) * 2
        )  # 2 punkty za każdy test (przyczyna + odpowiedzialność)
        accuracy_v1 = (total_accuracy_v1 / max_score) * 100
        accuracy_v2 = (total_accuracy_v2 / max_score) * 100

        print(f"\n📈 WYNIKI KOŃCOWE:")
        print(f"  Wersja 1 dokładność: {accuracy_v1:.1f}%")
        print(f"  Wersja 2 dokładność: {accuracy_v2:.1f}%")

        if accuracy_v1 > accuracy_v2:
            print("🏆 Wersja 1 jest lepsza")
        elif accuracy_v2 > accuracy_v1:
            print("🏆 Wersja 2 jest lepsza")
        else:
            print("🤝 Wersje są równie dobre")


class PromptProcessor:
    """Klasa do przetwarzania promptów i łączenia wyników"""

    @staticmethod
    def process_complete_case(
        issue_topic: str,
        photos: List[str] = None,
        damage_description: str = "",
        search_results: str = "",
    ) -> Dict[str, Any]:
        """
        Przetwarza kompletny case przez oba prompty

        Args:
            issue_topic: Temat zgłoszenia
            photos: Lista URLi zdjęć
            damage_description: Opis uszkodzenia
            search_results: Wyniki wyszukiwania kosztów

        Returns:
            Słownik z pełnym case i wynikami obu promptów
        """
        photos = photos or []

        # Krok 1: Weryfikacja uszkodzeń
        verification_result = PromptService.process_verification(
            issue_topic=issue_topic,
            photos=photos,
            damage_description=damage_description,
        )

        # Krok 2: Estymacja kosztów
        cost_result = PromptService.process_cost_estimation(
            verification_result, search_results
        )

        # Krok 3: Tworzenie pełnego case
        full_case = PromptProcessor._create_case_from_results(
            issue_topic, photos, verification_result, cost_result
        )

        return {
            "case": full_case,
            "verification_result": verification_result,
            "cost_estimation": cost_result,
            "processing_timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def _create_case_from_results(
        issue_topic: str,
        photos: List[str],
        verification: Dict[str, Any],
        cost_estimation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Tworzy pełny obiekt case z wyników obu promptów"""
        import uuid

        case_id = f"CASE-{datetime.now().year}-{str(uuid.uuid4())[:4].upper()}"

        return {
            "id": case_id,
            "title": issue_topic,
            "createdAt": datetime.now().isoformat() + "Z",
            "status": "ai_review",
            "damageDescription": verification.get("damage_description", issue_topic),
            "repairDescription": verification.get("repair_steps", ""),
            "photos": [
                {
                    "id": f"photo_{i+1:02d}",
                    "url": photo_url,
                    "isMain": i == 0,
                }
                for i, photo_url in enumerate(photos)
            ],
            "aiClassification": {
                "category": PromptProcessor._infer_category(
                    verification.get("detected_element", "")
                ),
                "damageType": verification.get("detected_element", ""),
                "confidence": verification.get("confidence_percentage", 0) / 100,
                "suggestedResponsibility": cost_estimation.get(
                    "responsibility", "unresolved"
                ),
                "suggestedRepair": verification.get("repair_steps", ""),
                "suggestedLaborCost": cost_estimation.get("cost_breakdown", {}).get(
                    "labor", 0
                ),
                "suggestedMaterialCost": cost_estimation.get("cost_breakdown", {}).get(
                    "materials", 0
                ),
            },
            "responsibility": cost_estimation.get("responsibility", "unresolved"),
            "cost": {
                "labor": cost_estimation.get("cost_breakdown", {}).get("labor", 0),
                "materials": cost_estimation.get("cost_breakdown", {}).get(
                    "materials", 0
                ),
                "total": cost_estimation.get("final_cost_pln", 0),
                "currency": "PLN",
            },
            "mail": {
                "shouldGenerate": cost_estimation.get("responsibility")
                in ["owner", "tenant"],
                "template": (
                    "owner_repair_notice"
                    if cost_estimation.get("responsibility") == "owner"
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
                    "createdBy": "AI System",
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

    @staticmethod
    def _infer_category(detected_element: str) -> str:
        """Inferuje kategorię na podstawie wykrytego elementu"""
        element_lower = detected_element.lower()

        if any(
            word in element_lower for word in ["bateria", "odpływ", "prysznic", "wanna"]
        ):
            return "Hydraulika"
        elif any(word in element_lower for word in ["szyba", "drzwi", "okno"]):
            return "Stolarka"
        elif any(word in element_lower for word in ["elektryczn", "prąd", "gniazdko"]):
            return "Elektryka"
        else:
            return "Inne"


# Funkcje pomocnicze do bezpośredniego użycia
def test_prompts():
    """Funkcja do uruchomienia testów promptów"""
    tester = PromptTester()
    results = tester.run_all_tests()
    tester.save_results_to_file()
    return results


def process_case_with_prompts(
    issue_topic: str,
    photos: List[str] = None,
    damage_description: str = "",
    search_results: str = "",
) -> Dict[str, Any]:
    """
    Główna funkcja do przetwarzania case przez oba prompty

    Zwraca pełny JSON z case gotowym do użycia w aplikacji
    """
    return PromptProcessor.process_complete_case(
        issue_topic=issue_topic,
        photos=photos,
        damage_description=damage_description,
        search_results=search_results,
    )


def send_to_api_endpoint(
    case_data: Dict[str, Any], api_url: str = "http://localhost:8000/api/create-case/"
):
    """
    Wysyła przetworzony case do API endpointu

    Args:
        case_data: Wynik z process_case_with_prompts()
        api_url: URL endpointu API

    Returns:
        Odpowiedź z API lub błąd
    """
    import requests

    try:
        # Przygotuj dane do wysłania (bez pełnego case, tylko input)
        # API endpoint sam przetworzy dane
        api_payload = {
            "title": case_data["case"]["title"],
            "photos": [photo["url"] for photo in case_data["case"]["photos"]],
            "damage_description": case_data["case"]["damageDescription"],
            "search_results": "",  # Można dodać jeśli dostępne
        }

        response = requests.post(api_url, json=api_payload, timeout=30)

        if response.status_code == 201:
            print("✅ Case wysłany pomyślnie do API")
            return response.json()
        else:
            print(f"❌ Błąd API: {response.status_code}")
            print(response.text)
            return None

    except requests.RequestException as e:
        print(f"❌ Błąd połączenia z API: {e}")
        return None


# Przykład użycia
if __name__ == "__main__":
    print("🧪 TESTOWANIE PROMPTÓW")
    print("=" * 50)

    # Test pojedynczego case
    test_case = {
        "issue_topic": "Uszkodzona bateria w łazience",
        "photos": ["https://example.com/battery.jpg"],
        "damage_description": "Bateria przecieka przy podstawie",
        "search_results": "Naprawa baterii kosztuje 250-350 PLN",
    }

    print("📝 Przetwarzanie przykładowego case...")
    result = process_case_with_prompts(**test_case)

    print("\n📊 WYNIKI:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Zapisz do pliku
    output_file = Path(__file__).parent / "sample_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Wyniki zapisane do: {output_file}")

    # Przykład wysyłania do API (zakomentowany - wymaga uruchomionego backendu)
    # print("\n📤 Przykład wysyłania do API...")
    # api_result = send_case_to_api(**test_case)
    # if api_result:
    #     print("✅ API Response:")
    #     print(json.dumps(api_result, ensure_ascii=False, indent=2))
    # else:
    #     print("❌ API call failed - prawdopodobnie backend nie jest uruchomiony")

    # Uruchom pełne testy
    print("\n🚀 Uruchamianie pełnych testów...")
    test_results = test_prompts()


def send_case_to_api(
    issue_topic: str,
    photos: List[str] = None,
    damage_description: str = "",
    search_results: str = "",
    api_url: str = "http://localhost:8000/api/create-case/",
) -> Dict[str, Any] | None:
    """
    Funkcja która przetwarza case przez oba prompty i wysyła do API

    Args:
        issue_topic: Temat zgłoszenia
        photos: Lista URLi zdjęć
        damage_description: Opis uszkodzenia
        search_results: Wyniki wyszukiwania kosztów
        api_url: URL endpointu API

    Returns:
        Odpowiedź z API lub None w przypadku błędu
    """
    print("🔄 Przetwarzanie case przez prompty...")

    # Krok 1: Przetwórz przez oba prompty
    case_data = process_case_with_prompts(
        issue_topic=issue_topic,
        photos=photos,
        damage_description=damage_description,
        search_results=search_results,
    )

    if not case_data:
        print("❌ Błąd podczas przetwarzania case")
        return None

    print("✅ Case przetworzony pomyślnie")
    print(f"📋 ID: {case_data['case']['id']}")
    print(f"🔍 Przyczyna: {case_data['verification_result']['damage_cause']}")
    print(f"👤 Odpowiedzialność: {case_data['cost_estimation']['responsibility']}")
    print(f"💰 Koszt: {case_data['cost_estimation']['final_cost_pln']} PLN")

    # Krok 2: Wyślij do API
    print(f"\n📤 Wysyłanie do API: {api_url}")

    api_response = send_to_api_endpoint(case_data, api_url)

    if api_response:
        print("🎉 Case wysłany pomyślnie!")
        return api_response
    else:
        print("❌ Nie udało się wysłać case do API")
        return None
