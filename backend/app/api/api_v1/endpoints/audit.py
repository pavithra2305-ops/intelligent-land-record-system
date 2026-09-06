from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.schemas.schemas import AuditLogResponse
from app.models import AuditLog, User, RoleEnum

router = APIRouter()

@router.get("", response_model=List[AuditLogResponse])
def get_audit_logs(
    action: Optional[str] = None,
    user_email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([RoleEnum.ADMIN.value]))
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_email:
        query = query.filter(AuditLog.user_email.ilike(f"%{user_email}%"))

    return query.order_by(AuditLog.id.desc()).limit(100).all()
