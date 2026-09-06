from typing import Dict, Any, Tuple
from app.core.config import settings

class ConfidenceService:
    @staticmethod
    def calculate_confidence(field_details: Dict[str, Any], ocr_confidence: float = 0.85) -> Tuple[float, str]:
        """
        Calculates normalized confidence score (0.0 to 1.0) and assigns HIGH, MEDIUM, or LOW rating.
        """
        scores = []
        for key, field_info in field_details.items():
            if isinstance(field_info, dict):
                conf = field_info.get("confidence", 0.0)
                # Give higher weight to critical fields
                if key in ["owner_name", "survey_number", "village", "district"]:
                    scores.extend([conf, conf])  # Double weight
                else:
                    scores.append(conf)

        if not scores:
            avg_score = 0.50
        else:
            avg_score = sum(scores) / len(scores)

        # Blend with OCR confidence
        overall = round(0.70 * avg_score + 0.30 * ocr_confidence, 2)

        if overall >= settings.HIGH_CONFIDENCE_THRESHOLD:
            level = "HIGH"
        elif overall >= settings.MEDIUM_CONFIDENCE_THRESHOLD:
            level = "MEDIUM"
        else:
            level = "LOW"

        return overall, level
