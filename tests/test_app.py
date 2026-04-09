import pytest
from fastapi.testclient import TestClient
from src import app as app_module

# Create a copy of the original activities for resetting
original_activities = app_module.activities.copy()

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dict before each test to ensure isolation."""
    app_module.activities = original_activities.copy()

client = TestClient(app_module.app)

def test_get_activities():
    """Test GET /activities returns the activity data."""
    # Arrange
    # (TestClient is set up)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]

    # Verify added to participants
    resp = client.get("/activities")
    data = resp.json()
    assert email in data[activity]["participants"]

def test_signup_duplicate():
    """Test signup fails if student is already signed up."""
    # Arrange
    email = "existing@mergington.edu"
    activity = "Chess Club"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_invalid_activity():
    """Test signup fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistent Activity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_success():
    """Test successful unregistration from an activity."""
    # Arrange
    email = "removeme@mergington.edu"
    activity = "Programming Class"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]

    # Verify removed from participants
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]

def test_unregister_not_signed_up():
    """Test unregistration fails if student is not signed up."""
    # Arrange
    email = "notsigned@mergington.edu"
    activity = "Gym Class"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]

def test_unregister_invalid_activity():
    """Test unregistration fails for non-existent activity."""
    # Arrange
    email = "test@mergington.edu"
    activity = "Invalid Activity"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]