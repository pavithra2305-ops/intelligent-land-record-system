import os
import fitz
from typing import Tuple
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

_rapidocr_engine = None
_easyocr_reader = None

def get_rapidocr_engine():
    global _rapidocr_engine
    if _rapidocr_engine is None:
        try:
            from rapidocr_onnxruntime import RapidOCR
            print("[OCR SERVICE] Initializing lightweight RapidOCR Engine (ONNX Runtime ~35MB RAM)...")
            _rapidocr_engine = RapidOCR()
        except Exception as err:
            print(f"[OCR SERVICE WARNING] RapidOCR init failed: {err}")
            _rapidocr_engine = False
    return _rapidocr_engine if _rapidocr_engine is not False else None

def get_easyocr_reader():
    global _easyocr_reader
    # Do NOT load heavy EasyOCR PyTorch model on Render / Free tier (512MB RAM limit)
    is_render_production = bool(os.environ.get("RENDER")) or os.environ.get("DISABLE_HEAVY_OCR", "").lower() in ["true", "1"]
    if is_render_production:
        print("[OCR SERVICE INFO] Heavy PyTorch EasyOCR skipped in production (512MB RAM guard active).")
        return None

    if _easyocr_reader is None:
        try:
            import easyocr
            print("[OCR SERVICE] Initializing local EasyOCR Reader (PyTorch)...")
            _easyocr_reader = easyocr.Reader(['en'], verbose=False)
        except Exception as err:
            print(f"[OCR SERVICE WARNING] EasyOCR init failed: {err}")
            _easyocr_reader = False
    return _easyocr_reader if _easyocr_reader is not False else None

class BaseOCRService:
    def extract_text(self, document_path: str, preprocessed_image_path: str, language: str = "English") -> Tuple[str, str]:
        raise NotImplementedError

class OCRService(BaseOCRService):
    def extract_text(self, document_path: str, preprocessed_image_path: str, language: str = "English") -> Tuple[str, str]:
        ext = os.path.splitext(document_path)[1].lower()

        # 1. Try PyMuPDF text extraction if file is PDF (< 10MB RAM)
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

        candidate_image_paths = []
        if ext != ".pdf" and document_path and os.path.exists(document_path):
            candidate_image_paths.append(document_path)
        if preprocessed_image_path and os.path.exists(preprocessed_image_path):
            candidate_image_paths.append(preprocessed_image_path)

        # 2. Try RapidOCR (ONNX Runtime, ~35MB RAM - Ideal for Production & Local)
        rapid_engine = get_rapidocr_engine()
        if rapid_engine:
            for img_path in candidate_image_paths:
                try:
                    res, _ = rapid_engine(img_path)
                    if res:
                        lines = [item[1] for item in res if item and len(item) > 1 and item[1]]
                        extracted_text = "\n".join(lines).strip()
                        if len(extracted_text) > 5:
                            print(f"[OCR SERVICE] Successfully extracted {len(extracted_text)} chars using RapidOCR (ONNX) from {os.path.basename(img_path)}.")
                            return extracted_text, "RapidOCR (ONNX Runtime)"
                except Exception as r_err:
                    print(f"[OCR SERVICE] RapidOCR path error ({img_path}): {r_err}")
                    continue

        # 3. Try EasyOCR (PyTorch, local dev fallback)
        try:
            reader = get_easyocr_reader()
            if reader:
                for img_path in candidate_image_paths:
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

        # 4. Try Tesseract OCR if pytesseract is available
        if pytesseract:
            for target_img in candidate_image_paths:
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

        # 5. Fallback clean notice (never crashes process)
        filename = os.path.basename(document_path)
        print(f"[OCR SERVICE WARNING] No text could be extracted for {filename}.")
        return f"OCR NOTICE: No text could be extracted from uploaded document '{filename}'.", "OCR Engine (No Text Found)"
