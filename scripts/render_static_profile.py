"""Generate an equivalent still profile from the primary README."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC_URL = "https://github.com/BuildWithRaymond/BuildWithRaymond/blob/main/STATIC.md"
PROFILE_URL = "https://github.com/BuildWithRaymond"


def render_static(readme):
    # Animated sources are selected only by this explicit media feature.
    # Remaining <source> tags are width-responsive still images; every <img>
    # already uses a still fallback. Preserve all native copy and project links.
    content = re.sub(
        r"[ \t]*<source\b(?=[^>]*prefers-reduced-motion)[^>]*>[^\S\n]*\n?",
        "", readme, flags=re.IGNORECASE,
    )
    content = content.replace(STATIC_URL, PROFILE_URL)
    content = content.replace("View without animation", "View animated profile")
    return content


def main():
    source = (ROOT / "README.md").read_text(encoding="utf-8")
    (ROOT / "STATIC.md").write_text(render_static(source), encoding="utf-8")
    print("Generated STATIC.md from README.md")


if __name__ == "__main__":
    main()
