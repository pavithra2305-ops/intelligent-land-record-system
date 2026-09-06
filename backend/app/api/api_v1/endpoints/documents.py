import os
import uuid
import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.schemas import DocumentResponse, ExtractionResponse
from app.models import (
    Document, LandRecord, ExtractionResult, ValidationResult, User,
    DocStatusEnum, ValidationStatusEnum
)
from app.services.storage_service import StorageService
from app.services.preprocessing_service import PreprocessingService
from app.services.ocr_service import OCRService
from app.services.classification_service import ClassificationService
from app.services.llm_service import LLMService
from app.services.confidence_service import ConfidenceService
from app.services.validation_service import ValidationService
from app.services.master_validation_service import MasterValidationService
from app.services.duplicate_service import DuplicateService
from app.services.audit_service import AuditService

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/pjpeg", "application/pdf", "application/octet-stream"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    language: str = Form("English"),
    document_type: str = Form("Ownership Record"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: PDF, PNG, JPG, JPEG")

    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported content type '{file.content_type}'. Allowed: image/png, image/jpeg, application/pdf")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 15 MB")

    file_hash = hashlib.sha256(contents).hexdigest()
    is_file_dup, existing_doc_id = DuplicateService.check_file_duplicate(db, file_hash)
    if is_file_dup:
        existing_doc = db.query(Document).filter(Document.id == existing_doc_id).first()
        if existing_doc:
            # Set status notice for exact duplicate
            existing_doc.status = "DUPLICATE_DOCUMENT"
            existing_doc.error_message = f"Duplicate document detected. This exact file has already been uploaded as Document #{existing_doc_id}."
            return existing_doc

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    rel_path, abs_path = StorageService.save_original(contents, unique_filename)

    # Validate image/PDF integrity immediately after saving
    try:
        PreprocessingService.validate_file_integrity(abs_path, ext[1:])
    except ValueError:
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                pass
        raise HTTPException(status_code=400, detail="Uploaded document is corrupted or invalid and cannot be processed.")

    document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=abs_path,
        file_type=ext[1:].upper(),
        file_size=len(contents),
        document_hash=file_hash,
        language=language,
        document_type=document_type,
        status=DocStatusEnum.UPLOADED.value,
        processing_stage="1/7: Uploaded",
        uploaded_by_id=current_user.id
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    AuditService.log_action(
        db, action="DOCUMENT_UPLOADED", entity="Document", entity_id=document.id, user=current_user,
        new_values={"filename": file.filename, "size": len(contents), "type": document_type, "hash": file_hash}
    )

    return document

@router.get("", response_model=List[DocumentResponse])
def get_documents(
    search: Optional[str] = None,
    doc_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if doc_type:
        query = query.filter(Document.document_type == doc_type)
    if status:
        query = query.filter(Document.status == status)
    if search:
        query = query.filter(Document.original_filename.ilike(f"%{search}%"))
    
    return query.order_by(Document.id.desc()).all()

@router.get("/{id}", response_model=DocumentResponse)
def get_document(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/{id}/process")
def process_document(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print("[PROCESS] ROUTE START")
    print(f"[PROCESS] DOCUMENT ID: {id}")

    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        print(f"[PROCESS] DOCUMENT NOT FOUND: {id}")
        raise HTTPException(status_code=404, detail=f"Document #{id} not found")

    file_exists = os.path.exists(doc.file_path) if doc.file_path else False
    file_size = os.path.getsize(doc.file_path) if file_exists else 0
    print(f"[PROCESS] FILE EXISTS: {file_exists}")
    print(f"[PROCESS] FILE TYPE: {doc.file_type}")
    print(f"[PROCESS] FILE SIZE: {file_size}")

    if not file_exists or file_size == 0:
        print("[PROCESS] FILE VALIDATION FAILED")
        print("[PROCESS] INVALID/CORRUPTED IMAGE")
        doc.status = DocStatusEnum.FAILED.value
        doc.processing_stage = "Failed"
        doc.error_message = "Uploaded document is corrupted or invalid and cannot be processed."
        db.commit()
        raise HTTPException(status_code=400, detail="Uploaded document is corrupted or invalid and cannot be processed.")

    print("[PROCESS] FILE VALIDATION START")
    try:
        PreprocessingService.validate_file_integrity(doc.file_path, doc.file_type)
        print("[PROCESS] FILE VALIDATION SUCCESS")
    except ValueError as val_err:
        print("[PROCESS] FILE VALIDATION FAILED")
        print("[PROCESS] INVALID/CORRUPTED IMAGE")
        doc.status = DocStatusEnum.FAILED.value
        doc.processing_stage = "Failed"
        doc.error_message = str(val_err)
        db.commit()
        raise HTTPException(status_code=400, detail="Uploaded document is corrupted or invalid and cannot be processed.")

    try:
        # Stage 2: Preprocessing
        doc.status = DocStatusEnum.PREPROCESSING.value
        doc.processing_stage = "2/7: Image Preprocessing"
        db.commit()

        print("[PROCESS] PREPROCESSING START")
        processed_img_path = StorageService.get_processed_path(doc.filename)
        PreprocessingService.preprocess_document(doc.file_path, processed_img_path)
        doc.processed_path = processed_img_path
        print("[PROCESS] PREPROCESSING COMPLETE")

        # Stage 3: OCR
        doc.status = DocStatusEnum.OCR.value
        doc.processing_stage = "3/7: Optical Character Recognition (OCR)"
        db.commit()

        print("[PROCESS] OCR START")
        ocr_service = OCRService()
        ocr_text, ocr_engine_used = ocr_service.extract_text(doc.file_path, processed_img_path, language=doc.language)
        ocr_save_path = StorageService.get_ocr_path(doc.filename)
        with open(ocr_save_path, "w", encoding="utf-8") as f:
            f.write(ocr_text)
        doc.ocr_path = ocr_save_path
        print("[PROCESS] OCR COMPLETE")

        AuditService.log_action(db, action="OCR_COMPLETED", entity="Document", entity_id=doc.id, user=current_user)

        # Stage 4: Classification
        doc.status = DocStatusEnum.CLASSIFICATION.value
        doc.processing_stage = "4/7: Document Classification"
        db.commit()

        classification_res = ClassificationService.classify_document(ocr_text, doc.original_filename)
        doc.document_type = classification_res["document_type"]

        # Stage 5: Extraction
        doc.status = DocStatusEnum.EXTRACTION.value
        doc.processing_stage = "5/7: AI Field Extraction"
        db.commit()

        print("[PROCESS] EXTRACTION START")
        llm_service = LLMService.get_service()
        extracted_fields, extraction_source = llm_service.extract_fields(ocr_text, doc.document_type)
        print("[PROCESS] EXTRACTION COMPLETE")

        overall_conf, conf_level = ConfidenceService.calculate_confidence(extracted_fields)

        # Create or update ExtractionResult
        ext_res = db.query(ExtractionResult).filter(ExtractionResult.document_id == doc.id).first()
        if not ext_res:
            ext_res = ExtractionResult(
                document_id=doc.id,
                raw_ocr_text=ocr_text,
                structured_json=extracted_fields,
                field_confidences={k: v.get("confidence", 0.0) for k, v in extracted_fields.items() if isinstance(v, dict)},
                ocr_confidence=0.90,
                ocr_engine_used=ocr_engine_used,
                extraction_source=extraction_source
            )
            db.add(ext_res)
        else:
            ext_res.raw_ocr_text = ocr_text
            ext_res.structured_json = extracted_fields
            ext_res.ocr_engine_used = ocr_engine_used
            ext_res.extraction_source = extraction_source

        AuditService.log_action(db, action="RECORD_EXTRACTED", entity="Document", entity_id=doc.id, user=current_user)

        # Stage 6: Master Database & GIS Validation & Duplicate Check
        doc.status = DocStatusEnum.VALIDATION.value
        doc.processing_stage = "6/7: Master DB & GIS Validation"
        db.commit()

        print("[PROCESS] VALIDATION START")
        val_status, errors, warnings = ValidationService.validate_record(db, extracted_fields)
        master_match_status, gis_match_status, field_comparison, m_id, m_parcel_id = MasterValidationService.validate_against_master_and_gis(db, extracted_fields)

        owner_name = extracted_fields.get("owner_name", {}).get("value")
        survey_number = extracted_fields.get("survey_number", {}).get("value")
        village_name = extracted_fields.get("village", {}).get("value")
        district_name = extracted_fields.get("district", {}).get("value")

        is_dup, dup_id, sim_score = DuplicateService.check_duplicate(
            db, owner_name, survey_number, village_name, district_name, current_document_id=doc.id
        )

        duplicate_status = "NO_DUPLICATE"
        if is_dup:
            duplicate_status = "POTENTIAL_RECORD_DUPLICATE"
            val_status = ValidationStatusEnum.DUPLICATE.value
            warnings.append(f"Potential Duplicate Record detected (Record #{dup_id}, Similarity: {int(sim_score * 100)}%)")

        if master_match_status == "MATCHED" and gis_match_status == "GIS_MATCH" and not errors and not is_dup:
            val_status = ValidationStatusEnum.VALID.value
        elif master_match_status == "MISMATCH" or master_match_status == "NOT_FOUND" or gis_match_status == "GIS_NOT_FOUND":
            if val_status != ValidationStatusEnum.INVALID.value and val_status != ValidationStatusEnum.DUPLICATE.value:
                val_status = ValidationStatusEnum.WARNING.value
            if master_match_status == "MISMATCH":
                warnings.append("Master Database record mismatch detected")
            elif master_match_status == "NOT_FOUND":
                warnings.append("Record not found in authoritative Master Database")
            if gis_match_status == "GIS_NOT_FOUND":
                warnings.append("GIS Parcel geometry not found in master parcel registry")

        val_res = db.query(ValidationResult).filter(ValidationResult.document_id == doc.id).first()
        if not val_res:
            val_res = ValidationResult(
                document_id=doc.id,
                status=val_status,
                errors=errors,
                warnings=warnings,
                duplicate_detected=is_dup,
                duplicate_record_id=dup_id,
                similarity_score=sim_score,
                master_match_status=master_match_status,
                gis_match_status=gis_match_status,
                duplicate_status=duplicate_status,
                field_comparison_details=field_comparison
            )
            db.add(val_res)
        else:
            val_res.status = val_status
            val_res.errors = errors
            val_res.warnings = warnings
            val_res.duplicate_detected = is_dup
            val_res.duplicate_record_id = dup_id
            val_res.similarity_score = sim_score
            val_res.master_match_status = master_match_status
            val_res.gis_match_status = gis_match_status
            val_res.duplicate_status = duplicate_status
            val_res.field_comparison_details = field_comparison
        print("[PROCESS] VALIDATION COMPLETE")

        # Create or update LandRecord
        land_rec = db.query(LandRecord).filter(LandRecord.document_id == doc.id).first()
        if not land_rec:
            land_rec = LandRecord(
                document_id=doc.id,
                owner_name=owner_name,
                survey_number=survey_number,
                khasra_number=extracted_fields.get("khasra_number", {}).get("value"),
                khata_number=extracted_fields.get("khata_number", {}).get("value"),
                plot_area=extracted_fields.get("plot_area", {}).get("value"),
                area_unit=extracted_fields.get("area_unit", {}).get("value") or "Acres",
                district_name=district_name,
                tehsil_name=extracted_fields.get("tehsil", {}).get("value"),
                village_name=village_name,
                land_classification=extracted_fields.get("land_classification", {}).get("value"),
                ownership_details=extracted_fields.get("ownership_details", {}).get("value"),
                mutation_number=extracted_fields.get("mutation_number", {}).get("value"),
                registration_number=extracted_fields.get("registration_number", {}).get("value"),
                confidence_score=overall_conf,
                confidence_level=conf_level,
                validation_status=val_status,
                is_verified=False
            )
            db.add(land_rec)
        else:
            land_rec.owner_name = owner_name
            land_rec.survey_number = survey_number
            land_rec.khasra_number = extracted_fields.get("khasra_number", {}).get("value")
            land_rec.khata_number = extracted_fields.get("khata_number", {}).get("value")
            land_rec.plot_area = extracted_fields.get("plot_area", {}).get("value")
            land_rec.area_unit = extracted_fields.get("area_unit", {}).get("value") or "Acres"
            land_rec.district_name = district_name
            land_rec.tehsil_name = extracted_fields.get("tehsil", {}).get("value")
            land_rec.village_name = village_name
            land_rec.land_classification = extracted_fields.get("land_classification", {}).get("value")
            land_rec.ownership_details = extracted_fields.get("ownership_details", {}).get("value")
            land_rec.mutation_number = extracted_fields.get("mutation_number", {}).get("value")
            land_rec.registration_number = extracted_fields.get("registration_number", {}).get("value")
            land_rec.confidence_score = overall_conf
            land_rec.confidence_level = conf_level
            land_rec.validation_status = val_status

        # Stage 7: Completed
        doc.status = DocStatusEnum.COMPLETED.value
        doc.processing_stage = "7/7: Completed"
        db.commit()
        print("[PROCESS] DATABASE UPDATE COMPLETE")
        print("[PROCESS] ROUTE SUCCESS")

        return {
            "message": "Document processed successfully",
            "document_id": doc.id,
            "status": doc.status,
            "confidence_score": overall_conf,
            "validation_status": val_status
        }
    except ValueError as val_e:
        print("[PROCESS] FILE VALIDATION FAILED")
        print(f"[PROCESS] IMAGE DECODING FAILED: {val_e}")
        try:
            doc.status = DocStatusEnum.FAILED.value
            doc.processing_stage = "Failed"
            doc.error_message = str(val_e)
            db.commit()
        except Exception:
            pass
        raise HTTPException(status_code=400, detail="Uploaded document is corrupted or invalid and cannot be processed.")
    except Exception as e:
        print(f"[PROCESS] FAILED: {e}")
        try:
            doc.status = DocStatusEnum.FAILED.value
            doc.processing_stage = "Failed"
            doc.error_message = "Document processing failed. Please try uploading the document again."
            db.commit()
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Please try uploading the document again."
        )

@router.get("/{id}/extraction", response_model=ExtractionResponse)
def get_extraction(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    ext_res = db.query(ExtractionResult).filter(ExtractionResult.document_id == id).first()
    val_res = db.query(ValidationResult).filter(ValidationResult.document_id == id).first()
    land_rec = db.query(LandRecord).filter(LandRecord.document_id == id).first()

    if not ext_res or not land_rec:
        raise HTTPException(status_code=400, detail="Document has not been processed yet")

    # Format field details with status and confidence level
    field_details = {}
    structured = ext_res.structured_json or {}
    for key, val_obj in structured.items():
        val = val_obj.get("value") if isinstance(val_obj, dict) else val_obj
        conf = val_obj.get("confidence", 0.85) if isinstance(val_obj, dict) else 0.85
        
        conf_level = "HIGH" if conf >= 0.85 else ("MEDIUM" if conf >= 0.60 else "LOW")
        status = "VALID"
        if not val and key in ["owner_name", "survey_number", "village", "district"]:
            status = "WARNING"
        
        field_details[key] = {
            "value": val,
            "confidence": round(conf, 2),
            "confidence_level": conf_level,
            "status": status
        }

    return {
        "document_id": doc.id,
        "document_type": doc.document_type,
        "classification_confidence": 0.92,
        "raw_ocr_text": ext_res.raw_ocr_text or "",
        "extracted_fields": {k: v["value"] for k, v in field_details.items()},
        "field_details": field_details,
        "overall_confidence": land_rec.confidence_score,
        "confidence_level": land_rec.confidence_level,
        "ocr_engine_used": ext_res.ocr_engine_used or "Dynamic OCR Engine",
        "extraction_source": ext_res.extraction_source or "Regex Extraction Engine",
        "validation": {
            "status": val_res.status if val_res else "VALID",
            "errors": val_res.errors if val_res else [],
            "warnings": val_res.warnings if val_res else [],
            "duplicate_detected": val_res.duplicate_detected if val_res else False,
            "duplicate_record_id": val_res.duplicate_record_id if val_res else None,
            "similarity_score": val_res.similarity_score if val_res else 0.0,
            "master_match_status": val_res.master_match_status if val_res else "NOT_FOUND",
            "gis_match_status": val_res.gis_match_status if val_res else "GIS_NOT_FOUND",
            "duplicate_status": val_res.duplicate_status if val_res else "NO_DUPLICATE",
            "field_comparison_details": val_res.field_comparison_details if val_res else {}
        }
    }

@router.get("/{id}/file")
def get_original_file(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Original document file not found")
    return FileResponse(doc.file_path)

@router.get("/{id}/processed-file")
def get_processed_file(id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc or not doc.processed_path or not os.path.exists(doc.processed_path):
        # Fall back to original file if processed path doesn't exist
        return get_original_file(id, db)
    return FileResponse(doc.processed_path)
