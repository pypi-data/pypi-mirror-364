"""
Shared utility functions for sall CLI tool.
"""

import re
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urlparse


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_html_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is an HTML file.

    Args:
        file_path: Path to the file

    Returns:
        True if the file is HTML, False otherwise
    """
    file_path = Path(file_path)
    return file_path.suffix.lower() in [".html", ".htm"]


def find_html_files(directory: Union[str, Path], recursive: bool = True) -> List[Path]:
    """
    Find all HTML files in a directory.

    Args:
        directory: Directory to search
        recursive: Whether to search recursively

    Returns:
        List of HTML file paths
    """
    directory = Path(directory)
    html_files = []

    if recursive:
        pattern = "**/*.html"
    else:
        pattern = "*.html"

    for file_path in directory.glob(pattern):
        if file_path.is_file():
            html_files.append(file_path)

    return html_files


def normalize_path(path: Union[str, Path]) -> str:
    """
    Normalize a file path for cross-platform compatibility.

    Args:
        path: Path to normalize

    Returns:
        Normalized path string
    """
    return str(Path(path).resolve())


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: URL to validate

    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for filesystem safety.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing spaces and dots
    filename = filename.strip(" .")

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"

    return filename


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes
    """
    try:
        return Path(file_path).stat().st_size
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    current_size = float(size_bytes)
    while current_size >= 1024 and i < len(size_names) - 1:
        current_size = current_size / 1024.0
        i += 1

    return f"{current_size:.1f} {size_names[i]}"


def backup_file(file_path: Union[str, Path], suffix: str = ".bak") -> Path:
    """
    Create a backup of a file.

    Args:
        file_path: Path to the file to backup
        suffix: Suffix for the backup file

    Returns:
        Path to the backup file
    """
    file_path = Path(file_path)
    backup_path = file_path.with_suffix(file_path.suffix + suffix)

    if file_path.exists():
        import shutil

        shutil.copy2(file_path, backup_path)

    return backup_path


def find_common_prefix(paths: List[Union[str, Path]]) -> Optional[Path]:
    """
    Find the common prefix directory for a list of paths.

    Args:
        paths: List of file paths

    Returns:
        Common prefix directory or None
    """
    if not paths:
        return None

    path_objects = [Path(p).resolve() for p in paths]
    common_prefix = path_objects[0].parent

    for path in path_objects[1:]:
        try:
            common_prefix = common_prefix.relative_to(path.parent)
        except ValueError:
            # Find the common ancestor
            current = path.parent
            while current != common_prefix and common_prefix != current:
                if len(current.parts) > len(common_prefix.parts):
                    current = current.parent
                else:
                    common_prefix = common_prefix.parent

    return common_prefix
