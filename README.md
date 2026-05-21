# AI Technical Veryficator

Narzędzie wspomagające koordynatora technicznego w weryfikacji usterek w
apartamentach na wynajem krótkoterminowy (Airbnb, Booking). Koordynator dodaje
zgłoszenie ze zdjęciami, AI przepuszcza je przez 5-etapowy pipeline (vision +
text), zwraca klasyfikację uszkodzenia, propozycję naprawy i koszt. Koordynator
może zatwierdzić, skorygować lub poprosić o ponowną weryfikację z dodatkową
informacją. Zatwierdzone sprawy trafiają do bazy wiedzy i służą jako kontekst
dla kolejnych weryfikacji.

## Stack

| Warstwa  | Technologia |
|----------|-------------|
| Frontend | React 19 + Vite + Tailwind CSS 4 |
| Backend  | Django 6 + Django REST Framework |
| Baza danych | PostgreSQL 16 (klasyczny, bez rozszerzeń wektorowych) |
| AI / LLM | OpenAI GPT-4o (Vision + structured output) przez LangChain |
| Orchestracja | Docker Compose |

## Pipeline weryfikacji

5 etapów, jeden plik promptu na etap, wspólny `System_Prompt.txt`:

```
   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
   │ 1. Detect    │ →  │ 2. Classify  │ →  │ 3. Repair    │ →  │ 4. Cost      │ →  │ 5. Merge │
   │  element     │    │ mech/amort   │    │ specialist   │    │ estimator    │    │  (det.)  │
   └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────┘
        LLM                 LLM                 LLM                  LLM            deterministic
   detected_element    damage_cause          repair_steps          cost             aggregate
                       confidence            durability           {labor,
                       description           difficulty            materials,
                                                                   total}
```

- **Etapy 1–4** to wywołania LLM z `llm.with_structured_output(PydanticModel)`
  — brak ręcznego parsowania JSON, model dostaje schemat przez function calling.
  Każdy etap dostaje zdjęcia jako `image_url` content blocks (OpenAI Vision).
- **Etap 5** to deterministyczny merge dictów w Pythonie. Plik `Prompt_5.txt`
  istnieje jako dokumentacja schematu finalnego JSON, ale nie ma wywołania LLM —
  oszczędza koszt i ryzyko halucynacji "agregator zmienił wartości".
- `responsibility` (`tenant` / `owner` / `unresolved`) wyprowadzane jest
  deterministycznie z `damage_cause` poza promptami.

### Klasyfikacja mechaniczne vs amortyzacyjne

`System_Prompt.txt` definiuje kategorie, podaje przykłady i twarde reguły
przeciw biasowi (model lubił klasyfikować wszystko jako amortyzacja "bo wynajem
krótkoterminowy = duże zużycie"):

1. Widoczne pęknięcie/wyrwanie/wgniecenie → **zawsze mechaniczne**.
2. Wilgoć/zaciek/korozja bez pęknięć → amortyzacyjne.
3. Niejasne / niewidoczne → confidence < 60% i ostrożna decyzja.

### Photo upload + Vision

Frontend uploaduje zdjęcia przez `POST /api/upload-photo/`, plik trafia do
`MEDIA_ROOT/cases/` przez `default_storage`. Przy wywołaniu pipelinu backend
czyta plik z dysku i koduje base64 do `data:image/...;base64,...` — bo OpenAI
nie ma dostępu do naszego localhost/sieci dockera. Pliki >20 MB są pomijane.

### Knowledge Base

`KnowledgeBaseEntry` to zatwierdzona sprawa jako snapshot referencyjny.
Powstaje przy `POST /api/cases/<id>/approve/`. Przy każdym uruchomieniu
pipelinu (create + reverify) `_build_kb_context()` pobiera ostatnie 5 wpisów
i wstrzykuje je jako tekstowy kontekst w human message stepów 1 i 2.

Model uczy się z decyzji koordynatora bez kosztu fine-tuningu — przykładami
"tak wygląda przypadek który koordynator uznał za mechaniczne, mimo że
to bateria łazienkowa".

## API

| Metoda | Endpoint | Co robi |
|--------|----------|---------|
| GET    | `/api/cases/` | Lista wszystkich case'ów |
| POST   | `/api/cases/create/` | Uruchamia pipeline, zapisuje case do DB |
| POST   | `/api/cases/<id>/approve/` | Flip `approved=True`, snapshot do KB |
| POST   | `/api/cases/<id>/correct/` | Korekta koordynatora (responsibility, koszty, kategoria) |
| POST   | `/api/cases/<id>/reverify/` | Re-run pipeline z `additional_info` |
| POST   | `/api/verify-case/` | Pipeline w trybie preview (bez zapisu) |
| POST   | `/api/upload-photo/` | Upload multipart, zwraca URL do `media/` |

Pełne payloady i odpowiedzi: zobacz docstringi w
[`technical_veryfication_backend/app/api/views.py`](technical_veryfication_backend/app/api/views.py).

## Uruchamianie lokalne

### Wymagania
- Docker Desktop (Engine + Compose)
- Klucz OpenAI API

### Setup

```bash
# 1. Skopiuj .env.example do .env i uzupełnij sekrety
cp technical_veryfication_backend/app/.env.example .env
# Wpisz w .env:
#   DJANGO_SECRET_KEY=...
#   POSTGRES_PASSWORD=...
#   AI_API_KEY=sk-...

# 2. Postaw stack
docker compose up -d
```

Serwisy:
- Frontend: http://localhost:5173 (Vite dev)
- Backend:  http://localhost:8000/api/
- Postgres: localhost:5433 (mapping na hosta; w sieci dockera `db:5432`)

Migracje aplikują się automatycznie przy starcie backendu (`command:` w
[`docker-compose.yml`](docker-compose.yml)).

### Reset bazy (drop dane + ponowna migracja)

```bash
docker compose down -v
docker compose up -d
```

### Tester pipelinu bez backendu (symulacja)

```bash
cd technical_veryfication_backend/app
python -m prompts.tests.test_prompts
# z prawdziwym API: python -m prompts.tests.test_prompts --api
```

## Struktura projektu

```
.
├── .env.example                       # Konfiguracja środowiska (skopiuj jako .env)
├── docker-compose.yml                 # Trzy serwisy: db, backend, frontend
│
├── technical-cases-ui/                # Frontend (React + Vite)
│   └── src/
│       ├── api/cases.js               # Klient API (fetchCases, createCase, approve, …)
│       ├── components/
│       │   ├── badges/                # ApprovalBadge, ConfidenceBadge, ResponsibilityBadge
│       │   ├── dashboard/             # Kafelki KPI, filtry, tabela
│       │   ├── details/               # Drawer ze szczegółami case'a (approve, reverify, correction)
│       │   └── forms/                 # Nowe zgłoszenie + upload zdjęć
│       └── App.jsx                    # Root — fetchuje cases z backendu na starcie
│
└── technical_veryfication_backend/app/
    ├── api/
    │   ├── models.py                  # Case, CasePhoto, CaseHistoryEvent, KnowledgeBaseEntry
    │   ├── serializers.py             # CaseSerializer + request serializery
    │   ├── views.py                   # Endpointy REST (create, approve, correct, reverify, upload)
    │   ├── urls.py
    │   └── migrations/
    ├── prompts/
    │   ├── System_Prompt.txt          # Rola, definicje, reguły klasyfikacji
    │   ├── Prompt_1.txt … Prompt_5.txt
    │   ├── prompt_service.py          # PromptService — LangChain pipeline
    │   └── tests/test_prompts.py
    └── backend/
        ├── settings.py                # Postgres warunkowo na env; SQLite fallback
        └── urls.py                    # /api/ + media serving w dev
```

## Klasyfikacja danych i sekrety

- `.env` jest w `.gitignore` — sekrety produkcyjne (klucz Django, hasło DB,
  klucz OpenAI) nigdy nie trafiają do repo.
- `.env.example` służy jako szablon — każdy klucz ma 1-linijkowy komentarz
  (max 20 słów) opisujący do czego służy.
- Pliki uploadowane przez użytkowników (`MEDIA_ROOT/cases/`) też są ignorowane
  — w produkcji powinien to być wolumin / S3 / CDN, nie repo.

## Rozwijanie

### Frontend bez Dockera

```bash
cd technical-cases-ui
npm install
npm run dev
# Wymaga: backend działający na :8000 lub VITE_API_URL wskazujący na inny host.
```

### Backend bez Dockera

```bash
cd technical_veryfication_backend/app
python -m venv .venv
.venv\Scripts\activate           # Windows
# source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python manage.py migrate          # Domyślnie SQLite jeśli POSTGRES_DB nieustawione
python manage.py runserver
```

### Wymiana modelu / temperatury

```env
AI_MODEL=gpt-4o-mini       # tańsza alternatywa (domyślnie gpt-4o)
AI_TEMPERATURE=0.0         # bardziej deterministycznie
```

## Decyzje projektowe

- **Klasyczny Postgres, nie pgvector** — KB działa na zwykłych kolumnach +
  prosty fetch po `created_at`. Bez wektorów wymiarowych, bez embeddingów.
  Wystarcza dla kilkudziesięciu wpisów; gdyby KB urosło do tysięcy, można
  dorobić pgvector / Elasticsearch bez zmiany API.
- **Brak fine-tuningu** — `KnowledgeBaseEntry` daje efekt uczenia per-organizacja
  bez retraining modelu. Decyzje koordynatora wpływają na kolejne weryfikacje
  od razu, bez czekania na nowy model.
- **Aggregator (etap 5) bez LLM** — sklejenie 4 odpowiedzi jest deterministyczne,
  wywołanie modelu tylko po to dodawałoby koszt i ryzyko że coś przekręci.
- **`responsibility` poza promptami** — mapowanie `mechaniczne→tenant,
  amortyzacyjne→owner` to czysta reguła biznesowa, nie wymaga LLM.
- **Mail tylko jako draft** — system generuje treść maila, wysyłka idzie
  innym kanałem. Dlatego nie ma pola `mail.status` ani logiki sent/draft.
