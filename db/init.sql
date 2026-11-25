CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    min_access_level INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    card_id TEXT UNIQUE NOT NULL,
    access_level INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS access_logs (
    id SERIAL PRIMARY KEY,
    card_id TEXT NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    granted BOOLEAN NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO rooms (code, name, min_access_level, is_active) VALUES
    ('BIURO-01', 'Biuro ogólne', 1, TRUE),
    ('LAB-01', 'Laboratorium sieciowe', 2, TRUE),
    ('LAB-02', 'Laboratorium systemowe', 2, TRUE),
    ('ARCH-01', 'Archiwum', 4, TRUE),
    ('SERW-01', 'Serwerownia główna', 5, TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO users (first_name, last_name, card_id, access_level, is_active) VALUES
    ('Adam', 'Kowalski', 'CARD-001', 1, TRUE),
    ('Ewa', 'Nowak', 'CARD-002', 2, TRUE),
    ('Jan', 'Wiśniewski', 'CARD-003', 3, TRUE),
    ('Anna', 'Kowalczyk', 'CARD-004', 4, TRUE),
    ('Piotr', 'Lewandowski', 'CARD-005', 5, TRUE),
    ('Jan', 'Kowalski', 'CARD-006', 2, FALSE)
ON CONFLICT (card_id) DO NOTHING;