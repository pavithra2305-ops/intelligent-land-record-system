from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import District, Tehsil, Village, MasterLandRecord
from fastapi import HTTPException

router = APIRouter()

@router.get("/districts")
def get_districts(db: Session = Depends(get_db)):
    districts = db.query(District).all()
    return [{"id": d.id, "name": d.name, "code": d.code, "state": d.state} for d in districts]

@router.get("/tehsils")
def get_tehsils(district_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Tehsil)
    if district_id:
        query = query.filter(Tehsil.district_id == district_id)
    tehsils = query.all()
    return [{"id": t.id, "district_id": t.district_id, "name": t.name, "code": t.code} for t in tehsils]

@router.get("/villages")
def get_villages(tehsil_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Village)
    if tehsil_id:
        query = query.filter(Village.tehsil_id == tehsil_id)
    villages = query.all()
    return [{"id": v.id, "tehsil_id": v.tehsil_id, "name": v.name, "code": v.code} for v in villages]

@router.get("/samples")
def get_sample_documents():
    """Returns empty list as sample documents have been removed."""
    return []

@router.get("/records")
def get_master_records(db: Session = Depends(get_db)):
    records = db.query(MasterLandRecord).all()
    return records

@router.get("/records/{id}")
def get_master_record(id: int, db: Session = Depends(get_db)):
    record = db.query(MasterLandRecord).filter(MasterLandRecord.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Master record not found")
    return record


