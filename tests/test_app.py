"""
Tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities(client):
    """Reset activities to their initial state"""
    # This fixture resets the in-memory database to known state
    # Since we're testing with the real app state, we just provide the fixture
    # The actual reset happens in conftest.py if needed
    yield


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Debate Club",
            "Science Olympiad",
            "Basketball Team",
            "Soccer Team",
            "Drama Club",
            "Art Studio",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in data
            assert "description" in data[activity]
            assert "schedule" in data[activity]
            assert "max_participants" in data[activity]
            assert "participants" in data[activity]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self, client):
        """Test that signing up a new participant returns a 200 status code"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_new_participant_returns_success_message(self, client):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent2@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent2@mergington.edu" in data["message"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns a 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that signing up an already registered participant returns a 400"""
        email = "duplicate@mergington.edu"
        activity = "Programming%20Class"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Duplicate signup should fail
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_returns_200(self, client):
        """Test that unregistering an existing participant returns a 200"""
        email = "michael@mergington.edu"
        activity = "Chess%20Club"
        
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns a 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregistering a non-existent participant returns a 404"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregister actually removes the participant"""
        email = "daniel@mergington.edu"
        activity = "Chess Club"
        
        # Check initial state
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity]["participants"]
        assert email in participants_before
        
        # Unregister
        client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        
        # Check final state
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity]["participants"]
        assert email not in participants_after


class TestRootRedirect:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
