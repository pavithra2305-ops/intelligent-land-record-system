import os
import shutil
from typing import Tuple
from app.core.config import settings

class StorageService:
    @staticmethod
    def save_original(file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Saves original file to storage/originals and returns (relative_path, absolute_path)"""
        save_path = os.path.join(settings.STORAGE_DIR, "originals", filename)
        with open(save_path, "wb") as f:
            f.write(file_bytes)
        return os.path.join("originals", filename), save_path

    @staticmethod
    def get_processed_path(filename: str) -> str:
        base, _ = os.path.splitext(filename)
        return os.path.join(settings.STORAGE_DIR, "processed", f"{base}_processed.png")

    @staticmethod
    def get_ocr_path(filename: str) -> str:
        base, _ = os.path.splitext(filename)
        return os.path.join(settings.STORAGE_DIR, "ocr", f"{base}_ocr.txt")
