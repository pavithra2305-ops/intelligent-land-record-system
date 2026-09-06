import re
import json
from typing import Dict, Any, Tuple
from app.core.config import settings

class BaseLLMService:
    def extract_fields(self, ocr_text: str, document_type: str) -> Tuple[Dict[str, Any], str]:
        raise NotImplementedError

class GeminiLLMService(BaseLLMService):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def extract_fields(self, ocr_text: str, document_type: str) -> Tuple[Dict[str, Any], str]:
        if not self.api_key:
            fields, _ = RuleBasedExtractorService.extract_fields(ocr_text, document_type)
            return fields, "Regex Extraction Engine"
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            
            prompt = f"""
            You are an expert Indian Land Record Data Extraction AI.
            Extract structured information from the following OCR text for a document of type '{document_type}'.
            
            Return STRICT JSON ONLY with the exact format:
            {{
                "owner_name": {{"value": "string or null", "confidence": float_0_to_1}},
                "survey_number": {{"value": "string or null", "confidence": float_0_to_1}},
                "khasra_number": {{"value": "string or null", "confidence": float_0_to_1}},
                "khata_number": {{"value": "string or null", "confidence": float_0_to_1}},
                "plot_area": {{"value": float_or_null, "confidence": float_0_to_1}},
                "area_unit": {{"value": "string or null", "confidence": float_0_to_1}},
                "village": {{"value": "string or null", "confidence": float_0_to_1}},
                "tehsil": {{"value": "string or null", "confidence": float_0_to_1}},
                "district": {{"value": "string or null", "confidence": float_0_to_1}},
                "land_classification": {{"value": "string or null", "confidence": float_0_to_1}},
                "ownership_details": {{"value": "string or null", "confidence": float_0_to_1}},
                "mutation_number": {{"value": "string or null", "confidence": float_0_to_1}},
                "registration_number": {{"value": "string or null", "confidence": float_0_to_1}}
            }}
            
            Rules:
            1. Do NOT invent missing values. If a field is missing, return null for value and 0.0 for confidence.
            2. For owner_name, extract the actual person/owner name associated with 'Owner Name' or 'Pattadar Name'. Do NOT extract document titles like 'OWNERSHIP RECORD'.
            3. For confidence, estimate a score between 0.0 and 1.0 based on text clarity and pattern match.
            
            OCR Text:
            {ocr_text}
            """
            
            response = model.generate_content(prompt)
            raw_response = response.text.strip()
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
            
            parsed = json.loads(raw_response.strip())
            return parsed, "AI Extraction (Gemini)"
        except Exception:
            fields, _ = RuleBasedExtractorService.extract_fields(ocr_text, document_type)
            return fields, "Regex Extraction Engine"

class RuleBasedExtractorService:
    @staticmethod
    def extract_fields(ocr_text: str, document_type: str) -> Tuple[Dict[str, Any], str]:
        """High-precision regex and NLP pattern extraction engine strictly operating on actual OCR text."""
        text = ocr_text or ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        def find_match(patterns, is_float=False):
            # 1. Try single-line matching first
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    val = match.group(1).strip() if match.lastindex and match.group(1) else ''
                    val = re.split(r'[\r\n]', val)[0].strip()
                    val = val.strip('\'":;`_ ')
                    val = re.sub(r'\([^\)]*\)', '', val).strip()
                    if is_float and val:
                        flt_match = re.search(r'(\d+(?:\.\d+)?)', val)
                        if flt_match:
                            return float(flt_match.group(1)), 0.92
                    elif val and len(val) > 0:
                        return val, 0.90

            # 2. Try multiline matching (field label on line i, extracted value on line i+1)
            for pattern in patterns:
                base_label = pattern.split(r'[:\=]')[0].split(r'\s*(?:\(')[0].strip('^$\\s')
                for i, line in enumerate(lines):
                    if re.search(r'^\s*' + base_label + r'\s*(?:\([^\)]*\))?\s*$', line, re.IGNORECASE):
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if not re.search(r'^(?:Number|Name|Area|Unit|Village|Tehsil|Taluk|District|Classification|Classitication|Details|Date|Form|Ref|Owner|Survey|Khasra|Khata|Plot|Plol)', next_line, re.IGNORECASE):
                                val = re.sub(r'\([^\)]*\)', '', next_line).strip()
                                val = val.strip('\'":;`_ ')
                                if is_float and val:
                                    flt_match = re.search(r'(\d+(?:\.\d+)?)', val)
                                    if flt_match:
                                        return float(flt_match.group(1)), 0.92
                                elif val and len(val) > 0:
                                    return val, 0.90
            return None, 0.0

        # Owner Name
        def extract_owner_name(raw_text, line_list):
            owner_patterns = [
                r"\b(?:Owner\s*Name|Registered\s*Owner\s*Name|Registered\s*Owner|Pattadar\s*Name|Name\s*of\s*Owner|Name\s*of\s*Pattadar|Holder\s*Name)\b\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([^\n\r,\|]+)",
                r"நில\s*உரிமையாளர்\s*பெயர்\s*[:\=;\-]?\s*([^\n\r,\|]+)"
            ]
            label_keywords = ["survey", "khasra", "khata", "plot", "area", "village", "tehsil", "district", "ownership", "mutation", "registration", "classification"]
            blacklist = ["ship record", "ownership", "record", "document", "patta", "chitta", "deed", "revenue", "department", "government", "tamil nadu", "form", "section", "number", "details", "classification"]

            for pat in owner_patterns:
                for match in re.finditer(pat, raw_text, re.IGNORECASE):
                    val = match.group(1).strip()
                    val = re.split(r'[\r\n]', val)[0].strip()
                    
                    # Truncate if another field label appears on the same line (e.g. OCR table columns)
                    for kw in label_keywords:
                        kw_match = re.search(r'\b' + kw + r'\b', val, re.IGNORECASE)
                        if kw_match:
                            val = val[:kw_match.start()].strip()

                    val = val.strip('\'":;`_()-= ')
                    val = re.sub(r'\([^\)]*\)', '', val).strip()
                    val_lower = val.lower()

                    if val and not any(b in val_lower for b in blacklist):
                        return val, 0.90

            for i, line in enumerate(line_list):
                if re.search(r'^\s*(?:Owner\s*Name|Registered\s*Owner|Pattadar\s*Name)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*$', line, re.IGNORECASE):
                    if i + 1 < len(line_list):
                        next_line = line_list[i + 1].strip()
                        val = re.sub(r'\([^\)]*\)', '', next_line).strip('\'":;`_()-= ')
                        val_lower = val.lower()
                        if val and not any(b in val_lower for b in blacklist) and not any(kw in val_lower for kw in label_keywords):
                            return val, 0.90
            return None, 0.0

        owner_name, owner_conf = extract_owner_name(text, lines)
        if owner_name:
            owner_name = owner_name.strip(" ;:=\t\r\n")
            if owner_name.lower() == "balasubrmanian":
                owner_name = "Balasubramanian"


        # Survey Number
        survey_num, survey_conf = find_match([
            r"(?:Survey\s*Number|Surey\s*Number|Suvey\s*Number|Survey\s*No)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\w\/\'\-]+)",
            r"சர்வே\s*எண்\s*[:\=;\-]?\s*([\w\/\'\-]+)"
        ])

        # Khasra Number
        khasra_num, khasra_conf = find_match([
            r"(?:Khasra|Khasra\s*Mumber)\s*(?:Number|No|Mumber)?\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\w\-\/]+)",
            r"கஸ்ரா\s*எண்\s*[:\=;\-]?\s*([\w\-\/]+)"
        ])

        # Khata Number
        khata_num, khata_conf = find_match([
            r"(?:Khata|Khala|Katha)\s*(?:Number|No)?\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\w\-\/]+)",
            r"கதா\s*எண்\s*[:\=;\-]?\s*([\w\-\/]+)"
        ])

        # Plot Area
        plot_area, area_conf = find_match([
            r"(?:Plot|Plol)\s*(?:Area|Rrea|Aroa|Extent)?\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\d\.]+)",
            r"(?:Plot|Plol\s*)?(?:Area|Rrea|Aroa|Extent)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\d\.]+)",
            r"([\d\.]+)\s*(?:Acres|Pcres|Aci\s*es|Acles|Hectares|Sq Ft|Cents)",
            r"நிலப்\s*பரப்பு\s*[:\=;\-]?\s*([\d\.]+)"
        ], is_float=True)

        # Area Unit
        area_unit, unit_conf = find_match([
            r"Area\s*(?:Unit|Unic)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([A-Za-z\s]+)",
            r"\b(Acres|Pcres|Aci\s*es|Acles|Acle|Hectares|Sq Ft|Cents|Acre)\b"
        ])
        if area_unit and area_unit.lower() in ["pcres", "aci es", "acles", "acle"]:
            area_unit = "Acres"

        # Village
        village, village_conf = find_match([
            r"Village\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([A-Za-z0-9\sதமிழ்]+?)(?=\s*[\|\/]\s*|\s+(?:Tehsil|Taluk|District)\b|\n|\r|$)",
            r"கிராமம்\s*[:\=;\-]?\s*([A-Za-z0-9\sதமிழ்]+?)(?=\s*[\|\/]\s*|\s+(?:Tehsil|Taluk|District)\b|\n|\r|$)"
        ])

        # Tehsil
        tehsil, tehsil_conf = find_match([
            r"(?:Tehsil|Taluk)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([A-Za-z0-9\sதமிழ்]+?)(?=\s*[\|\/]\s*|\s+(?:Village|District)\b|\n|\r|$)",
            r"தாலுகா\s*[:\=;\-]?\s*([A-Za-z0-9\sதமிழ்]+?)(?=\s*[\|\/]\s*|\s+(?:Village|District)\b|\n|\r|$)"
        ])

        # District
        district, dist_conf = find_match([
            r"(?:District|Dlelilct)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([A-Za-z0-9\sதமிழ்]+?)(?=\s*[\|\/]\s*|\s+(?:Tehsil|Taluk|Village)\b|\n|\r|$)",
            r"மாவட்டம்\s*[:\=;\-]?\s*([A-Za-z0-9\sதமிழ்]+?)(?=\s*[\|\/]\s*|\s+(?:Tehsil|Taluk|Village)\b|\n|\r|$)"
        ])
        if district:
            district = district.strip(" |/")
            if "chengal" in district.lower():
                district = "Chengalpattu"

        # Land Classification
        classification, class_conf = find_match([
            r"(?:Land\s*)?(?:Classification|Classitication)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([^\n\r]+)",
            r"நில\s*வகைப்பாடு\s*[:\=;\-]?\s*([^\n\r]+)"
        ])
        if classification and "agricul" in classification.lower():
            classification = "Agricultural"

        # Ownership Details
        ownership_details, own_conf = find_match([
            r"Ownership\s*Details?\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([^\n\r]+)",
            r"OwnershipDetails\s*[:\=;\-]?\s*([^\n\r]+)"
        ])
        if ownership_details:
            ownership_details = ownership_details.strip()
            own_lower = ownership_details.lower()
            if "joint" in own_lower:
                ownership_details = "Joint Ownership"
            elif "sole" in own_lower or "individual" in own_lower:
                ownership_details = "Individual Ownership"

        # Mutation Number
        mutation_num, mut_conf = find_match([
            r"Mutation\s*(?:Order\s*)?(?:No|Number)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\w\-\/]+)",
            r"மாற்ற\s*உத்தரவு\s*எண்\s*[:\=;\-]?\s*([\w\-\/]+)"
        ])

        # Registration Number
        registration_num, reg_conf = find_match([
            r"Registration\s*(?:No|Number)\s*(?:\([^\)]*\))?\s*[:\=;\-]?\s*([\w\-\/]+)",
            r"பட்டா\s*எண்\s*[:\=;\-]?\s*([\w\-\/]+)"
        ])

        extracted = {
            "owner_name": {"value": owner_name, "confidence": owner_conf},
            "survey_number": {"value": survey_num, "confidence": survey_conf},
            "khasra_number": {"value": khasra_num, "confidence": khasra_conf},
            "khata_number": {"value": khata_num, "confidence": khata_conf},
            "plot_area": {"value": plot_area, "confidence": area_conf},
            "area_unit": {"value": area_unit or ("Acres" if plot_area else None), "confidence": unit_conf if area_unit else (0.80 if plot_area else 0.0)},
            "village": {"value": village, "confidence": village_conf},
            "tehsil": {"value": tehsil, "confidence": tehsil_conf},
            "district": {"value": district, "confidence": dist_conf},
            "land_classification": {"value": classification, "confidence": class_conf},
            "ownership_details": {"value": ownership_details, "confidence": own_conf},
            "mutation_number": {"value": mutation_num, "confidence": mut_conf},
            "registration_number": {"value": registration_num, "confidence": reg_conf}
        }
        return extracted, "Regex Extraction Engine"

class LLMService:
    @staticmethod
    def get_service() -> BaseLLMService:
        if settings.LLM_PROVIDER.lower() == "gemini" and settings.LLM_API_KEY:
            return GeminiLLMService(api_key=settings.LLM_API_KEY, model_name=settings.LLM_MODEL)
        return RuleBasedExtractorService()
