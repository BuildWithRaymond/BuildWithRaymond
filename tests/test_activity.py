import importlib.util
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


class ActivityTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).parents[1] / "scripts" / "update_activity.py"
        spec = importlib.util.spec_from_file_location("activity", path)
        self.activity = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.activity)

    def test_private_fork_profile_and_unknown_privacy_are_excluded(self):
        repositories = [
            {"name": "DAOrganizer", "private": False, "fork": False, "language": "C#", "stargazers_count": 3},
            {"name": "private", "private": True, "fork": False, "language": "Secret", "stargazers_count": 99},
            {"name": "NewAges", "private": False, "fork": True, "stargazers_count": 20},
            {"name": "BuildWithRaymond", "private": False, "fork": False, "stargazers_count": 8},
            {"name": "unknown", "fork": False, "stargazers_count": 50},
        ]
        summary = self.activity.summarize(repositories, "BuildWithRaymond")
        self.assertEqual(summary, {"projects": 1, "stars": 3, "languages": [("C#", 1)]})

    def test_languages_count_repositories(self):
        repositories = [{"name": name, "private": False, "language": language}
                        for name, language in [("a", "C#"), ("b", "C#"), ("c", "TypeScript"), ("d", None)]]
        summary = self.activity.summarize(repositories, "BuildWithRaymond")
        self.assertEqual(summary["languages"], [("C#", 2), ("TypeScript", 1)])
        self.assertEqual(summary["projects"], 4)

    def test_every_repository_page_is_fetched(self):
        calls = []
        def fetch(url):
            calls.append(url)
            return [{"name": str(index)} for index in range(100)] if url.endswith("&page=1") else [{"name": "last"}]
        self.assertEqual(len(self.activity.fetch_repositories("BuildWithRaymond", fetch)), 101)
        self.assertEqual(len(calls), 2)

    def test_svg_handles_xml_text_and_empty_languages(self):
        summary = {"projects": 0, "stars": 0, "languages": [("<x & y>", 1)]}
        document = self.activity.render(summary, "2026-10-12")
        ET.fromstring(document)
        self.assertIn("&lt;x &amp; y&gt;", document)
        self.assertNotIn("<x", document)
        self.assertIn('fill="#0B0B0B"', document)
        self.assertIn('fill="#F3EEE7"', document)
        self.assertIn('fill="#FF6A00"', document)
        self.assertNotIn('rx=', document)
        self.assertNotIn('#67e8f9', document)
        ET.fromstring(self.activity.render({"projects": 0, "stars": 0, "languages": []}, "2026-10-12"))

    def test_preview_height_uses_every_asset_and_tallest_card(self):
        from types import SimpleNamespace

        path = Path(__file__).parents[1] / "scripts" / "render_preview.py"
        spec = importlib.util.spec_from_file_location("preview", path)
        preview = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preview)
        heights = {"header.svg": 900, "now.svg": 300, "stack.svg": 250,
                   "da-workshop.svg": 600, "da-organizer.svg": 700,
                   "da-merchant.svg": 100, "da-quester.svg": 300,
                   "da-speaker.svg": 500, "da-dasb.svg": 240,
                   "da-wiki.svg": 280, "activity.svg": 252, "footer.svg": 140}
        calls = []

        def render(path, width):
            calls.append(path.name)
            return SimpleNamespace(name=path.name, width=width, height=heights[path.name])

        pictures, height, _ = preview.preview_layout(renderer=render)
        self.assertEqual(height, 4076)
        self.assertEqual(len(calls), 12)
        footer, _, top = pictures[-1]
        self.assertEqual(footer.name, "footer.svg")
        self.assertEqual(top + footer.height + preview.GUTTER, height)
        left, _, row_top = pictures[4]
        self.assertLessEqual(row_top + left.height, pictures[6][2])

    def test_mobile_activity_preserves_data_and_readable_geometry(self):
        self.assertTrue(callable(getattr(self.activity, "render_mobile", None)), "Mobile activity renderer is required")
        self.assertTrue(callable(getattr(self.activity, "write_activity", None)), "One updater must write both variants")
        summary = {"projects": 11, "stars": 4, "languages": [("C#", 4), ("TypeScript", 2), ("C++", 1)]}
        document = self.activity.render_mobile(summary, "2026-10-27")
        svg = ET.fromstring(document)
        self.assertEqual(svg.attrib["width"], "480")
        self.assertGreaterEqual(int(svg.attrib["height"]), 380)
        self.assertLessEqual(int(svg.attrib["height"]), 440)
        texts = {node.text: node for node in svg.iter("{http://www.w3.org/2000/svg}text")}
        for label in ["Original public", "repositories", "Stars across", "these repos", "C#", "TypeScript", "C++", "4 repositories", "2 repositories", "1 repository"]:
            self.assertIn(label, texts)
            self.assertGreaterEqual(float(texts[label].attrib["font-size"]) * 308 / 480, 14)
        self.assertIn("11", texts)
        self.assertIn("04", texts)
        self.assertIn("2026-10-27", document)
        for node in texts.values():
            self.assertGreaterEqual(float(node.attrib["font-size"]), 22)
        fourth = self.activity.render_mobile({**summary, "languages": summary["languages"] + [("Rust", 1)]}, "2026-10-27")
        fourth_svg = ET.fromstring(fourth)
        self.assertIn("Rust", "".join(fourth_svg.itertext()))
        for node in fourth_svg.iter("{http://www.w3.org/2000/svg}text"):
            self.assertLess(float(node.attrib["x"]), 480)
            self.assertLess(float(node.attrib["y"]), 440)
        unsafe = self.activity.render_mobile({"projects": 0, "stars": 0, "languages": [("<x & y>", 1)]}, "2026-10-27 & review")
        ET.fromstring(unsafe)
        self.assertIn("&lt;x &amp; y&gt;", unsafe)
        self.assertIn("2026-10-27 &amp; review", unsafe)
        ET.fromstring(self.activity.render_mobile({"projects": 0, "stars": 0, "languages": []}, "2026-10-27"))
        with tempfile.TemporaryDirectory(prefix=".profile-test-", dir=Path(__file__).resolve().parent) as temporary:
            destination = Path(temporary)
            self.activity.write_activity(summary, "2026-10-27", destination)
            desktop = ET.parse(destination / "activity.svg").getroot()
            mobile = ET.parse(destination / "activity-mobile.svg").getroot()
            self.assertEqual(desktop.find("{http://www.w3.org/2000/svg}title").text, mobile.find("{http://www.w3.org/2000/svg}title").text)
            for name in ["activity.svg", "activity-mobile.svg"]:
                self.assertIn("2026-10-27", (destination / name).read_text(encoding="utf-8"))

    def test_render_asset_loads_its_image_decoder_at_runtime(self):
        import sys
        from types import ModuleType, SimpleNamespace
        from unittest.mock import MagicMock, patch

        path = Path(__file__).parents[1] / "scripts" / "render_preview.py"
        spec = importlib.util.spec_from_file_location("preview", path)
        preview = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preview)
        picture = MagicMock()
        decoder = MagicMock()
        decoder.open.return_value.__enter__.return_value = picture
        pillow = ModuleType("PIL")
        pillow.Image = decoder
        svg = SimpleNamespace(svg2png=MagicMock(return_value=b"rendered-png"))
        with patch.dict(sys.modules, {"PIL": pillow, "cairosvg": svg}):
            self.assertIs(preview.render_asset(Path("sample.svg"), 128), picture.convert.return_value)
        svg.svg2png.assert_called_once_with(url="sample.svg", output_width=128)
        self.assertEqual(decoder.open.call_args.args[0].getvalue(), b"rendered-png")
        picture.convert.assert_called_once_with("RGBA")

    def test_validator_accepts_local_and_profile_urls_without_path_escape(self):
        path = Path(__file__).parents[1] / "scripts" / "validate_profile.py"
        spec = importlib.util.spec_from_file_location("validator", path)
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        with tempfile.TemporaryDirectory(prefix=".profile-test-", dir=Path(__file__).resolve().parent) as temporary:
            root = Path(temporary)
            (root / "assets").mkdir()
            asset = root / "assets" / "sample.svg"
            asset.write_text('<svg xmlns="http://www.w3.org/2000/svg"><title>Sample</title><desc>Test artwork</desc></svg>', encoding="utf-8")
            (root / "README.md").write_text('<img src="./assets/sample.svg" alt="Sample">', encoding="utf-8")
            self.assertEqual(validator.validate_profile(root), 1)
            (root / "README.md").write_text('<picture><source srcset="assets/sample.svg 1x, assets/sample.svg 2x"><img src="assets/sample.svg" alt="Sample"></picture>', encoding="utf-8")
            self.assertEqual(validator.validate_profile(root), 3)
            (root / "README.md").write_text('<picture><source srcset="https://example.org/hidden.svg"><img src="assets/sample.svg" alt="Sample"></picture>', encoding="utf-8")
            with self.assertRaises(AssertionError):
                validator.validate_profile(root)
            for source in ["assets/sample.svg", "./assets/sample.svg",
                           "https://raw.githubusercontent.com/BuildWithRaymond/BuildWithRaymond/main/assets/sample.svg",
                           "https://raw.githubusercontent.com/BuildWithRaymond/BuildWithRaymond/" + "a" * 40 + "/assets/sample.svg"]:
                self.assertEqual(validator.local_asset_path(source, root), asset.resolve())
            for source in ["../assets/sample.svg", "assets/../README.md", "assets/%2e%2e/sample.svg",
                           "https://example.org/assets/sample.svg", "//example.org/assets/sample.svg",
                           "https://raw.githubusercontent.com/other/profile/main/assets/sample.svg",
                           "assets/sample.svg?fetch=remote", "data:image/svg+xml,sample"]:
                with self.subTest(source=source), self.assertRaises(AssertionError):
                    validator.local_asset_path(source, root)


if __name__ == "__main__":
    unittest.main()

