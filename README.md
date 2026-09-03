# AUTOFOX — Reflection-Level Interactive Tool

> Branch: `Reflection_Level_Interactive_Tool`. A variant of the `master`
> gallery. For each car it shows the **original (reflective)** photo on the
> left and a **processed** photo on the right whose **body reflection-removal
> level** is driven by a single slider (0% keeps the reflection, 100% shows the
> fully cleaned body). Glass is always cleaned.

## How the slider works

Every setting from the source Colab notebook is fixed except the **body** alpha:

```python
FIXED_SETTINGS = {
    'tolerance': 60, 'alpha_background': 0.0, 'erosion_strength': 6,
    'alpha_wheel': 0.0, 'alpha_glass': 1.0, 'alpha_light': 0.0,
    'alpha_grille': 0.0, 'alpha_plate': 0.0, 'alpha_logo': 0.0,
}
```

Because only the body alpha `t` varies, the per-class blend
`processed*alpha + original*(1-alpha)` is **linear in `t`**, so the whole
slider range is an exact cross-fade between two precomputed endpoints:

- `<id>_base.jpg` — `t = 0`: original everywhere, glass cleaned
- `<id>_bodyclean.jpg` — `t = 1`: body **and** glass cleaned

`blend(t) = base*(1-t) + bodyclean*t` reproduces the Colab math exactly. The
browser just cross-fades the two images, so there is no OpenCV/NumPy at
runtime and the tool deploys as a static site.

## Rebuilding the endpoint images

The endpoints are generated offline from three local folders (matched by car id):

| Role | Filename pattern | Source |
|------|------------------|--------|
| Original (reflective) | `<id>_original.*` | `docs/gallery-images/` (default) |
| Processed (reflection-removed) | `<id>_minibyte.*` | local `reflection_removed_masks_selected/` |
| Segmentation mask | `<id>_original.*` (colour-coded) | local `client_original_masks_selected/` |

```bash
python scripts/build_reflection_endpoints.py \
    --proc "C:/path/to/reflection_removed_masks_selected" \
    --mask "C:/path/to/client_original_masks_selected"
# writes docs/reflection-images/<id>_{original,base,bodyclean}.jpg
```

Optional flags: `--orig <dir>` (defaults to `docs/gallery-images`),
`--out <dir>`, `--max-width 1400`, `--quality 90`.

## Two pages, one deploy

This app serves both the original gallery and the interactive tool, and the
static export publishes both from the same GitHub Pages source (`docs/`):

| Page | Flask route | Static file | Pages URL |
|------|-------------|-------------|-----------|
| Gallery (Original vs Minibyte vs After) | `/` | `docs/index.html` | `…github.io/<repo>/` |
| Reflection-Level interactive tool | `/interactive_tool` | `docs/interactive_tool/index.html` | `…github.io/<repo>/interactive_tool/` |

## Run locally (Flask)

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000/** (gallery) and **http://localhost:5000/interactive_tool** (tool).

## Static export (GitHub Pages)

```bash
python scripts/build_static.py     # writes docs/index.html and docs/interactive_tool/index.html
```

`docs/` is self-contained (`index.html`, `interactive_tool/index.html`,
`static/`, `gallery-images/`, `reflection-images/`). The tool page lives one
level deeper, so it references shared assets with a `../` prefix.

## Run with Docker

```bash
docker compose up --build
```

## Structure

```
app.py                              Flask server (serves the tool at /)
reflection_data.py                  Groups docs/reflection-images/ by car id
templates/reflection.html           UI: original | processed + slider
static/js/reflection.js             Slider cross-fade + per-car pagination
static/css/style.css                Branding + slider/pane styles
scripts/build_reflection_endpoints.py  Offline endpoint generator (cv2/numpy)
scripts/build_static.py             Renders docs/ for GitHub Pages
docs/reflection-images/             <id>_{original,base,bodyclean}.jpg (72 cars)
```
