import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["existing@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["existing@example.com"]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.com for Chess Club"}
    assert "new@example.com" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "existing@example.com"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "new@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_unregisters_student(client):
    response = client.delete(
        "/activities/Chess Club/participants/existing@example.com"
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed existing@example.com from Chess Club"}
    assert "existing@example.com" not in app_module.activities["Chess Club"]["participants"]


def test_remove_participant_returns_not_found_when_not_signed_up(client):
    response = client.delete(
        "/activities/Chess Club/participants/missing@example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_remove_participant_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/participants/existing@example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"