export const initialCases = [
  {
    id: "CASE-2026-0001",
    title: "Uszkodzona bateria w łazience",
    createdAt: "2026-05-01T12:30:00Z",
    status: "ai_review",
    damageDescription:
      "Bateria łazienkowa przecieka przy podstawie i powoduje zalewanie blatu.",
    repairDescription:
      "Wymiana uszczelki lub całej baterii po weryfikacji przez serwisanta.",
    photos: [
      {
        id: "photo_01",
        url: "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?q=80&w=1200&auto=format&fit=crop",
        isMain: true,
      },
    ],
    aiClassification: {
      category: "Hydraulika",
      damageType: "Przeciek",
      confidence: 0.87,
      suggestedResponsibility: "owner",
      suggestedRepair: "Wymiana uszczelki lub baterii",
      suggestedLaborCost: 180,
      suggestedMaterialCost: 120,
    },
    responsibility: "owner",
    cost: {
      labor: 180,
      materials: 120,
      total: 300,
      currency: "PLN",
    },
    mail: {
      shouldGenerate: true,
      template: "owner_repair_notice",
      status: "draft",
    },
    feedback: {
      aiHelpful: null,
      rating: null,
      comment: null,
    },
    history: [
      {
        type: "created",
        label: "Utworzono zgłoszenie",
        createdAt: "2026-05-01T12:30:00Z",
        createdBy: "Maciej",
      },
      {
        type: "ai_classified",
        label: "AI sklasyfikowało zgłoszenie",
        createdAt: "2026-05-01T12:32:00Z",
        createdBy: "AI",
      },
    ],
  },
  {
    id: "CASE-2026-0002",
    title: "Pęknięta szyba balkonowa",
    createdAt: "2026-05-01T13:00:00Z",
    status: "verification",
    damageDescription:
      "Na szybie balkonowej widoczne jest pęknięcie w dolnej części tafli.",
    repairDescription:
      "Wymiana szyby po oględzinach i potwierdzeniu przyczyny uszkodzenia.",
    photos: [
      {
        id: "photo_01",
        url: "https://images.unsplash.com/photo-1513694203232-719a280e022f?q=80&w=1200&auto=format&fit=crop",
        isMain: true,
      },
    ],
    aiClassification: {
      category: "Stolarka",
      damageType: "Pęknięcie",
      confidence: 0.62,
      suggestedResponsibility: "unresolved",
      suggestedRepair: "Wymiana szyby po oględzinach",
      suggestedLaborCost: 250,
      suggestedMaterialCost: 400,
    },
    responsibility: "unresolved",
    cost: {
      labor: 250,
      materials: 400,
      total: 650,
      currency: "PLN",
    },
    mail: {
      shouldGenerate: true,
      template: "issue_verification_request",
      status: "draft",
    },
    feedback: {
      aiHelpful: null,
      rating: null,
      comment: null,
    },
    history: [
      {
        type: "created",
        label: "Utworzono zgłoszenie",
        createdAt: "2026-05-01T13:00:00Z",
        createdBy: "Maciej",
      },
    ],
  },
  {
    id: "CASE-2026-0003",
    title: "Zatkany odpływ w kuchni",
    createdAt: "2026-04-30T09:15:00Z",
    status: "closed",
    damageDescription:
      "Odpływ w zlewie kuchennym jest zatkany i woda spływa bardzo wolno.",
    repairDescription: "Udrożnienie odpływu i oczyszczenie syfonu.",
    photos: [
      {
        id: "photo_01",
        url: "https://images.unsplash.com/photo-1556911220-bff31c812dba?q=80&w=1200&auto=format&fit=crop",
        isMain: true,
      },
    ],
    aiClassification: {
      category: "Hydraulika",
      damageType: "Zator",
      confidence: 0.91,
      suggestedResponsibility: "tenant",
      suggestedRepair: "Udrożnienie odpływu",
      suggestedLaborCost: 150,
      suggestedMaterialCost: 0,
    },
    responsibility: "tenant",
    cost: {
      labor: 150,
      materials: 0,
      total: 150,
      currency: "PLN",
    },
    mail: {
      shouldGenerate: false,
      template: null,
      status: null,
    },
    feedback: {
      aiHelpful: "partially",
      rating: 4,
      comment: "AI dobrze rozpoznało kategorię.",
    },
    history: [
      {
        type: "created",
        label: "Utworzono zgłoszenie",
        createdAt: "2026-04-30T09:15:00Z",
        createdBy: "Maciej",
      },
      {
        type: "closed",
        label: "Zamknięto sprawę",
        createdAt: "2026-04-30T12:00:00Z",
        createdBy: "System",
      },
    ],
  },
];

export const statusLabels = {
  draft: "Szkic",
  submitted: "Wysłane",
  ai_processing: "Analiza AI",
  ai_review: "Do weryfikacji AI",
  correction_needed: "Wymaga korekty",
  pending_owner: "Oczekuje na właściciela",
  pending_tenant: "Oczekuje na najemcę",
  verification: "Weryfikacja",
  approved: "Zatwierdzone",
  in_repair: "W naprawie",
  closed: "Zamknięte",
  rejected: "Odrzucone",
};

export const responsibilityLabels = {
  owner: "Właściciel",
  tenant: "Najemca",
  unresolved: "Nierozstrzygnięte",
};