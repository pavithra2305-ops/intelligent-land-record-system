import pytest
from app.models import User, LandRecord, RoleEnum, Document
from app.core.security import get_password_hash

def test_viewer1_my_records_filtering(client, db_session):
    # Ensure Ramesh Kumar (viewer1) and Priya Kumar (viewer2) exist in test DB
    v1 = db_session.query(User).filter(User.email == "viewer1@test.com").first()
    if not v1:
        v1 = User(email="viewer1@test.com", password_hash=get_password_hash("password123"), full_name="Ramesh Kumar", role=RoleEnum.VIEWER.value)
        db_session.add(v1)
        db_session.commit()

    v2 = db_session.query(User).filter(User.email == "viewer2@test.com").first()
    if not v2:
        v2 = User(email="viewer2@test.com", password_hash=get_password_hash("password123"), full_name="Priya Kumar", role=RoleEnum.VIEWER.value)
        db_session.add(v2)
        db_session.commit()

    # Create land records for v1 (Ramesh) and v2 (Priya)
    doc1 = Document(filename="doc1.png", original_filename="doc1.png", file_path="doc1.png", file_type="PNG", file_size=100)
    db_session.add(doc1)
    db_session.commit()

    rec_ramesh = LandRecord(
        document_id=doc1.id, owner_name="Ramesh Kumar", owner_user_id=v1.id, survey_number="124/2A",
        plot_area=2.5, village_name="Annur", district_name="Coimbatore"
    )
    db_session.add(rec_ramesh)

    doc2 = Document(filename="doc2.png", original_filename="doc2.png", file_path="doc2.png", file_type="PNG", file_size=100)
    db_session.add(doc2)
    db_session.commit()

    rec_priya = LandRecord(
        document_id=doc2.id, owner_name="Priya Kumar", owner_user_id=v2.id, survey_number="56/1",
        plot_area=1.2, village_name="Sulur", district_name="Coimbatore"
    )
    db_session.add(rec_priya)
    db_session.commit()

    # 1. Login as Viewer 1 (Ramesh Kumar)
    login_res1 = client.post("/api/auth/login", json={"email": "viewer1@test.com", "password": "password123"})
    token1 = login_res1.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    res1 = client.get("/api/land-records/my-records", headers=headers1)
    assert res1.status_code == 200
    records1 = res1.json()
    assert all(r["owner_name"] == "Ramesh Kumar" for r in records1)
    assert not any(r["owner_name"] == "Priya Kumar" for r in records1)

    # 2. Login as Viewer 2 (Priya Kumar)
    login_res2 = client.post("/api/auth/login", json={"email": "viewer2@test.com", "password": "password123"})
    token2 = login_res2.json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    res2 = client.get("/api/land-records/my-records", headers=headers2)
    assert res2.status_code == 200
    records2 = res2.json()
    assert all(r["owner_name"] == "Priya Kumar" for r in records2)
    assert not any(r["owner_name"] == "Ramesh Kumar" for r in records2)

    # 3. Security test: Viewer 1 attempting to access Viewer 2's record by ID
    forbidden_res = client.get(f"/api/land-records/my-records/{rec_priya.id}", headers=headers1)
    assert forbidden_res.status_code == 404

    # 4. Download PDF test for Viewer 1 owned record
    pdf_res = client.get(f"/api/land-records/my-records/{rec_ramesh.id}/download", headers=headers1)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 100

    # 5. Non-VIEWER role restriction test (Admin/Verifier get 403 Forbidden)
    admin_user = db_session.query(User).filter(User.email == "admin@landgov.in").first()
    if not admin_user:
        admin_user = User(email="admin@landgov.in", password_hash=get_password_hash("admin123"), full_name="Admin", role=RoleEnum.ADMIN.value)
        db_session.add(admin_user)
        db_session.commit()

    admin_login = client.post("/api/auth/login", json={"email": "admin@landgov.in", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    admin_res = client.get("/api/land-records/my-records", headers=admin_headers)
    assert admin_res.status_code == 403

