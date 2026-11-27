# Kontrola-dostępu-do-pomieszczeń

System webowy realizowany w architekturze kontenerowej. Obsługuje zarządzaniem dostępem do pomieszczeń.

## Skład zespołu

* [Adam Wojtkowiak]
* [Maksymilian Stieler]

## Architektura
Projektmskłada się z trzech odizolowanych kontenerów zarządzanych przez `docker-compose`:
* **Frontend (`nginx`)** - serwuje pliki statyczne `index.html`, `app.js` oraz działa jako Reverse Proxy, przekierowując zapytania z prefiksem `/api/` bezpośrednio do kontenera backendu. Jest to jedyny wystawiony kontener na port hosta '8080:80'.
* **Backend (`python`, `FastAPI` `SQLAlchemy`, `uvicorn`)** - wystawia REST API komunikujące się w formacie JSON oraz weryfikuje połączenie z bazą danych.
* **Baza danych (`postgres:17-alpine`)** - relacyjna baza danych PostgreSQL, działa na oficjalnym obrazie wraz z trwałym wolumenem danych `pgdata` oraz skonfigurowanym mechanizmem `healthcheck`.

## Instrukcja uruchomienia

### 1. Wymagania wstępne
* Zainstalowany **Docker** oraz **Docker Compose**

### 2. Konfiguracja zmiennych środowiskowych
Należy skopiować plik przykładowy `.env.example` do pliku `.env` w głównym katalogu projektu.

Przykładowa zawartość pliku `.env`:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=tajne_haslo
POSTGRES_DB=kontrola_dostepu
```

### 3. Budowanie i uruchomienie kontenerów
W głównym katalogu projektu należy wykonać polecenie:
```bash
docker compose up --build -d
```

### 4. Weryfikacja działania
* **Aplikacja webowa (Frontend):** `http://localhost:8080`
* **Endpoint statusu (przez proxy):** `http://localhost:8080/api/health`

Aby zatrzymać kontenery, należy użyć polecenia:
```bash
docker compose down
```

### 5. Format wymiany danych (JSON)

Komunikacja z API odbywa się w formacie **JSON** (UTF-8). Żądania `POST` i `PUT` wymagają nagłówka:

```http
Content-Type: application/json
```

### Ogólne zasady normalizacji i błędów

* **Normalizacja tekstu:** białe znaki na początku i końcu są usuwane (`strip`), a identyfikatory `rooms.code` oraz `users.card_id` są konwertowane na wielkie litery (np. `" test-01 "` → `"TEST-01"`, `" test-card-1 "` → `"TEST-CARD-1"`).
* **Kody błędów HTTP:**
  * `404 Not Found` — zasób (pokój lub użytkownik) nie istnieje.
  * `409 Conflict` — naruszenie unikalności (`rooms.code` lub `users.card_id` już istnieje).
  * `422 Unprocessable Entity` — błąd walidacji danych wejściowych (np. zbyt krótkie pola lub `min_access_level` spoza dozwolonego zakresu).

---

### 1. Status systemu (`/health`)

#### `GET /health` — sprawdzenie dostępności API i bazy danych

**Odpowiedź (`200 OK`):**

```json
{
  "status": "success",
  "backend": "online",
  "database": "connected"
}
```

---

### 2. Pomieszczenia (`/rooms`)

#### Struktura pól

| Pole | Typ | Wymagane (`POST`) | Opis |
| :--- | :--- | :---: | :--- |
| `id` | `integer` | — (tylko odpowiedź) | Unikalny identyfikator pokoju. |
| `code` | `string` | Tak | Unikalny kod pokoju (normalizowany: `trim` + wielkie litery). |
| `name` | `string` | Tak | Nazwa pokoju (normalizowana: `trim`). |
| `min_access_level` | `integer` | Tak | Minimalny poziom dostępu wymagany do wejścia. |
| `is_active` | `boolean` | Nie | Status aktywności pokoju. |

#### `POST /rooms` — utworzenie pomieszczenia

**Żądanie:**

```json
{
  "code": " test-01 ",
  "name": " Pokój testowy ",
  "min_access_level": 3,
  "is_active": true
}
```

**Odpowiedzi:**
* **`201 Created`** — zwraca utworzony obiekt ze znormalizowanymi wartościami:

```json
{
  "id": 1,
  "code": "TEST-01",
  "name": "Pokój testowy",
  "min_access_level": 3,
  "is_active": true
}
```

* **`409 Conflict`** — pokój o podanym `code` już istnieje.
* **`422 Unprocessable Entity`** — niepoprawne dane wejściowe (np. `{"code": "A", "name": "X", "min_access_level": 99}`).

#### `GET /rooms` — lista wszystkich pomieszczeń

**Odpowiedź (`200 OK`):** tablica obiektów pomieszczeń (`[...]`).

#### `GET /rooms/{room_id}` — pobranie szczegółów pomieszczenia

* **`200 OK`** — zwraca obiekt pomieszczenia.
* **`404 Not Found`** — pomieszczenie o podanym `room_id` nie istnieje.

#### `PUT /rooms/{room_id}` — aktualizacja pomieszczenia

**Żądanie:**

```json
{
  "name": "Pokój zaktualizowany",
  "min_access_level": 4,
  "is_active": false
}
```

**Odpowiedź (`200 OK`):** zaktualizowany obiekt pomieszczenia.

#### `DELETE /rooms/{room_id}` — usunięcie pomieszczenia

* **`200 OK`** — potwierdzenie usunięcia pokoju.
* **`404 Not Found`** — pomieszczenie nie istnieje lub zostało już usunięte.

---

### 3. Użytkownicy (`/users`)

#### Struktura pól

| Pole | Typ | Wymagane (`POST`) | Opis |
| :--- | :--- | :---: | :--- |
| `id` | `integer` | — (tylko odpowiedź) | Unikalny identyfikator użytkownika. |
| `first_name` | `string` | Tak | Imię użytkownika. |
| `last_name` | `string` | Tak | Nazwisko użytkownika. |
| `card_id` | `string` | Tak | Unikalny numer karty (normalizowany: `trim` + wielkie litery). |
| `access_level` | `integer` | Tak | Poziom uprawnień użytkownika. |
| `is_active` | `boolean` | Nie | Status aktywności użytkownika/karty. |

#### `POST /users` — dodanie użytkownika

**Żądanie:**

```json
{
  "first_name": "Test",
  "last_name": "User",
  "card_id": " test-card-1 ",
  "access_level": 2,
  "is_active": true
}
```

**Odpowiedzi:**
* **`201 Created`** — zwraca utworzony obiekt użytkownika (z nadanym `id` i znormalizowanym `card_id`: `"TEST-CARD-1"`).
* **`409 Conflict`** — użytkownik o podanym `card_id` już istnieje.

#### `GET /users` — lista użytkowników

**Odpowiedź (`200 OK`):** tablica obiektów użytkowników (`[...]`).

#### `PUT /users/{user_id}` — aktualizacja danych użytkownika

**Żądanie:**

```json
{
  "first_name": "Nowe",
  "last_name": "Nazwisko",
  "access_level": 4,
  "is_active": true
}
```

**Odpowiedź (`200 OK`):** zaktualizowany obiekt użytkownika.

#### `PATCH /users/{user_id}/toggle` — przełączenie statusu `is_active`

* **Żądanie:** brak ciała.
* **`200 OK`** — zwraca obiekt użytkownika z odwróconą wartością `is_active` (`true` ↔ `false`).
* **`404 Not Found`** — użytkownik o podanym `user_id` nie istnieje.

---

### 4. Weryfikacja dostępu i logi (`/access`)

#### `POST /access` — sprawdzenie uprawnień wejścia

**Żądanie:**

```json
{
  "card_id": "TEST-CARD-OK",
  "room_code": "TEST-ROOM"
}
```

**Przypadki odpowiedzi:**

1. **Dostęp przyznany (`200 OK`)** — aktywny użytkownik z wymaganym poziomem uprawnień:

```json
{
  "granted": true
}
```

2. **Dostęp odrzucony: nieaktywny użytkownik (`200 OK`)** — karta istnieje, ale `is_active` wynosi `false`:

```json
{
  "granted": false
}
```

3. **Dostęp odrzucony: nieznana karta (`200 OK`)** — brak karty w bazie:

```json
{
  "granted": false,
  "user": null
}
```

4. **Nieistniejące pomieszczenie (`404 Not Found`)** — brak pokoju o podanym `room_code` (np. `"NO-ROOM"`).

> Każda próba weryfikacji dla istniejącego pokoju (zarówno udana, jak i odrzucona) jest zapisywana w historii logów dostępu.

#### `GET /access/logs` — pobranie logów dostępu

**Parametry zapytania (query parameters):**

| Parametr | Typ | Przykład | Opis |
| :--- | :--- | :--- | :--- |
| `room_code` | `string` | `TEST-ROOM` | Filtruje logi dla wybranego kodu pokoju. |
| `limit` | `integer` | `10` | Maksymalna liczba zwracanych wpisów. |

**Przykładowe wywołanie:**

```http
GET /access/logs?room_code=TEST-ROOM&limit=10
```

**Odpowiedź (`200 OK`):** tablica obiektów reprezentujących zarejestrowane próby dostępu.