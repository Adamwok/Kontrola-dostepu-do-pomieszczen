Zajęcia 1:
Wybrany temat projektowy: 47. Kontrola dostępu do pomieszczeń.
Pierwsze popełnienia:
    1.Zainicjowano repozytorium.
    2.Naprawiono literówkę w nazwie repozytorium i pliku README.md.
    3.Zainicjowana została struktura bazowa projektu (szkielet).
    4.Dodano szkielet 3 kontenerów: backend, frontend oraz DB, na podstawie wiedzy z części wykładowej, dodatkowo sprawdzone za pomocą AI.
    5.Dodano pole nazwa w pliku docker-compose.yml.
    6.Naprawione punkty końcowe w backend oraz frontend. Dodano testowy kod, który testuje działanie połączenie pomiędzy backend a DB.

Zajęcia 2:
    Udane uruchomienie trzech kontenerów. Kontenery łączą się ze sobą przez sieć wewnętrzną. Dodano mechanizm healthcheck: frontend sprawdza stan backend, backend sprawdza stan bazy danych.
    Backend pomyślnie testuje połączenie z bazą danych. Frontend pobiera z backendu JSON ze statusem połączenia z bazą danych.

Zajęcia 3:
    Opracowanie wstępnej struktury API backendu i dodanie 4 pierwszych endpoiontów:
        - GET /rooms
        - GET /rooms/{room_id}
        - POST /access
        - DELETE /rooms/{room_id}

Zajęcia 4:
    Dodano bazę danych i konfigurację:
        - Utworzono skrypt inisjalizujący db/init.sql ze schematem 3 powiązanych tabel (rooms, users, access_logs) oraz danymi startowymi.
        - Zaktualizowano docker-compose.yml i dodano plik .env.example.
    Backend:
        - Rozbito kod backendu na moduły (db.py, room.py, user.py, accesscheck.py, main.py).
        - Przełączono połączenie z bazą danych na psycopg[binary] (v3).
        - Rozbudowano API:
            - POST /rooms, PUT /rooms/{room_id}
            -GET /users, POST /users, PUT /users/{user_id}, PATCH /users/{user_id}/toggle
            - POST /access
            - GET /access/logs
    Frontend:
        - Przygotowano aplikację z dwoma widokami, podzieloną na pliki (index.html, style.css, app.js):
            1. Symulator drzwi z czytnikiem RFID, wyborem pomieszczenia, wyborem użytkownika i podglądem ostatnich zdarzeń.
            2. Panel administracyjny do dodawania, edycji i usuwania pomieszczeń, zarządzania użytkownikami/kartami oraz przeglądania pełnych logów.
    
    Użycie AI:
        - Wykorzystano narzędzia AI wspomagając tworzenie skryptu frontendu:
            1. Schemat funkcji i ich wykorzystania.
            2. Funkcje api, updateRoomPlaqueMeta całkowicie napisana przez AI.
            3. Na podstawie funkcji `updateRoomPlaqueMeta` utworzono pozostałe funkcje ręcznie.
            4. Analiza błędów, które powstały w trakcie pisania ręcznie kodu.
