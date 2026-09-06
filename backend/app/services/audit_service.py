from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models import AuditLog, User

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        entity: str,
        entity_id: Optional[int] = None,
        user: Optional[User] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = "127.0.0.1"
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user.id if user else None,
            user_email=user.email if user else "system@landgov.in",
            action=action,
            entity=entity,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
