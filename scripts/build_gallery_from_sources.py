"""
Build web-optimized gallery images from the high-res source folders.

For every car that has all three sources it writes three JPEGs into
docs/gallery-images/ (clean numeric ids, "_high" stripped):

    <id>_original.jpg   <- <high>/<id>_high_original.png
    <id>_blended.jpg    <- <high>/<id>_high_blended.png
    <id>_after.jpg      <- <after>/<id>.(jpg|jpeg|png)

Only ids present in BOTH the high (blended) set and the after set are included.
Images are downscaled to --max-width and saved at --quality so the gallery
stays lightweight (the raw PNG sources are up to ~20 MB each).

Run:
    python scripts/build_gallery_from_sources.py \
        --high  "C:/.../high" \
        --after "C:/.../1000 Exterior Processed Images"
"""

from __future__ import annotations

import argparse
import glob
import os
from pathlib import Path

from PIL import Image

VALID_EXTS = (".png", ".jpg", ".jpeg")


def find_after(after_dir: str, base_id: str):
    for f in sorted(glob.glob(os.path.join(after_dir, f"{base_id}.*"))):
        if f.lower().endswith(VALID_EXTS):
            return f
    return None


def matched_ids(high_dir: str, after_dir: str):
    ids = []
    for f in glob.glob(os.path.join(high_dir, "*_high_blended.png")):
        base = os.path.basename(f)[: -len("_high_blended.png")]
        orig = os.path.join(high_dir, f"{base}_high_original.png")
        if os.path.exists(orig) and find_after(after_dir, base):
            ids.append(base)
    return sorted(set(ids))


def save_web(src_path: str, dst_path: Path, max_width: int, quality: int):
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if max_width and w > max_width:
            im = im.resize((max_width, round(h * max_width / w)), Image.LANCZOS)
        im.save(dst_path, "JPEG", quality=quality, optimize=True, progressive=True)


def main():
    ap = argparse.ArgumentParser()
    repo = Path(__file__).resolve().parent.parent
    ap.add_argument("--high", required=True, help="folder with <id>_high_original.png / <id>_high_blended.png")
    ap.add_argument("--after", required=True, help="folder with <id>.jpg processed images")
    ap.add_argument("--out", default=str(repo / "docs" / "gallery-images"))
    ap.add_argument("--max-width", type=int, default=1600)
    ap.add_argument("--quality", type=int, default=88)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ids = matched_ids(args.high, args.after)
    if not ids:
        print("No cars with all three sources found. Check the paths.")
        return
    print(f"Building {len(ids)} cars -> {out_dir}  (max_width={args.max_width}, q={args.quality})")

    for i, base in enumerate(ids, 1):
        save_web(os.path.join(args.high, f"{base}_high_original.png"),
                 out_dir / f"{base}_original.jpg", args.max_width, args.quality)
        save_web(os.path.join(args.high, f"{base}_high_blended.png"),
                 out_dir / f"{base}_blended.jpg", args.max_width, args.quality)
        save_web(find_after(args.after, base),
                 out_dir / f"{base}_after.jpg", args.max_width, args.quality)
        print(f"[{i:>3}/{len(ids)}] {base}")

    print("Done.")


if __name__ == "__main__":
    main()
