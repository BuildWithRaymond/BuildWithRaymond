"""Manually render animated profile artwork from the approved outlined identity.

Run from the Agency workspace:
    python github-profile/scripts/render_brand_assets.py --brand-dir public/brand

For another checkout, pass the directory containing the approved logo-cream.svg
and mark-cream.svg files. This script is not run by the activity
workflow. Each output is a standalone SVG without external resources.
Short authored passes repeat with quiet holds and invisible resets. Reduced
motion and generated *-static.svg versions show complete static artwork.
Supplied identity geometry and all text stay stationary.
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


def construction_motion(name, actions, cycle=3.8):
    """Forward draws hold, fade, then reset invisibly over a complete track."""
    rules = [f'#{name}-art .draw {{stroke-dasharray: 100 100;}}']
    for index, (class_name, duration, delay, ease) in enumerate(actions):
        finish = min(48, 4 + duration / cycle * 100)
        keyframes = f"{name}-draw-{index}"
        rules.append(
            f'#{name}-art .{class_name} {{animation: {keyframes} '
            f'{cycle}s linear {delay}s infinite both;}}'
        )
        rules.append(
            f'@keyframes {keyframes} {{'
            '0% {stroke-dashoffset: 100; opacity: 0; animation-timing-function: linear;}'
            f'4% {{stroke-dashoffset: 100; opacity: 1; animation-timing-function: {ease};}}'
            f'{finish:.3f}% {{stroke-dashoffset: 0; opacity: 1; animation-timing-function: linear;}}'
            '57% {stroke-dashoffset: 0; opacity: 1; animation-timing-function: cubic-bezier(.4,0,1,1);}'
            '72% {stroke-dashoffset: 0; opacity: 0; animation-timing-function: steps(1,end);}'
            '73%,100% {stroke-dashoffset: 100; opacity: 0;}'
            '}'
        )
    return motion_style(name, '\n'.join(rules))


def drawn_path(d, action, color=ORANGE, width=2, track_opacity=".18"):
    """The complete underdrawing is visible even before decorative construction."""
    return (
        f'<path d="{d}" fill="none" stroke="{CREAM}" '
        f'stroke-opacity="{track_opacity}" stroke-width="{width}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path class="motion draw {action}" d="{d}" pathLength="100" '
        f'fill="none" stroke="{color}" stroke-width="{width}" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def header_accent(name, mobile=False):
    """A fixed brand rule; its faint highlight never leaves the rule itself."""
    x, y, width, height = (28, 446, 66, 6) if mobile else (44, 378, 72, 6)
    return (
        f'<defs><clipPath id="{name}-rule-clip"><rect x="{x}" y="{y}" '
        f'width="{width}" height="{height}"/></clipPath>'
        f'<linearGradient id="{name}-rule-light" x1="0%" x2="100%">'
        f'<stop offset="0" stop-color="{CREAM}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{CREAM}" stop-opacity=".7"/>'
        f'<stop offset="1" stop-color="{CREAM}" stop-opacity="0"/>'
        '</linearGradient></defs>'
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{ORANGE}"/>'
        f'<g clip-path="url(#{name}-rule-clip)">'
        f'<rect class="motion rule-highlight" x="{x - 28}" y="{y}" '
        f'width="28" height="{height}" fill="url(#{name}-rule-light)" opacity="0"/>'
        '</g>'
    )


def header_motion(name, width, repeat=True):
    """One soft light pass inside an anchored rule, with a long quiet interval."""
    travel = width + 28
    count = "infinite" if repeat else "1"
    duration = 6 if repeat else 1.8
    return motion_style(name, f"""
#{name}-art .rule-highlight {{animation: {name}-light {duration}s linear {count} both; transform-box: view-box;}}
@keyframes {name}-light {{
0%,8% {{transform: translateX(0); opacity: 0;}}
10% {{opacity: .22;}}
26% {{transform: translateX({travel}px); opacity: .22;}}
28%,100% {{transform: translateX({travel}px); opacity: 0;}}
}}
@media (prefers-reduced-motion: reduce) {{
#{name}-art .motion.rule-highlight {{animation: none !important; opacity: 0 !important; transform: none !important;}}
}}
""")


def category_gesture(name):
    """Original small category drawings, not application logos or interfaces."""
    out = "cubic-bezier(.16,1,.3,1)"
    settle = "cubic-bezier(.22,.7,.2,1)"
    gestures = {
        "da-organizer": [
            ("M389 24H423V33H389Z", MUTED, .42, .10, out),
            ("M389 39H423V48H389Z", ORANGE, .50, .20, settle),
            ("M389 54H423V63H389Z", MUTED, .48, .30, out),
        ],
        "da-merchant": [
            ("M389 32H423M417 26L423 32L417 38", ORANGE, .54, .10, out),
            ("M423 51H389M395 45L389 51L395 57", MUTED, .60, .22, settle),
        ],
        "da-quester": [
            ("M389 55V40H416V27", ORANGE, .64, .12, settle),
            ("M392 55A3 3 0 1 1 386 55A3 3 0 1 1 392 55", MUTED, .26, .10, out),
            ("M419 27A3 3 0 1 1 413 27A3 3 0 1 1 419 27", MUTED, .26, .64, out),
        ],
        "da-speaker": [
            ("M389 39V45", MUTED, .22, .10, out),
            ("M397 32V52", MUTED, .30, .18, out),
            ("M405 25V59", ORANGE, .38, .26, settle),
            ("M413 32V52", MUTED, .30, .34, out),
            ("M421 39V45", MUTED, .22, .42, out),
        ],
        "da-dasb": [
            ("M398 27L389 41L398 55", MUTED, .42, .10, out),
            ("M414 27L423 41L414 55", MUTED, .42, .22, out),
            ("M400 41H412", ORANGE, .32, .46, settle),
        ],
        "da-wiki": [
            ("M386 32V62H414", MUTED, .40, .10, out),
            ("M391 24H414L423 33V57H391Z M414 24V33H423", MUTED, .62, .20, settle),
            ("M398 41H416M398 48H409", ORANGE, .36, .56, out),
        ],
    }
    paths = []
    actions = []
    for index, (d, color, duration, delay, ease) in enumerate(gestures[name]):
        action = f"gesture-{index}"
        paths.append(drawn_path(d, action, color=color, width=2.2))
        actions.append((action, duration, delay, ease))
    cycle = {"da-organizer": 3.6, "da-merchant": 3.8, "da-quester": 4.0,
             "da-speaker": 3.6, "da-dasb": 3.8, "da-wiki": 4.0}[name]
    return paths, construction_motion(name, actions, cycle=cycle)


def static_copy(source):
    """Removing CSS reveals complete base paths, without duplicating artwork."""
    root = ET.fromstring(source)
    for parent in root.iter():
        for child in list(parent):
            if child.tag.rsplit("}", 1)[-1] == "style":
                parent.remove(child)
    title = root.find(f"{{{NS}}}title")
    description = root.find(f"{{{NS}}}desc")
    if title is not None:
        title.text = (title.text or "") + " — Static version"
    if description is not None:
        description.text = (
            "Motion-free static artwork. All text, supplied identity, and category "
            "drawings are shown in their complete resting state."
        )
    return ET.tostring(root, encoding="unicode") + "\n"


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
        "Raymond Hernbrode and the supplied outlined Hernbrode identity. A fixed short orange rule carries a faint light pass; both logos and all typography remain stationary.",
        [
            f'<rect x="688" width="272" height="420" fill="{CHARCOAL}"/>',
            identity(brand_dir, "logo-cream.svg", 44, 38, 246),
            rule(44, 108, 642, 108),
            text(40, 190, "Raymond", 72, weight=600, spacing="-3.4"),
            text(40, 269, "Hernbrode.", 72, weight=600, spacing="-3.4"),
            text(44, 341, "A higher standard online.", 39, spacing="-1.3"),
            header_accent("header"),
            identity(brand_dir, "mark-cream.svg", 748, 116, 152),
            f'<rect x="688" y="412" width="272" height="8" fill="{ORANGE}"/>',
        ], motion=header_motion("header", 72),
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
            header_accent("header-mobile", mobile=True),
            identity(brand_dir, "mark-cream.svg", 369, 406, 58),
        ], motion=header_motion("header-mobile", 66),
    )
    assets["now.svg"] = svg(
        "now", 960, 130,
        "Web apps. Desktop tools. Game systems.",
        "Raymond's areas of work: web applications, desktop tools, and game systems. A short underline draws once; the words remain visible and stationary.",
        [
            f'<rect x="44" y="32" width="48" height="5" fill="{ORANGE}"/>',
            text(44, 93, "Web apps. Desktop tools. Game systems.", 40, spacing="-1.2"),
            rule(44, 112, 916, 112),
            drawn_path("M44 112H184", "area-rule", width=2),
        ], background=CHARCOAL, motion=construction_motion("now", [
            ("area-rule", .72, .12, "cubic-bezier(.22,.7,.2,1)"),
        ], cycle=4.2),
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
            drawn_path("M18 60H26", "stack-top", width=2),
            drawn_path("M18 130H26", "stack-middle", width=2),
            drawn_path("M18 200H26", "stack-bottom", width=2),
        ], motion=construction_motion("stack", [
            ("stack-top", .32, .12, "cubic-bezier(.16,1,.3,1)"),
            ("stack-middle", .32, .22, "cubic-bezier(.16,1,.3,1)"),
            ("stack-bottom", .32, .32, "cubic-bezier(.16,1,.3,1)"),
        ]),
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
            drawn_path("M590 42V86", "workshop-rule", width=2),
        ], background=CHARCOAL, motion=construction_motion("da-workshop", [
            ("workshop-rule", .52, .18, "cubic-bezier(.22,.7,.2,1)"),
        ], cycle=4.0),
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
    for name, title, category, original_line, description, background in projects:
        foreground = CREAM
        gesture, motion = category_gesture(name)
        assets[name + ".svg"] = svg(
            name, 460, 220, f"{title} — {original_line}",
            f"{description} A small monoline category drawing repeats a forward construction and gentle fade over a complete static track. It is decorative artwork, not an application identity. Reduced motion shows the complete drawing.",
            [
                f'<rect x="28" y="28" width="46" height="5" fill="{ORANGE}"/>',
                text(25, 107, title, 53, fill=foreground, weight=600, spacing="-2.4"),
                text(28, 153, category, 25, fill=foreground, spacing="-.5"),
                rule(28, 188, 432, 188, color=foreground),
                *gesture,
            ], background=background, motion=motion,
        )
    assets["footer.svg"] = svg(
        "footer", 960, 176,
        "Make something useful. Explore Raymond's repositories.",
        "An invitation to explore Raymond Hernbrode's public repositories. The arrow shaft and head repeat a short forward construction over a static track, while the supplied mark, words, and orange rule remain stationary.",
        [
            identity(brand_dir, "mark-cream.svg", 44, 51, 60),
            text(140, 89, "Make something useful.", 52, weight=600, spacing="-2"),
            text(143, 133, "Explore the repositories.", 28, spacing="-.5"),
            drawn_path("M872 94H911", "arrow-shaft", color=CREAM, width=3),
            drawn_path("M895 78L911 94L895 110", "arrow-head", color=CREAM, width=3),
            f'<rect x="0" y="170" width="960" height="6" fill="{ORANGE}"/>',
        ], background=CHARCOAL, motion=construction_motion("footer", [
            ("arrow-shaft", .24, .08, "cubic-bezier(.2,.7,.2,1)"),
            ("arrow-head", .24, .20, "cubic-bezier(.16,1,.3,1)"),
        ], cycle=3.4),
    )
    for filename, content in assets.items():
        (output / filename).write_text(content, encoding="utf-8")
        (output / filename.replace(".svg", "-static.svg")).write_text(
            static_copy(content), encoding="utf-8"
        )
    print(f"Rendered {len(assets)} repeating SVG assets and matching static versions to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--brand-dir", type=Path, required=True)
    args = parser.parse_args()
    render(args.brand_dir, Path(__file__).resolve().parents[1] / "assets")
