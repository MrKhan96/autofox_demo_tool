"""
AUTOFOX Reflection Removal — Gallery
=====================================

Flask app that serves a read-only gallery of pre-generated image sets from
GALLERY_DIR, each shown as two before/after sliders: original-vs-minibyte
and original-vs-after.
"""

from __future__ import annotations

from flask import Flask, render_template, send_from_directory, url_for

from gallery_data import GALLERY_DIR, group_gallery_files

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


@app.route("/")
def gallery():
    return render_template(
        "gallery.html",
        items=list_gallery_items(),
        css_url=url_for("static", filename="css/style.css"),
        js_url=url_for("static", filename="js/gallery.js"),
    )


@app.route("/gallery-images/<path:filename>")
def gallery_file(filename):
    return send_from_directory(GALLERY_DIR, filename)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
