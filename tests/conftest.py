import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before and after each test."""
    # Arrange: Save original state
    original_activities = deepcopy(activities)
    
    yield  # Test runs here
    
    # Cleanup: Restore original state
    activities.clear()
    activities.update(original_activities)
