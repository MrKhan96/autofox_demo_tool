"""
Generate a synthetic 'car with reflections' sample image for the demo, so the
page has an impressive default before the real model is wired in.

Run once:  python model/make_sample.py
Output:    static/img/sample_car.jpg
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H = 960, 600
OUT = Path(__file__).resolve().parent.parent / "static" / "img" / "sample_car.jpg"
OUT.parent.mkdir(parents=True, exist_ok=True)


def vgrad(size, top, bottom):
    """Vertical gradient image."""
    w, h = size
    base = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / (h - 1)
        base.putpixel(
            (0, y),
            tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return base.resize((w, h))


def main():
    # Showroom: wall gradient on top, glossy floor on the bottom.
    img = vgrad((W, H), (34, 40, 56), (12, 15, 22))
    floor = vgrad((W, H // 3), (26, 30, 42), (8, 10, 16))
    img.paste(floor, (0, H - H // 3))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Car body (simple side-view silhouette) ---
    body = (196, 32, 28)          # red
    body_dark = (120, 18, 16)
    glass = (150, 175, 200)

    # lower body
    draw.polygon(
        [(150, 430), (230, 360), (720, 360), (820, 430), (820, 470), (150, 470)],
        fill=body,
    )
    # cabin / roof
    draw.polygon(
        [(300, 360), (360, 285), (620, 285), (700, 360)],
        fill=body_dark,
    )
    # windows (the reflective surfaces)
    draw.polygon([(330, 355), (375, 300), (485, 300), (485, 355)], fill=glass)
    draw.polygon([(505, 355), (505, 300), (610, 300), (665, 355)], fill=glass)
    # wheels
    for cx in (300, 700):
        draw.ellipse([cx - 55, 415, cx + 55, 525], fill=(18, 18, 20))
        draw.ellipse([cx - 26, 444, cx + 26, 496], fill=(150, 150, 155))
    # simple ground shadow
    draw.ellipse([170, 500, 800, 545], fill=(0, 0, 0, 90))

    # --- REFLECTIONS: this is what the model is meant to remove ---
    refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(refl)

    # Bright diagonal glare bands sweeping across the whole car.
    for off, alpha, wide in [(-120, 90, 70), (60, 70, 55), (240, 55, 40)]:
        rd.polygon(
            [
                (250 + off, 270), (250 + off + wide, 270),
                (60 + off + wide, 500), (60 + off, 500),
            ],
            fill=(255, 255, 255, alpha),
        )

    # A "window frame" reflection (like a building window mirrored on the glass).
    for i in range(3):
        x = 360 + i * 70
        rd.rectangle([x, 300, x + 45, 352], fill=(235, 240, 255, 70))
    for j in range(2):
        y = 310 + j * 26
        rd.line([(345, y), (655, y)], fill=(235, 240, 255, 55), width=3)

    # Soft blooming highlight on the hood.
    rd.ellipse([520, 365, 760, 420], fill=(255, 255, 255, 60))

    refl = refl.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img.convert("RGBA"), refl).convert("RGB")

    img.save(OUT, quality=90)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
