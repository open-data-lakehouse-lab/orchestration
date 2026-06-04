from pathlib import Path
from typing import Optional

def ensure_dir(path: Path) -> Path:
    """Ensures a directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path

def find_file_by_pattern(directory: Path, pattern: str) -> Optional[Path]:
    """Finds a file by pattern using rglob."""
    for file in directory.rglob(pattern):
        if file.is_file():
            return file
    return None
