import os
import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.core.config import settings
from app.models import (
    User, District, Tehsil, Village, Document, LandRecord,
    ExtractionResult, ValidationResult, AuditLog, Parcel,
    MasterLandRecord, MasterParcel, RoleEnum, ValidationStatusEnum
)

def run_schema_migration():
    """
    Safely ensures existing SQLite tables contain all model columns via ALTER TABLE.
    Does not drop tables or delete data.
    """
    from sqlalchemy import text
    with engine.connect() as conn:
        # 1. Update extraction_results table
        try:
            res = conn.execute(text("PRAGMA table_info(extraction_results)")).fetchall()
            cols = {row[1] for row in res}
            if cols:
                if "ocr_engine_used" not in cols:
                    conn.execute(text("ALTER TABLE extraction_results ADD COLUMN ocr_engine_used VARCHAR DEFAULT 'Dynamic OCR Engine'"))
                    conn.commit()
                if "extraction_source" not in cols:
                    conn.execute(text("ALTER TABLE extraction_results ADD COLUMN extraction_source VARCHAR DEFAULT 'Regex Extraction Engine'"))
                    conn.commit()
        except Exception as e:
            print(f"[MIGRATION NOTICE] extraction_results schema check: {e}")

        # 2. Update documents table
        try:
            res = conn.execute(text("PRAGMA table_info(documents)")).fetchall()
            cols = {row[1] for row in res}
            if cols and "document_hash" not in cols:
                conn.execute(text("ALTER TABLE documents ADD COLUMN document_hash VARCHAR"))
                conn.commit()
                print("[MIGRATION] Added column 'document_hash' to 'documents' table.")
        except Exception as e:
            print(f"[MIGRATION NOTICE] documents schema check: {e}")

        # 3. Update validation_results table
        try:
            res = conn.execute(text("PRAGMA table_info(validation_results)")).fetchall()
            cols = {row[1] for row in res}
            if cols:
                if "master_match_status" not in cols:
                    conn.execute(text("ALTER TABLE validation_results ADD COLUMN master_match_status VARCHAR DEFAULT 'NOT_FOUND'"))
                    conn.commit()
                if "gis_match_status" not in cols:
                    conn.execute(text("ALTER TABLE validation_results ADD COLUMN gis_match_status VARCHAR DEFAULT 'GIS_NOT_FOUND'"))
                    conn.commit()
                if "duplicate_status" not in cols:
                    conn.execute(text("ALTER TABLE validation_results ADD COLUMN duplicate_status VARCHAR DEFAULT 'NO_DUPLICATE'"))
                    conn.commit()
                if "field_comparison_details" not in cols:
                    conn.execute(text("ALTER TABLE validation_results ADD COLUMN field_comparison_details JSON"))
                    conn.commit()
        except Exception as e:
            print(f"[MIGRATION NOTICE] validation_results schema check: {e}")

def seed_database():
    Base.metadata.create_all(bind=engine)
    run_schema_migration()
    db: Session = SessionLocal()

    try:
        # 1. Seed Users
        admin = db.query(User).filter(User.email == "admin@landgov.in").first()
        if not admin:
            admin = User(
                email="admin@landgov.in",
                password_hash=get_password_hash("admin123"),
                full_name="Rajesh Sharma (Admin)",
                role=RoleEnum.ADMIN.value
            )
            db.add(admin)

        verifier = db.query(User).filter(User.email == "verifier@landgov.in").first()
        if not verifier:
            verifier = User(
                email="verifier@landgov.in",
                password_hash=get_password_hash("verifier123"),
                full_name="Priya Raman (Verifier)",
                role=RoleEnum.VERIFIER.value
            )
            db.add(verifier)

        v_default = db.query(User).filter(User.email == "viewer@landgov.in").first()
        if not v_default:
            v_default = User(
                email="viewer@landgov.in",
                password_hash=get_password_hash("viewer123"),
                full_name="Ramesh Kumar",
                role=RoleEnum.VIEWER.value
            )
            db.add(v_default)

        v1 = db.query(User).filter(User.email == "viewer1@landgov.in").first()
        if not v1:
            v1 = User(
                email="viewer1@landgov.in",
                password_hash=get_password_hash("viewer123"),
                full_name="Ramesh Kumar",
                role=RoleEnum.VIEWER.value
            )
            db.add(v1)

        v2 = db.query(User).filter(User.email == "viewer2@landgov.in").first()
        if not v2:
            v2 = User(
                email="viewer2@landgov.in",
                password_hash=get_password_hash("viewer123"),
                full_name="Priya Kumar",
                role=RoleEnum.VIEWER.value
            )
            db.add(v2)

        db.commit()
        print("[OK] Seeded Admin, Verifier, and Viewer accounts")

        # 2. Seed Master Locations
        if db.query(District).count() == 0:
            d1 = District(name="Kancheepuram", code="DIST-TN-01")
            d2 = District(name="Chengalpattu", code="DIST-TN-02")
            d3 = District(name="Coimbatore", code="DIST-TN-03")
            db.add_all([d1, d2, d3])
            db.commit()

            t1 = Tehsil(district_id=d1.id, name="Sriperumbudur", code="TH-01")
            t2 = Tehsil(district_id=d1.id, name="Kancheepuram North", code="TH-02")
            t3 = Tehsil(district_id=d2.id, name="Tambaram", code="TH-03")
            t4 = Tehsil(district_id=d2.id, name="Thiruporur", code="TH-04")
            t5 = Tehsil(district_id=d3.id, name="Pollachi", code="TH-05")
            db.add_all([t1, t2, t3, t4, t5])
            db.commit()

            vil1 = Village(tehsil_id=t1.id, name="Vallam", code="VIL-101")
            vil2 = Village(tehsil_id=t1.id, name="Sunguvarchatram", code="VIL-102")
            vil3 = Village(tehsil_id=t1.id, name="Annur", code="VIL-103")
            vil4 = Village(tehsil_id=t3.id, name="Sulur", code="VIL-201")
            vil5 = Village(tehsil_id=t3.id, name="Mudichur", code="VIL-202")
            vil6 = Village(tehsil_id=t4.id, name="Thiruporur", code="VIL-203")
            vil7 = Village(tehsil_id=t5.id, name="Anaimalai", code="VIL-301")
            vil8 = Village(tehsil_id=t5.id, name="Avinashi", code="VIL-302")
            db.add_all([vil1, vil2, vil3, vil4, vil5, vil6, vil7, vil8])
            db.commit()
            print("[OK] Seeded Districts, Tehsils, and Villages")

        # 3. Seed 10 Authoritative Master Reference Records & Master Parcels
        if db.query(MasterLandRecord).count() == 0:
            master_data = [
                {
                    "owner_name": "Balasubramanian", "survey_number": "489/3C", "khata_number": "712", "khasra_number": "KH-489/3C",
                    "plot_area": 3.10, "area_unit": "Acres", "village_name": "Thiruporur", "tehsil_name": "Thiruporur", "district_name": "Chengalpattu",
                    "land_classification": "Agricultural (Nanjai)", "ownership_details": "Joint Ownership", "mutation_number": "MUT/2026/088", "registration_number": "REG/2025/321",
                    "lat": 12.7244, "lng": 80.1863, "boundary": [[12.7240, 80.1860], [12.7248, 80.1860], [12.7248, 80.1868], [12.7240, 80.1868]]
                },
                {
                    "owner_name": "Arun Kumar", "survey_number": "215/4B", "khata_number": "903", "khasra_number": "KH-215/4B",
                    "plot_area": 5.25, "area_unit": "Acres", "village_name": "Avinashi", "tehsil_name": "Pollachi", "district_name": "Coimbatore",
                    "land_classification": "Agricultural", "ownership_details": "Sole Ownership", "mutation_number": "MUT/2025/112", "registration_number": "REG/2024/903",
                    "lat": 11.1932, "lng": 77.2684, "boundary": [[11.1930, 77.2680], [11.1938, 77.2680], [11.1938, 77.2690], [11.1930, 77.2690]]
                },
                {
                    "owner_name": "Senthil Kumar", "survey_number": "124/2A", "khata_number": "441", "khasra_number": "KH-882/1",
                    "plot_area": 2.45, "area_unit": "Acres", "village_name": "Vallam", "tehsil_name": "Sriperumbudur", "district_name": "Kancheepuram",
                    "land_classification": "Agricultural (Nanjai)", "ownership_details": "Ancestral property", "mutation_number": "MUT-2024-88492", "registration_number": "REG-2024-55102",
                    "lat": 12.9644, "lng": 79.9463, "boundary": [[12.9640, 79.9460], [12.9648, 79.9460], [12.9648, 79.9468], [12.9640, 79.9468]]
                },
                {
                    "owner_name": "Kavitha R", "survey_number": "442/3C", "khata_number": "312", "khasra_number": "KH-442/3C",
                    "plot_area": 3.12, "area_unit": "Acres", "village_name": "Anaimalai", "tehsil_name": "Pollachi", "district_name": "Coimbatore",
                    "land_classification": "Coconut Plantation", "ownership_details": "Individual", "mutation_number": "MUT/2024/442", "registration_number": "REG/2024/312",
                    "lat": 10.6609, "lng": 76.9360, "boundary": [[10.6605, 76.9355], [10.6613, 76.9355], [10.6613, 76.9365], [10.6605, 76.9365]]
                },
                {
                    "owner_name": "Rajesh V", "survey_number": "88/1B", "khata_number": "108", "khasra_number": "KH-88/1B",
                    "plot_area": 1.80, "area_unit": "Acres", "village_name": "Mudichur", "tehsil_name": "Tambaram", "district_name": "Chengalpattu",
                    "land_classification": "Residential / Punjai", "ownership_details": "Sole ownership", "mutation_number": "MUT/2024/881", "registration_number": "REG/2024/108",
                    "lat": 12.9224, "lng": 80.0811, "boundary": [[12.9220, 80.0805], [12.9228, 80.0805], [12.9228, 80.0815], [12.9220, 80.0815]]
                },
                {
                    "owner_name": "Meena K", "survey_number": "56/1", "khata_number": "201", "khasra_number": "KH-56/1",
                    "plot_area": 1.20, "area_unit": "Acres", "village_name": "Sulur", "tehsil_name": "Tambaram", "district_name": "Chengalpattu",
                    "land_classification": "Residential", "ownership_details": "Transferred via deed", "mutation_number": "MUT/2024/561", "registration_number": "REG/2024/201",
                    "lat": 12.9150, "lng": 80.0900, "boundary": [[12.9145, 80.0895], [12.9155, 80.0895], [12.9155, 80.0905], [12.9145, 80.0905]]
                },
                {
                    "owner_name": "Suresh P", "survey_number": "301/2", "khata_number": "512", "khasra_number": "KH-301/2",
                    "plot_area": 4.50, "area_unit": "Acres", "village_name": "Sunguvarchatram", "tehsil_name": "Sriperumbudur", "district_name": "Kancheepuram",
                    "land_classification": "Agricultural", "ownership_details": "Ancestral", "mutation_number": "MUT/2024/301", "registration_number": "REG/2024/512",
                    "lat": 12.9800, "lng": 79.8900, "boundary": [[12.9790, 79.8890], [12.9810, 79.8890], [12.9810, 79.8910], [12.9790, 79.8910]]
                },
                {
                    "owner_name": "Anitha M", "survey_number": "112/5A", "khata_number": "604", "khasra_number": "KH-112/5A",
                    "plot_area": 2.15, "area_unit": "Acres", "village_name": "Annur", "tehsil_name": "Sriperumbudur", "district_name": "Kancheepuram",
                    "land_classification": "Agricultural", "ownership_details": "Individual", "mutation_number": "MUT/2024/112", "registration_number": "REG/2024/604",
                    "lat": 12.9700, "lng": 79.9200, "boundary": [[12.9695, 79.9195], [12.9705, 79.9195], [12.9705, 79.9205], [12.9695, 79.9205]]
                },
                {
                    "owner_name": "Dinesh R", "survey_number": "78/4", "khata_number": "802", "khasra_number": "KH-78/4",
                    "plot_area": 6.80, "area_unit": "Acres", "village_name": "Anaimalai", "tehsil_name": "Pollachi", "district_name": "Coimbatore",
                    "land_classification": "Agricultural", "ownership_details": "Self-acquired", "mutation_number": "MUT/2024/784", "registration_number": "REG/2024/802",
                    "lat": 10.6550, "lng": 76.9300, "boundary": [[10.6540, 76.9290], [10.6560, 76.9290], [10.6560, 76.9310], [10.6540, 76.9310]]
                },
                {
                    "owner_name": "Lakshmi S", "survey_number": "99/1C", "khata_number": "115", "khasra_number": "KH-99/1C",
                    "plot_area": 0.95, "area_unit": "Acres", "village_name": "Mudichur", "tehsil_name": "Tambaram", "district_name": "Chengalpattu",
                    "land_classification": "Residential", "ownership_details": "Sole owner", "mutation_number": "MUT/2024/991", "registration_number": "REG/2024/115",
                    "lat": 12.9260, "lng": 80.0850, "boundary": [[12.9255, 80.0845], [12.9265, 80.0845], [12.9265, 80.0855], [12.9255, 80.0855]]
                }
            ]

            for item in master_data:
                rec = MasterLandRecord(
                    owner_name=item["owner_name"],
                    survey_number=item["survey_number"],
                    khasra_number=item["khasra_number"],
                    khata_number=item["khata_number"],
                    plot_area=item["plot_area"],
                    area_unit=item["area_unit"],
                    village_name=item["village_name"],
                    tehsil_name=item["tehsil_name"],
                    district_name=item["district_name"],
                    land_classification=item["land_classification"],
                    ownership_details=item["ownership_details"],
                    mutation_number=item["mutation_number"],
                    registration_number=item["registration_number"]
                )
                db.add(rec)
                db.commit()
                db.refresh(rec)

                master_parcel = MasterParcel(
                    master_land_record_id=rec.id,
                    survey_number=item["survey_number"],
                    district_name=item["district_name"],
                    tehsil_name=item["tehsil_name"],
                    village_name=item["village_name"],
                    owner_name=item["owner_name"],
                    lat=item["lat"],
                    lng=item["lng"],
                    boundary=item["boundary"],
                    area_acre=item["plot_area"],
                    land_classification=item["land_classification"]
                )
                db.add(master_parcel)
                db.commit()

            print("[OK] Seeded 10 Master Reference Records & Master Parcels successfully")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

