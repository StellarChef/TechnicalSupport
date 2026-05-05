// Symulacja analizy AI obrazów - w produkcji byłby API do rzeczywistego modelu AI
export async function analyzeImageForDamage(imageData) {
  // Symulacja opóźnienia API
  await new Promise((resolve) => setTimeout(resolve, 1500));

  // Mockowe dane analizy - w produkcji byłby prawdziwy AI
  const analyses = [
    {
      detectedObjects: ["Bateria łazienkowa", "Umywalka", "Zbiornik"],
      damageType: "Przeciek",
      damagedElement: "Bateria",
      damageSeverity: "średni",
      confidence: 0.87,
      damageClass: "amortyzacyjne", // amortyzacyjne | mechaniczne
      damageClassConfidence: 0.78,
      description: "Widoczne ślady przecieku z podstawy baterii, bielego osadu oraz zacieku na umywalce",
      scenario: "Długotrwałe oddziaływanie wody, stopniowe zużycie uszczelek",
      repairOptions: [
        {
          title: "Wymiana uszczelki (najtańsze)",
          steps: "1. Odkręcić pokrywę baterii\n2. Wymienić uszczelkę\n3. Zamontować wstecz",
          laborCost: 80,
          materialCost: 35,
          durability: "3-5 lat",
          difficulty: "Łatwe",
        },
        {
          title: "Czyszczenie i przesmolenie (ekonomiczne)",
          steps: "1. Odmontować baterię\n2. Czyścić zawory\n3. Przesmolić połączenia",
          laborCost: 120,
          materialCost: 50,
          durability: "2-3 lata",
          difficulty: "Średnie",
        },
        {
          title: "Pełna wymiana baterii (najtrwałe)",
          steps: "1. Wyłączyć wodę\n2. Odmontować starą baterię\n3. Zainstalować nową\n4. Testować",
          laborCost: 180,
          materialCost: 180,
          durability: "10+ lat",
          difficulty: "Średnie",
          recommended: true,
        },
      ],
    },
    {
      detectedObjects: ["Deska klozetowa", "Ceramika", "Dach"],
      damageType: "Pęknięcie",
      damagedElement: "Deska klozetowa",
      damageSeverity: "poważny",
      confidence: 0.92,
      damageClass: "mechaniczne",
      damageClassConfidence: 0.85,
      description: "Widoczne pęknięcie i dziura w desce klozetowej",
      scenario: "Upadek ciężkiego przedmiotu lub nagłe uderzenie",
      repairOptions: [
        {
          title: "Tymczasowa naprawa żywicą (tania)",
          steps: "1. Oczyścić pęknięcie\n2. Użyć żywicy epoksydowej\n3. Wygładzić\n4. Czekać 24h",
          laborCost: 50,
          materialCost: 30,
          durability: "1-2 miesiące",
          difficulty: "Łatwe",
        },
        {
          title: "Wymiana deski (standardowe)",
          steps: "1. Odkręcić zawiasy\n2. Zdjąć starą deskę\n3. Zainstalować nową\n4. Regulacja zawiasów",
          laborCost: 120,
          materialCost: 150,
          durability: "5+ lat",
          difficulty: "Łatwe",
          recommended: true,
        },
        {
          title: "Wymiana muszli (kompleksowe)",
          steps: "1. Wyłączyć wodę\n2. Demontaż muszli\n3. Zainstalować nową\n4. Podłączyć wodę",
          laborCost: 250,
          materialCost: 400,
          durability: "10+ lat",
          difficulty: "Trudne",
        },
      ],
    },
    {
      detectedObjects: ["Zawias drzwiowy", "Drewno", "Drzwi"],
      damageType: "Wyrwanie zawiasu",
      damagedElement: "Zawias",
      damageSeverity: "poważny",
      confidence: 0.89,
      damageClass: "mechaniczne",
      damageClassConfidence: 0.92,
      description: "Zawias drzwiowy wyrwany ze swojego gniazda, widoczne uszkodzenie drewna",
      scenario: "Nagłe mocne szarpnięcie drzwi lub zły montaż zawiasu",
      repairOptions: [
        {
          title: "Wymiana zawiasu (szybka)",
          steps: "1. Zdjąć zawias\n2. Wywiercić nowe dziury\n3. Zainstalować nowy zawias",
          laborCost: 60,
          materialCost: 45,
          durability: "5 lat",
          difficulty: "Średnie",
        },
        {
          title: "Wzmocnienie i wymiana (rekomendowana)",
          steps: "1. Wzmocnić drewno kołkami\n2. Zainstalować zawias wyższej klasy\n3. Regulacja",
          laborCost: 120,
          materialCost: 80,
          durability: "10+ lat",
          difficulty: "Średnie",
          recommended: true,
        },
      ],
    },
  ];

  // Zwróć losową analizę (symulacja)
  return analyses[Math.floor(Math.random() * analyses.length)];
}

export const damageCategories = {
  Hydraulika: {
    color: "bg-blue-100 text-blue-800",
    icon: "💧",
  },
  Stolarka: {
    color: "bg-amber-100 text-amber-800",
    icon: "🪟",
  },
  Urządzenia: {
    color: "bg-red-100 text-red-800",
    icon: "⚡",
  },
  Wyposażenie: {
    color: "bg-purple-100 text-purple-800",
    icon: "🛋️",
  },
  Oświetlenie: {
    color: "bg-yellow-100 text-yellow-800",
    icon: "💡",
  },
  Inne: {
    color: "bg-gray-100 text-gray-800",
    icon: "❓",
  },
};

export function getDamageTypeColor(type) {
  const colors = {
    Przeciek: "bg-cyan-100 text-cyan-800",
    Pęknięcie: "bg-orange-100 text-orange-800",
    "Wyrwanie zawiasu": "bg-red-100 text-red-800",
    Zalanie: "bg-blue-100 text-blue-800",
    Spalony: "bg-red-900/20 text-red-900",
    Wilgoć: "bg-slate-100 text-slate-800",
  };
  return colors[type] || "bg-gray-100 text-gray-800";
}

export function getDamageClassLabel(damageClass) {
  return damageClass === "amortyzacyjne"
    ? "Uszkodzenie amortyzacyjne"
    : "Uszkodzenie mechaniczne";
}
