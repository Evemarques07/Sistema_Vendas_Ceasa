import os
import uuid
import subprocess
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles

from app.core.config import settings

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_IMAGE_SIZE = (1920, 1920)  # Max width, height

async def save_upload_file(upload_file: UploadFile, destination: str) -> None:
    """Save uploaded file to destination"""
    async with aiofiles.open(destination, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)

def validate_image_file(filename: str, file_size: int) -> None:
    """Validate image file"""
    if not filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo não fornecido")
    
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de arquivo não permitido. Use: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Check file size
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )

def resize_image(image_path: str, max_size: tuple = MAX_IMAGE_SIZE) -> None:
    """Resize image if it's too large"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if necessary
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(image_path, optimize=True, quality=85)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

async def upload_image_to_gdrive(local_path: str, filename: str) -> Optional[str]:
    """Upload image to Google Drive using rclone"""
    try:
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Upload to Google Drive
        cmd = [
            "rclone", 
            "copy", 
            local_path,
            f"{settings.GDRIVE_REMOTE_NAME}:{settings.GDRIVE_FOLDER_ID}/{unique_filename}",
            "--config", settings.RCLONE_CONFIG_PATH
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Generate public link (this would need to be implemented based on your Google Drive setup)
            # For now, return a placeholder URL
            return f"https://drive.google.com/file/d/{unique_filename}/view"
        else:
            print(f"Erro no rclone: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Erro ao fazer upload para Google Drive: {str(e)}")
        return None

async def process_and_upload_image(upload_file: UploadFile) -> Optional[str]:
    """Process and upload image file"""
    # Validate file
    validate_image_file(upload_file.filename, upload_file.size or 0)
    
    # Generate unique filename
    ext = os.path.splitext(upload_file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    local_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
    
    try:
        # Save file locally
        await save_upload_file(upload_file, local_path)
        
        # Resize image if necessary
        resize_image(local_path)
        
        # Upload to Google Drive
        gdrive_url = await upload_image_to_gdrive(local_path, unique_filename)
        
        # Clean up local file
        if os.path.exists(local_path):
            os.remove(local_path)
        
        return gdrive_url
        
    except Exception as e:
        # Clean up local file on error
        if os.path.exists(local_path):
            os.remove(local_path)
        raise e

def delete_image_from_gdrive(image_url: str) -> bool:
    """Delete image from Google Drive"""
    try:
        # Extract filename from URL (this is a simplified example)
        # You would need to implement proper URL parsing based on your Google Drive setup
        filename = image_url.split('/')[-2] if '/' in image_url else image_url
        
        cmd = [
            "rclone", 
            "delete", 
            f"{settings.GDRIVE_REMOTE_NAME}:{settings.GDRIVE_FOLDER_ID}/{filename}",
            "--config", settings.RCLONE_CONFIG_PATH
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
        
    except Exception as e:
        print(f"Erro ao deletar imagem do Google Drive: {str(e)}")
        return False
