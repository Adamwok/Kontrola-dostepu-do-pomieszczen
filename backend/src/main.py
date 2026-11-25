from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
import psycopg

from src.db import get_conn
from src.room import CreateRoom, UpdateRoom
from src.user import CreateUser, UpdateUser
from src.accesscheck import AccessCheckRequest

class RoomResponse(BaseModel):
    id: int
    code: str
    name: str
    min_access_level: int
    is_active: bool

app = FastAPI(title="Kontrola dostępu do pomieszczeń", root_path="/api")


@app.get("/health")
def get_status():
    try:
        with get_conn() as conn, conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="Database disconnected")#Kod statusu i detail zaproponowany przez AI

    return {
        "status": "success",
        "backend": "online",
        "database": "connected",
    }


@app.get("/rooms", response_model=List[RoomResponse])
def get_rooms():
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT id, code, name, min_access_level, is_active FROM rooms ORDER BY min_access_level")
        return cursor.fetchall()


@app.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: int):
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, code, name, min_access_level, is_active FROM rooms WHERE id = %s",
            (room_id,),
        )
        room = cursor.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail="Pokój nie istnieje")#Kod statusu i detail zaproponowany przez AI
        return room


@app.post("/rooms", response_model=RoomResponse, status_code=201)
def create_room(payload: CreateRoom):
    try:
        with get_conn() as conn, conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO rooms (code, name, min_access_level, is_active) VALUES (%s, %s, %s, %s) RETURNING id, code, name, min_access_level, is_active",
                (
                    payload.code.strip().upper(),
                    payload.name.strip(),
                    payload.min_access_level,
                    payload.is_active,
                ),
            )
            conn.commit()
            return cursor.fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Pokój o tym kodzie już istnieje")#Kod statusu i detail zaproponowany przez AI


@app.delete("/rooms/{room_id}")
def delete_room(room_id: int):
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute("DELETE from rooms WHERE id = %s RETURNING id", (room_id,))
        deleted = cursor.fetchone()
        conn.commit()

        if not deleted:
            raise HTTPException(status_code=404, detail="Pokój nie istnieje")#Kod statusu i detail zaproponowany przez AI
        return {"status": "success", "message": "Pokój został usunięty"}


@app.put("/rooms/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, payload: UpdateRoom):
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(
            "UPDATE rooms SET name = %s, min_access_level = %s, is_active = %s WHERE id = %s RETURNING id, code, name, min_access_level, is_active",
            (payload.name.strip(), payload.min_access_level, payload.is_active, room_id),
        )
        room = cursor.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail="Pokój nie istnieje")#Kod statusu i detail zaproponowany przez AI
        conn.commit()
        return room


@app.get("/users")
def get_users():
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY id")
        return cursor.fetchall()


@app.post("/users", status_code=201)
def create_user(payload: CreateUser):
    try:
        with get_conn() as conn, conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, card_id, access_level, is_active) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                (
                    payload.first_name.strip(),
                    payload.last_name.strip(),
                    payload.card_id.strip().upper(),
                    payload.access_level,
                    payload.is_active,
                ),
            )
            conn.commit()
            return cursor.fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Karta o tym ID już istnieje")#Kod statusu i detail zaproponowany przez AI


@app.patch("/users/{user_id}/toggle")
def toggle_user_status(user_id: int):
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET is_active = NOT is_active WHERE id = %s RETURNING *",
            (user_id,),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")#Kod statusu i detail zaproponowany przez AI
        conn.commit()
        return user


@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UpdateUser):
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET first_name = %s, last_name = %s, access_level = %s, is_active = %s WHERE id = %s RETURNING *",
            (
                payload.first_name.strip(),
                payload.last_name.strip(),
                payload.access_level,
                payload.is_active,
                user_id,
            ),
        )
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")
        conn.commit()
        return user

@app.post("/access")
def verify_access(payload: AccessCheckRequest):
    card_id = payload.card_id.strip().upper()
    room_code = payload.room_code.strip().upper()

    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT * FROM rooms WHERE code = %s", (room_code,))
        room = cursor.fetchone()
        if not room:
            raise HTTPException(status_code=404, detail="Pokój nie istnieje")#Kod statusu i detail zaproponowany przez AI

        cursor.execute("SELECT * FROM users WHERE card_id = %s", (card_id,))
        user = cursor.fetchone()

        granted = False
        reason = "Karta nie istnieje"
        if user:
            user_id = user["id"]
        else:
            user_id = None

        if user:
            if not room["is_active"]:
                reason = "Pokój jest zablokowany"
            elif not user["is_active"]:
                reason = "Karta jest nieaktywna"
            elif user["access_level"] < room["min_access_level"]:
                reason = "Brak dostępu do tego pokoju"
            else:
                granted = True
                reason = "Dostęp przyznany"

        cursor.execute(
            "INSERT INTO access_logs (card_id, user_id, room_id, granted, reason) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (card_id, user_id, room["id"], granted, reason),
        )
        log_entry = cursor.fetchone()
        conn.commit()

        return {
            "status": "success" if granted else "denied",
            "granted": granted,
            "message": reason,
            "room": room["code"],
            "user": f"{user['first_name']} {user['last_name']}" if user else None,
            "log_id": log_entry["id"]
        }


@app.get("/access/logs")
def get_access_logs(limit: int = Query(default=20, ge=1, le=200), room_code: str | None = None):
    with get_conn() as conn, conn.cursor() as cursor:
        if room_code:
            cursor.execute(
                """
                SELECT
                    access_logs.id,
                    access_logs.card_id,
                    users.first_name,
                    users.last_name,
                    rooms.code AS room_code,
                    access_logs.granted,
                    access_logs.reason,
                    access_logs.created_at
                FROM access_logs
                JOIN rooms ON rooms.id = access_logs.room_id
                LEFT JOIN users ON users.id = access_logs.user_id
                WHERE rooms.code = %s
                ORDER BY access_logs.created_at DESC
                LIMIT %s
                """,
                (room_code.strip().upper(), limit),
            )
        else:
            cursor.execute(
                """
                SELECT
                    access_logs.id,
                    access_logs.card_id,
                    users.first_name,
                    users.last_name,
                    rooms.code AS room_code,
                    access_logs.granted,
                    access_logs.reason,
                    access_logs.created_at
                FROM access_logs
                JOIN rooms ON rooms.id = access_logs.room_id
                LEFT JOIN users ON users.id = access_logs.user_id
                ORDER BY access_logs.created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
        return cursor.fetchall()