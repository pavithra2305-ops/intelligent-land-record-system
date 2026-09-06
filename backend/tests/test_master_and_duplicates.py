import io
import pytest
from PIL import Image, ImageDraw, ImageFont
from app.models import MasterLandRecord, Document, LandRecord

def make_test_image(lines):
    try:
        font = ImageFont.load_default(size=24)
    except TypeError:
        font = ImageFont.load_default()
    img = Image.new("RGB", (1000, 60 + len(lines) * 50), color="white")
    draw = ImageDraw.Draw(img)
    y = 30
    for line in lines:
        draw.text((40, y), line, fill="black", font=font)
        y += 50
    img_buf = io.BytesIO()
    img.save(img_buf, format="PNG")
    return img_buf.getvalue()

def test_master_matched_scenario(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document matching Master Record #1 (Balasubramanian, 489/3C, Thiruporur, Chengalpattu)
    img_bytes = make_test_image([
        "Owner Name: Balasubramanian",
        "Survey Number: 489/3C",
        "Khata Number: 712",
        "Plot Area: 3.10",
        "Village: Thiruporur",
        "District: Chengalpattu"
    ])

    files = {"file": ("balasubramanian_matched.png", io.BytesIO(img_bytes), "image/png")}
    upload_res = client.post("/api/documents/upload", files=files, data={"language": "English"}, headers=headers)
    doc_id = upload_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers=headers)
    ext_res = client.get(f"/api/documents/{doc_id}/extraction", headers=headers).json()
    print("\n[TEST DEBUG] ext_res validation:", ext_res["validation"])

    assert ext_res["validation"]["master_match_status"] == "MATCHED"

    assert ext_res["validation"]["gis_match_status"] == "GIS_MATCH"
    assert ext_res["validation"]["duplicate_status"] == "NO_DUPLICATE"

def test_master_mismatch_scenario(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document resembling Arun Kumar but mismatching survey number 999/9X
    img_bytes = make_test_image([
        "Owner Name: Arun Kumar",
        "Survey Number: 999/9X",
        "Village: Avinashi",
        "District: Coimbatore"
    ])

    files = {"file": ("arun_kumar_mismatch.png", io.BytesIO(img_bytes), "image/png")}
    upload_res = client.post("/api/documents/upload", files=files, data={"language": "English"}, headers=headers)
    doc_id = upload_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers=headers)
    ext_res = client.get(f"/api/documents/{doc_id}/extraction", headers=headers).json()

    assert ext_res["validation"]["master_match_status"] in ["PARTIAL_MATCH", "MISMATCH", "NOT_FOUND"]
    assert ext_res["validation"]["gis_match_status"] in ["GIS_MATCH", "GIS_NOT_FOUND"]

def test_master_not_found_scenario(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload document containing unknown survey 777/7Z and unknown location
    img_bytes = make_test_image([
        "Owner Name: Unknown Owner",
        "Survey Number: 777/7Z",
        "Village: UnknownVillage",
        "District: UnknownDistrict"
    ])

    files = {"file": ("unknown_777.png", io.BytesIO(img_bytes), "image/png")}
    upload_res = client.post("/api/documents/upload", files=files, data={"language": "English"}, headers=headers)
    doc_id = upload_res.json()["id"]

    client.post(f"/api/documents/{doc_id}/process", headers=headers)
    ext_res = client.get(f"/api/documents/{doc_id}/extraction", headers=headers).json()

    assert ext_res["validation"]["master_match_status"] == "NOT_FOUND"
    assert ext_res["validation"]["gis_match_status"] == "GIS_NOT_FOUND"


def test_sha256_exact_duplicate_scenario(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    img_bytes = make_test_image([
        "Owner Name: Unique Upload Test",
        "Survey Number: 555/5A",
        "Village: Thiruporur",
        "District: Chengalpattu"
    ])

    files = {"file": ("sha256_test.png", io.BytesIO(img_bytes), "image/png")}
    upload_res1 = client.post("/api/documents/upload", files=files, data={"language": "English"}, headers=headers)
    doc_id1 = upload_res1.json()["id"]

    # Re-upload exact same file bytes
    files_dup = {"file": ("sha256_test_copy.png", io.BytesIO(img_bytes), "image/png")}
    upload_res2 = client.post("/api/documents/upload", files=files_dup, data={"language": "English"}, headers=headers)
    
    assert upload_res2.status_code == 200
    res2_json = upload_res2.json()
    assert res2_json["status"] == "DUPLICATE_DOCUMENT"
    assert "Duplicate document detected" in res2_json["error_message"]

def test_logical_duplicate_scenario(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    img1 = make_test_image(["Owner Name: Suresh P", "Survey Number: 301/2", "Village: Sunguvarchatram", "District: Kancheepuram"])
    img2 = make_test_image(["RECORD HEADER", "Owner Name: Suresh P", "Survey Number: 301/2", "Village: Sunguvarchatram", "District: Kancheepuram"])

    files1 = {"file": ("suresh_doc1.png", io.BytesIO(img1), "image/png")}
    up1 = client.post("/api/documents/upload", files=files1, data={"language": "English"}, headers=headers)
    doc_id1 = up1.json()["id"]
    client.post(f"/api/documents/{doc_id1}/process", headers=headers)

    files2 = {"file": ("suresh_doc2.png", io.BytesIO(img2), "image/png")}
    up2 = client.post("/api/documents/upload", files=files2, data={"language": "English"}, headers=headers)
    doc_id2 = up2.json()["id"]
    client.post(f"/api/documents/{doc_id2}/process", headers=headers)

    ext2 = client.get(f"/api/documents/{doc_id2}/extraction", headers=headers).json()
    assert ext2["validation"]["duplicate_status"] == "POTENTIAL_RECORD_DUPLICATE"

def test_master_db_never_modified_by_upload(client, db_session):
    master_count_before = db_session.query(MasterLandRecord).count()

    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    img = make_test_image(["Owner Name: New Random Person", "Survey Number: 111/1A", "Village: Sulur", "District: Chengalpattu"])
    up = client.post("/api/documents/upload", files={"file": ("new_random.png", io.BytesIO(img), "image/png")}, headers=headers)
    doc_id = up.json()["id"]
    client.post(f"/api/documents/{doc_id}/process", headers=headers)

    master_count_after = db_session.query(MasterLandRecord).count()
    assert master_count_before == master_count_after
