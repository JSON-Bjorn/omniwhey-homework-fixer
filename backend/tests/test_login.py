from fastapi.testclient import TestClient
import pytest
from ..app.main import app, fake_users_db, pwd_context, authenticate_user

# Create a test client
client = TestClient(app)


def test_login_success():
    """Test successful login with correct credentials"""
    response = client.post(
        "/api/login", json={"email": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password"""
    response = client.post(
        "/api/login", json={"email": "user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user():
    """Test login with nonexistent user"""
    response = client.post(
        "/api/login",
        json={"email": "nonexistent@example.com", "password": "password123"},
    )
    assert response.status_code == 401


# Test adding a new user to the database
def test_add_user():
    """Test adding a new user to the fake database"""
    # Add a test user
    test_email = "test@example.com"
    test_password = "testpassword123"

    fake_users_db[test_email] = {
        "email": test_email,
        "hashed_password": pwd_context.hash(test_password),
        "is_active": True,
        "is_admin": False,
    }

    # Try to login with the new user
    response = client.post(
        "/api/login", json={"email": test_email, "password": test_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
