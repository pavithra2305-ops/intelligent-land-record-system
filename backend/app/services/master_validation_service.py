import re
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.models import MasterLandRecord, MasterParcel

class MasterValidationService:
    @staticmethod
    def _normalize(val: Optional[str]) -> str:
        if not val:
            return ""
        s = str(val).lower().strip()
        s = re.sub(r'[\r\n\t]', ' ', s)
        s = re.sub(r'[^\w\s\/]', '', s)
        return re.sub(r'\s+', ' ', s).strip()

    @classmethod
    def validate_against_master_and_gis(cls, db: Session, extracted: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any], Optional[int], Optional[int]]:
        """
        Validates extracted document fields against authoritative MasterLandRecord and MasterParcel datasets.
        Returns: (master_match_status, gis_match_status, field_comparison_details, matched_master_id, matched_master_parcel_id)
        
        Statuses:
        - master_match_status: MATCHED, PARTIAL_MATCH, MISMATCH, NOT_FOUND
        - gis_match_status: GIS_MATCH, GIS_MISMATCH, GIS_NOT_FOUND
        """
        def get_val(key: str) -> Optional[Any]:
            item = extracted.get(key)
            if isinstance(item, dict):
                return item.get("value")
            return item

        surv_raw = get_val("survey_number")
        vill_raw = get_val("village")
        dist_raw = get_val("district")
        owner_raw = get_val("owner_name")
        area_raw = get_val("plot_area")
        khata_raw = get_val("khata_number")
        mut_raw = get_val("mutation_number")
        reg_raw = get_val("registration_number")

        surv_norm = cls._normalize(surv_raw)
        vill_norm = cls._normalize(vill_raw)
        dist_norm = cls._normalize(dist_raw)
        owner_norm = cls._normalize(owner_raw)

        # 1. Search MasterLandRecord
        master_records = db.query(MasterLandRecord).all()
        matched_master: Optional[MasterLandRecord] = None

        # Priority 1: Match by survey_number + village (or district)
        for m in master_records:
            m_surv = cls._normalize(m.survey_number)
            m_vill = cls._normalize(m.village_name)
            m_dist = cls._normalize(m.district_name)

            if surv_norm and m_surv == surv_norm:
                if (vill_norm and (vill_norm in m_vill or m_vill in vill_norm)) or (dist_norm and (dist_norm in m_dist or m_dist in dist_norm)):
                    matched_master = m
                    break

        # Priority 2: Match by owner_name if survey number lookup did not hit exact
        if not matched_master and owner_norm:
            for m in master_records:
                m_owner = cls._normalize(m.owner_name)
                if m_owner and (owner_norm in m_owner or m_owner in owner_norm):
                    matched_master = m
                    break

        # Build Field Comparison Details
        field_comparison = {}
        fields_to_compare = [
            ("owner_name", "Owner Name", owner_raw, matched_master.owner_name if matched_master else None),
            ("survey_number", "Survey Number", surv_raw, matched_master.survey_number if matched_master else None),
            ("khata_number", "Khata Number", khata_raw, matched_master.khata_number if matched_master else None),
            ("plot_area", "Plot Area", area_raw, matched_master.plot_area if matched_master else None),
            ("village", "Village", vill_raw, matched_master.village_name if matched_master else None),
            ("district", "District", dist_raw, matched_master.district_name if matched_master else None),
            ("mutation_number", "Mutation Number", mut_raw, matched_master.mutation_number if matched_master else None),
            ("registration_number", "Registration Number", reg_raw, matched_master.registration_number if matched_master else None),
        ]

        match_count = 0
        total_compared = 0

        for key, label, u_val, m_val in fields_to_compare:
            if u_val is not None or m_val is not None:
                total_compared += 1
                u_norm = cls._normalize(str(u_val)) if u_val is not None else ""
                m_norm = cls._normalize(str(m_val)) if m_val is not None else ""
                
                # Check match
                is_match = False
                if u_val is not None and m_val is not None:
                    if u_norm == m_norm or (len(u_norm) > 3 and u_norm in m_norm) or (len(m_norm) > 3 and m_norm in u_norm):
                        is_match = True
                    elif key == "plot_area":
                        try:
                            is_match = abs(float(u_val) - float(m_val)) < 0.05
                        except Exception:
                            is_match = False

                if is_match:
                    match_count += 1

                field_comparison[key] = {
                    "label": label,
                    "uploaded_value": u_val,
                    "master_value": m_val,
                    "match": is_match,
                    "status": "MATCH" if is_match else ("MISMATCH" if (u_val and m_val) else "NOT_FOUND")
                }

        # Determine Master Match Status
        if not matched_master:
            master_match_status = "NOT_FOUND"
        elif match_count == total_compared or (field_comparison.get("owner_name", {}).get("match") and field_comparison.get("survey_number", {}).get("match")):
            master_match_status = "MATCHED"
        elif field_comparison.get("owner_name", {}).get("match") or field_comparison.get("survey_number", {}).get("match"):
            master_match_status = "PARTIAL_MATCH"
        else:
            master_match_status = "MISMATCH"

        # 2. Search MasterParcel for GIS match
        master_parcels = db.query(MasterParcel).all()
        matched_parcel: Optional[MasterParcel] = None

        if surv_norm:
            for p in master_parcels:
                p_surv = cls._normalize(p.survey_number)
                p_vill = cls._normalize(p.village_name)
                p_dist = cls._normalize(p.district_name)

                if p_surv == surv_norm and ((vill_norm and vill_norm in p_vill) or (dist_norm and dist_norm in p_dist)):
                    matched_parcel = p
                    break

        if matched_parcel:
            gis_match_status = "GIS_MATCH"
        elif matched_master and matched_master.master_parcel:
            matched_parcel = matched_master.master_parcel
            gis_match_status = "GIS_MATCH"
        else:
            gis_match_status = "GIS_NOT_FOUND"

        return (
            master_match_status,
            gis_match_status,
            field_comparison,
            matched_master.id if matched_master else None,
            matched_parcel.id if matched_parcel else None
        )
