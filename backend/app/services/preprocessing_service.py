import os
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF

class PreprocessingService:
    @staticmethod
    def preprocess_document(original_file_path: str, output_image_path: str) -> str:
        """
        Converts PDF to PNG (if PDF) and applies OpenCV image enhancement steps:
        - Grayscale conversion
        - Resizing & Denoising
        - CLAHE contrast enhancement
        - Thresholding & Deskewing
        Saves preprocessed image to output_image_path and returns the path.
        """
        # Step 1: Render PDF to image or load image
        ext = os.path.splitext(original_file_path)[1].lower()
        if ext == ".pdf":
            doc = fitz.open(original_file_path)
            page = doc[0]
            pix = page.get_pixmap(dpi=300)
            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            if pix.n == 4:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
            elif pix.n == 3:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            elif pix.n == 1:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
        else:
            img_np = cv2.imread(original_file_path)
            if img_np is None:
                # Fallback loading via PIL
                pil_img = Image.open(original_file_path).convert("RGB")
                img_np = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        if img_np is None:
            raise ValueError(f"Could not load image from {original_file_path}")

        # Step 2: Grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        # Step 3: Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Step 4: Denoising
        denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)

        # Step 5: Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

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
        return output_image_path
