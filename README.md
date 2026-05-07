# AI Technical Verificator

Aplikacja do weryfikacji spraw technicznych w mieszkaniach przeznaczonych na wynajem krótkoterminowy.

## Architektura

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Django REST Framework + Python
- **AI Processing**: Prompt-based damage analysis and cost estimation

## Uruchamianie

```bash
# Uruchom wszystkie serwisy
docker compose up --build

# Frontend będzie dostępny na http://localhost:5173
# Backend API na http://localhost:8000/api/
```

## API Endpoints

### POST `/api/create-case/`

Tworzy nowe zgłoszenie techniczne z pełną analizą AI.

**Request Body:**
```json
{
  "title": "Uszkodzona bateria w łazience",
  "photos": ["https://example.com/photo1.jpg"],
  "damage_description": "Bateria przecieka przy podstawie",
  "search_results": "opcjonalne wyniki wyszukiwania kosztów"
}
```

**Response:**
```json
{
  "case": {
    "id": "CASE-2026-ABCD",
    "title": "Uszkodzona bateria w łazience",
    "createdAt": "2026-05-07T10:30:00Z",
    "status": "ai_review",
    "damageDescription": "Bateria łazienkowa przecieka przy podstawie i powoduje zalewanie blatu.",
    "repairDescription": "Sprawdź uszczelnienia, wymień uszczelkę lub baterię i przetestuj szczelność pod ciśnieniem.",
    "photos": [...],
    "aiClassification": {...},
    "responsibility": "owner",
    "cost": {...},
    "mail": {...},
    "feedback": {...},
    "history": [...]
  },
  "verification_result": {...},
  "cost_estimation": {...}
}
```

### Inne Endpoints

- `POST /api/verify-case/` - Tylko weryfikacja uszkodzeń
- `POST /api/estimate-cost/` - Tylko estymacja kosztów
- `POST /api/classify-case/` - Połączona weryfikacja + koszty

## Struktura Projektu

```
.
├── technical-cases-ui/          # Frontend React
├── technical_veryfication_backend/app/  # Backend Django
│   ├── api/                     # REST API
│   ├── prompts/                 # AI Prompts
│   └── backend/                 # Django settings
├── docker-compose.yml
└── .env
```

## Development

### Frontend
```bash
cd technical-cases-ui
npm install
npm run dev
```

### Backend
```bash
cd technical_veryfication_backend/app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
