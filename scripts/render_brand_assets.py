"""Manually render static profile artwork from the approved outlined identity.

Run from the Agency workspace:
    python github-profile/scripts/render_brand_assets.py --brand-dir public/brand

For another checkout, pass the directory containing the approved logo-cream.svg,
mark-cream.svg, and mark-black.svg files. This script is not run by the activity
workflow. Each output is a standalone SVG without external resources.
"""

import argparse
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET


INK = "#0B0B0B"
CHARCOAL = "#1F1F1F"
CREAM = "#F3EEE7"
ORANGE = "#FF6A00"
MUTED = "#BDB6AD"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)


def text(x, y, value, size, fill=CREAM, weight=400, spacing=None):
    tracking = f' letter-spacing="{spacing}"' if spacing is not None else ""
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-weight="{weight}"{tracking}>{escape(value)}</text>'
    )


def rule(x1, y1, x2, y2, color=CREAM, opacity=".2"):
    return (
        f'<path d="M{x1} {y1}H{x2}" fill="none" stroke="{color}" '
        f'stroke-opacity="{opacity}"/>'
        if y1 == y2
        else f'<path d="M{x1} {y1}V{y2}" fill="none" stroke="{color}" '
        f'stroke-opacity="{opacity}"/>'
    )


def identity(brand_dir, filename, x, y, width):
    source = ET.parse(brand_dir / filename).getroot()
    source_width = float(source.attrib["viewBox"].split()[2])
    geometry = "".join(
        ET.tostring(child, encoding="unicode").replace(f' xmlns="{NS}"', "")
        for child in source
        if child.tag.rsplit("}", 1)[-1] == "g"
    )
    return f'<g transform="translate({x} {y}) scale({width / source_width:.9f})">{geometry}</g>'


def svg(name, width, height, title, description, artwork, background=INK):
    return (
        f'<svg xmlns="{NS}" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-labelledby="{name}-title {name}-desc" '
        'font-family="Inter, Segoe UI, Arial, sans-serif">\n'
        f'<title id="{name}-title">{escape(title)}</title>\n'
        f'<desc id="{name}-desc">{escape(description)}</desc>\n'
        f'<rect width="{width}" height="{height}" fill="{background}"/>\n'
        + "\n".join(artwork)
        + f'\n<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" '
        f'fill="none" stroke="{CREAM if background != CREAM else INK}" stroke-opacity=".18"/>\n'
        '</svg>\n'
    )


def render(brand_dir, output):
    assets = {}
    assets["header.svg"] = svg(
        "header", 960, 420,
        "Raymond Hernbrode — A higher standard online.",
        "Raymond Hernbrode and the supplied outlined Hernbrode identity. Static ink, cream, and orange profile artwork.",
        [
            f'<rect x="688" width="272" height="420" fill="{CREAM}"/>',
            identity(brand_dir, "logo-cream.svg", 44, 38, 246),
            rule(44, 108, 642, 108),
            text(40, 190, "Raymond", 72, weight=600, spacing="-3.4"),
            text(40, 269, "Hernbrode.", 72, weight=600, spacing="-3.4"),
            text(44, 341, "A higher standard online.", 39, spacing="-1.3"),
            f'<rect x="44" y="378" width="72" height="6" fill="{ORANGE}"/>',
            identity(brand_dir, "mark-black.svg", 748, 116, 152),
            f'<rect x="688" y="412" width="272" height="8" fill="{ORANGE}"/>',
        ],
    )
    assets["header-mobile.svg"] = svg(
        "header-mobile", 480, 500,
        "Raymond Hernbrode — A higher standard online.",
        "Mobile composition of the supplied Hernbrode identity, Raymond Hernbrode's name, and the brand line.",
        [
            identity(brand_dir, "logo-cream.svg", 28, 30, 250),
            rule(28, 102, 452, 102),
            text(26, 175, "Raymond", 64, weight=600, spacing="-3"),
            text(26, 246, "Hernbrode.", 64, weight=600, spacing="-3"),
            text(28, 317, "A higher standard", 37, spacing="-1.2"),
            text(28, 360, "online.", 37, spacing="-1.2"),
            f'<rect x="344" y="386" width="108" height="114" fill="{CREAM}"/>',
            identity(brand_dir, "mark-black.svg", 369, 406, 58),
            f'<rect x="28" y="446" width="66" height="6" fill="{ORANGE}"/>',
        ],
    )
    assets["now.svg"] = svg(
        "now", 960, 130,
        "Web apps. Desktop tools. Game systems.",
        "Raymond's areas of work: web applications, desktop tools, and game systems. Static profile artwork.",
        [
            f'<rect x="44" y="32" width="48" height="5" fill="{ORANGE}"/>',
            text(44, 93, "Web apps. Desktop tools. Game systems.", 40, spacing="-1.2"),
        ], background=CHARCOAL,
    )
    assets["stack.svg"] = svg(
        "stack", 960, 240,
        "C#, .NET, Avalonia, TypeScript, React, Next.js, Node.js, and SQLite",
        "Selected technologies, presented as a static typographic list without proficiency ratings or invented metrics.",
        [
            rule(480, 28, 480, 212),
            text(44, 74, "C# / .NET", 40, weight=550, spacing="-1"),
            text(524, 74, "Avalonia", 40, weight=550, spacing="-1"),
            rule(44, 98, 436, 98), rule(524, 98, 916, 98),
            text(44, 144, "TypeScript", 40, weight=550, spacing="-1"),
            text(524, 144, "React / Next.js", 40, weight=550, spacing="-1"),
            rule(44, 168, 436, 168), rule(524, 168, 916, 168),
            text(44, 214, "Node.js", 40, weight=550, spacing="-1"),
            text(524, 214, "SQLite", 40, weight=550, spacing="-1"),
        ],
    )
    assets["da-workshop.svg"] = svg(
        "da-workshop", 960, 220,
        "Dark Ages — Apps and community tools",
        "A section header for Raymond's actual Dark Ages applications and community tools. Brand typography, not an application logo or invented interface.",
        [
            f'<rect x="44" y="36" width="60" height="6" fill="{ORANGE}"/>',
            text(40, 123, "Dark Ages", 76, weight=600, spacing="-3.8"),
            text(44, 181, "Apps & community tools", 32, fill=MUTED, spacing="-.6"),
            rule(590, 42, 590, 178),
            text(638, 104, "Selected", 32, fill=MUTED, spacing="-.5"),
            text(638, 150, "projects.", 40, weight=550, spacing="-1.2"),
        ], background=CHARCOAL,
    )
    projects = [
        ("da-organizer", "DAOrganizer", "Inventory & transfers", "Your collection, brought together.",
         "Find items. Arrange inventories. Review transfers. C# / Avalonia / .NET.", CREAM),
        ("da-merchant", "DAMerchant", "Trading & exchange", "Set up shop. Keep it connected.",
         "Trading tools with AislingExchange integration. TypeScript / Windows.", INK),
        ("da-quester", "DAQuester", "Quest planning", "A journal for the journey ahead.",
         "Plan quests and keep each character's progress. C# / Avalonia / .NET.", CHARCOAL),
        ("da-speaker", "DASpeaker", "Speech preparation", "Your words, at your pace.",
         "Prepare speeches. Preview messages. Stay in control. C# / .NET / Windows.", CREAM),
        ("da-dasb", "DASB", "Protocol & tooling", "A toolkit beneath the game.",
         "Protocol tools, automation, and a web dashboard. TypeScript / Node.js.", CREAM),
        ("da-wiki", "UnoraWiki", "Community wiki / Fork", "Knowledge worth keeping together.",
         "A Dark Ages community wiki. Forked from Unora. Community fork with upstream credit.", CHARCOAL),
    ]
    for name, title, category, original_line, description, background in projects:
        foreground = INK if background == CREAM else CREAM
        assets[name + ".svg"] = svg(
            name, 460, 220, f"{title} — {original_line}",
            f"{description} Static Hernbrode profile project header; not a replacement application identity.",
            [
                f'<rect x="28" y="28" width="46" height="5" fill="{ORANGE}"/>',
                text(25, 107, title, 53, fill=foreground, weight=600, spacing="-2.4"),
                text(28, 153, category, 25, fill=foreground, spacing="-.5"),
                rule(28, 188, 432, 188, color=foreground),
                f'<rect x="426" y="28" width="6" height="22" fill="{ORANGE}"/>',
            ], background=background,
        )
    assets["footer.svg"] = svg(
        "footer", 960, 176,
        "Make something useful. Explore Raymond's repositories.",
        "A static closing invitation to explore Raymond Hernbrode's public repositories. Supplied Hernbrode mark and approved ink, cream, and orange identity.",
        [
            identity(brand_dir, "mark-black.svg", 44, 51, 60),
            text(140, 89, "Make something useful.", 52, fill=INK, weight=600, spacing="-2"),
            text(143, 133, "Explore the repositories.", 28, fill=INK, spacing="-.5"),
            f'<path d="M872 94H911M895 78L911 94L895 110" fill="none" stroke="{INK}" stroke-width="3"/>',
            f'<rect x="0" y="170" width="960" height="6" fill="{ORANGE}"/>',
        ], background=CREAM,
    )
    for filename, content in assets.items():
        (output / filename).write_text(content, encoding="utf-8")
    print(f"Rendered {len(assets)} static SVG assets to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand-dir", type=Path, required=True)
    args = parser.parse_args()
    render(args.brand_dir, Path(__file__).resolve().parents[1] / "assets")
