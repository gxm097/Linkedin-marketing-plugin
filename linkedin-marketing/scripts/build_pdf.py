#!/usr/bin/env python3
"""Stitch carousel slide images into the single multi-page PDF LinkedIn wants.

LinkedIn switched off native multi-image carousels in December 2023. A swipeable
carousel is now a *document post*: one multi-page file, one page per slide. So
however the slides were produced, they have to arrive as a single PDF.

Usage:
    python3 -I build_pdf.py <slides_dir> -o <out.pdf> [--title "Deck title"]
"""

import argparse
import sys
from pathlib import Path

# LinkedIn's documented caps for document posts.
MAX_PAGES = 300
MAX_BYTES = 100 * 1024 * 1024

SUFFIXES = (".png", ".jpg", ".jpeg")


def find_slides(slides_dir: Path) -> list[Path]:
    slides = sorted(
        p for p in slides_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUFFIXES
    )
    if not slides:
        sys.exit(f"No slide images ({', '.join(SUFFIXES)}) found in {slides_dir}")
    if len(slides) > MAX_PAGES:
        sys.exit(f"{len(slides)} slides exceeds LinkedIn's {MAX_PAGES}-page limit")
    return slides


def build_with_img2pdf(slides: list[Path], out: Path) -> bool:
    """Lossless and exact, but img2pdf is often not installed."""
    try:
        import img2pdf
    except ImportError:
        return False
    with out.open("wb") as fh:
        img2pdf.convert([str(p) for p in slides], outputstream=fh)
    return True


def build_with_pillow(slides: list[Path], out: Path) -> bool:
    try:
        from PIL import Image
    except ImportError:
        return False
    # Flattening onto white matters: a transparent PNG converted straight to RGB
    # turns its transparent areas black, which looks like a rendering bug.
    pages = []
    for path in slides:
        img = Image.open(path)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            canvas = Image.new("RGB", img.size, (255, 255, 255))
            canvas.paste(img, mask=img.split()[-1])
            img = canvas
        else:
            img = img.convert("RGB")
        pages.append(img)
    pages[0].save(
        out, "PDF", save_all=True, append_images=pages[1:], resolution=150.0
    )
    return True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slides_dir", type=Path, help="Directory of slide images")
    ap.add_argument("-o", "--out", type=Path, required=True, help="Output PDF path")
    ap.add_argument("--title", default=None, help="Deck title, for the log line only")
    args = ap.parse_args()

    if not args.slides_dir.is_dir():
        sys.exit(f"Not a directory: {args.slides_dir}")

    slides = find_slides(args.slides_dir)

    # Mixed slide sizes make LinkedIn letterbox some pages and not others, which
    # reads as a mistake in the feed. Worth a warning, not worth refusing.
    try:
        from PIL import Image
        sizes = {Image.open(p).size for p in slides}
        if len(sizes) > 1:
            print(
                f"warning: slides are not all the same size ({sorted(sizes)}); "
                "LinkedIn will pad the odd ones out",
                file=sys.stderr,
            )
    except ImportError:
        pass

    args.out.parent.mkdir(parents=True, exist_ok=True)

    if not (build_with_img2pdf(slides, args.out) or build_with_pillow(slides, args.out)):
        sys.exit(
            "Need img2pdf or Pillow to build the PDF. Install one with:\n"
            "  python3 -m pip install Pillow"
        )

    size = args.out.stat().st_size
    if size > MAX_BYTES:
        sys.exit(
            f"{args.out} is {size / 1024 / 1024:.1f} MB, over LinkedIn's 100 MB "
            "limit. Re-export the slides at a lower quality."
        )

    label = f" ({args.title})" if args.title else ""
    print(f"{args.out}: {len(slides)} pages, {size / 1024:.0f} KB{label}")


if __name__ == "__main__":
    main()
