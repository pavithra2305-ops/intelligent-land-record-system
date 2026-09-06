import io
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
import fitz  # PyMuPDF for PDF generation

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.schemas import LandRecordResponse
from app.models import LandRecord, User, RoleEnum

router = APIRouter()

def is_owner_or_staff(record: LandRecord, user: User) -> bool:
    if user.role in [RoleEnum.ADMIN.value, RoleEnum.VERIFIER.value]:
        return True
    if record.owner_user_id == user.id:
        return True
    if record.owner_name and user.full_name and record.owner_name.lower().strip() in user.full_name.lower().strip():
        return True
    if record.owner_name and user.full_name and user.full_name.lower().strip() in record.owner_name.lower().strip():
        return True
    return False

@router.get("/my-records", response_model=List[LandRecordResponse])
def get_my_land_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns land records associated ONLY with the currently authenticated VIEWER account.
    Returns HTTP 403 Forbidden if user is not a VIEWER.
    """
    if current_user.role != RoleEnum.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to VIEWER role only."
        )

    records = db.query(LandRecord).filter(
        (LandRecord.owner_user_id == current_user.id) |
        (LandRecord.owner_name.ilike(f"%{current_user.full_name}%"))
    ).order_by(LandRecord.id.desc()).all()

    return records

@router.get("/my-records/{id}", response_model=LandRecordResponse)
def get_my_land_record_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns a single land record ONLY if it belongs to the authenticated VIEWER.
    Returns 403 Forbidden for non-VIEWER roles.
    Returns 404 Not Found if record doesn't exist or doesn't belong to the Viewer.
    """
    if current_user.role != RoleEnum.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to VIEWER role only."
        )

    record = db.query(LandRecord).filter(LandRecord.id == id).first()
    if not record or not is_owner_or_staff(record, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land record not found or access denied."
        )
    return record

@router.get("/my-records/{id}/download")
def download_land_record_pdf(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a downloadable PDF of the land record details for the authenticated VIEWER.
    Returns 403 Forbidden for non-VIEWER roles.
    """
    if current_user.role != RoleEnum.VIEWER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to VIEWER role only."
        )

    record = db.query(LandRecord).filter(LandRecord.id == id).first()
    if not record or not is_owner_or_staff(record, current_user):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land record not found or access denied."
        )

    # Build PDF document using PyMuPDF (fitz)
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size

    # Header Navy Banner
    banner_rect = fitz.Rect(30, 30, 565, 95)
    page.draw_rect(banner_rect, color=(0.06, 0.09, 0.16), fill=(0.06, 0.09, 0.16)) # Deep Navy
    page.insert_text(fitz.Point(190, 60), "DIGITAL LAND RECORD", fontsize=16, color=(1, 1, 1), fontname="helv")
    page.insert_text(
        fitz.Point(100, 80),
        "Generated from Intelligent Land Record Digitization & Validation System",
        fontsize=9, color=(0.8, 0.88, 0.98), fontname="helv"
    )

    # Subtitle Info Bar
    page.insert_text(fitz.Point(35, 120), f"Owner: {record.owner_name or 'N/A'}", fontsize=11, color=(0.06, 0.09, 0.16), fontname="helv")
    page.insert_text(fitz.Point(350, 120), f"Date: {datetime.datetime.utcnow().strftime('%Y-%m-%d')}", fontsize=10, color=(0.35, 0.45, 0.55), fontname="helv")
    page.draw_line(fitz.Point(30, 130), fitz.Point(565, 130), color=(0.88, 0.91, 0.94), width=1.5)

    # Structured Fields Table
    fields = [
        ("Owner Name", record.owner_name or "N/A"),
        ("Survey Number", record.survey_number or "N/A"),
        ("Khasra Number", record.khasra_number or "N/A"),
        ("Khata Number", record.khata_number or "N/A"),
        ("Plot Area", f"{record.plot_area or 'N/A'} {record.area_unit or 'Acres'}"),
        ("Village", record.village_name or "N/A"),
        ("Tehsil", record.tehsil_name or "N/A"),
        ("District", record.district_name or "N/A"),
        ("Land Classification", record.land_classification or "N/A"),
        ("Ownership Details", record.ownership_details or "Sole ownership record"),
        ("Mutation Number", record.mutation_number or "N/A"),
        ("Registration Number", record.registration_number or "N/A"),
        ("Validation Status", record.validation_status or "VALID"),
        ("Verification Status", "Verified" if record.is_verified else "Pending QA Review")
    ]

    y = 155
    for label, val in fields:
        # Background row tinting
        row_rect = fitz.Rect(30, y - 12, 565, y + 16)
        fill_color = (0.97, 0.98, 0.99) if (y // 28) % 2 == 0 else (1, 1, 1)
        page.draw_rect(row_rect, color=(0.91, 0.93, 0.95), fill=fill_color, width=0.5)

        page.insert_text(fitz.Point(45, y + 3), label, fontsize=10, color=(0.35, 0.45, 0.55), fontname="helv")
        page.insert_text(fitz.Point(230, y + 3), str(val), fontsize=10, color=(0.06, 0.09, 0.16), fontname="helv")
        y += 28

    # Footer Seal
    stamp_rect = fitz.Rect(360, 720, 550, 780)
    page.draw_rect(stamp_rect, color=(0.08, 0.64, 0.29), fill=(0.94, 0.99, 0.95), width=1.5)
    page.insert_text(fitz.Point(380, 745), "OFFICIAL DIGITAL EXTRACT", fontsize=9, color=(0.08, 0.64, 0.29), fontname="helv")
    page.insert_text(fitz.Point(395, 765), "AUTHENTICATED RECORD", fontsize=8, color=(0.08, 0.64, 0.29), fontname="helv")

    pdf_bytes = doc.tobytes()
    filename = f"Digital_Land_Record_{(record.survey_number or 'REC').replace('/', '_')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
