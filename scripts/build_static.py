"""
Build a static export of the gallery for GitHub Pages.

Renders templates/gallery.html with plain relative asset paths (no Flask
url_for/request context needed) into docs/index.html, and copies the CSS/JS
into docs/static/. Images already live in docs/gallery-images/ and are
picked up automatically -- add/remove files there and re-run this script.

Run:  python scripts/build_static.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"

import sys

sys.path.insert(0, str(BASE_DIR))
from gallery_data import group_gallery_files  # noqa: E402


def build_items():
    items = []
    for base, files in sorted(group_gallery_files().items()):
        items.append(
            {
                "name": base,
                "orignal_url": f"gallery-images/{files['orignal']}",
                "minibyte_url": f"gallery-images/{files['minibyte']}"
                if "minibyte" in files
                else None,
                "after_url": f"gallery-images/{files['after']}"
                if "after" in files
                else None,
            }
        )
    return items


def main():
    (DOCS_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        BASE_DIR / "static" / "css" / "style.css",
        DOCS_DIR / "static" / "css" / "style.css",
    )
    shutil.copyfile(
        BASE_DIR / "static" / "js" / "gallery.js",
        DOCS_DIR / "static" / "js" / "gallery.js",
    )

    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))
    template = env.get_template("gallery.html")
    html = template.render(
        items=build_items(),
        css_url="static/css/style.css",
        js_url="static/js/gallery.js",
    )
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"wrote {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
