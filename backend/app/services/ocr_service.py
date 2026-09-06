import os
import fitz
from typing import Tuple
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None

_easyocr_reader = None

def get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        print("[OCR SERVICE] Initializing EasyOCR Reader (English)...")
        _easyocr_reader = easyocr.Reader(['en'], verbose=False)
    return _easyocr_reader

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
                    print("[OCR SERVICE] Successfully extracted text using PyMuPDF Engine.")
                    return pdf_text.strip(), "PyMuPDF Engine"
            except Exception as pdf_err:
                print(f"[OCR SERVICE] PyMuPDF extraction warning: {pdf_err}")

        # 2. Try EasyOCR Deep Learning Engine
        try:
            reader = get_easyocr_reader()
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
                            print(f"[OCR SERVICE] Successfully extracted {len(extracted_text)} chars using EasyOCR from {os.path.basename(img_path)}.")
                            return extracted_text, "EasyOCR Deep Learning Engine"
                except Exception as img_err:
                    print(f"[OCR SERVICE] EasyOCR candidate path error ({img_path}): {img_err}")
                    continue
        except Exception as eocr_err:
            print(f"[OCR SERVICE] EasyOCR engine warning: {eocr_err}")

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
                        print(f"[OCR SERVICE] Successfully extracted text using Tesseract OCR ({lang_code}).")
                        return ocr_text, f"Tesseract OCR ({lang_code})"
                except Exception as tess_err:
                    print(f"[OCR SERVICE] Tesseract candidate path error ({target_img}): {tess_err}")
                    continue

        # 4. If no text could be extracted, return clean OCR notice
        filename = os.path.basename(document_path)
        print(f"[OCR SERVICE WARNING] No text could be extracted for {filename}.")
        return f"OCR NOTICE: No text could be extracted from uploaded document '{filename}'.", "OCR Engine (No Text Found)"
