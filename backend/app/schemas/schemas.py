from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# Auth Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "VIEWER"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Field level detail schema for 2-column view
class FieldValueConfidence(BaseModel):
    value: Optional[Any] = None
    confidence: float = 0.0
    confidence_level: str = "LOW" # HIGH, MEDIUM, LOW
    status: str = "VALID" # VALID, WARNING, INVALID

# Document Schemas
class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    document_hash: Optional[str] = None
    language: str
    document_type: str
    status: str
    processing_stage: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MasterLandRecordResponse(BaseModel):
    id: int
    owner_name: str
    survey_number: str
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_area: float
    area_unit: str = "Acres"
    village_name: str
    tehsil_name: str
    district_name: str
    land_classification: Optional[str] = None
    ownership_details: Optional[str] = None
    mutation_number: Optional[str] = None
    registration_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MasterParcelResponse(BaseModel):
    id: int
    master_land_record_id: Optional[int] = None
    survey_number: str
    district_name: str
    tehsil_name: str
    village_name: str
    owner_name: str
    lat: float
    lng: float
    boundary: Optional[List[List[float]]] = None
    area_acre: float
    land_classification: str

    class Config:
        from_attributes = True

# Land Record Schemas
class LandRecordUpdate(BaseModel):
    owner_name: Optional[str] = None
    survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_area: Optional[float] = None
    area_unit: Optional[str] = "Acres"
    district_name: Optional[str] = None
    tehsil_name: Optional[str] = None
    village_name: Optional[str] = None
    land_classification: Optional[str] = None
    ownership_details: Optional[str] = None
    mutation_number: Optional[str] = None
    registration_number: Optional[str] = None
    comment: Optional[str] = None

class LandRecordResponse(BaseModel):
    id: int
    document_id: int
    owner_name: Optional[str] = None
    survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_area: Optional[float] = None
    area_unit: Optional[str] = "Acres"
    district_name: Optional[str] = None
    tehsil_name: Optional[str] = None
    village_name: Optional[str] = None
    land_classification: Optional[str] = None
    ownership_details: Optional[str] = None
    mutation_number: Optional[str] = None
    registration_number: Optional[str] = None
    confidence_score: float = 0.0
    confidence_level: str = "LOW"
    validation_status: str = "WARNING"
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    verifier_comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StructuredExtractionDetail(BaseModel):
    owner_name: FieldValueConfidence
    survey_number: FieldValueConfidence
    khasra_number: FieldValueConfidence
    khata_number: FieldValueConfidence
    plot_area: FieldValueConfidence
    area_unit: FieldValueConfidence
    village: FieldValueConfidence
    tehsil: FieldValueConfidence
    district: FieldValueConfidence
    land_classification: FieldValueConfidence
    ownership_details: FieldValueConfidence
    mutation_number: FieldValueConfidence
    registration_number: FieldValueConfidence

class ExtractionResponse(BaseModel):
    document_id: int
    document_type: str
    classification_confidence: float
    raw_ocr_text: str
    extracted_fields: Dict[str, Any]
    field_details: Dict[str, FieldValueConfidence]
    overall_confidence: float
    confidence_level: str
    ocr_engine_used: str = "Dynamic OCR Engine"
    extraction_source: str = "Regex Extraction Engine"
    validation: Dict[str, Any]

class VerificationApprovalRequest(BaseModel):
    comments: Optional[str] = "Approved by verifier"

class VerificationRejectionRequest(BaseModel):
    comments: str # Required on rejection

# Dashboard Statistics Schemas
class DashboardStatsResponse(BaseModel):
    total_documents: int
    processed_documents: int
    verified_records: int
    pending_verification: int
    validation_errors: int
    average_confidence: float
    overall_accuracy: float
    time_series: List[Dict[str, Any]]
    verification_breakdown: List[Dict[str, Any]]
    document_type_distribution: List[Dict[str, Any]]
    district_distribution: List[Dict[str, Any]]
    validation_error_categories: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]

# GIS Schema
class ParcelResponse(BaseModel):
    id: int
    land_record_id: Optional[int] = None
    survey_number: str
    district_name: str
    tehsil_name: str
    village_name: str
    owner_name: str
    lat: float
    lng: float
    boundary: Optional[List[List[float]]] = None
    area_acre: float
    land_classification: str

# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    entity: str
    entity_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    timestamp: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True
