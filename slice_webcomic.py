#!/usr/bin/env python3
from pathlib import Path
import argparse
from PIL import Image

def slice_image(in_path: Path, out_dir: Path, slice_height: int, overlap: int, clean: bool):
    if slice_height <= 0:
        raise ValueError("slice_height must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= slice_height:
        raise ValueError("overlap must be < slice_height")

    out_dir.mkdir(parents=True, exist_ok=True)

    if clean:
        for p in out_dir.glob("*.png"):
            p.unlink()

    img = Image.open(in_path)
    W, H = img.size

    step = slice_height - overlap
    if step <= 0:
        raise ValueError("step must be > 0 (slice_height must be greater than overlap)")

    # Compute slice count up front (for debugging)
    # This guarantees the remainder is included.
    n = 0
    y = 0
    while y < H:
        n += 1
        y += step

    print(f"📌 Input:  {in_path}")
    print(f"📌 Size:   {W}x{H}")
    print(f"📌 Slice:  height={slice_height}, overlap={overlap}, step={step}")
    print(f"📌 Will write: {n} slice(s) to {out_dir}")

    y = 0
    i = 1
    while y < H:
        y2 = min(y + slice_height, H)  # ALWAYS includes final remainder
        crop = img.crop((0, y, W, y2))
        crop.save(out_dir / f"{i:03d}.png")
        i += 1
        y += step

    print(f"✅ Done. Wrote {i-1} slice(s). Last slice height = {Image.open(out_dir / f'{i-1:03d}.png').size[1]}px")

def main():
    ap = argparse.ArgumentParser(description="Slice a tall webcomic image into smaller images.")
    ap.add_argument("--input", required=True, help="Input image (e.g., output/webcomic.png)")
    ap.add_argument("--outdir", default="", help="Output folder (default: <input_dir>/slices)")
    ap.add_argument("--slice-height", type=int, default=1200, help="Slice height in px (default: 1200)")
    ap.add_argument("--overlap", type=int, default=0, help="Overlap in px (default: 0)")
    ap.add_argument("--clean", action="store_true", help="Delete old PNG slices in outdir before writing new ones")
    args = ap.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    out_dir = Path(args.outdir) if args.outdir else in_path.parent / "slices"
    slice_image(in_path, out_dir, args.slice_height, args.overlap, args.clean)

if __name__ == "__main__":
    main()
