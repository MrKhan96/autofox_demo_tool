"""
AUTOFOX — Flask app serving two pages:

  /                  the read-only gallery (Original vs Minibyte vs After)
  /interactive_tool  the Reflection-Level interactive tool (original + slider-
                     driven body reflection removal, with a downloadable output)

The static export (scripts/build_static.py) mirrors this as:
  docs/index.html                   -> gallery      (Pages root URL)
  docs/interactive_tool/index.html  -> interactive  (Pages /interactive_tool/ URL)

so both are published from the same GitHub Pages source (docs/).
"""

from __future__ import annotations

from flask import Flask, render_template, send_from_directory, url_for

from gallery_data import GALLERY_DIR, group_gallery_files
from reflection_data import REFLECTION_DIR, group_reflection_files

app = Flask(__name__)


def list_gallery_items():
    items = []
    for base, files in sorted(group_gallery_files().items()):
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


def list_reflection_items():
    items = []
    for base, files in sorted(group_reflection_files().items()):
        items.append(
            {
                "name": base,
                "original_url": url_for("reflection_file", filename=files["original"]),
                "base_url": url_for("reflection_file", filename=files["base"]),
                "bodyclean_url": url_for("reflection_file", filename=files["bodyclean"]),
            }
        )
    return items


@app.route("/")
def gallery():
    return render_template(
        "gallery.html",
        items=list_gallery_items(),
        css_url=url_for("static", filename="css/style.css"),
        js_url=url_for("static", filename="js/gallery.js"),
        tool_url=url_for("interactive_tool"),
    )


@app.route("/interactive_tool")
def interactive_tool():
    return render_template(
        "reflection.html",
        items=list_reflection_items(),
        css_url=url_for("static", filename="css/style.css"),
        js_url=url_for("static", filename="js/reflection.js"),
        gallery_url=url_for("gallery"),
    )


@app.route("/gallery-images/<path:filename>")
def gallery_file(filename):
    return send_from_directory(GALLERY_DIR, filename)


@app.route("/reflection-images/<path:filename>")
def reflection_file(filename):
    return send_from_directory(REFLECTION_DIR, filename)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
