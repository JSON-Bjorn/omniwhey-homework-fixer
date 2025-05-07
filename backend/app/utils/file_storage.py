import os
import shutil
import uuid
from fastapi import UploadFile
from pathlib import Path
from typing import Tuple


def get_file_storage_path():
    """Get the base path for file storage"""
    # Use a directory within the project for file storage
    storage_dir = Path(__file__).resolve().parent.parent.parent.parent / "uploads"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def validate_file_type(extension: str) -> bool:
    """Validate if the file extension is allowed"""
    allowed_extensions = [".pdf", ".docx", ".txt", ".ipynb"]
    return extension in allowed_extensions


def save_uploaded_file(file: UploadFile, user_id: int) -> Tuple[str, str]:
    """
    Save uploaded file to storage

    Returns:
        Tuple[str, str]: (file_path, file_type)
    """
    file_extension = get_file_extension(file.filename)

    if not validate_file_type(file_extension):
        raise ValueError(f"File type {file_extension} is not allowed")

    # Create user directory if it doesn't exist
    storage_path = get_file_storage_path()
    user_dir = storage_path / f"user_{user_id}"
    user_dir.mkdir(exist_ok=True)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = user_dir / unique_filename

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get file type (mime type)
    file_type_map = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".ipynb": "application/x-ipynb+json",
    }

    file_type = file_type_map.get(file_extension, "application/octet-stream")

    # Return the relative path (from storage_path)
    return f"user_{user_id}/{unique_filename}", file_type


def get_file_path(relative_path: str) -> Path:
    """
    Get absolute file path from relative path

    Args:
        relative_path: Path relative to the storage directory

    Returns:
        Path: Absolute file path
    """
    storage_path = get_file_storage_path()
    return storage_path / relative_path


def delete_file(relative_path: str) -> bool:
    """
    Delete a file from storage

    Args:
        relative_path: Path relative to the storage directory

    Returns:
        bool: True if deletion was successful
    """
    file_path = get_file_path(relative_path)

    try:
        if file_path.exists():
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
