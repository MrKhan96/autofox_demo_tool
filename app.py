"""
AUTOFOX Reflection-Level Interactive Tool
=========================================

Flask app that serves an interactive viewer: for each car the original
(reflective) image is shown on the left, and on the right a "processed" image
whose **body reflection-removal level** is driven by a single slider.

The slider is a straight cross-fade between two precomputed endpoints
(<id>_base.jpg at level 0 and <id>_bodyclean.jpg at level 1), which reproduces
the Colab per-class blend exactly for the body class while every other class
setting is fixed. See scripts/build_reflection_endpoints.py for the offline
generation, and reflection_data.py for the file grouping.
"""

from __future__ import annotations

from flask import Flask, render_template, send_from_directory, url_for

from reflection_data import REFLECTION_DIR, group_reflection_files

app = Flask(__name__)


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
def index():
    return render_template(
        "reflection.html",
        items=list_reflection_items(),
        css_url=url_for("static", filename="css/style.css"),
        js_url=url_for("static", filename="js/reflection.js"),
    )


@app.route("/reflection-images/<path:filename>")
def reflection_file(filename):
    return send_from_directory(REFLECTION_DIR, filename)


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
