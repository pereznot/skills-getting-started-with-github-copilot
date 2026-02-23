import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_dict(self, client):
        # Arrange: No setup needed, activities already loaded
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) > 0

    def test_activity_has_required_fields(self, client):
        # Arrange: No setup needed
        
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, details in activities_data.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_student(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"

    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Basketball Team",
    ])
    def test_signup_multiple_activities(self, client, activity_name):
        # Arrange
        email = "multi_student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_activity_not_found(self, client):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "not_signed_up@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_signup_then_unregister(self, client):
        # Arrange
        activity_name = "Art Studio"
        email = "artist_student@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]


class TestAvailabilityTracking:
    """Tests for availability calculation"""
    
    def test_availability_decreases_after_signup(self, client):
        # Arrange
        activity_name = "Tennis Club"
        email = "tennis_player@mergington.edu"
        
        # Act
        response = client.get("/activities")
        initial_spots = response.json()[activity_name]["max_participants"] - len(response.json()[activity_name]["participants"])
        
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        final_spots = response.json()[activity_name]["max_participants"] - len(response.json()[activity_name]["participants"])
        
        # Assert
        assert final_spots == initial_spots - 1

    def test_availability_increases_after_unregister(self, client):
        # Arrange
        activity_name = "Drama Club"
        email = "noah@mergington.edu"  # Already signed up
        
        # Act
        response = client.get("/activities")
        initial_spots = response.json()[activity_name]["max_participants"] - len(response.json()[activity_name]["participants"])
        
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
        response = client.get("/activities")
        final_spots = response.json()[activity_name]["max_participants"] - len(response.json()[activity_name]["participants"])
        
        # Assert
        assert final_spots == initial_spots + 1
