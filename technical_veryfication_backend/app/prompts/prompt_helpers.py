from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

BASE_PROMPTS_DIR = Path(__file__).resolve().parent


class PromptService:
    @staticmethod
    def load_prompt_file(filename: str) -> str:
        prompt_file = BASE_PROMPTS_DIR / filename
        return prompt_file.read_text(encoding="utf-8")

    @staticmethod
    def build_verification_prompt(issue_topic: str, photos: List[str]) -> str:
        prompt = PromptService.load_prompt_file("Prompt-Veryfication.txt")
        prompt = prompt.replace(
            "Temat usterki: [opis przekazany przez użytkownika]",
            f"Temat usterki: {issue_topic}",
        )
        photos_text = ", ".join(photos) if photos else "brak zdjęć"
        prompt = prompt.replace(
            "Zdjęcia: [załączone obrazy]",
            f"Zdjęcia: {photos_text}",
        )
        return prompt

    @staticmethod
    def build_cost_estimation_prompt(
        input_data: Dict[str, Any], search_results: str
    ) -> str:
        prompt = PromptService.load_prompt_file("Prompt2-Cost-Estimation")
        prompt = prompt.replace(
            "{input_data}",
            json.dumps(input_data, ensure_ascii=False, indent=2),
        )
        prompt = prompt.replace(
            "{search_results}",
            search_results or "Brak wyników wyszukiwania",
        )
        return prompt

    @staticmethod
    def process_verification(
        issue_topic: str,
        photos: List[str] | None = None,
        damage_description: str | None = None,
    ) -> Dict[str, Any]:
        content = " ".join(
            filter(None, [issue_topic.strip(), (damage_description or "").strip()])
        ).lower()
        photos = photos or []

        damage_cause = PromptService._infer_damage_cause(content)
        confidence_percentage = PromptService._calculate_confidence(content)
        detected_element = PromptService._detect_element(content, photos)
        repair_steps = PromptService._build_repair_steps(content, damage_cause)
        estimated_cost_pln = PromptService._estimate_cost(content, damage_cause)
        repair_durability = (
            "wysoka" if damage_cause == "Uszkodzenie amortyzacyjne" else "średnia"
        )
        repair_difficulty = (
            "niski" if damage_cause == "Uszkodzenie amortyzacyjne" else "średni"
        )

        return {
            "damage_cause": damage_cause,
            "confidence_percentage": confidence_percentage,
            "detected_element": detected_element,
            "damage_description": damage_description or issue_topic,
            "repair_steps": repair_steps,
            "estimated_cost_pln": estimated_cost_pln,
            "repair_durability": repair_durability,
            "repair_difficulty": repair_difficulty,
        }

    @staticmethod
    def process_cost_estimation(
        input_data: Dict[str, Any], search_results: str = ""
    ) -> Dict[str, Any]:
        damage_cause = input_data.get("damage_cause", "").lower()
        responsibility = "unclear"
        if "mechaniczne" in damage_cause:
            responsibility = "tenant"
        elif "amortyzacyjne" in damage_cause:
            responsibility = "landlord"

        baseline = int(input_data.get("estimated_cost_pln", 0) or 0)
        search_cost = PromptService._extract_cost_from_search(search_results)
        if search_cost:
            final_cost = max(baseline, search_cost)
        else:
            final_cost = baseline or 250

        labor = int(round(final_cost * 0.6))
        materials = final_cost - labor

        cost_validation = "valid"
        if baseline and final_cost > baseline * 1.15:
            cost_validation = "underestimated"
        elif baseline and final_cost < baseline * 0.85:
            cost_validation = "overestimated"

        reasoning = (
            f"Responsibility set to {responsibility} based on damage cause. "
            f"Final cost calculated from baseline {baseline} PLN and market references. "
        )
        if search_cost:
            reasoning += (
                f"Search output contained a market indication of {search_cost} PLN."
            )

        return {
            "responsibility": responsibility,
            "final_cost_pln": final_cost,
            "cost_breakdown": {"labor": labor, "materials": materials},
            "cost_validation": cost_validation,
            "reasoning": reasoning.strip(),
        }

    @staticmethod
    def _infer_damage_cause(text: str) -> str:
        mechanical_terms = [
            "pęknię",
            "wyrwan",
            "złama",
            "uszkodz",
            "spal",
            "zniekształc",
            "rozsyp",
            "odłami",
            "przebij",
        ]
        amortization_terms = [
            "przeciek",
            "nieszczel",
            "wyciek",
            "zatk",
            "wilgoć",
            "korozj",
            "zużycie",
            "osadz",
            "stare",
        ]
        mechanical_score = sum(text.count(term) for term in mechanical_terms)
        amortization_score = sum(text.count(term) for term in amortization_terms)
        if mechanical_score > amortization_score:
            return "Uszkodzenie mechaniczne"
        return "Uszkodzenie amortyzacyjne"

    @staticmethod
    def _calculate_confidence(text: str) -> int:
        if not text:
            return 50
        score = 50 + min(45, max(0, len(text.split()) - 3) * 3)
        return max(50, min(95, score))

    @staticmethod
    def _detect_element(text: str, photos: List[str]) -> str:
        elements = {
            "bateria": "bateria łazienkowa",
            "szyba": "szyba balkonowa",
            "odpływ": "odpływ kuchenny",
            "kabina": "kabina prysznicowa",
            "zawias": "zawias drzwiowy",
            "front": "front szafkowy",
            "desk": "deska klozetowa",
        }
        for key, name in elements.items():
            if key in text:
                return name
        if photos:
            return "obiekt ze zdjęcia"
        return "niezidentyfikowany element"

    @staticmethod
    def _build_repair_steps(text: str, damage_cause: str) -> str:
        if "bateria" in text or "przeciek" in text or "wyciek" in text:
            return "Sprawdź uszczelnienia, wymień uszczelkę lub baterię i przetestuj szczelność pod ciśnieniem."
        if "szyba" in text or "pęknię" in text:
            return "Wymień szybę po oględzinach i usuń uszkodzoną taflę, zabezpiecz nowe szkło."
        if "odpływ" in text or "zatk" in text:
            return "Oczyść syfon, udrożnij odpływ i sprawdź przelew oraz szczelność po naprawie."
        return "Zidentyfikuj uszkodzony element, dobierz części i wykonaj naprawę zgodnie ze specyfikacją."

    @staticmethod
    def _estimate_cost(text: str, damage_cause: str) -> int:
        if "bateria" in text or "przeciek" in text or "wyciek" in text:
            return 300 if damage_cause == "Uszkodzenie amortyzacyjne" else 380
        if "szyba" in text or "pęknię" in text:
            return 650
        if "odpływ" in text or "zatk" in text:
            return 220
        return 300

    @staticmethod
    def _extract_cost_from_search(search_results: str) -> int | None:
        matches = re.findall(r"(\d+[\s\u00A0]?PLN)", search_results)
        if matches:
            values = [int(re.sub(r"[^0-9]", "", item)) for item in matches]
            return max(values) if values else None
        return None
