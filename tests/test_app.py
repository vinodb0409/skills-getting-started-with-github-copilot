import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_success(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "teststudent@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up teststudent@mergington.edu for Chess Club"
    assert "teststudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity_returns_404(client):
    response = client.post(
        "/activities/Nonexistent/signup",
        params={"email": "teststudent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_existing_participant_returns_400(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_success(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_participant_nonexistent_activity_returns_404(client):
    response = client.delete(
        "/activities/Nonexistent/participants",
        params={"email": "someone@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_missing_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "missingstudent@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
