def test_verification_reject_requires_comment(client):
    login_res = client.post("/api/auth/login", json={"email": "verifier@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Reject without mandatory comment
    res = client.post("/api/verification/999/reject", json={"comments": ""}, headers=headers)
    assert res.status_code == 400
    assert "mandatory" in res.json()["detail"]

def test_verification_role_protection(client):
    login_res = client.post("/api/auth/login", json={"email": "viewer@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Viewer role attempting to approve record should be forbidden (403)
    res = client.post("/api/verification/1/approve", json={"comments": "Viewer approval"}, headers=headers)
    assert res.status_code == 403

def test_admin_only_endpoints_verifier_access(client):
    # Log in as VERIFIER
    login_res = client.post("/api/auth/login", json={"email": "verifier@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # VERIFIER calling GET /api/audit-logs MUST receive 403 Forbidden
    audit_res = client.get("/api/audit-logs", headers=headers)
    assert audit_res.status_code == 403

    # VERIFIER calling GET /api/users MUST receive 403 Forbidden
    users_res = client.get("/api/users", headers=headers)
    assert users_res.status_code == 403

def test_admin_only_endpoints_admin_access(client):
    # Log in as ADMIN
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ADMIN calling GET /api/audit-logs succeeds (200 OK)
    audit_res = client.get("/api/audit-logs", headers=headers)
    assert audit_res.status_code == 200

    # ADMIN calling GET /api/users succeeds (200 OK)
    users_res = client.get("/api/users", headers=headers)
    assert users_res.status_code == 200
