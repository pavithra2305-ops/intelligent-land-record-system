from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    auth, users, documents, verification, dashboard, gis, audit, master_data, land_records
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents & Processing"])
api_router.include_router(land_records.router, prefix="/land-records", tags=["My Land Records"])
api_router.include_router(verification.router, prefix="/verification", tags=["Human Verification Queue"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Analytics Dashboard"])
api_router.include_router(gis.router, prefix="/gis", tags=["GIS Visualization"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Audit Trail"])
api_router.include_router(master_data.router, prefix="/master", tags=["Master Location Data & Samples"])
