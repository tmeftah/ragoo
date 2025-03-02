# Test user routes
def test_register_user(client):
    response = client.post(
        "/users/register",
        json={"username": "newuser", "email": "new@example.com", "password": "newpass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "newuser"


def test_register_duplicate_user(client):
    client.post(
        "/users/register",
        json={"username": "duplicate", "email": "dup@example.com", "password": "dup"},
    )
    response = client.post(
        "/users/register",
        json={"username": "duplicate", "email": "dup@example.com", "password": "dup"},
    )
    assert response.status_code == 400


def test_login_success(client):
    # First register the user
    client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass",
        },
    )

    # Then test login
    response = client.post(
        "/users/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post(
        "/users/login", data={"username": "testuser", "password": "wrong"}
    )
    assert response.status_code == 401
