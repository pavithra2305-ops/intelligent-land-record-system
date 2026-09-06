from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models import MasterParcel, User
from app.schemas.schemas import MasterParcelResponse

router = APIRouter()

@router.get("/parcels", response_model=List[MasterParcelResponse])
def get_parcels(
    district: Optional[str] = None,
    tehsil: Optional[str] = None,
    village: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MasterParcel)
    if district:
        query = query.filter(MasterParcel.district_name.ilike(f"%{district}%"))
    if tehsil:
        query = query.filter(MasterParcel.tehsil_name.ilike(f"%{tehsil}%"))
    if village:
        query = query.filter(MasterParcel.village_name.ilike(f"%{village}%"))

    parcels = query.all()
    return parcels


