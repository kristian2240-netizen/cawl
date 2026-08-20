"""C.A.W.L. Image Forge — Pillow generation (Layer 3 / Layer 6).

Kinds: banner, seelbon (Mechanicus crest), avatar, map, quote.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config
from .tools import generate_image_filename

_COGS = {
    "mech": (189, 54, 54),       # Mechanicus red
    "bone": (226, 207, 170),     # parchment bone
    "steel": (94, 105, 118),     # steel grey
    "gold": (200, 160, 60),      # trim gold
    "abyss": (16, 18, 24),       # deep dark
}


def _font(size: int) -> ImageFont.ImageFont | ImageFont.FreeTypeFont:
    for candidate in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def _gradient(w: int, h: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        row = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(w):
            px[x, y] = row
    return img


def _gear(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, teeth: int, color: tuple) -> None:
    import math  # noqa: PLC0415

    for i in range(teeth):
        a0 = math.pi * 2 * i / teeth
        a1 = a0 + math.pi * 2 / teeth * 0.5
        pts = [(cx + r * 1.2 * math.cos(a), cy + r * 1.2 * math.sin(a)) for a in (a0, a1)]
        draw.line(pts, fill=color, width=max(3, r // 8))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=max(3, r // 10))
    draw.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], outline=color, width=2)


def forge(kind: str, **params: str) -> dict:
    width = int(params.get("width", params.get("w", 1024)))
    height = int(params.get("height", params.get("h", 384)))
    text = params.get("text", "C.A.W.L. — Archmagos Dominus")
    accent = _COGS.get(params.get("color", "mech"), _COGS["mech"])

    if kind == "banner":
        img = _gradient(width, height, _COGS["abyss"], (accent[0] // 2, accent[1] // 2, accent[2] // 2))
        draw = ImageDraw.Draw(img)
        _gear(draw, width // 6, height // 2, min(width, height) // 5, 12, accent)
        _gear(draw, width // 6 + min(width, height) // 3, height // 2, min(width, height) // 7, 8, _COGS["gold"])
        _draw_centered(draw, text, width // 2, height // 2 - 20, _font(max(28, height // 10)), _COGS["bone"])
        _draw_centered(draw, "$0 RUNTIME · FREE FOREVER", width // 2, height // 2 + height // 8,
                       _font(max(16, height // 16)), _COGS["gold"])
    elif kind == "seelbon":
        size = min(width, height)
        img = Image.new("RGB", (size, size), _COGS["abyss"])
        draw = ImageDraw.Draw(img)
        _gear(draw, size // 2, size // 2, size // 3, 16, accent)
        _draw_centered(draw, "C", size // 2, size // 2, _font(size // 3), _COGS["bone"])
    elif kind == "avatar":
        size = min(width, height)
        img = Image.new("RGB", (size, size), _COGS["abyss"])
        draw = ImageDraw.Draw(img)
        draw.ellipse([size * 0.1, size * 0.1, size * 0.9, size * 0.9], outline=accent, width=max(4, size // 20))
        _gear(draw, size // 2, size // 2, size // 3, 10, accent)
    elif kind == "map":
        img = _gradient(width, height, (28, 34, 40), (10, 12, 16))
        draw = ImageDraw.Draw(img)
        seed = sum(map(ord, params.get("seed", "redwood")))
        for i in range(width // 20):
            x0 = (seed * (i + 7)) % width
            y0 = (seed * (i * 13 + 3)) % height
            draw.line([(x0, y0), ((x0 + 60) % width, (y0 + 40) % height)], fill=_COGS["steel"], width=2)
        _draw_centered(draw, text, width // 2, height // 2, _font(max(22, height // 12)), _COGS["bone"])
    elif kind == "quote":
        img = _gradient(width, height, (20, 20, 26), _COGS["abyss"])
        draw = ImageDraw.Draw(img)
        words = text.split()
        wrapped = []
        line = []
        for w in words:
            if sum(len(x) for x in line) + len(line) > 28:
                wrapped.append(" ".join(line))
                line = [w]
            else:
                line.append(w)
        wrapped.append(" ".join(line))
        f = _font(max(20, height // 14))
        y = height // 2 - len(wrapped) * (f.size + 8) // 2
        for line in wrapped:
            _draw_centered(draw, line, width // 2, y, f, _COGS["bone"])
            y += f.size + 8
    else:
        raise ValueError(f"unknown forge kind: {kind}")

    if kind in {"avatar", "seelbon"}:
        img = img.convert("RGBA")
        mask = Image.new("L", img.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, img.size[0], img.size[1]], fill=255)
        img.putalpha(mask)
    out = generate_image_filename(kind + ("-" + params.get("tag", "") if params.get("tag") else ""))
    img.save(out)
    return {"kind": kind, "path": out.as_posix(), "size": f"{img.size[0]}x{img.size[1]}"}


def _draw_centered(draw: ImageDraw.ImageDraw, text: str, cx: int, cy: int,
                   font: ImageFont.ImageFont | ImageFont.FreeTypeFont, color: tuple) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, fill=color, font=font)
