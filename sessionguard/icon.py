"""Tray icon artwork, generated at runtime."""

from PIL import Image, ImageDraw

COLORS = {
    "active": ((46, 204, 113, 255), (39, 174, 96, 255)),
    "waiting": ((243, 156, 18, 255), (211, 84, 0, 255)),
    "paused": ((149, 165, 166, 255), (127, 140, 141, 255)),
}


def create_icon_image(status: str) -> Image.Image:
    """64x64 tray icon. Green = active, amber = waiting, gray = paused."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    fill, outline = COLORS.get(status, COLORS["paused"])
    draw.ellipse((4, 4, size - 4, size - 4), fill=fill, outline=outline, width=4)
    draw.ellipse((22, 22, size - 22, size - 22), fill=(255, 255, 255, 230))
    return img
