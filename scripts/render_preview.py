"""Render the complete artwork contact sheet, preserving the workflow log format."""
import argparse
import base64
import io
from pathlib import Path

ASSET_ROOT = Path(__file__).resolve().parents[1] / "assets"
CANVAS_WIDTH = 960
GUTTER = 12
FULL_WIDTH = CANVAS_WIDTH - 2 * GUTTER
CARD_WIDTH = (FULL_WIDTH - GUTTER) // 2
CARD_PAIRS = [
    ("da-organizer.svg", "da-merchant.svg"),
    ("da-quester.svg", "da-speaker.svg"),
    ("da-dasb.svg", "da-wiki.svg"),
]


def render_asset(path, width):
    # The workflow installs CairoSVG; lazy import also permits local layout tests.
    import cairosvg
    from PIL import Image

    data = cairosvg.svg2png(url=str(path), output_width=width)
    with Image.open(io.BytesIO(data)) as picture:
        return picture.convert("RGBA")


def preview_layout(asset_root=ASSET_ROOT, renderer=render_asset):
    """Place rendered assets using their actual heights, including uneven rows."""
    pictures = []
    y = GUTTER

    def add_full(name):
        nonlocal y
        picture = renderer(asset_root / name, FULL_WIDTH)
        pictures.append((picture, GUTTER, y))
        y += picture.height + GUTTER

    for name in ["header.svg", "now.svg", "stack.svg"]:
        add_full(name)
    caption_y = y + 3
    y += 34
    add_full("da-workshop.svg")

    for left, right in CARD_PAIRS:
        row_height = 0
        for name, x in [(left, GUTTER), (right, GUTTER * 2 + CARD_WIDTH)]:
            picture = renderer(asset_root / name, CARD_WIDTH)
            pictures.append((picture, x, y))
            row_height = max(row_height, picture.height)
        y += row_height + GUTTER

    for name in ["activity.svg", "footer.svg"]:
        add_full(name)

    return pictures, y, caption_y


def compose_preview(asset_root=ASSET_ROOT, renderer=render_asset):
    from PIL import Image, ImageDraw

    pictures, height, caption_y = preview_layout(asset_root, renderer)
    canvas = Image.new("RGB", (CANVAS_WIDTH, height), "#0B0B0B")
    for picture, x, top in pictures:
        canvas.paste(picture, (x, top), picture)
    ImageDraw.Draw(canvas).text(
        (24, caption_y), "Dark Ages apps & tools", fill="#F3EEE7"
    )
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Also save the complete PNG locally.")
    args = parser.parse_args()
    output = io.BytesIO()
    compose_preview().save(output, format="PNG")
    data = output.getvalue()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(data)
    # Keep this exact prefix and default output for existing workflow consumers.
    print("SVG_PREVIEW_BASE64:" + base64.b64encode(data).decode("ascii"))


if __name__ == "__main__":
    main()
