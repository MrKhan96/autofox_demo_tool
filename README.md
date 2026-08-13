# AUTOFOX — Reflection Removal Demo

A demo web app: upload one or many car photos, run them through the
reflection-removal model, and view **before/after** comparisons with draggable
sliders, then download the cleaned images.

Features:
- **Batch upload** — drag in multiple images; each gets its own before/after card
- **"Try a sample"** — one-click demo using a bundled sample car image
- **Download** cleaned results individually

## Run with Docker (recommended for handoff)

```bash
docker compose up --build
```

Open **http://localhost:5000**.

The `model/` folder is mounted as a volume, so you can edit
`model/reflection_model.py` (plug in the real model) and just restart the
container — no rebuild needed. `results/` and `uploads/` are persisted to the
host.

To build/run without compose:

```bash
docker build -t autofox-reflection-demo .
docker run -p 5000:5000 autofox-reflection-demo
```

## Run locally (no Docker)

```bash
# from the project folder
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# (macOS/Linux: source .venv/bin/activate)

pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000**.

## Plugging in the real model

The web app calls exactly one function. Edit the body of:

```
model/reflection_model.py  ->  remove_reflection(input_path, output_path)
```

Keep the signature `(input_path, output_path) -> output_path`. Everything else
(upload, processing, before/after view, download) keeps working unchanged.

Example:

```python
from PIL import Image
img = Image.open(input_path).convert("RGB")
result = your_model.predict(img)   # PIL.Image or ndarray
result.save(output_path)
return str(output_path)
```

Add your model's Python dependencies to `requirements.txt`.

## Structure

```
app.py                      Flask server + /process endpoint
model/reflection_model.py   <-- plug the model in here (currently a passthrough)
templates/index.html        UI
static/css/style.css        Branding + before/after slider styles
static/js/main.js           Upload, fetch, slider logic
uploads/ , results/         Runtime image storage (gitignored)
```

> The current model is a **placeholder** that passes the image through
> unchanged, so the before/after slider will show identical images until the
> real model is connected.
