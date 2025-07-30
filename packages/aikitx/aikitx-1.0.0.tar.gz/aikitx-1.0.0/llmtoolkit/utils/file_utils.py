"""
File Utilities

This module provides utility functions for file operations.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger("gguf_loader.utils.file")

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Size of the file in bytes, or 0 if the file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"Error getting file size for {file_path}: {e}")
        return 0

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (lowercase, without the dot)
    """
    return os.path.splitext(file_path)[1].lower()[1:]

def is_gguf_file(file_path: str) -> bool:
    """
    Check if a file is a GGUF file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a GGUF file, False otherwise
    """
    return get_file_extension(file_path) == "gguf"

def copy_file(source_path: str, destination_path: str) -> bool:
    """
    Copy a file from source to destination.
    
    Args:
        source_path: Path to the source file
        destination_path: Path to the destination file
        
    Returns:
        True if the file was copied successfully, False otherwise
    """
    try:
        # Ensure destination directory exists
        destination_dir = os.path.dirname(destination_path)
        ensure_directory_exists(destination_dir)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        return True
    except Exception as e:
        logger.error(f"Error copying file from {source_path} to {destination_path}: {e}")
        return False

def list_files_with_extension(directory_path: str, extension: str) -> List[str]:
    """
    List all files in a directory with a specific extension.
    
    Args:
        directory_path: Path to the directory
        extension: File extension to filter by (without the dot)
        
    Returns:
        List of file paths
    """
    try:
        if not os.path.exists(directory_path):
            return []
        
        extension = extension.lower()
        return [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f)) and
            get_file_extension(f) == extension
        ]
    except Exception as e:
        logger.error(f"Error listing files in {directory_path}: {e}")
        return []