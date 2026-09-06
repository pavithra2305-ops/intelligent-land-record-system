def test_login_success(client):
    res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.com"
    assert data["user"]["role"] == "ADMIN"

def test_login_invalid_password(client):
    res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrongpassword"})
    assert res.status_code in [400, 401]
    assert res.json()["detail"] == "Invalid email or password."

def test_login_unregistered_email(client):
    res = client.post("/api/auth/login", json={"email": "nonexistent@test.com", "password": "password123"})
    assert res.status_code == 404
    assert res.json()["detail"] == "Account not found. Please sign up first."

def test_signup_arun_kumar_flow(client, db_session):
    # 1. Sign Up Arun Kumar with "name" field
    signup_res = client.post("/api/auth/register", json={
        "name": "Arun Kumar",
        "email": "arun@gmail.com",
        "password": "Arun@12345"
    })
    assert signup_res.status_code == 200
    res_data = signup_res.json()
    assert res_data["message"] == "Account created successfully"
    assert res_data["user"]["email"] == "arun@gmail.com"
    assert res_data["user"]["role"] == "VIEWER"

    # 2. Login using arun@gmail.com / Arun@12345
    login_res = client.post("/api/auth/login", json={
        "email": "arun@gmail.com",
        "password": "Arun@12345"
    })
    assert login_res.status_code == 200
    assert login_res.json()["user"]["role"] == "VIEWER"

    # 3. Try registering arun@gmail.com again -> Duplicate email error
    dup_res = client.post("/api/auth/register", json={
        "name": "Arun Kumar Duplicate",
        "email": "arun@gmail.com",
        "password": "Arun@12345"
    })
    assert dup_res.status_code == 400
    assert dup_res.json()["detail"] == "Email already registered. Please login."

    # 4. Verify Database
    from app.models import User
    arun_db = db_session.query(User).filter(User.email == "arun@gmail.com").first()
    assert arun_db is not None
    assert arun_db.full_name == "Arun Kumar"
    assert arun_db.role == "VIEWER"
    assert arun_db.password_hash != "Arun@12345" # Password is hashed, NOT plain text!

def test_signup_duplicate_email(client):
    # TEST 6: Duplicate email -> FAIL
    signup_res = client.post("/api/auth/register", json={
        "full_name": "Duplicate User",
        "email": "admin@test.com", # already exists in fixture
        "password": "password123",
        "confirm_password": "password123"
    })
    assert signup_res.status_code == 400
    assert "already registered" in signup_res.json()["detail"].lower()

def test_signup_password_mismatch(client):
    # TEST 7: Password mismatch -> FAIL
    signup_res = client.post("/api/auth/register", json={
        "full_name": "Mismatch User",
        "email": "mismatch@test.com",
        "password": "password123",
        "confirm_password": "differentpassword"
    })
    assert signup_res.status_code == 400
    assert "do not match" in signup_res.json()["detail"].lower()

def test_get_me(client):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]

    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "admin@test.com"
