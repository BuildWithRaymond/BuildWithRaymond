"""Validate references, standalone SVGs and project exclusions."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

root = Path(__file__).resolve().parents[1]
readme = (root / "README.md").read_text(encoding="utf-8")
assert "Chaos.Client" not in readme, "Excluded project must not be listed"
references = re.findall(r'main/(assets/[^"]+)', readme)
for name in references:
    assert (root / name).is_file(), f"Missing image: {name}"
for path in (root / "assets").glob("*.svg"):
    svg = ET.parse(path).getroot()
    assert svg.tag == "{http://www.w3.org/2000/svg}svg"
    for tag in ["title", "desc"]:
        assert svg.find("{http://www.w3.org/2000/svg}" + tag) is not None
    for element in svg.iter():
        assert element.tag.rsplit("}", 1)[-1] not in {"script", "foreignObject"}
        assert not any(key.startswith("on") for key in element.attrib)
print(f"Validated {len(references)} README image references and all SVGs")
