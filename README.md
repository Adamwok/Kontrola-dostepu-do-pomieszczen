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
Należy skopiować plik przykładowy `.env.example` do pliku `.env` w głównym katalogu projektu

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
* **Endpoint statusu (przez proxy):** `http://localhost:8080/api/healthy`

Aby zatrzymać kontenery, należy użyć polecenia:
```bash
docker compose down
```