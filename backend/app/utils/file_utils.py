from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def resolve_duplicate_filename(file_name: str, storage_dir: str | Path) -> str:
    target_dir = Path(storage_dir)
    original_name = Path(file_name).name
    if not (target_dir / original_name).exists():
        return original_name

    stem = Path(original_name).stem
    suffix = Path(original_name).suffix
    counter = 1
    while True:
        candidate = f"{stem}_{counter}{suffix}"
        if not (target_dir / candidate).exists():
            logger.info("Duplicate filename detected; saved as %s", candidate)
            return candidate
        counter += 1
