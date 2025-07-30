"""
File utility functions for py-config-ai.
"""

import os
from pathlib import Path
from typing import Optional


def read_file_content(file_path: str) -> Optional[str]:
    """
    Read content from a file.

    Args:
        file_path: Path to the file

    Returns:
        Optional[str]: File content or None if file doesn't exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        return None


def write_file_content(file_path: str, content: str) -> bool:
    """
    Write content to a file.

    Args:
        file_path: Path to the file
        content: Content to write

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError:
        return False


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.

    Args:
        file_path: Path to the file

    Returns:
        str: File extension (including the dot)
    """
    return Path(file_path).suffix


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: Path to the file

    Returns:
        bool: True if file exists, False otherwise
    """
    return Path(file_path).exists()


def is_directory(path: str) -> bool:
    """
    Check if a path is a directory.

    Args:
        path: Path to check

    Returns:
        bool: True if path is a directory, False otherwise
    """
    return Path(path).is_dir()


def list_files(directory: str, pattern: str = "*") -> list:
    """
    List files in a directory matching a pattern.

    Args:
        directory: Directory to search
        pattern: File pattern to match

    Returns:
        list: List of matching file paths
    """
    try:
        return [str(f) for f in Path(directory).glob(pattern)]
    except (FileNotFoundError, PermissionError):
        return []


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        Optional[int]: File size in bytes or None if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except (FileNotFoundError, OSError):
        return None 