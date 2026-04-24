import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)

def test_get_activities():
    """Test GET /activities returns all activities"""
    # Arrange - activities are already set up
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_success():
    """Test successful signup for an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]

def test_signup_duplicate():
    """Test signup fails when student is already signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in Chess Club
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

def test_signup_activity_not_found():
    """Test signup fails for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    """Test successful unregister from an activity"""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already signed up
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity_name]["participants"]

def test_unregister_not_signed_up():
    """Test unregister fails when student is not signed up"""
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student not signed up" in data["detail"]

def test_unregister_activity_not_found():
    """Test unregister fails for non-existent activity"""
    # Arrange
    activity_name = "NonExistent Activity"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    """Test root endpoint redirects to static index.html"""
    # Arrange
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"
