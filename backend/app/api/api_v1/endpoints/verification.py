import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.schemas import (
    LandRecordResponse, LandRecordUpdate, VerificationApprovalRequest, VerificationRejectionRequest
)
from app.models import (
    LandRecord, Document, User, RoleEnum, ValidationStatusEnum
)
from app.services.audit_service import AuditService

router = APIRouter()

@router.get("/pending", response_model=List[LandRecordResponse])
def get_pending_verifications(
    doc_type: Optional[str] = None,
    district: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(LandRecord).filter(LandRecord.is_verified == False)
    
    if district:
        query = query.filter(LandRecord.district_name.ilike(f"%{district}%"))
    if status:
        query = query.filter(LandRecord.validation_status == status)

    records = query.order_by(LandRecord.id.desc()).all()
    return records

@router.put("/{id}/record", response_model=LandRecordResponse)
def update_land_record(
    id: int,
    request: LandRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.ADMIN.value, RoleEnum.VERIFIER.value]))
):
    rec = db.query(LandRecord).filter(LandRecord.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Land record not found")

    old_values = {
        "owner_name": rec.owner_name,
        "survey_number": rec.survey_number,
        "plot_area": rec.plot_area,
        "district_name": rec.district_name,
        "village_name": rec.village_name
    }

    update_data = request.dict(exclude_unset=True)
    comment = update_data.pop("comment", None)

    for field, val in update_data.items():
        if hasattr(rec, field) and val is not None:
            setattr(rec, field, val)

    rec.updated_at = datetime.datetime.utcnow()
    # Recalculate confidence boost after human edit
    rec.confidence_score = min(rec.confidence_score + 0.15, 0.98)
    rec.confidence_level = "HIGH" if rec.confidence_score >= 0.85 else "MEDIUM"
    db.commit()
    db.refresh(rec)

    AuditService.log_action(
        db, action="RECORD_EDITED", entity="LandRecord", entity_id=rec.id, user=current_user,
        old_values=old_values, new_values=update_data
    )

    return rec

@router.post("/{id}/approve", response_model=LandRecordResponse)
def approve_record(
    id: int,
    request: VerificationApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.ADMIN.value, RoleEnum.VERIFIER.value]))
):
    rec = db.query(LandRecord).filter(LandRecord.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Land record not found")

    rec.is_verified = True
    rec.verified_by_id = current_user.id
    rec.verified_at = datetime.datetime.utcnow()
    rec.verifier_comments = request.comments
    rec.validation_status = ValidationStatusEnum.VALID.value

    # Update document status
    doc = db.query(Document).filter(Document.id == rec.document_id).first()
    if doc:
        doc.status = "VERIFIED"

    db.commit()
    db.refresh(rec)

    AuditService.log_action(
        db, action="RECORD_APPROVED", entity="LandRecord", entity_id=rec.id, user=current_user,
        new_values={"comments": request.comments, "verified_by": current_user.email}
    )

    return rec

@router.post("/{id}/reject", response_model=LandRecordResponse)
def reject_record(
    id: int,
    request: VerificationRejectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.ADMIN.value, RoleEnum.VERIFIER.value]))
):
    if not request.comments or not request.comments.strip():
        raise HTTPException(status_code=400, detail="Rejection reason comment is mandatory")

    rec = db.query(LandRecord).filter(LandRecord.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Land record not found")

    rec.is_verified = False
    rec.verified_by_id = current_user.id
    rec.verified_at = datetime.datetime.utcnow()
    rec.verifier_comments = f"REJECTED: {request.comments}"
    rec.validation_status = ValidationStatusEnum.INVALID.value

    doc = db.query(Document).filter(Document.id == rec.document_id).first()
    if doc:
        doc.status = "REJECTED"

    db.commit()
    db.refresh(rec)

    AuditService.log_action(
        db, action="RECORD_REJECTED", entity="LandRecord", entity_id=rec.id, user=current_user,
        new_values={"rejection_reason": request.comments, "rejected_by": current_user.email}
    )

    return rec
