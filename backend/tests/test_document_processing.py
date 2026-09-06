import io
import pytest
from PIL import Image, ImageDraw, ImageFont
from app.models import ExtractionResult, LandRecord

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

def test_document_upload_and_processing(client, db_session):
    # 1. Login as Admin
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload a valid sample image document containing Karthik details
    img_bytes = make_test_image([
        "Owner Name: Karthik",
        "Survey Number: 124/2A",
        "Plot Area: 2.50 Acres",
        "Village: Annur"
    ])

    files = {"file": ("test_karthik_doc.png", io.BytesIO(img_bytes), "image/png")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    # 3. Process the document
    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "COMPLETED"

    # 4. Verify ExtractionResult in DB
    ext_result = db_session.query(ExtractionResult).filter(ExtractionResult.document_id == doc_id).first()
    assert ext_result is not None

    # 5. Fetch Extraction details and verify extracted fields match THIS uploaded document
    ext_detail_res = client.get(f"/api/documents/{doc_id}/extraction", headers=headers)
    assert ext_detail_res.status_code == 200
    res_json = ext_detail_res.json()
    fields = res_json["extracted_fields"]

    assert fields["owner_name"] == "Karthik"
    assert fields["plot_area"] == 2.5
    assert fields["village"] == "Annur"

def test_balasubramanian_document_upload_and_processing(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    img_bytes = make_test_image([
        "GOVERNMENT OF TAMIL NADU - REVENUE DEPARTMENT",
        "RECORD OF RIGHTS / PATTA EXTRACT",
        "District: Chengalpattu | Tehsil: Thiruporur | Village: Thiruporur",
        "Owner Name: Balasubramanian",
        "Survey Number: 489/3C",
        "Khata Number: 712",
        "Plot Area: 3.10",
        "Area Unit: Acres",
        "Ownership Details: Joint Ownership"
    ])

    files = {"file": ("test_balasubramanian_doc.png", io.BytesIO(img_bytes), "image/png")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "COMPLETED"

    ext_detail_res = client.get(f"/api/documents/{doc_id}/extraction", headers=headers)
    assert ext_detail_res.status_code == 200
    res_json = ext_detail_res.json()
    assert res_json["document_id"] == doc_id
    fields = res_json["extracted_fields"]

    # Verify extracted fields are NOT sample/Ramasamy values
    assert fields["owner_name"] != "Ramasamy"
    assert fields["survey_number"] != "124/2A"
    assert fields["plot_area"] != 2.45
    assert fields["village"] != "Vallam"

    # Verify extracted fields match exact uploaded document values
    assert fields["owner_name"] == "Balasubramanian"
    assert fields["survey_number"] == "489/3C"
    assert fields["khata_number"] == "712"
    assert fields["plot_area"] == 3.1
    assert fields["area_unit"] == "Acres"
    assert fields["village"] == "Thiruporur"
    assert fields["district"] == "Chengalpattu"
    assert fields["ownership_details"] == "Joint Ownership"

def test_arun_kumar_document_upload_and_processing(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    img_bytes = make_test_image([
        "GOVERNMENT OF TAMIL NADU - REVENUE DEPARTMENT",
        "RECORD OF RIGHTS / PATTA EXTRACT",
        "Village: Avinashi",
        "Owner Name: Arun Kumar",
        "Survey Number: 215/4B",
        "Khata Number: 903",
        "Plot Area: 5.25",
        "Area Unit: Acres"
    ])

    files = {"file": ("test_arun_kumar_doc.png", io.BytesIO(img_bytes), "image/png")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "COMPLETED"

    ext_detail_res = client.get(f"/api/documents/{doc_id}/extraction", headers=headers)
    assert ext_detail_res.status_code == 200
    res_json = ext_detail_res.json()
    assert res_json["document_id"] == doc_id
    fields = res_json["extracted_fields"]

    assert fields["owner_name"] == "Arun Kumar"
    assert fields["survey_number"] == "215/4B"
    assert fields["khata_number"] == "903"
    assert fields["plot_area"] == 5.25
    assert fields["village"] == "Avinashi"

def test_valid_jpeg_upload_and_processing(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    img = Image.new("RGB", (800, 400), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((40, 40), "Owner Name: Suresh\nSurvey Number: 501/2\nPlot Area: 1.80 Acres\nVillage: Annur", fill="black")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")

    files = {"file": ("test_suresh_doc.jpg", io.BytesIO(buf.getvalue()), "image/jpeg")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "COMPLETED"

def test_valid_pdf_upload_and_processing(client, db_session):
    import pymupdf
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 50), "Owner Name: Rajesh\nSurvey Number: 302/1A\nPlot Area: 4.20 Acres\nVillage: Annur", fontsize=14)
    pdf_bytes = doc.tobytes()
    doc.close()

    files = {"file": ("test_rajesh_doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 200
    doc_id = upload_res.json()["id"]

    process_res = client.post(f"/api/documents/{doc_id}/process", headers=headers)
    assert process_res.status_code == 200
    assert process_res.json()["status"] == "COMPLETED"

def test_corrupted_png_upload_handling(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    corrupt_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRcorrupted_crc_header_data_block"
    files = {"file": ("test_corrupt_doc.png", io.BytesIO(corrupt_bytes), "image/png")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 400
    assert "corrupted or invalid" in upload_res.json()["detail"].lower()

def test_zero_byte_file_upload_handling(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("empty_doc.png", io.BytesIO(b""), "image/png")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 400
    assert "empty" in upload_res.json()["detail"].lower()

def test_unsupported_file_extension_handling(client, db_session):
    login_res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("doc.exe", io.BytesIO(b"binary_executable_data"), "application/octet-stream")}
    data = {"language": "English", "document_type": "Ownership Record"}

    upload_res = client.post("/api/documents/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 400
    assert "unsupported file type" in upload_res.json()["detail"].lower()


