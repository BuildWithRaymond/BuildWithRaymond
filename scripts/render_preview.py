"""Render an artwork contact sheet for visual QA in the workflow log."""
import base64
import io
from pathlib import Path
import cairosvg
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1] / "assets"
canvas = Image.new("RGB", (960, 1600), "#080d16")
draw = ImageDraw.Draw(canvas)
y = 12

def render(name, width):
    data = cairosvg.svg2png(url=str(root / name), output_width=width)
    return Image.open(io.BytesIO(data)).convert("RGBA")

for name in ["header.svg", "now.svg", "stack.svg"]:
    picture = render(name, 936)
    canvas.paste(picture, (12, y), picture)
    y += picture.height + 12
draw.text((24, y + 3), "Dark Ages apps & tools", fill="#d9e4f1")
y += 34
picture = render("da-section.svg", 936)
canvas.paste(picture, (12, y), picture)
y += picture.height + 10
for left, right in [("organizer.svg", "merchant.svg"), ("quester.svg", "speaker.svg"), ("dasb.svg", "wiki.svg")]:
    for name, x in [(left, 12), (right, 486)]:
        picture = render(name, 462)
        canvas.paste(picture, (x, y), picture)
    y += picture.height + 12
for name in ["activity.svg", "footer.svg"]:
    picture = render(name, 936)
    canvas.paste(picture, (12, y), picture)
    y += picture.height + 12
output = io.BytesIO()
canvas.crop((0, 0, 960, y)).save(output, format="PNG")
print("SVG_PREVIEW_BASE64:" + base64.b64encode(output.getvalue()).decode("ascii"))
