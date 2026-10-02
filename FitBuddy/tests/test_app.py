import os
from pathlib import Path


Path(
    "test_fitbuddy.db"
).unlink(
    missing_ok=True
)


os.environ["GEMINI_API_KEY"] = "test-key"

os.environ["ADMIN_PASSWORD"] = "test-admin"

os.environ["SESSION_SECRET"] = "test-session-secret"

os.environ["DATABASE_URL"] = (
    "sqlite:///./test_fitbuddy.db"
)


from fastapi.testclient import TestClient

from app.main import app

from app import routes

from app.database import init_db


init_db()


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert (
        "Create your 7-day fitness plan"
        in response.text
    )


def test_validation():

    response = client.post(
        "/api/generate-workout",

        json={
            "username": "A",
            "user_id": "bad id",
            "age": 12,
            "weight": 0,
            "goal": "unknown",
            "intensity": "high"
        }
    )

    assert response.status_code == 422


def test_generate_and_update_without_real_gemini(
    monkeypatch
):

    monkeypatch.setattr(
        routes,
        "generate_workout_gemini",
        lambda data:
            "Day 1\nFull body\nDay 2\nRecovery"
    )


    monkeypatch.setattr(
        routes,
        "generate_nutrition_tip_with_flash",
        lambda data:
            "Stay hydrated and eat balanced meals."
    )


    monkeypatch.setattr(
        routes,
        "update_workout_plan",
        lambda original,
        feedback,
        goal,
        intensity:
            original
            + "\nUpdated: "
            + feedback
    )


    payload = {

        "username": "Test User",

        "user_id": "test001",

        "age": 25,

        "weight": 65,

        "goal": "general wellness",

        "intensity": "medium",
    }


    response = client.post(
        "/api/generate-workout",
        json=payload
    )


    assert response.status_code == 200


    assert (
        response.json()["workout_plan"]
        .startswith("Day 1")
    )


    response = client.post(

        "/api/submit-feedback",

        json={
            "user_id": "test001",
            "feedback": "add more mobility"
        }
    )


    assert response.status_code == 200


    assert (
        "add more mobility"
        in response.json()["updated_plan"]
    )