from typing import Dict, Any

class ClassificationService:
    @staticmethod
    def classify_document(ocr_text: str, filename: str = "") -> Dict[str, Any]:
        text = (ocr_text + " " + filename).lower()
        
        mutation_keywords = ["mutation", "chitta extract", "mut-", "date of mutation", "மாற்ற உத்தரவு", "சிட்டா"]
        sale_keywords = ["sale deed", "registration", "reg-", "buyer", "consideration", "stamps department", "பத்திரப் பதிவு", "விற்பனை"]
        ownership_keywords = ["patta", "record of rights", "khasra", "khata", "owner", "ownership", "பட்டா", "உரிமையாளர்"]

        mutation_score = sum(1 for kw in mutation_keywords if kw in text)
        sale_score = sum(1 for kw in sale_keywords if kw in text)
        ownership_score = sum(1 for kw in ownership_keywords if kw in text)

        scores = {
            "Mutation Record": mutation_score,
            "Sale / Registration Record": sale_score,
            "Ownership Record": ownership_score
        }

        best_match = max(scores, key=scores.get)
        max_score = scores[best_match]

        if max_score == 0:
            return {"document_type": "Ownership Record", "confidence": 0.75}

        confidence = round(min(0.70 + (max_score * 0.08), 0.98), 2)
        return {"document_type": best_match, "confidence": confidence}
