import os
import fitz
from typing import Tuple
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None

class BaseOCRService:
    def extract_text(self, document_path: str, preprocessed_image_path: str, language: str = "English") -> Tuple[str, str]:
        raise NotImplementedError

class OCRService(BaseOCRService):
    def extract_text(self, document_path: str, preprocessed_image_path: str, language: str = "English") -> Tuple[str, str]:
        # 1. Try PyMuPDF text extraction if file is PDF
        ext = os.path.splitext(document_path)[1].lower()
        if ext == ".pdf":
            try:
                doc = fitz.open(document_path)
                pdf_text = ""
                for page in doc:
                    pdf_text += page.get_text() + "\n"
                if len(pdf_text.strip()) > 10:
                    return pdf_text.strip(), "PyMuPDF Engine"
            except Exception:
                pass

        # 2. Try EasyOCR Deep Learning Engine
        try:
            import easyocr
            reader = easyocr.Reader(['en'], verbose=False)
            paths_to_try = []
            if ext != ".pdf" and document_path and os.path.exists(document_path):
                paths_to_try.append(document_path)
            if preprocessed_image_path and os.path.exists(preprocessed_image_path):
                paths_to_try.append(preprocessed_image_path)
            if ext == ".pdf" and document_path and os.path.exists(document_path):
                paths_to_try.append(document_path)

            for img_path in paths_to_try:
                try:
                    ocr_results = reader.readtext(img_path, detail=0)
                    if ocr_results:
                        extracted_text = "\n".join(ocr_results).strip()
                        if len(extracted_text) > 5:
                            return extracted_text, "EasyOCR Deep Learning Engine"
                except Exception as img_err:
                    continue
        except Exception:
            pass

        # 3. Try Tesseract OCR if pytesseract is available
        if pytesseract:
            paths_to_try = []
            if preprocessed_image_path and os.path.exists(preprocessed_image_path):
                paths_to_try.append(preprocessed_image_path)
            if ext != ".pdf" and document_path and os.path.exists(document_path):
                paths_to_try.append(document_path)

            for target_img in paths_to_try:
                try:
                    lang_code = "tam+eng" if language.lower() == "tamil" else "eng"
                    img = Image.open(target_img)
                    ocr_text = pytesseract.image_to_string(img, lang=lang_code).strip()
                    if len(ocr_text) > 10:
                        return ocr_text, f"Tesseract OCR ({lang_code})"
                except Exception:
                    continue

        # 4. If no text could be extracted, return clean OCR notice
        filename = os.path.basename(document_path)
        return f"OCR NOTICE: No text could be extracted from uploaded document '{filename}'.", "OCR Engine (No Text Found)"
