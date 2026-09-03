"""
Shared grouping logic for the Reflection-Level Interactive tool, used by both
the Flask app (app.py) and the static-site builder (scripts/build_static.py)
so the two stay in sync.

Each car contributes three web images in docs/reflection-images/:
    <id>_original.jpg    reflective original            (left pane)
    <id>_base.jpg        body slider = 0 endpoint       (right pane, t=0)
    <id>_bodyclean.jpg   body slider = 1 endpoint       (right pane, t=1)

These are produced offline by scripts/build_reflection_endpoints.py.
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REFLECTION_DIR = BASE_DIR / "docs" / "reflection-images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}

# Longest-first so "_bodyclean" is never mistaken for something else.
REFLECTION_SUFFIXES = {
    "original": ("_original",),
    "base": ("_base",),
    "bodyclean": ("_bodyclean",),
}


def group_reflection_files(directory: Path = REFLECTION_DIR) -> dict[str, dict[str, str]]:
    """Group image filenames in `directory` by car id into original/base/bodyclean.
    A car is included only if all three endpoint images are present."""
    groups: dict[str, dict[str, str]] = {}
    if not directory.is_dir():
        return groups

    for f in sorted(directory.iterdir()):
        if not f.is_file() or f.suffix.lower().lstrip(".") not in ALLOWED_EXTENSIONS:
            continue
        stem = f.stem
        for kind, suffixes in REFLECTION_SUFFIXES.items():
            matched = next((s for s in suffixes if stem.endswith(s)), None)
            if matched:
                base = stem[: -len(matched)]
                groups.setdefault(base, {})[kind] = f.name
                break

    return {
        base: files
        for base, files in groups.items()
        if {"original", "base", "bodyclean"} <= files.keys()
    }
