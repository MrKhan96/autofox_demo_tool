"""
Build web-optimized gallery images from the high-res source folders.

For every car that has all sources it writes three JPEGs into
docs/gallery-images/ (clean numeric ids, "_high" stripped):

    <id>_original.jpg   <- <high>/<id>_high_original.png
    <id>_blended.jpg    <- <high>/<id>_high_blended.png
    <id>_after.jpg      <- RIGHT half of <composite>/<id>_*.jpg

The "after" (processed) image is the RIGHT half of a side-by-side composite
(left = original, right = processed), split at the horizontal midpoint.

Only ids present in BOTH the high (blended) set and the composite set are
included. Images are downscaled to --max-width and saved at --quality so the
gallery stays lightweight (the raw PNG sources are up to ~20 MB each).

Run:
    python scripts/build_gallery_from_sources.py \
        --high      "C:/.../high" \
        --composite "C:/.../1000 Original_Processed Images Mapped"
"""

from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path

from PIL import Image

VALID_EXTS = (".png", ".jpg", ".jpeg")


def find_composite(comp_dir: str, base_id: str):
    """Composites are named <id>_<quality>.<ext> (e.g. 15894457_high.jpg)."""
    for f in sorted(glob.glob(os.path.join(comp_dir, f"{base_id}_*"))):
        if f.lower().endswith(VALID_EXTS):
            return f
    return None


def matched_ids(high_dir: str, comp_dir: str):
    ids = []
    for f in glob.glob(os.path.join(high_dir, "*_high_blended.png")):
        base = os.path.basename(f)[: -len("_high_blended.png")]
        orig = os.path.join(high_dir, f"{base}_high_original.png")
        if os.path.exists(orig) and find_composite(comp_dir, base):
            ids.append(base)
    return sorted(set(ids))


def target_size(src_path: str, max_width: int):
    """The web dimensions of the original: capped to max_width, keeping aspect."""
    with Image.open(src_path) as im:
        w, h = im.size
    if max_width and w > max_width:
        return (max_width, round(h * max_width / w))
    return (w, h)


def _save_exact(im: Image.Image, dst_path: Path, size, quality: int):
    """Resize to an EXACT (w, h) so every variant lines up pixel-for-pixel."""
    im = im.convert("RGB").resize(size, Image.LANCZOS)
    im.save(dst_path, "JPEG", quality=quality, optimize=True, progressive=True)


def save_source(src_path: str, dst_path: Path, size, quality: int):
    with Image.open(src_path) as im:
        _save_exact(im, dst_path, size, quality)


def save_after_from_composite(comp_path: str, dst_path: Path, size, quality: int):
    """Crop the right half (processed side) of the side-by-side composite,
    then force it to the original's exact dimensions."""
    with Image.open(comp_path) as im:
        w, h = im.size
        right = im.crop((w // 2, 0, w, h))
        _save_exact(right, dst_path, size, quality)


def main():
    ap = argparse.ArgumentParser()
    repo = Path(__file__).resolve().parent.parent
    ap.add_argument("--high", required=True, help="folder with <id>_high_original.png / <id>_high_blended.png")
    ap.add_argument("--composite", required=True, help="folder with <id>_<quality>.jpg side-by-side composites")
    ap.add_argument("--out", default=str(repo / "docs" / "gallery-images"))
    ap.add_argument("--max-width", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=88)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ids = matched_ids(args.high, args.composite)
    if not ids:
        print("No cars with all sources found. Check the paths.")
        return
    print(f"Building {len(ids)} cars -> {out_dir}  (max_width={args.max_width}, q={args.quality})")

    for i, base in enumerate(ids, 1):
        orig_src = os.path.join(args.high, f"{base}_high_original.png")
        size = target_size(orig_src, args.max_width)  # every variant matches this
        save_source(orig_src, out_dir / f"{base}_original.jpg", size, args.quality)
        save_source(os.path.join(args.high, f"{base}_high_blended.png"),
                    out_dir / f"{base}_blended.jpg", size, args.quality)
        save_after_from_composite(find_composite(args.composite, base),
                                  out_dir / f"{base}_after.jpg", size, args.quality)
        print(f"[{i:>3}/{len(ids)}] {base}  {size[0]}x{size[1]}")

    print("Done.")


if __name__ == "__main__":
    main()
