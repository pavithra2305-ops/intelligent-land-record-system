import os
import gc
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
import pymupdf  # PyMuPDF

class PreprocessingService:
    @staticmethod
    def validate_file_integrity(file_path: str, file_type: str = "") -> None:
        """
        Validates file existence, non-zero size, and image/PDF integrity using Pillow and PyMuPDF.
        Raises ValueError with a user-friendly detail message if the file is corrupted or invalid.
        """
        if not os.path.exists(file_path):
            raise ValueError("Original document file missing on server path.")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf" or file_type.lower() == "pdf":
            try:
                doc = pymupdf.open(file_path)
                if doc.page_count == 0:
                    doc.close()
                    raise ValueError("Uploaded PDF document contains no pages.")
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                if pix is None or pix.width == 0 or pix.height == 0:
                    doc.close()
                    raise ValueError("Uploaded PDF page could not be decoded or rendered.")
                doc.close()
                del pix
            except Exception as e:
                raise ValueError("Uploaded document is corrupted or invalid and cannot be processed.")
        else:
            try:
                with Image.open(file_path) as img:
                    img.verify()
                with Image.open(file_path) as img:
                    img.load()
                    _ = img.convert("RGB")
            except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Exception):
                raise ValueError("Uploaded image is corrupted or invalid and cannot be processed.")

    @staticmethod
    def preprocess_document(original_file_path: str, output_image_path: str) -> str:
        """
        Converts PDF to PNG (if PDF) or loads image safely via Pillow & OpenCV:
        - Grayscale conversion
        - CLAHE contrast enhancement
        - Fast Gaussian blur denoising
        - Adaptive thresholding & Deskewing
        - Memory bounded resizing (max 2000px)
        """
        # Step 1: Validate file integrity
        PreprocessingService.validate_file_integrity(original_file_path)

        ext = os.path.splitext(original_file_path)[1].lower()
        if ext == ".pdf":
            try:
                doc = pymupdf.open(original_file_path)
                page = doc[0]
                pix = page.get_pixmap(dpi=150)
                img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                if pix.n == 4:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
                elif pix.n == 3:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                elif pix.n == 1:
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
                doc.close()
                del pix
            except Exception as e:
                raise ValueError(f"Failed to render PDF page: {str(e)}")
        else:
            try:
                with Image.open(original_file_path) as pil_img:
                    pil_img = pil_img.convert("RGB")
                    w, h = pil_img.size
                    max_dim = 2000
                    if max(w, h) > max_dim:
                        scale = max_dim / float(max(w, h))
                        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
                        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    img_np = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                raise ValueError(f"Unable to decode uploaded image: {str(e)}")

        if img_np is None or img_np.size == 0:
            raise ValueError("Unable to decode uploaded image.")

        # Step 2: Grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        del img_np

        # Step 3: Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        del gray

        # Step 4: Fast Denoising (GaussianBlur avoids heavy C++ memory allocation of fastNlMeansDenoising)
        denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
        del enhanced

        # Step 5: Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        del denoised

        # Step 6: Deskewing
        try:
            coords = np.column_stack(np.where(thresh < 255))
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                if abs(angle) > 0.5 and abs(angle) < 45:
                    (h, w) = thresh.shape[:2]
                    center = (w // 2, h // 2)
                    M = cv2.getRotationMatrix2D(center, angle, 1.0)
                    thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        except Exception:
            pass  # Keep current image if deskew fails

        # Save output image
        cv2.imwrite(output_image_path, thresh)
        del thresh
        gc.collect()

        return output_image_path
