"""
Shared gallery-grouping logic, used by both the Flask app (app.py) and the
static-site builder (scripts/build_static.py) so the two stay in sync.
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
GALLERY_DIR = BASE_DIR / "docs" / "gallery-images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
# Groups images by <basename><suffix>.<ext>. Both spellings of "original" are
# accepted since the source folder uses "_original". Suffixes are matched
# longest-first so "_minibyte_final" wins over "_minibyte".
GALLERY_SUFFIXES = {
    "orignal": ("_orignal", "_original"),
    "minibyte": ("_minibyte_final", "_minibyte"),
    "after": ("_after",),
}


def group_gallery_files(directory: Path = GALLERY_DIR) -> dict[str, dict[str, str]]:
    """Group image filenames in `directory` by basename into orignal/minibyte/after."""
    groups: dict[str, dict[str, str]] = {}
    if not directory.is_dir():
        return groups

    for f in sorted(directory.iterdir()):
        if not f.is_file() or f.suffix.lower().lstrip(".") not in ALLOWED_EXTENSIONS:
            continue
        stem = f.stem
        for kind, suffixes in GALLERY_SUFFIXES.items():
            matched = next((s for s in suffixes if stem.endswith(s)), None)
            if matched:
                base = stem[: -len(matched)]
                groups.setdefault(base, {})[kind] = f.name
                break

    return {base: files for base, files in groups.items() if "orignal" in files}
