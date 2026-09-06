from typing import Tuple, Optional
from sqlalchemy.orm import Session
from rapidfuzz import fuzz
from app.models import LandRecord, Document

class DuplicateService:
    @staticmethod
    def check_file_duplicate(db: Session, file_hash: str) -> Tuple[bool, Optional[int]]:
        """
        Checks SHA-256 hash of uploaded file against existing Document records.
        Returns (is_duplicate, existing_document_id)
        """
        if not file_hash:
            return False, None

        existing_doc = db.query(Document).filter(Document.document_hash == file_hash).first()
        if existing_doc:
            return True, existing_doc.id

        return False, None

    @staticmethod
    def check_duplicate(
        db: Session,
        owner_name: str,
        survey_number: str,
        village_name: str,
        district_name: str,
        current_document_id: Optional[int] = None
    ) -> Tuple[bool, Optional[int], float]:
        """
        Fuzzy matches incoming record against existing uploaded DB records using RapidFuzz.
        Returns (duplicate_detected, duplicate_record_id, similarity_score)
        """
        if not owner_name or not survey_number:
            return False, None, 0.0

        query = db.query(LandRecord)
        if current_document_id:
            query = query.filter(LandRecord.document_id != current_document_id)

        existing_records = query.all()
        best_match_id = None
        highest_score = 0.0

        for rec in existing_records:
            if not rec.owner_name or not rec.survey_number:
                continue

            owner_sim = fuzz.token_sort_ratio(owner_name.lower(), rec.owner_name.lower())
            survey_sim = 100.0 if survey_number.lower() == rec.survey_number.lower() else fuzz.ratio(survey_number.lower(), rec.survey_number.lower())
            village_sim = 100.0 if (village_name and rec.village_name and village_name.lower() in rec.village_name.lower()) else 80.0

            # Composite similarity calculation
            composite_score = (owner_sim * 0.45) + (survey_sim * 0.45) + (village_sim * 0.10)

            if composite_score > highest_score:
                highest_score = composite_score
                best_match_id = rec.id

        if highest_score >= 82.0:
            return True, best_match_id, round(highest_score / 100.0, 2)

        return False, None, round(highest_score / 100.0, 2)

