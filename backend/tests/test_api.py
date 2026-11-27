import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.db import get_conn

client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield
    with get_conn() as conn, conn.cursor() as cursor:
        cursor.execute("DELETE FROM access_logs WHERE card_id LIKE 'TEST-%'")
        cursor.execute("DELETE FROM users WHERE card_id LIKE 'TEST-%'")
        cursor.execute("DELETE FROM rooms WHERE code LIKE 'TEST-%'")
        conn.commit()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "backend": "online",
        "database": "connected",
    }


def test_rooms_crud_and_errors():
    create_res = client.post(
        "/rooms",
        json={
            "code": " test-01 ",
            "name": " Pokój testowy ",
            "min_access_level": 3,
            "is_active": True,
        },
    )
    assert create_res.status_code == 201
    room = create_res.json()
    assert room["code"] == "TEST-01"
    assert room["name"] == "Pokój testowy"
    room_id = room["id"]

    dup_res = client.post(
        "/rooms",
        json={"code": "TEST-01", "name": "Duplikat", "min_access_level": 1},
    )
    assert dup_res.status_code == 409

    list_res = client.get("/rooms")
    assert list_res.status_code == 200
    assert any(r["id"] == room_id for r in list_res.json())

    get_res = client.get(f"/rooms/{room_id}")
    assert get_res.status_code == 200
    assert get_res.json()["code"] == "TEST-01"

    assert client.get("/rooms/999999").status_code == 404

    put_res = client.put(
        f"/rooms/{room_id}",
        json={"name": "Pokój zaktualizowany", "min_access_level": 4, "is_active": False},
    )
    assert put_res.status_code == 200
    assert put_res.json()["name"] == "Pokój zaktualizowany"
    assert put_res.json()["is_active"] is False

    del_res = client.delete(f"/rooms/{room_id}")
    assert del_res.status_code == 200
    assert client.get(f"/rooms/{room_id}").status_code == 404
    assert client.delete(f"/rooms/{room_id}").status_code == 404


def test_rooms_validation():
    res = client.post(
        "/rooms",
        json={"code": "A", "name": "X", "min_access_level": 99},
    )
    assert res.status_code == 422


def test_users_crud_and_toggle():
    create_res = client.post(
        "/users",
        json={
            "first_name": "Test",
            "last_name": "User",
            "card_id": " test-card-1 ",
            "access_level": 2,
            "is_active": True,
        },
    )
    assert create_res.status_code == 201
    user = create_res.json()
    assert user["card_id"] == "TEST-CARD-1"
    user_id = user["id"]

    dup_res = client.post(
        "/users",
        json={
            "first_name": "Inny",
            "last_name": "User",
            "card_id": "TEST-CARD-1",
            "access_level": 1,
        },
    )
    assert dup_res.status_code == 409

    list_res = client.get("/users")
    assert list_res.status_code == 200
    assert any(u["id"] == user_id for u in list_res.json())

    put_res = client.put(
        f"/users/{user_id}",
        json={
            "first_name": "Nowe",
            "last_name": "Nazwisko",
            "access_level": 4,
            "is_active": True,
        },
    )
    assert put_res.status_code == 200
    assert put_res.json()["access_level"] == 4

    toggle_res = client.patch(f"/users/{user_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["is_active"] is False

    assert client.patch("/users/999999/toggle").status_code == 404


def test_access_verification_and_logs():
    client.post(
        "/rooms",
        json={"code": "TEST-ROOM", "name": "Strefa", "min_access_level": 3, "is_active": True},
    )
    user_res = client.post(
        "/users",
        json={
            "first_name": "Jan",
            "last_name": "Testowy",
            "card_id": "TEST-CARD-OK",
            "access_level": 3,
            "is_active": True,
        },
    )
    user_id = user_res.json()["id"]

    ok_res = client.post("/access", json={"card_id": "TEST-CARD-OK", "room_code": "TEST-ROOM"})
    assert ok_res.status_code == 200
    assert ok_res.json()["granted"] is True

    client.patch(f"/users/{user_id}/toggle")
    inactive_res = client.post("/access", json={"card_id": "TEST-CARD-OK", "room_code": "TEST-ROOM"})
    assert inactive_res.status_code == 200
    assert inactive_res.json()["granted"] is False

    unknown_res = client.post("/access", json={"card_id": "TEST-UNKNOWN", "room_code": "TEST-ROOM"})
    assert unknown_res.status_code == 200
    assert unknown_res.json()["granted"] is False
    assert unknown_res.json()["user"] is None

    no_room_res = client.post("/access", json={"card_id": "TEST-CARD-OK", "room_code": "NO-ROOM"})
    assert no_room_res.status_code == 404

    logs_res = client.get("/access/logs", params={"room_code": "TEST-ROOM", "limit": 10})
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) == 3