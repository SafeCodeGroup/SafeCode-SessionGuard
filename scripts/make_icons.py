"""Generate the application icons in assets/ (run after changing the artwork).

Usage: python scripts/make_icons.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "assets"
NAVY = (16, 37, 66, 255)
GREEN = (46, 204, 113, 255)
WHITE = (255, 255, 255, 255)


def draw_icon(size: int = 1024) -> Image.Image:
    """Navy rounded square with a green shield and a white check mark."""
    s = size / 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80 * s, 80 * s, 944 * s, 944 * s), radius=200 * s, fill=NAVY)
    shield = [(512, 200), (780, 300), (760, 560), (512, 830), (264, 560), (244, 300)]
    d.polygon([(x * s, y * s) for x, y in shield], fill=GREEN)
    check = [(380, 520), (480, 620), (660, 420)]
    d.line([(x * s, y * s) for x, y in check], fill=WHITE, width=int(64 * s), joint="curve")
    return img


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    icon = draw_icon()
    icon.save(ASSETS / "icon.png")
    icon.resize((256, 256), Image.LANCZOS).save(ASSETS / "icon-256.png")
    icon.save(ASSETS / "icon.icns")
    sizes = [(n, n) for n in (16, 24, 32, 48, 64, 128, 256)]
    icon.save(ASSETS / "icon.ico", sizes=sizes)
    print(f"Wrote icons to {ASSETS}")


if __name__ == "__main__":
    main()
