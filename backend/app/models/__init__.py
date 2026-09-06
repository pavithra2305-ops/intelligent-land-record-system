import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    VERIFIER = "VERIFIER"
    VIEWER = "VIEWER"

class DocStatusEnum(str, Enum):
    UPLOADED = "UPLOADED"
    PREPROCESSING = "PREPROCESSING"
    OCR = "OCR"
    CLASSIFICATION = "CLASSIFICATION"
    EXTRACTION = "EXTRACTION"
    VALIDATION = "VALIDATION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ValidationStatusEnum(str, Enum):
    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"
    DUPLICATE = "DUPLICATE"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default=RoleEnum.VIEWER.value, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    documents = relationship("Document", back_populates="uploaded_by")
    verified_records = relationship("LandRecord", foreign_keys="[LandRecord.verified_by_id]", back_populates="verified_by_user")
    owned_records = relationship("LandRecord", foreign_keys="[LandRecord.owner_user_id]", back_populates="owner_user")

class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    code = Column(String, unique=True, index=True)
    state = Column(String, default="Tamil Nadu")

    tehsils = relationship("Tehsil", back_populates="district")

class Tehsil(Base):
    __tablename__ = "tehsils"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    code = Column(String, index=True)

    district = relationship("District", back_populates="tehsils")
    villages = relationship("Village", back_populates="tehsil")

class Village(Base):
    __tablename__ = "villages"

    id = Column(Integer, primary_key=True, index=True)
    tehsil_id = Column(Integer, ForeignKey("tehsils.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    code = Column(String, index=True)

    tehsil = relationship("Tehsil", back_populates="villages")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    processed_path = Column(String, nullable=True)
    ocr_path = Column(String, nullable=True)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    document_hash = Column(String, index=True, nullable=True)
    language = Column(String, default="English")
    document_type = Column(String, default="Ownership Record")
    status = Column(String, default=DocStatusEnum.UPLOADED.value)
    processing_stage = Column(String, default="1/7: Uploaded")
    error_message = Column(Text, nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    uploaded_by = relationship("User", back_populates="documents")
    land_record = relationship("LandRecord", back_populates="document", uselist=False)
    extraction_result = relationship("ExtractionResult", back_populates="document", uselist=False)
    validation_result = relationship("ValidationResult", back_populates="document", uselist=False)

class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    
    owner_name = Column(String, index=True)
    survey_number = Column(String, index=True)
    khasra_number = Column(String, nullable=True)
    khata_number = Column(String, nullable=True)
    plot_area = Column(Float, nullable=True)
    area_unit = Column(String, default="Acres")
    
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    tehsil_id = Column(Integer, ForeignKey("tehsils.id"), nullable=True)
    village_id = Column(Integer, ForeignKey("villages.id"), nullable=True)
    
    district_name = Column(String, index=True, nullable=True)
    tehsil_name = Column(String, index=True, nullable=True)
    village_name = Column(String, index=True, nullable=True)
    
    land_classification = Column(String, nullable=True)
    ownership_details = Column(Text, nullable=True)
    mutation_number = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)
    
    confidence_score = Column(Float, default=0.0)
    confidence_level = Column(String, default="LOW") # HIGH, MEDIUM, LOW
    validation_status = Column(String, default=ValidationStatusEnum.WARNING.value)
    
    is_verified = Column(Boolean, default=False)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verifier_comments = Column(Text, nullable=True)

    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="land_record")
    verified_by_user = relationship("User", foreign_keys=[verified_by_id], back_populates="verified_records")
    owner_user = relationship("User", foreign_keys=[owner_user_id], back_populates="owned_records")
    parcel = relationship("Parcel", back_populates="land_record", uselist=False)

class MasterLandRecord(Base):
    __tablename__ = "master_land_records"

    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String, index=True, nullable=False)
    survey_number = Column(String, index=True, nullable=False)
    khasra_number = Column(String, nullable=True)
    khata_number = Column(String, nullable=True)
    plot_area = Column(Float, nullable=False)
    area_unit = Column(String, default="Acres")
    village_name = Column(String, index=True, nullable=False)
    tehsil_name = Column(String, index=True, nullable=False)
    district_name = Column(String, index=True, nullable=False)
    land_classification = Column(String, nullable=True)
    ownership_details = Column(Text, nullable=True)
    mutation_number = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    master_parcel = relationship("MasterParcel", back_populates="master_land_record", uselist=False)

class MasterParcel(Base):
    __tablename__ = "master_parcels"

    id = Column(Integer, primary_key=True, index=True)
    master_land_record_id = Column(Integer, ForeignKey("master_land_records.id"), nullable=True)
    survey_number = Column(String, index=True, nullable=False)
    district_name = Column(String, nullable=False)
    tehsil_name = Column(String, nullable=False)
    village_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    boundary = Column(JSON, nullable=True) # GeoJSON style coordinate polygon array
    area_acre = Column(Float, default=1.5)
    land_classification = Column(String, default="Agricultural")

    master_land_record = relationship("MasterLandRecord", back_populates="master_parcel")

class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    raw_ocr_text = Column(Text, nullable=True)
    structured_json = Column(JSON, nullable=True)
    field_confidences = Column(JSON, nullable=True)
    page_count = Column(Integer, default=1)
    ocr_confidence = Column(Float, default=0.85)
    ocr_engine_used = Column(String, default="Dynamic OCR Engine")
    extraction_source = Column(String, default="Regex Extraction Engine")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="extraction_result")

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    status = Column(String, default=ValidationStatusEnum.VALID.value)
    errors = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    duplicate_detected = Column(Boolean, default=False)
    duplicate_record_id = Column(Integer, nullable=True)
    similarity_score = Column(Float, default=0.0)
    master_match_status = Column(String, default="NOT_FOUND") # MATCHED, PARTIAL_MATCH, MISMATCH, NOT_FOUND
    gis_match_status = Column(String, default="GIS_NOT_FOUND") # GIS_MATCH, GIS_MISMATCH, GIS_NOT_FOUND
    duplicate_status = Column(String, default="NO_DUPLICATE") # EXACT_FILE_DUPLICATE, POTENTIAL_RECORD_DUPLICATE, NO_DUPLICATE
    field_comparison_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("Document", back_populates="validation_result")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    user_email = Column(String, nullable=True)
    action = Column(String, index=True, nullable=False)
    entity = Column(String, index=True, nullable=False)
    entity_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    ip_address = Column(String, nullable=True)

class Parcel(Base):
    __tablename__ = "parcels"

    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id"), nullable=True)
    survey_number = Column(String, index=True, nullable=False)
    district_name = Column(String, nullable=False)
    tehsil_name = Column(String, nullable=False)
    village_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    boundary = Column(JSON, nullable=True)
    area_acre = Column(Float, default=1.5)
    land_classification = Column(String, default="Agricultural")

    land_record = relationship("LandRecord", back_populates="parcel")
