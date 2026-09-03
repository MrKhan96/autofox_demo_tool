"""
Build a static export for GitHub Pages with BOTH pages published from docs/:

  docs/index.html        the gallery            -> https://<user>.github.io/<repo>/
  docs/tool/index.html   the interactive tool   -> https://<user>.github.io/<repo>/tool/

Shared assets live in docs/static/ and the two image sets in
docs/gallery-images/ and docs/reflection-images/. The tool page sits one level
deeper (docs/tool/), so it references assets with a "../" prefix.

Run:  python scripts/build_static.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"

sys.path.insert(0, str(BASE_DIR))
from gallery_data import group_gallery_files  # noqa: E402
from reflection_data import group_reflection_files  # noqa: E402


def build_gallery_items():
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


def build_tool_items(prefix="../"):
    items = []
    for base, files in sorted(group_reflection_files().items()):
        items.append(
            {
                "name": base,
                "original_url": f"{prefix}reflection-images/{files['original']}",
                "base_url": f"{prefix}reflection-images/{files['base']}",
                "bodyclean_url": f"{prefix}reflection-images/{files['bodyclean']}",
            }
        )
    return items


def main():
    (DOCS_DIR / "static" / "css").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "static" / "js").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "tool").mkdir(parents=True, exist_ok=True)

    for rel in ("css/style.css", "js/gallery.js", "js/reflection.js"):
        shutil.copyfile(BASE_DIR / "static" / rel, DOCS_DIR / "static" / rel)

    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

    # Gallery at the Pages root.
    gallery_items = build_gallery_items()
    gallery_html = env.get_template("gallery.html").render(
        items=gallery_items,
        css_url="static/css/style.css",
        js_url="static/js/gallery.js",
        tool_url="tool/",
    )
    (DOCS_DIR / "index.html").write_text(gallery_html, encoding="utf-8")

    # Interactive tool at /tool/ (one level deeper -> ../ asset prefix).
    tool_items = build_tool_items(prefix="../")
    tool_html = env.get_template("reflection.html").render(
        items=tool_items,
        css_url="../static/css/style.css",
        js_url="../static/js/reflection.js",
        gallery_url="../",
    )
    (DOCS_DIR / "tool" / "index.html").write_text(tool_html, encoding="utf-8")

    print(f"wrote {DOCS_DIR / 'index.html'}       ({len(gallery_items)} cars, gallery)")
    print(f"wrote {DOCS_DIR / 'tool' / 'index.html'}  ({len(tool_items)} cars, interactive tool)")


if __name__ == "__main__":
    main()
