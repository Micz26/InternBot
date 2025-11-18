# Dokumentacja Techniczna InternBot

## Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Architektura Systemu](#architektura-systemu)
3. [Stack Technologiczny](#stack-technologiczny)
4. [Struktura Projektu](#struktura-projektu)
5. [Moduły Backendu](#moduły-backendu)
6. [Moduły Frontendu](#moduły-frontendu)
7. [Baza Danych](#baza-danych)
8. [API Endpoints](#api-endpoints)
9. [Konfiguracja](#konfiguracja)
10. [Setup i Instalacja](#setup-i-instalacja)
11. [Deployment](#deployment)
12. [Bezpieczeństwo](#bezpieczeństwo)

---

## Wprowadzenie

**InternBot** to inteligentny asystent AI dedykowany rekomendacji staży i praktyk dla studentów. System wykorzystuje zaawansowane techniki przetwarzania języka naturalnego oraz wyszukiwanie semantyczne w bazie danych wektorowej do znajdowania najbardziej odpowiednich ofert stażowych na podstawie preferencji użytkownika.

### Główne Funkcjonalności

- **Interfejs konwersacyjny**: Naturalna komunikacja z użytkownikiem w języku polskim
- **Wyszukiwanie semantyczne**: Wykorzystanie embeddingów do znajdowania podobnych ofert
- **Automatyczne zbieranie danych**: Scraping ofert z wielu źródeł (PWR, Nokia, SII)
- **Geolokalizacja**: Personalizacja odpowiedzi w kontekście lokalizacji użytkownika
- **Aktualizacja danych**: Automatyczne codzienne aktualizowanie bazy ofert

---

## Architektura Systemu

System InternBot składa się z trzech głównych warstw:

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                       │
│  React + TypeScript + Tailwind CSS                      │
│  - Interfejs użytkownika                                │
│  - Komunikacja z API                                    │
│  - Zarządzanie stanem sesji                            │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────────┐
│                    BACKEND LAYER                         │
│  FastAPI + LangChain + LangGraph                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   API Layer  │  │  Agent Layer  │  │ Data Manager │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                  │          │
│  ┌──────▼─────────────────▼──────────────────▼───────┐ │
│  │         Data Scraper + Scheduler                   │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │ SQL + Vector Operations
┌──────────────────▼──────────────────────────────────────┐
│                  DATABASE LAYER                          │
│  PostgreSQL + pgvector                                  │
│  - Tabela ofert                                         │
│  - Wektory embeddingów (1536 wymiarów)                  │
│  - Indeksy wektorowe (IVFFlat)                          │
└──────────────────────────────────────────────────────────┘
```

### Przepływ Danych

1. **Użytkownik** wysyła zapytanie przez interfejs frontendu
2. **Frontend** przekazuje zapytanie do API backendu wraz z lokalizacją geograficzną
3. **API** przekazuje zapytanie do agenta LangGraph
4. **Agent** analizuje zapytanie i wywołuje odpowiednie narzędzia (tools)
5. **DataManager** wykonuje wyszukiwanie semantyczne w bazie danych
6. **Baza danych** zwraca najbardziej podobne oferty
7. **Agent** formatuje odpowiedź i zwraca do API
8. **API** przekazuje odpowiedź do frontendu
9. **Frontend** renderuje odpowiedź w interfejsie użytkownika

---

## Stack Technologiczny

### Backend

| Technologia | Wersja | Zastosowanie |
|------------|--------|--------------|
| Python | 3.10+ | Język programowania |
| FastAPI | 0.112.2 | Framework webowy |
| LangChain | 0.3.9 | Framework AI/LLM |
| LangGraph | - | Graf stanów dla agenta |
| LangChain OpenAI | 0.2.10 | Integracja z GPT-4 |
| PostgreSQL | 16 | Baza danych relacyjna |
| pgvector | - | Rozszerzenie wektorowe |
| psycopg2 | - | Adapter PostgreSQL |
| BeautifulSoup4 | - | Parsowanie HTML |
| Selenium | - | Web scraping |
| APScheduler | - | Harmonogram zadań |
| Pydantic | - | Walidacja danych |
| Uvicorn | - | Serwer ASGI |

### Frontend

| Technologia | Wersja | Zastosowanie |
|------------|--------|--------------|
| React | 18.2.0 | Framework UI |
| TypeScript | 5.2.2 | Typowanie statyczne |
| Vite | 4.5.0 | Build tool |
| Tailwind CSS | 3.3.5 | Framework CSS |
| Axios | 1.6.0 | Klient HTTP |
| React Markdown | 9.0.1 | Renderowanie Markdown |
| Lucide React | 0.294.0 | Ikony |
| UUID | 9.0.1 | Generowanie ID sesji |

### Infrastruktura

| Technologia | Zastosowanie |
|------------|--------------|
| Docker | Konteneryzacja |
| Docker Compose | Orchestracja kontenerów |
| Nginx | Reverse proxy (produkcja) |
| PostgreSQL | Baza danych |

---

## Struktura Projektu

```
InternBot/
├── backend/                          # Aplikacja backendowa
│   ├── src/
│   │   └── intern_bot/
│   │       ├── agent/                # Moduł agenta AI
│   │       │   ├── agent.py         # Implementacja agenta LangGraph
│   │       │   └── __init__.py
│   │       ├── api/                  # Warstwa API
│   │       │   ├── api.py            # Główna aplikacja FastAPI
│   │       │   └── utils/
│   │       │       ├── routes.py     # Definicje endpointów
│   │       │       ├── models.py     # Modele Pydantic
│   │       │       └── scheduler.py  # Harmonogram zadań
│   │       ├── data_manager/         # Zarządzanie danymi
│   │       │   ├── data_manager.py   # Operacje na bazie danych
│   │       │   └── __init__.py
│   │       ├── data_scraper/         # Scraping danych
│   │       │   ├── data_scraper.py   # Główny moduł scrapingu
│   │       │   └── scrapers/
│   │       │       ├── base_scraper.py    # Klasa bazowa
│   │       │       ├── pwr_scraper.py     # Scraper PWR
│   │       │       ├── nokia_scraper.py   # Scraper Nokia
│   │       │       └── sii_scraper.py     # Scraper SII
│   │       └── settings/              # Konfiguracja
│   │           └── settings.py       # Ustawienia aplikacji
│   ├── scripts/
│   │   └── evaluate.py               # Skrypty ewaluacji
│   ├── Dockerfile                    # Obraz Docker backendu
│   └── pyproject.toml                # Konfiguracja projektu Python
│
├── frontend/                         # Aplikacja frontendowa
│   ├── src/
│   │   ├── components/               # Komponenty React
│   │   │   ├── Toast.tsx             # System powiadomień
│   │   │   └── PasswordModal.tsx     # Modal hasła (dev)
│   │   ├── views/                    # Widoki
│   │   │   └── Chat.tsx              # Główny widok czatu
│   │   ├── services/                 # Serwisy
│   │   │   └── chatService.ts        # Komunikacja z API
│   │   ├── hooks/                    # React hooks
│   │   │   └── useAuth.ts            # Hook autoryzacji
│   │   ├── lib/                      # Biblioteki pomocnicze
│   │   │   └── consts.ts             # Stałe aplikacji
│   │   ├── App.tsx                   # Główny komponent
│   │   └── main.tsx                  # Punkt wejścia
│   ├── Dockerfile                    # Obraz Docker frontendu
│   ├── vite.config.ts                # Konfiguracja Vite
│   ├── tailwind.config.js            # Konfiguracja Tailwind
│   └── package.json                  # Zależności Node.js
│
├── postgres/
│   └── schema.sql                    # Schemat bazy danych
│
├── docker-compose.yml                # Konfiguracja Docker Compose
├── config.env                        # Zmienne środowiskowe
└── README.md                         # Dokumentacja użytkownika
```

---

## Moduły Backendu

### 1. Moduł Agent (`agent/`)

Moduł agenta implementuje inteligentnego asystenta wykorzystującego LangGraph do zarządzania konwersacją i wywoływania narzędzi.

#### Komponenty

**`agent.py`** - Główny moduł agenta:

- **Model LLM**: GPT-4-turbo-mini z temperaturą 0 dla deterministycznych odpowiedzi
- **Graf stanów**: Prosty graf z jednym węzłem `chatbot`
- **Narzędzia (Tools)**:
  - `retrieve_offers`: Wyszukiwanie ofert na podstawie podobieństwa semantycznego
  - `get_offer_details`: Pobieranie szczegółów konkretnej oferty
- **Checkpointer**: InMemorySaver do zarządzania kontekstem konwersacji
- **System Prompt**: Instrukcje dla agenta dotyczące formatowania odpowiedzi i użycia narzędzi

#### Przepływ Pracy Agenta

1. Agent otrzymuje zapytanie użytkownika
2. Analizuje zapytanie i decyduje, czy użyć narzędzi
3. Jeśli potrzebne, wywołuje `retrieve_offers` z parametrami:
   - `internship_info`: Opis wyszukiwanej oferty
   - `include_companies`: Lista firm do uwzględnienia (opcjonalne)
   - `exclude_companies`: Lista firm do wykluczenia (opcjonalne)
   - `limit`: Liczba wyników (domyślnie 5)
   - `offset`: Przesunięcie dla paginacji
4. Wyniki są przetwarzane i formatowane w odpowiedź
5. Agent może wykonać maksymalnie 3 iteracje z użyciem narzędzi

### 2. Moduł API (`api/`)

Moduł API zapewnia interfejs REST do komunikacji z frontendem.

#### Komponenty

**`api.py`** - Główna aplikacja FastAPI:

- Inicjalizacja aplikacji z lifecycle hooks
- Konfiguracja CORS dla frontendu
- Integracja routerów

**`routes.py`** - Definicje endpointów:

- `POST /agent/invoke`: Wywołanie agenta z zapytaniem
- `POST /agent/stream`: Streamowanie odpowiedzi agenta (SSE)
- `POST /scrape/data`: Ręczne uruchomienie scrapingu
- `GET /data/info`: Informacje o stanie danych
- `GET /data/current_offers`: Lista wszystkich ofert
- `GET /scheduler/status`: Status harmonogramu zadań

**`scheduler.py`** - Harmonogram zadań:

- APScheduler z AsyncIOScheduler
- Codzienne zadanie scrapingu o godzinie 2:00
- Równoległe przetwarzanie źródeł (ThreadPoolExecutor)
- Automatyczne usuwanie przestarzałych ofert

**`models.py`** - Modele Pydantic:

- `AgentInput`: Model wejściowy dla agenta
- `AgentConfig`: Konfiguracja agenta (thread_id)

### 3. Moduł Data Manager (`data_manager/`)

Moduł zarządzania danymi odpowiada za wszystkie operacje na bazie danych.

#### Główne Funkcje

**`data_manager.py`**:

- **`similarity_search_cosine`**: Wyszukiwanie semantyczne z wykorzystaniem podobieństwa cosinusowego
  - Parametry: query, k (liczba wyników), offset, include_filters, exclude_filters
  - Wykorzystuje operatory pgvector (`<=>`)
  - Obsługuje filtry na kolumnach: company, location, contract_type, source
  
- **`add_offer`**: Dodawanie pojedynczej oferty
  - Automatyczne generowanie embeddingu dla opisu
  - Wykorzystanie OpenAIEmbeddings (1536 wymiarów)
  
- **`add_offers`**: Masowe dodawanie ofert
  
- **`get_offer`**: Pobieranie szczegółów oferty po linku
  
- **`get_current_offers`**: Pobieranie wszystkich ofert
  
- **`get_current_offers_links`**: Pobieranie listy linków ofert
  
- **`remove_offer`**: Usuwanie oferty
  
- **`diff_offers`**: Porównanie list ofert (nowe/usunięte)
  
- **`get_outdated_offers`**: Pobieranie przestarzałych ofert (date_closing < dzisiaj)
  
- **`create_vector_index`**: Tworzenie indeksu IVFFlat dla szybkiego wyszukiwania

#### Optymalizacje

- Indeks IVFFlat z 100 listami dla szybkiego wyszukiwania wektorowego
- Connection pooling przez psycopg2
- Batch operations dla masowego dodawania ofert

### 4. Moduł Data Scraper (`data_scraper/`)

Moduł scrapingu automatycznie zbiera oferty z różnych źródeł.

#### Architektura

**`data_scraper.py`** - Główny moduł:

- Fabryka scraperów dla różnych źródeł
- Równoległe przetwarzanie ofert (ThreadPoolExecutor, max_workers=5)
- Obsługa błędów i logowanie

**`scrapers/base_scraper.py`** - Klasa abstrakcyjna:

- Definiuje interfejs dla wszystkich scraperów
- Metody abstrakcyjne:
  - `scrape_offers()`: Pobieranie listy linków ofert
  - `scrape_offer_details()`: Pobieranie szczegółów oferty

**Implementacje scraperów**:

- **`pwr_scraper.py`**: Scraping z portalu Politechniki Wrocławskiej
- **`nokia_scraper.py`**: Scraping z portalu karier Nokia
- **`sii_scraper.py`**: Scraping z portalu karier SII Polska

#### Proces Scrapingu

1. Pobranie listy aktualnych linków z bazy danych
2. Scraping nowych linków ze źródła
3. Porównanie list (diff) - identyfikacja nowych i usuniętych ofert
4. Usunięcie przestarzałych ofert z bazy
5. Równoległe pobieranie szczegółów nowych ofert
6. Generowanie embeddingów i dodanie do bazy danych

### 5. Moduł Settings (`settings/`)

Centralne zarządzanie konfiguracją aplikacji.

**`settings.py`**:

- Pydantic Settings dla walidacji zmiennych środowiskowych
- Sekretne wartości (SecretStr) dla haseł i kluczy API
- Konfiguracja z pliku `.env`

#### Zmienne Środowiskowe

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=internbot
DB_USER=postgres
DB_PASSWORD=...

# Server
SERVER_IP=localhost
FRONTEND_PORT=3000

# Optional
OFFERS_TABLE_NAME=offers
```

---

## Moduły Frontendu

### 1. Komponent Chat (`views/Chat.tsx`)

Główny komponent interfejsu użytkownika implementujący interfejs konwersacyjny.

#### Funkcjonalności

- **Zarządzanie wiadomościami**: Stan historii konwersacji
- **Geolokalizacja**: Automatyczne pobieranie lokalizacji użytkownika
- **Renderowanie Markdown**: Formatowanie odpowiedzi agenta
- **Automatyczne przewijanie**: Do najnowszej wiadomości
- **Wskaźniki ładowania**: Wizualna informacja o przetwarzaniu
- **Obsługa błędów**: Wyświetlanie komunikatów błędów przez Toast

#### Struktura Komponentu

```typescript
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}
```

### 2. Serwis Chat (`services/chatService.ts`)

Serwis komunikacji z backendem.

#### Funkcjonalności

- **`sendMessage`**: Wysyłanie zapytania do API
- **Zarządzanie sesją**: Generowanie i przechowywanie `thread_id` w sessionStorage
- **Obsługa lokalizacji**: Przekazywanie współrzędnych geograficznych
- **Obsługa błędów**: Przechwytywanie i propagacja błędów

#### Implementacja Thread ID

```typescript
const getThreadId = (): string => {
  const storageKey = 'internbot_thread_id';
  let threadId = sessionStorage.getItem(storageKey);
  
  if (!threadId) {
    threadId = uuidv4();
    sessionStorage.setItem(storageKey, threadId);
  }
  
  return threadId;
};
```

### 3. System Powiadomień (`components/Toast.tsx`)

Globalny system powiadomień wykorzystujący React Context.

#### Typy Powiadomień

- `success`: Sukces operacji
- `error`: Błąd
- `warning`: Ostrzeżenie
- `info`: Informacja

#### Funkcjonalności

- Automatyczne znikanie po określonym czasie (domyślnie 5s)
- Możliwość ręcznego zamknięcia
- Animacje pojawiania się i znikania
- Kolejkowanie wielu powiadomień

### 4. Hook Autoryzacji (`hooks/useAuth.ts`)

Zarządzanie stanem autoryzacji użytkownika.

#### Funkcjonalności

- Sprawdzanie statusu autoryzacji z localStorage
- Funkcje `authenticate()` i `logout()`
- Stan ładowania podczas inicjalizacji

### 5. Konfiguracja (`lib/consts.ts`)

Centralne definicje stałych aplikacji.

```typescript
export const BACKEND_URL = import.meta.env?.VITE_BACKEND_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  AGENT_INVOKE: '/agent/invoke',
  AGENT_STREAM: '/agent/stream',
  SCRAPE_DATA: '/scrape/data',
} as const;
```

### 6. Stylizacja

**Tailwind CSS**:
- Utility-first approach
- Niestandardowe kolory (primary, secondary)
- Animacje (fade-in, slide-up)
- Responsywny design

**App.css**:
- Globalne style
- Niestandardowe scrollbary
- Animacje keyframes
- Style focus

---

## Baza Danych

### Schemat

```sql
CREATE TABLE offers (
  id SERIAL PRIMARY KEY,
  link TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  company TEXT,
  location TEXT,
  contract_type TEXT,
  date_posted DATE,
  date_closing DATE,
  source TEXT,
  description TEXT,
  embedding vector(1536)
);
```

### Rozszerzenia

- **pgvector**: Rozszerzenie PostgreSQL do obsługi wektorów
- **IVFFlat Index**: Indeks dla szybkiego wyszukiwania podobieństwa cosinusowego

### Operacje Wektorowe

- **`<=>`**: Operator podobieństwa cosinusowego
- **Embeddingi**: 1536-wymiarowe wektory generowane przez OpenAI
- **Indeksowanie**: IVFFlat z 100 listami dla optymalizacji

### Zarządzanie Danymi

- **Aktualizacja**: Codzienne automatyczne aktualizowanie o 2:00
- **Czyszczenie**: Automatyczne usuwanie przestarzałych ofert
- **Deduplikacja**: Unikalność ofert na podstawie linku

---

## API Endpoints

### Agent Endpoints

#### `POST /agent/invoke`

Wywołanie agenta z zapytaniem użytkownika.

**Request Body**:
```json
{
  "query": "Znajdź mi staże związane z programowaniem w Pythonie",
  "config": {
    "configurable": {
      "thread_id": "uuid-sesji"
    }
  },
  "location": {
    "lat": 50.0647,
    "lng": 19.9450
  }
}
```

**Response**:
```json
[
  {
    "content": "Odpowiedź agenta...",
    "additional_kwargs": {}
  }
]
```

#### `POST /agent/stream`

Streamowanie odpowiedzi agenta (Server-Sent Events).

**Response**: `text/event-stream`
```
data: {"content": "Część odpowiedzi..."}

data: {"content": "Kolejna część..."}
```

### Data Endpoints

#### `POST /scrape/data`

Ręczne uruchomienie zadania scrapingu.

**Response**:
```json
{
  "message": "Test scraping completed successfully"
}
```

#### `GET /data/info`

Informacje o stanie danych w bazie.

**Response**:
```json
{
  "message": "123 offers in vector database"
}
```

#### `GET /data/current_offers`

Lista wszystkich ofert w bazie danych.

**Response**:
```json
{
  "message": [
    {
      "id": 1,
      "link": "https://...",
      "title": "Staż w programowaniu",
      "company": "Nokia",
      ...
    }
  ]
}
```

### Scheduler Endpoints

#### `GET /scheduler/status`

Status harmonogramu zadań.

**Response**:
```json
{
  "scheduler_running": true,
  "jobs": [
    {
      "id": "daily_scraping",
      "name": "Daily Data Scraping",
      "next_run_time": "2024-01-20T02:00:00",
      "trigger": "cron[hour='2', minute='0']"
    }
  ]
}
```

---

## Konfiguracja

### Plik `config.env`

Centralny plik konfiguracyjny dla całego projektu.

```env
# Server Configuration
SERVER_IP=localhost
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Backend URL
VITE_BACKEND_URL=http://localhost:8000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
DB_NAME=internbot

# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Optional
OFFERS_TABLE_NAME=offers
```

### Docker Compose

Plik `docker-compose.yml` definiuje trzy serwisy:

1. **db**: PostgreSQL z pgvector
2. **backend**: Aplikacja FastAPI
3. **frontend**: Aplikacja React (Nginx)

### Zmienne Środowiskowe w Docker

Zmienne są przekazywane do kontenerów przez sekcję `environment` w docker-compose.yml.

---

## Setup i Instalacja

### Wymagania Wstępne

Przed rozpoczęciem instalacji upewnij się, że masz zainstalowane:

- **Docker** (wersja 20.10 lub nowsza)
- **Docker Compose** (wersja 2.0 lub nowsza)
- **Git** (do klonowania repozytorium)
- **Klucz API OpenAI** (dla funkcjonalności AI)

#### Sprawdzenie Wymagań

```bash
# Sprawdź wersję Docker
docker --version

# Sprawdź wersję Docker Compose
docker-compose --version

# Sprawdź wersję Git
git --version
```

### Szybki Start

#### Krok 1: Klonowanie Repozytorium

```bash
git clone <repository-url>
cd InternBot
```

#### Krok 2: Uzyskanie Klucza API OpenAI

1. Przejdź na stronę [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Zaloguj się lub utwórz konto
3. Kliknij "Create new secret key"
4. Skopiuj klucz API (zaczyna się od `sk-proj-`)

**Uwaga**: Klucz API jest widoczny tylko raz. Zapisz go w bezpiecznym miejscu.

#### Krok 3: Konfiguracja Środowiska

##### Opcja A: Automatyczna Konfiguracja (Rekomendowana)

Użyj skryptu setup, który automatycznie utworzy potrzebne pliki:

```bash
chmod +x setup.sh
./setup.sh
```

Skrypt automatycznie:
- Utworzy plik `backend/.env` z szablonem konfiguracji
- Utworzy plik `frontend/.env.local` z konfiguracją frontendu
- Załaduje konfigurację z `config.env` (jeśli istnieje)

##### Opcja B: Ręczna Konfiguracja

**Backend** - Utwórz plik `backend/.env`:

```bash
cd backend
cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-actual-openai-api-key-here

# Database Configuration
DB_HOST=db
DB_PORT=5432
DB_NAME=internbot
DB_USER=postgres
DB_PASSWORD=password

# Optional: Table name
OFFERS_TABLE_NAME=offers

# Server Configuration
SERVER_IP=localhost
FRONTEND_PORT=3000
EOF
```

**Frontend** - Utwórz plik `frontend/.env.local`:

```bash
cd frontend
cat > .env.local << EOF
VITE_BACKEND_URL=http://localhost:8000
VITE_NODE_ENV=development
EOF
```

**Konfiguracja Serwera** (opcjonalnie) - Utwórz plik `config.env` w głównym katalogu:

```bash
cat > config.env << EOF
# Server Configuration
SERVER_IP=localhost
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Backend URL
VITE_BACKEND_URL=http://localhost:8000
EOF
```

#### Krok 4: Uruchomienie Aplikacji

##### Tryb Produkcyjny (Docker Compose)

```bash
# Z głównego katalogu projektu
docker-compose up --build
```

Aplikacja będzie dostępna pod adresami:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Dokumentacja**: http://localhost:8000/docs

##### Tryb Deweloperski

Dla rozwoju lokalnego możesz uruchomić poszczególne komponenty osobno:

**Backend** (lokalnie, bez Dockera):

```bash
cd backend
pip install -e .
uvicorn intern_bot.api.api:app --reload --host 0.0.0.0 --port 8000
```

**Frontend** (lokalnie, bez Dockera):

```bash
cd frontend
npm install
npm run dev
```

**Baza danych** (tylko Docker):

```bash
docker-compose up db
```

### Weryfikacja Instalacji

#### Sprawdzenie Statusu Kontenerów

```bash
docker-compose ps
```

Wszystkie serwisy powinny być w stanie "Up".

#### Sprawdzenie Logów

```bash
# Wszystkie serwisy
docker-compose logs -f

# Tylko backend
docker-compose logs -f backend

# Tylko frontend
docker-compose logs -f frontend

# Tylko baza danych
docker-compose logs -f db
```

#### Test Połączenia z API

```bash
# Sprawdź status API
curl http://localhost:8000/data/info

# Sprawdź status schedulera
curl http://localhost:8000/scheduler/status
```

#### Test Frontendu

Otwórz przeglądarkę i przejdź do http://localhost:3000. Powinien pojawić się interfejs czatu.

### Rozwiązywanie Problemów

#### Problem: Błąd "Invalid API key"

**Przyczyna**: Nieprawidłowy lub brakujący klucz API OpenAI.

**Rozwiązanie**:
1. Sprawdź, czy plik `backend/.env` istnieje
2. Upewnij się, że klucz API jest poprawny i zaczyna się od `sk-proj-`
3. Zrestartuj kontener backendu: `docker-compose restart backend`

#### Problem: Błąd połączenia z bazą danych

**Przyczyna**: Baza danych nie jest uruchomiona lub nieprawidłowe dane dostępowe.

**Rozwiązanie**:
1. Sprawdź, czy kontener bazy danych jest uruchomiony: `docker-compose ps db`
2. Sprawdź logi bazy danych: `docker-compose logs db`
3. Upewnij się, że dane w `backend/.env` są zgodne z `docker-compose.yml`
4. Zrestartuj wszystkie serwisy: `docker-compose down && docker-compose up --build`

#### Problem: Frontend nie łączy się z backendem

**Przyczyna**: Nieprawidłowa konfiguracja URL backendu lub problemy z CORS.

**Rozwiązanie**:
1. Sprawdź zmienną `VITE_BACKEND_URL` w `frontend/.env.local`
2. Sprawdź, czy backend działa: `curl http://localhost:8000/data/info`
3. Sprawdź konfigurację CORS w `backend/src/intern_bot/api/api.py`
4. Sprawdź logi przeglądarki (F12) pod kątem błędów CORS

#### Problem: Baza danych nie ma rozszerzenia pgvector

**Przyczyna**: Schemat bazy danych nie został zainicjalizowany.

**Rozwiązanie**:
1. Sprawdź, czy plik `postgres/schema.sql` jest poprawnie zamontowany w docker-compose.yml
2. Sprawdź logi bazy danych podczas startu
3. Ręcznie wykonaj schemat:

```bash
docker-compose exec db psql -U postgres -d internbot -f /docker-entrypoint-initdb.d/schema.sql
```

#### Problem: Kontenery nie startują

**Przyczyna**: Porty są już zajęte lub problemy z Dockerem.

**Rozwiązanie**:
1. Sprawdź, czy porty 3000, 8000, 5432 są wolne:
   ```bash
   # Linux/Mac
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   
   # Windows
   netstat -ano | findstr :3000
   ```
2. Zatrzymaj inne aplikacje używające tych portów
3. Sprawdź status Dockera: `docker info`
4. Zrestartuj Docker Desktop (jeśli używasz)

### Pierwsze Uruchomienie Scrapingu

Po pierwszym uruchomieniu aplikacji, baza danych będzie pusta. Aby wypełnić ją danymi:

#### Opcja 1: Automatyczne (Rekomendowane)

Poczekaj do 2:00 rano, kiedy scheduler automatycznie uruchomi scraping.

#### Opcja 2: Ręczne Uruchomienie

```bash
# Przez API
curl -X POST http://localhost:8000/scrape/data

# Lub przez Docker
docker-compose exec backend python -c "from intern_bot.api.utils.scheduler import run_daily_scraping; run_daily_scraping()"
```

**Uwaga**: Pierwszy scraping może zająć kilka minut, w zależności od liczby ofert.

### Konfiguracja Zaawansowana

#### Zmiana Portów

Edytuj plik `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Zmień 8000 na 8001
  frontend:
    ports:
      - "3001:80"    # Zmień 3000 na 3001
  db:
    ports:
      - "5433:5432"  # Zmień 5432 na 5433
```

#### Zmiana Harmonogramu Scrapingu

Edytuj plik `backend/src/intern_bot/api/utils/scheduler.py`:

```python
scheduler.add_job(
    run_daily_scraping,
    trigger=CronTrigger(hour=2, minute=0),  # Zmień godzinę/minutę
    id='daily_scraping',
    name='Daily Data Scraping',
    replace_existing=True
)
```

#### Konfiguracja dla Różnych Środowisk

**Development**:
- Użyj `docker-compose.dev.yml` (jeśli istnieje)
- Włącz hot reload
- Użyj lokalnych zmiennych środowiskowych

**Production**:
- Użyj `docker-compose.yml`
- Ustaw silne hasła
- Skonfiguruj HTTPS
- Włącz monitoring

### Czyszczenie i Reset

#### Zatrzymanie Wszystkich Kontenerów

```bash
docker-compose down
```

#### Usunięcie Kontenerów i Wolumenów

```bash
docker-compose down -v
```

**Uwaga**: To usunie wszystkie dane z bazy danych!

#### Pełne Czyszczenie

```bash
# Zatrzymaj i usuń kontenery
docker-compose down -v --remove-orphans

# Usuń nieużywane obrazy
docker system prune -a

# Usuń nieużywane wolumeny
docker volume prune
```

### Następne Kroki

Po pomyślnej instalacji:

1. **Przetestuj aplikację**: Otwórz frontend i zadaj pytanie o staże
2. **Sprawdź dokumentację API**: Odwiedź http://localhost:8000/docs
3. **Monitoruj logi**: Użyj `docker-compose logs -f` do monitorowania
4. **Skonfiguruj scraping**: Uruchom pierwszy scraping ręcznie lub poczekaj na automatyczny
5. **Przeczytaj dokumentację**: Zapoznaj się z sekcjami Deployment i Bezpieczeństwo

---

## Deployment

### Opcje Deploymentu

#### 1. Docker Compose (Lokalne/Produkcja)

```bash
docker-compose up -d --build
```

#### 2. Vercel (Frontend) + Railway (Backend)

- Frontend: Automatyczny build i deploy z Vercel
- Backend: Railway z PostgreSQL
- Konfiguracja przez zmienne środowiskowe w panelach

#### 3. VPS z Docker

- Pełna kontrola nad infrastrukturą
- Nginx jako reverse proxy
- SSL przez Let's Encrypt

### Wymagania Produkcyjne

- **Backend**: Minimum 2GB RAM, 1 CPU core
- **Database**: Minimum 4GB RAM, 2 CPU cores (dla indeksów wektorowych)
- **Frontend**: Statyczne pliki, może być hostowane na CDN

### Monitoring

- Logi aplikacji przez Docker logs
- Health checks endpointów
- Monitoring bazy danych (połączenia, zapytania)

---

## Bezpieczeństwo

### Implementowane Zabezpieczenia

1. **CORS**: Konfiguracja dozwolonych originów
2. **Secret Management**: Pydantic SecretStr dla wrażliwych danych
3. **Input Validation**: Walidacja przez Pydantic
4. **Error Handling**: Bezpieczne obsługiwanie błędów bez ujawniania szczegółów

### Rekomendacje Produkcyjne

1. **HTTPS**: Wymuszanie połączeń SSL/TLS
2. **Rate Limiting**: Ograniczenie liczby żądań
3. **Authentication**: Implementacja systemu autoryzacji
4. **Database Security**: 
   - Silne hasła
   - SSL connections
   - Ograniczenie dostępu sieciowego
5. **API Keys**: Bezpieczne przechowywanie kluczy API
6. **Backup**: Regularne kopie zapasowe bazy danych

---

## Rozwój i Utrzymanie

### Dodawanie Nowego Scrapera

1. Utwórz klasę dziedziczącą po `BaseScraper`
2. Zaimplementuj metody `scrape_offers()` i `scrape_offer_details()`
3. Dodaj scraper do słownika w `DataScraper._scrappers`

### Dodawanie Nowego Narzędzia Agenta

1. Zdefiniuj funkcję z dekoratorem `@tool`
2. Dodaj funkcję do listy `tools` w `agent.py`
3. Zaktualizuj system prompt z instrukcjami użycia

### Optymalizacja Wydajności

- **Database**: Regularne ANALYZE, optymalizacja indeksów
- **Embeddings**: Cache dla często używanych zapytań
- **Scraping**: Równoległe przetwarzanie, rate limiting
- **Frontend**: Code splitting, lazy loading

---

## Podsumowanie

InternBot to kompleksowe rozwiązanie wykorzystujące najnowsze technologie AI i web development do tworzenia inteligentnego asystenta rekomendacji staży. Architektura modułowa zapewnia łatwość utrzymania i rozbudowy, a wykorzystanie wyszukiwania semantycznego gwarantuje trafne rekomendacje dopasowane do preferencji użytkownika.

System jest gotowy do wdrożenia produkcyjnego i może być łatwo rozszerzany o nowe źródła danych, funkcjonalności oraz optymalizacje wydajnościowe.

