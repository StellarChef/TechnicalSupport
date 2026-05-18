// Mock `analyzeImageForDamage` usunięty — analizę robi teraz backend przez
// `POST /api/cases/create/` (patrz `src/api/cases.js`).
// Poniżej zostały tylko etykiety/kolory używane przez komponenty UI.

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
