"""Manually render animated profile artwork from the approved outlined identity.

Run from the Agency workspace:
    python github-profile/scripts/render_brand_assets.py --brand-dir public/brand

For another checkout, pass the directory containing the approved logo-cream.svg
and mark-cream.svg files. This script is not run by the activity
workflow. Each output is a standalone SVG without external resources.
Motion has long rests; reduced-motion preferences return complete static art.
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


def motion_style(name, rules):
    return (
        '<style>\n' + rules + '\n'
        '@media (prefers-reduced-motion: reduce) {\n'
        f'#{name}-art .motion, #{name}-art .motion * '
        '{animation: none !important; transition: none !important; '
        'transform: none !important; opacity: 1 !important; '
        'stroke-dasharray: none !important; stroke-dashoffset: 0 !important;}\n'
        '}\n</style>'
    )


def sweep_motion(name, distance, duration=10.8):
    return motion_style(name, f"""
#{name}-art .sweep {{animation: {name}-sweep {duration}s cubic-bezier(.4,0,.2,1) infinite; transform-box: view-box;}}
#{name}-art .rail {{animation: {name}-rail {duration}s cubic-bezier(.4,0,.2,1) infinite; transform-box: fill-box; transform-origin: left center;}}
@keyframes {name}-sweep {{0%,8%,35%,100% {{transform: translateX(0);}} 23% {{transform: translateX({distance}px);}}}}
@keyframes {name}-rail {{0%,10%,35%,100% {{transform: scaleX(1);}} 23% {{transform: scaleX(.58);}}}}
""")


def project_motion(name, index):
    duration = 9.6 + (index % 3) * .8
    travel = 260 if index % 2 == 0 else -270
    return motion_style(name, f"""
#{name}-art .corner {{animation: {name}-corner {duration}s ease-in-out {index * .18:.2f}s infinite;}}
#{name}-art .underline {{animation: {name}-underline {duration}s cubic-bezier(.4,0,.2,1) {index * .18:.2f}s infinite; transform-box: fill-box; transform-origin: left center;}}
@keyframes {name}-corner {{0%,8%,35%,100% {{stroke-dasharray: 120 0; stroke-dashoffset: 0;}} 16% {{stroke-dasharray: 28 92; stroke-dashoffset: 0;}} 28% {{stroke-dasharray: 28 92; stroke-dashoffset: -120;}} 34% {{stroke-dasharray: 120 0; stroke-dashoffset: -120;}}}}
@keyframes {name}-underline {{0%,10%,36%,100% {{transform: translateX(0) scaleX(1);}} 25% {{transform: translateX({travel}px) scaleX(1.45);}}}}
""")


def svg(name, width, height, title, description, artwork, background=INK, motion=""):
    if background not in {INK, CHARCOAL}:
        raise ValueError("Profile artwork uses ink or charcoal surfaces only.")
    return (
        f'<svg xmlns="{NS}" id="{name}-art" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-labelledby="{name}-title {name}-desc" '
        'font-family="Inter, Segoe UI, Arial, sans-serif">\n'
        f'<title id="{name}-title">{escape(title)}</title>\n'
        f'<desc id="{name}-desc">{escape(description)}</desc>\n'
        + motion + '\n'
        +
        f'<rect width="{width}" height="{height}" fill="{background}"/>\n'
        + "\n".join(artwork)
        + f'\n<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" '
        f'fill="none" stroke="{CREAM}" stroke-opacity=".18"/>\n'
        '</svg>\n'
    )


def render(brand_dir, output):
    assets = {}
    assets["header.svg"] = svg(
        "header", 960, 420,
        "Raymond Hernbrode — A higher standard online.",
        "Raymond Hernbrode and the supplied outlined Hernbrode identity. A measured orange sweep sits behind the stationary mark; reduced motion preserves the complete artwork.",
        [
            f'<rect x="688" width="272" height="420" fill="{CHARCOAL}"/>',
            identity(brand_dir, "logo-cream.svg", 44, 38, 246),
            rule(44, 108, 642, 108),
            text(40, 190, "Raymond", 72, weight=600, spacing="-3.4"),
            text(40, 269, "Hernbrode.", 72, weight=600, spacing="-3.4"),
            text(44, 341, "A higher standard online.", 39, spacing="-1.3"),
            f'<rect x="44" y="378" width="72" height="6" fill="{ORANGE}"/>',
            '<defs><clipPath id="header-panel"><rect x="688" width="272" height="412"/></clipPath></defs>',
            f'<g clip-path="url(#header-panel)"><path class="motion sweep" d="M692 -40H718L942 452H916Z" fill="{ORANGE}" fill-opacity=".13"/></g>',
            identity(brand_dir, "mark-cream.svg", 748, 116, 152),
            f'<rect class="motion rail" x="688" y="412" width="272" height="8" fill="{ORANGE}"/>',
        ], motion=sweep_motion("header", 100),
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
            f'<rect x="344" y="386" width="108" height="114" fill="{CHARCOAL}"/>',
            '<defs><clipPath id="header-mobile-panel"><rect x="344" y="386" width="108" height="114"/></clipPath></defs>',
            f'<g clip-path="url(#header-mobile-panel)"><path class="motion sweep" d="M346 376H357L421 510H410Z" fill="{ORANGE}" fill-opacity=".13"/></g>',
            identity(brand_dir, "mark-cream.svg", 369, 406, 58),
            f'<rect class="motion rail" x="28" y="446" width="66" height="6" fill="{ORANGE}"/>',
        ], motion=sweep_motion("header-mobile", 30),
    )
    assets["now.svg"] = svg(
        "now", 960, 130,
        "Web apps. Desktop tools. Game systems.",
        "Raymond's areas of work: web applications, desktop tools, and game systems. A quiet marker follows the areas without moving the text.",
        [
            f'<rect x="44" y="32" width="48" height="5" fill="{ORANGE}"/>',
            text(44, 93, "Web apps. Desktop tools. Game systems.", 40, spacing="-1.2"),
            rule(44, 112, 916, 112),
            f'<rect class="motion category-marker" x="44" y="110" width="140" height="3" fill="{ORANGE}"/>',
        ], background=CHARCOAL, motion=motion_style("now", """
#now-art .category-marker {animation: now-categories 12s cubic-bezier(.4,0,.2,1) infinite; transform-box: view-box;}
@keyframes now-categories {0%,8%,35%,100% {transform: translateX(0);} 17% {transform: translateX(235px);} 26% {transform: translateX(560px);}}
"""),
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
            f'<rect class="motion stack-marker" x="18" y="48" width="4" height="24" fill="{ORANGE}"/>',
        ], motion=motion_style("stack", """
#stack-art .stack-marker {animation: stack-rows 11.4s cubic-bezier(.4,0,.2,1) .18s infinite; transform-box: view-box;}
@keyframes stack-rows {0%,8%,35%,100% {transform: translateY(0);} 17% {transform: translateY(70px);} 26% {transform: translateY(140px);}}
"""),
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
            f'<rect class="motion workshop-marker" x="588.5" y="42" width="3" height="26" fill="{ORANGE}"/>',
        ], background=CHARCOAL, motion=motion_style("da-workshop", """
#da-workshop-art .workshop-marker {animation: workshop-rule 10.4s cubic-bezier(.4,0,.2,1) .36s infinite; transform-box: view-box;}
@keyframes workshop-rule {0%,8%,35%,100% {transform: translateY(0);} 23% {transform: translateY(110px);}}
"""),
    )
    projects = [
        ("da-organizer", "DAOrganizer", "Inventory & transfers", "Your collection, brought together.",
         "Find items. Arrange inventories. Review transfers. C# / Avalonia / .NET.", CHARCOAL),
        ("da-merchant", "DAMerchant", "Trading & exchange", "Set up shop. Keep it connected.",
         "Trading tools with AislingExchange integration. TypeScript / Windows.", INK),
        ("da-quester", "DAQuester", "Quest planning", "A journal for the journey ahead.",
         "Plan quests and keep each character's progress. C# / Avalonia / .NET.", CHARCOAL),
        ("da-speaker", "DASpeaker", "Speech preparation", "Your words, at your pace.",
         "Prepare speeches. Preview messages. Stay in control. C# / .NET / Windows.", INK),
        ("da-dasb", "DASB", "Protocol & tooling", "A toolkit beneath the game.",
         "Protocol tools, automation, and a web dashboard. TypeScript / Node.js.", CHARCOAL),
        ("da-wiki", "UnoraWiki", "Community wiki / Fork", "Knowledge worth keeping together.",
         "A Dark Ages community wiki. Forked from Unora. Community fork with upstream credit.", CHARCOAL),
    ]
    for index, (name, title, category, original_line, description, background) in enumerate(projects):
        foreground = CREAM
        corner = "M402 28H432V58" if index % 2 == 0 else "M28 173V188H58"
        marker_x = 28 if index % 2 == 0 else 360
        assets[name + ".svg"] = svg(
            name, 460, 220, f"{title} — {original_line}",
            f"{description} A restrained corner trace and underline frame the stationary project name. Complete static artwork is shown with reduced motion.",
            [
                f'<rect x="28" y="28" width="46" height="5" fill="{ORANGE}"/>',
                text(25, 107, title, 53, fill=foreground, weight=600, spacing="-2.4"),
                text(28, 153, category, 25, fill=foreground, spacing="-.5"),
                rule(28, 188, 432, 188, color=foreground),
                f'<path class="motion corner" d="{corner}" pathLength="120" fill="none" stroke="{ORANGE}" stroke-width="2"/>',
                f'<rect class="motion underline" x="{marker_x}" y="187" width="32" height="2" fill="{ORANGE}"/>',
            ], background=background, motion=project_motion(name, index),
        )
    assets["footer.svg"] = svg(
        "footer", 960, 176,
        "Make something useful. Explore Raymond's repositories.",
        "An invitation to explore Raymond Hernbrode's public repositories. The arrow and orange rule move briefly, while the supplied mark and words remain stationary.",
        [
            identity(brand_dir, "mark-cream.svg", 44, 51, 60),
            text(140, 89, "Make something useful.", 52, weight=600, spacing="-2"),
            text(143, 133, "Explore the repositories.", 28, spacing="-.5"),
            f'<path class="motion footer-arrow" d="M872 94H911M895 78L911 94L895 110" fill="none" stroke="{CREAM}" stroke-width="3"/>',
            f'<rect class="motion footer-rail" x="0" y="170" width="960" height="6" fill="{ORANGE}"/>',
        ], background=CHARCOAL, motion=motion_style("footer", """
#footer-art .footer-arrow {animation: footer-invitation 9.8s cubic-bezier(.4,0,.2,1) infinite; transform-box: view-box;}
#footer-art .footer-rail {animation: footer-rule 9.8s cubic-bezier(.4,0,.2,1) infinite; transform-box: fill-box; transform-origin: left center;}
@keyframes footer-invitation {0%,10%,35%,100% {transform: translateX(0);} 20% {transform: translateX(9px);} 30% {transform: translateX(0);}}
@keyframes footer-rule {0%,8%,35%,100% {transform: scaleX(1);} 23% {transform: scaleX(.88);}}
"""),
    )
    for filename, content in assets.items():
        (output / filename).write_text(content, encoding="utf-8")
    print(f"Rendered {len(assets)} animated SVG assets with reduced-motion fallbacks to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand-dir", type=Path, required=True)
    args = parser.parse_args()
    render(args.brand_dir, Path(__file__).resolve().parents[1] / "assets")
