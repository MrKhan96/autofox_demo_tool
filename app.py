"""
AUTOFOX Reflection Removal — Gallery
=====================================

Flask app that serves a read-only gallery of pre-generated image sets from
GALLERY_DIR, each shown as two before/after sliders: original-vs-minibyte
and original-vs-after.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template, send_from_directory, url_for

BASE_DIR = Path(__file__).resolve().parent
GALLERY_DIR = (
    BASE_DIR
    / "images_suite"
    / "minibyte_outputs-20260812T115009Z-1-001"
    / "minibyte_outputs"
)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
# Groups images by <basename><suffix>.<ext>. Both spellings of "original" are
# accepted since the source folder uses "_original".
GALLERY_SUFFIXES = {
    "orignal": ("_orignal", "_original"),
    "minibyte": ("_minibyte",),
    "after": ("_after",),
}

app = Flask(__name__)


def list_gallery_items():
    """Group images in GALLERY_DIR by basename into orignal/minibyte/after sets."""
    groups: dict[str, dict[str, str]] = {}
    if not GALLERY_DIR.is_dir():
        return []

    for f in sorted(GALLERY_DIR.iterdir()):
        if not f.is_file() or f.suffix.lower().lstrip(".") not in ALLOWED_EXTENSIONS:
            continue
        stem = f.stem
        for kind, suffixes in GALLERY_SUFFIXES.items():
            matched = next((s for s in suffixes if stem.endswith(s)), None)
            if matched:
                base = stem[: -len(matched)]
                groups.setdefault(base, {})[kind] = f.name
                break

    items = []
    for base, files in sorted(groups.items()):
        if "orignal" not in files:
            continue
        items.append(
            {
                "name": base,
                "orignal_url": url_for("gallery_file", filename=files["orignal"]),
                "minibyte_url": url_for("gallery_file", filename=files["minibyte"])
                if "minibyte" in files
                else None,
                "after_url": url_for("gallery_file", filename=files["after"])
                if "after" in files
                else None,
            }
        )
    return items


@app.route("/")
def gallery():
    return render_template("gallery.html", items=list_gallery_items())


@app.route("/gallery-images/<path:filename>")
def gallery_file(filename):
    return send_from_directory(GALLERY_DIR, filename)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
