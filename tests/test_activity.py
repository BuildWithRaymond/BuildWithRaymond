import importlib.util
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
        ET.fromstring(self.activity.render({"projects": 0, "stars": 0, "languages": []}, "2026-10-12"))


if __name__ == "__main__":
    unittest.main()
