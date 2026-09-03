"""
Build the two cross-fade endpoint images used by the Reflection-Level
Interactive tool, for every car that has a full (original, processed, mask)
triplet.

Why two images per car
-----------------------
The interactive tool exposes a single live control: the **body** reflection
level `t` (0..1). Every other setting is fixed (see FIXED_SETTINGS), so the
segmentation label map is constant per image and the per-class blend

    blended = processed * alpha + original * (1 - alpha)

is *linear in the body alpha*. That means the whole slider range is an exact
cross-fade between two endpoints:

    base       (t = 0): original everywhere, except glass = processed
    bodyclean  (t = 1): body AND glass = processed, rest = original

    blended(t) = base * (1 - t) + bodyclean * t     # identical to the Colab math

So we precompute `base` and `bodyclean` once here (heavy cv2/numpy work), and
the browser just cross-fades between them at runtime -- no OpenCV in the client
and it deploys as a static site.

This is a direct port of the Colab notebook's CLASS_ANCHORS / build_label_map /
erode_outer_boundary_only logic, pinned to FIXED_SETTINGS.

Run:
    python scripts/build_reflection_endpoints.py \
        --orig  docs/gallery-images \
        --proc  "C:/Users/wajee/Downloads/Required_Directories/reflection_removed_masks_selected" \
        --mask  "C:/Users/wajee/Downloads/Required_Directories/client_original_masks_selected"
"""

from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path

import cv2
import numpy as np

# --- Colab config (verbatim) -------------------------------------------------

CLASS_ANCHORS = {
    1: ("body",   [(255, 0, 0)]),      # red
    2: ("wheel",  [(0, 0, 255)]),      # blue
    3: ("glass",  [(0, 255, 255)]),    # cyan
    4: ("light",  [(255, 255, 0)]),    # yellow
    5: ("grille", [(255, 0, 255)]),    # magenta
    6: ("plate",  [(0, 0, 255)]),      # (shares blue with wheel; irrelevant here)
    7: ("logo",   [(255, 165, 0)]),    # orange
}

# The only live control is alpha_body (the slider). Everything else is pinned.
FIXED_SETTINGS = {
    "tolerance": 60,
    "alpha_background": 0.0,
    "erosion_strength": 6,
    "alpha_wheel": 0.0,
    "alpha_glass": 1.0,
    "alpha_light": 0.0,
    "alpha_grille": 0.0,
    "alpha_plate": 0.0,
    "alpha_logo": 0.0,
}

SUFFIX_ORIG = "_original"
SUFFIX_PROC = "_minibyte"
SUFFIX_MASK = "_original"
VALID_EXTS = (".png", ".jpg", ".jpeg")


# --- Colab helpers (verbatim logic) ------------------------------------------

def find_file(directory: str, base_name: str, suffix: str):
    if not os.path.exists(directory):
        return None
    matches = glob.glob(os.path.join(directory, f"{base_name}{suffix}.*"))
    valid = [f for f in matches if f.lower().endswith(VALID_EXTS)]
    return valid[0] if valid else None


def build_label_map(img_mask: np.ndarray, tolerance: float) -> np.ndarray:
    keys = list(CLASS_ANCHORS.keys())
    anchors = np.array([CLASS_ANCHORS[k][1][0] for k in keys], dtype=np.float32)

    flat = img_mask.reshape(-1, 1, 3).astype(np.float32)
    dists = np.linalg.norm(flat - anchors[None, :, :], axis=-1)

    nearest = np.argmin(dists, axis=1)
    min_dist = dists[np.arange(dists.shape[0]), nearest]

    labels = np.array(keys, dtype=np.int32)[nearest]
    labels[min_dist > tolerance] = 0
    return labels.reshape(img_mask.shape[:2])


def erode_outer_boundary_only(mask_rgb, erode_amount=6, background_color=(0, 0, 0)):
    bg = np.array(background_color)
    foreground = np.any(mask_rgb != bg, axis=-1).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (erode_amount * 2 + 1, erode_amount * 2 + 1)
    )
    eroded_fg = cv2.erode(foreground, kernel)
    result = mask_rgb.copy()
    result[eroded_fg == 0] = background_color
    return result


# --- Endpoint construction ---------------------------------------------------

def get_ids(orig_dir: str, proc_dir: str, mask_dir: str) -> list[str]:
    """Same matching rule as the Colab get_image_pairs(): a car is included
    only if it has original + processed + mask files."""
    if not os.path.isdir(mask_dir):
        return []
    ids = []
    for fn in os.listdir(mask_dir):
        name, ext = os.path.splitext(fn)
        if ext.lower() in VALID_EXTS and name.endswith(SUFFIX_MASK):
            base = name[: -len(SUFFIX_MASK)]
            if find_file(proc_dir, base, SUFFIX_PROC) and find_file(orig_dir, base, SUFFIX_ORIG):
                ids.append(base)
    return sorted(set(ids))


def label_map_for(orig, proc, mask):
    """Resize proc/mask to orig, erode the mask boundary, return the label map
    plus the RGB (float) original and processed arrays."""
    h, w = orig.shape[:2]
    if proc.shape[:2] != (h, w):
        proc = cv2.resize(proc, (w, h), interpolation=cv2.INTER_AREA)
    if mask.shape[:2] != (h, w):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

    if FIXED_SETTINGS["erosion_strength"] > 0:
        mask = erode_outer_boundary_only(
            mask, erode_amount=FIXED_SETTINGS["erosion_strength"], background_color=(0, 0, 0)
        )
    return build_label_map(mask, FIXED_SETTINGS["tolerance"]), orig, proc


def resize_max_width(img_rgb: np.ndarray, max_width: int) -> np.ndarray:
    h, w = img_rgb.shape[:2]
    if max_width and w > max_width:
        new_h = round(h * max_width / w)
        return cv2.resize(img_rgb, (max_width, new_h), interpolation=cv2.INTER_AREA)
    return img_rgb


def save_jpg(path: Path, img_rgb: np.ndarray, quality: int):
    bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])


def build_one(base_id, orig_dir, proc_dir, mask_dir, out_dir, max_width, quality):
    p_orig = find_file(orig_dir, base_id, SUFFIX_ORIG)
    p_proc = find_file(proc_dir, base_id, SUFFIX_PROC)
    p_mask = find_file(mask_dir, base_id, SUFFIX_MASK)

    orig = cv2.cvtColor(cv2.imread(p_orig), cv2.COLOR_BGR2RGB)
    proc = cv2.cvtColor(cv2.imread(p_proc), cv2.COLOR_BGR2RGB)
    mask = cv2.cvtColor(cv2.imread(p_mask), cv2.COLOR_BGR2RGB)

    label_map, orig, proc = label_map_for(orig, proc, mask)

    body = label_map == 1
    glass = label_map == 3

    # base (t=0): original, with glass cleaned (glass alpha is fixed at 1.0)
    base = orig.copy()
    base[glass] = proc[glass]

    # bodyclean (t=1): base + body cleaned
    bodyclean = base.copy()
    bodyclean[body] = proc[body]

    orig_web = resize_max_width(orig, max_width)
    base = resize_max_width(base, max_width)
    bodyclean = resize_max_width(bodyclean, max_width)

    save_jpg(out_dir / f"{base_id}_original.jpg", orig_web, quality)
    save_jpg(out_dir / f"{base_id}_base.jpg", base, quality)
    save_jpg(out_dir / f"{base_id}_bodyclean.jpg", bodyclean, quality)

    return int(body.sum()), int(glass.sum())


def main():
    ap = argparse.ArgumentParser()
    repo = Path(__file__).resolve().parent.parent
    ap.add_argument("--orig", default=str(repo / "docs" / "gallery-images"),
                    help="dir of <id>_original.* (defaults to the master gallery images)")
    ap.add_argument("--proc", required=True, help="dir of <id>_minibyte.* (reflection-removed)")
    ap.add_argument("--mask", required=True, help="dir of <id>_original.* colour-coded masks")
    ap.add_argument("--out", default=str(repo / "docs" / "reflection-images"),
                    help="output dir for the web endpoint images")
    ap.add_argument("--max-width", type=int, default=1400)
    ap.add_argument("--quality", type=int, default=90)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ids = get_ids(args.orig, args.proc, args.mask)
    if not ids:
        print("No complete (original, processed, mask) triplets found. Check the paths.")
        return
    print(f"Building endpoints for {len(ids)} cars -> {out_dir}")

    for i, base_id in enumerate(ids, 1):
        body_px, glass_px = build_one(
            base_id, args.orig, args.proc, args.mask, out_dir, args.max_width, args.quality
        )
        print(f"[{i:>2}/{len(ids)}] {base_id}  body_px={body_px:>8}  glass_px={glass_px:>8}")

    print("Done.")


if __name__ == "__main__":
    main()
