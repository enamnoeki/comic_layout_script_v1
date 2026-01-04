#!/usr/bin/env python3
import json
from pathlib import Path
from PIL import Image, ImageColor

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp"}

def rgba(color: str):
    return ImageColor.getcolor(color, "RGBA")

def open_rgba(path: Path) -> Image.Image:
    img = Image.open(path)
    return img.convert("RGBA")

def fit_contain(img: Image.Image, w: int, h: int) -> Image.Image:
    # preserves aspect ratio, fits inside w x h
    img = img.copy()
    img.thumbnail((w, h), resample=Image.Resampling.LANCZOS)
    return img

def fit_cover(img: Image.Image, w: int, h: int) -> Image.Image:
    # preserves aspect ratio, fills w x h (may crop)
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    nw, nh = int(round(iw * scale)), int(round(ih * scale))
    resized = img.resize((nw, nh), resample=Image.Resampling.LANCZOS)
    left = (nw - w) // 2
    top = (nh - h) // 2
    return resized.crop((left, top, left + w, top + h))

def make_background(cfg_bg: dict, canvas_w: int, canvas_h: int) -> Image.Image:
    bg_type = cfg_bg.get("type", "solid")

    if bg_type == "solid":
        color = cfg_bg.get("color", "#ffffff")
        return Image.new("RGBA", (canvas_w, canvas_h), rgba(color))

    if bg_type == "image":
        file = Path(cfg_bg["file"])
        mode = cfg_bg.get("mode", "cover")  # cover|contain|stretch
        img = open_rgba(file)

        if mode == "stretch":
            out = img.resize((canvas_w, canvas_h), resample=Image.Resampling.LANCZOS)
        elif mode == "contain":
            placed = fit_contain(img, canvas_w, canvas_h)
            out = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            x = (canvas_w - placed.width) // 2
            y = (canvas_h - placed.height) // 2
            out.alpha_composite(placed, (x, y))
        else:  # cover
            out = fit_cover(img, canvas_w, canvas_h)

        return out

    if bg_type == "pattern":
        file = Path(cfg_bg["file"])
        scale = float(cfg_bg.get("scale", 1.0))
        tile = open_rgba(file)

        if scale != 1.0:
            tw = max(1, int(round(tile.width * scale)))
            th = max(1, int(round(tile.height * scale)))
            tile = tile.resize((tw, th), resample=Image.Resampling.LANCZOS)

        out = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        for y in range(0, canvas_h, tile.height):
            for x in range(0, canvas_w, tile.width):
                out.alpha_composite(tile, (x, y))
        return out

    raise ValueError(f"Unknown background type: {bg_type}")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--layout", default="layout.json", help="Path to layout JSON")
    args = ap.parse_args()

    layout_path = Path(args.layout)
    cfg = json.loads(layout_path.read_text(encoding="utf-8"))

    canvas = cfg.get("canvas", {})
    W = int(canvas.get("width", 800))
    H = int(canvas.get("height", 1200))

    bg_cfg = cfg.get("background", {"type": "solid", "color": "#ffffff"})
    base = make_background(bg_cfg, W, H)

    defaults = cfg.get("defaults", {})
    def_w = int(defaults.get("w", 0)) or None
    def_h = int(defaults.get("h", 0)) or None
    def_fit = defaults.get("fit", "contain")  # contain|cover|none

    items = cfg.get("items", [])
    for it in items:
        f = Path(it["file"])
        if f.suffix.lower() not in SUPPORTED:
            raise ValueError(f"Unsupported file type: {f}")

        x = int(it.get("x", 0))
        y = int(it.get("y", 0))
        w = it.get("w", def_w)
        h = it.get("h", def_h)
        fit = it.get("fit", def_fit)  # contain|cover|none

        img = open_rgba(f)

        if w and h and fit != "none":
            w, h = int(w), int(h)
            if fit == "cover":
                img = fit_cover(img, w, h)
            else:  # contain default
                img = fit_contain(img, w, h)

        base.alpha_composite(img, (x, y))

    export = cfg.get("export", {})
    out_file = Path(export.get("file", "output/webcomic.png"))
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Save as PNG
    base.save(out_file)
    print(f"✅ Saved: {out_file}  ({W}x{H})")

if __name__ == "__main__":
    main()
