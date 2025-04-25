import os
import shutil
import uuid
from fastapi import UploadFile
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Директории для хранения
UPLOAD_DIR = "uploads"
PHOTOS_DIR = os.path.join(UPLOAD_DIR, "photos")
DOCUMENTS_DIR = os.path.join(UPLOAD_DIR, "documents")

# Создание директорий, если их нет
for directory in [UPLOAD_DIR, PHOTOS_DIR, DOCUMENTS_DIR]:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Проверена директория для загрузки: {directory}")

# Допустимые типы файлов
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
ALLOWED_DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"}

def get_file_extension(filename: str) -> str:
    """Получить расширение файла."""
    return os.path.splitext(filename)[1].lower()

async def save_upload_file(upload_file: UploadFile, directory: str) -> Optional[str]:
    """
    Сохраняет загруженный файл в указанную директорию.
    Возвращает путь к сохраненному файлу относительно корня приложения.
    """
    try:
        # Генерируем уникальное имя файла
        ext = get_file_extension(upload_file.filename)
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(directory, unique_filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        logger.info(f"Файл сохранён: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла: {str(e)}")
        return None
    finally:
        # Обязательно закрываем файл
        upload_file.file.close()

async def validate_photo_file(upload_file: UploadFile) -> bool:
    """Проверяет, является ли файл допустимым изображением."""
    ext = get_file_extension(upload_file.filename)
    is_valid = ext in ALLOWED_PHOTO_EXTENSIONS
    if not is_valid:
        logger.warning(f"Недопустимый тип фото: {ext}")
    return is_valid

async def validate_document_file(upload_file: UploadFile) -> bool:
    """Проверяет, является ли файл допустимым документом."""
    ext = get_file_extension(upload_file.filename)
    is_valid = ext in ALLOWED_DOCUMENT_EXTENSIONS
    if not is_valid:
        logger.warning(f"Недопустимый тип документа: {ext}")
    return is_valid

async def save_staff_photo(upload_file: UploadFile) -> Optional[str]:
    """Сохраняет фотографию сотрудника."""
    if not await validate_photo_file(upload_file):
        return None
    return await save_upload_file(upload_file, PHOTOS_DIR)

async def save_staff_document(upload_file: UploadFile, doc_type: str) -> Optional[Dict[str, str]]:
    """
    Сохраняет документ сотрудника.
    Возвращает словарь с типом документа и путем к нему.
    """
    if not await validate_document_file(upload_file):
        return None
    
    # Создаем поддиректорию для типа документа, если нужно
    doc_dir = os.path.join(DOCUMENTS_DIR, doc_type)
    os.makedirs(doc_dir, exist_ok=True)
    
    file_path = await save_upload_file(upload_file, doc_dir)
    if file_path:
        return {doc_type: file_path}
    return None

def delete_file(file_path: str) -> bool:
    """Удаляет файл."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Файл удалён: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {file_path}: {str(e)}")
        return False 