import re
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models import District, Tehsil, Village, ValidationStatusEnum

class ValidationService:
    @staticmethod
    def validate_record(db: Session, fields: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
        """
        Executes strict government land record validation rules.
        Returns (status, errors, warnings)
        """
        errors = []
        warnings = []

        # 1. Required Fields Check
        required_fields = ["owner_name", "survey_number", "village", "district"]
        for field in required_fields:
            val = fields.get(field)
            if isinstance(val, dict):
                val = val.get("value")
            if not val:
                errors.append(f"Missing required field: {field.replace('_', ' ').title()}")

        # 2. Survey Number Format Check
        survey_val = fields.get("survey_number")
        if isinstance(survey_val, dict):
            survey_val = survey_val.get("value")
        if survey_val:
            # Pattern e.g. 124/2A or 88/1B or 442
            if not re.match(r"^\d+[\/\w\-]*$", str(survey_val)):
                warnings.append(f"Non-standard Survey Number format: '{survey_val}'")
            if len(str(survey_val)) < 2:
                errors.append("Survey Number is suspiciously short or incomplete")

        # 3. Plot Area Validation
        area_val = fields.get("plot_area")
        if isinstance(area_val, dict):
            area_val = area_val.get("value")
        if area_val is not None:
            try:
                area_num = float(area_val)
                if area_num <= 0:
                    errors.append(f"Plot area must be positive (got {area_num})")
                elif area_num > 5000:
                    warnings.append(f"Plot area ({area_num}) is exceptionally large for standard land parcels")
            except (ValueError, TypeError):
                errors.append(f"Plot area must be a valid number (got '{area_val}')")

        # 4. Master Location Hierarchy Lookup Check
        dist_name = fields.get("district")
        if isinstance(dist_name, dict):
            dist_name = dist_name.get("value")

        tehsil_name = fields.get("tehsil")
        if isinstance(tehsil_name, dict):
            tehsil_name = tehsil_name.get("value")

        village_name = fields.get("village")
        if isinstance(village_name, dict):
            village_name = village_name.get("value")

        if dist_name and village_name:
            district_obj = db.query(District).filter(District.name.ilike(f"%{dist_name}%")).first()
            if not district_obj:
                warnings.append(f"District '{dist_name}' not found in master database registry")
            else:
                if tehsil_name:
                    tehsil_obj = db.query(Tehsil).filter(
                        Tehsil.district_id == district_obj.id,
                        Tehsil.name.ilike(f"%{tehsil_name}%")
                    ).first()
                    if not tehsil_obj:
                        warnings.append(f"Tehsil '{tehsil_name}' is not registered under District '{district_obj.name}'")

        # Determine final status
        if errors:
            status = ValidationStatusEnum.INVALID.value
        elif warnings:
            status = ValidationStatusEnum.WARNING.value
        else:
            status = ValidationStatusEnum.VALID.value

        return status, errors, warnings
