import pytest
from app.services.validation_service import ValidationService
from app.services.duplicate_service import DuplicateService
from app.models import ValidationStatusEnum

def test_case_a_valid_record(db_session):
    fields = {
        "owner_name": "Senthil Kumar",
        "survey_number": "124/2A",
        "plot_area": 2.45,
        "district": "Kancheepuram",
        "tehsil": "Sriperumbudur",
        "village": "Vallam"
    }
    status, errors, warnings = ValidationService.validate_record(db_session, fields)
    assert status == ValidationStatusEnum.VALID.value
    assert len(errors) == 0

def test_case_b_missing_owner_name(db_session):
    fields = {
        "owner_name": "",
        "survey_number": "124/2A",
        "plot_area": 2.45,
        "district": "Kancheepuram",
        "village": "Vallam"
    }
    status, errors, warnings = ValidationService.validate_record(db_session, fields)
    assert status == ValidationStatusEnum.INVALID.value
    assert any("Missing required field: Owner Name" in err for err in errors)

def test_case_c_invalid_area(db_session):
    fields = {
        "owner_name": "Senthil Kumar",
        "survey_number": "124/2A",
        "plot_area": -5.0,  # Negative area
        "district": "Kancheepuram",
        "village": "Vallam"
    }
    status, errors, warnings = ValidationService.validate_record(db_session, fields)
    assert status == ValidationStatusEnum.INVALID.value
    assert any("Plot area must be positive" in err for err in errors)

def test_case_d_location_mismatch(db_session):
    fields = {
        "owner_name": "Senthil Kumar",
        "survey_number": "124/2A",
        "plot_area": 2.45,
        "district": "NonExistentDistrict",
        "village": "Vallam"
    }
    status, errors, warnings = ValidationService.validate_record(db_session, fields)
    assert status == ValidationStatusEnum.WARNING.value
    assert any("not found in master database" in warn for warn in warnings)

def test_case_e_fuzzy_duplicate_detection(db_session):
    from app.models import Document, LandRecord
    doc = Document(filename="existing_doc.png", original_filename="existing_doc.png", file_path="existing_doc.png", file_type="PNG", file_size=100)
    db_session.add(doc)
    db_session.commit()

    rec = LandRecord(
        document_id=doc.id,
        owner_name="Senthil Kumar",
        survey_number="124/2A",
        village_name="Vallam",
        district_name="Kancheepuram"
    )
    db_session.add(rec)
    db_session.commit()

    is_dup, dup_id, score = DuplicateService.check_duplicate(
        db_session,
        owner_name="Senthil Kumar S",  # Slightly different spelling vs Senthil Kumar
        survey_number="124/2A",
        village_name="Vallam",
        district_name="Kancheepuram"
    )
    assert score > 0.70  # RapidFuzz similarity score calculated


