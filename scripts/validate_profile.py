"""Validate local profile references, standalone SVGs and project exclusions."""
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


class ImageReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        tag = tag.lower()
        if tag == "img":
            source = attributes.get("src")
            assert source, "README image requires a source"
            self.sources.append(source)
        if tag == "source" or (tag == "img" and "srcset" in attributes):
            srcset = attributes.get("srcset")
            assert srcset, "README picture source requires srcset"
            for candidate in srcset.split(","):
                parts = candidate.split()
                assert 1 <= len(parts) <= 2, "Invalid README srcset candidate"
                if len(parts) == 2:
                    assert re.fullmatch(r"(?:[1-9][0-9]*w|[0-9]+(?:\.[0-9]+)?x)", parts[1]), "Invalid README srcset descriptor"
                self.sources.append(parts[0])


def local_asset_path(source, root=ROOT):
    """Map supported README image references to files; never make a web request."""
    parsed = urlsplit(source)
    assert not parsed.query and not parsed.fragment, f"Unexpected image suffix: {source}"
    if parsed.scheme or parsed.netloc:
        assert parsed.scheme == "https" and parsed.netloc == "raw.githubusercontent.com", f"Untrusted image host: {source}"
        match = re.fullmatch(
            r"/BuildWithRaymond/BuildWithRaymond/(?:main|refs/heads/main|[0-9a-fA-F]{40})/(assets/.+)",
            unquote(parsed.path),
        )
        assert match, f"Image must belong to this profile's assets: {source}"
        relative = match.group(1)
    else:
        relative = unquote(parsed.path)
        if relative.startswith("./"):
            relative = relative[2:]
    assert re.fullmatch(r"assets/[A-Za-z0-9][A-Za-z0-9._/-]*\.(?:svg|png|webp)", relative), f"Unsupported image path: {source}"
    assert all(part not in {"", ".", ".."} for part in relative.split("/")), f"Unsafe image path: {source}"
    path = (root / relative).resolve()
    assert path.is_relative_to((root / "assets").resolve()), f"Image escapes local assets: {source}"
    assert path.is_file(), f"Missing image: {relative}"
    return path


def validate_profile(root=ROOT):
    readme = (root / "README.md").read_text(encoding="utf-8")
    for excluded in ["Chaos.Client", "github.com/BuildWithRaymond/NewAges", "github.com/BuildWithRaymond/da)"]:
        assert excluded not in readme, "An excluded project must not appear in the public profile"
    parser = ImageReferences()
    parser.feed(readme)
    references = parser.sources + re.findall(r"!\[[^\]]*\]\(\s*<?([^\s)>]+)>?(?:\s+\"[^\"]*\")?\s*\)", readme)
    assert references, "README must reference its profile artwork"
    for source in references:
        local_asset_path(source, root)
    for path in (root / "assets").glob("*.svg"):
        svg = ET.parse(path).getroot()
        assert svg.tag == SVG_NAMESPACE + "svg", f"Invalid SVG root: {path.name}"
        for tag in ["title", "desc"]:
            node = svg.find(SVG_NAMESPACE + tag)
            assert node is not None and "".join(node.itertext()).strip(), f"SVG requires {tag}: {path.name}"
        for element in svg.iter():
            assert element.tag.rsplit("}", 1)[-1].lower() not in {"script", "foreignobject"}, f"Unsupported SVG element: {path.name}"
            assert not any(key.rsplit("}", 1)[-1].lower().startswith("on") for key in element.attrib), f"SVG event handler: {path.name}"
            for key, value in element.attrib.items():
                if key.rsplit("}", 1)[-1].lower() == "href":
                    assert value.startswith("#"), f"SVG must be standalone: {path.name}"
            if element.tag == SVG_NAMESPACE + "style":
                assert "@import" not in (element.text or "").lower(), f"External SVG stylesheet: {path.name}"
            for target in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", " ".join(element.attrib.values()) + " " + (element.text or "")):
                assert target.startswith("#"), f"External SVG resource: {path.name}"
    return len(references)


if __name__ == "__main__":
    print(f"Validated {validate_profile()} README image references and all SVGs")
