"""Refresh the profile SVG using public GitHub repository metadata."""
import json
import os
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen


def fetch_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "BuildWithRaymond-profile"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urlopen(Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def fetch_repositories(username, fetch=fetch_json):
    result, page = [], 1
    while True:
        batch = fetch(f"https://api.github.com/users/{username}/repos?per_page=100&page={page}")
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def summarize(repositories, username):
    # Unknown privacy metadata is excluded instead of being assumed public.
    projects = [repo for repo in repositories if repo.get("private") is False
                and not repo.get("fork", False) and repo.get("name", "").lower() != username.lower()]
    languages = Counter(repo["language"] for repo in projects if repo.get("language"))
    return {"projects": len(projects), "stars": sum(repo.get("stargazers_count", 0) for repo in projects),
            "languages": sorted(languages.items(), key=lambda item: (-item[1], item[0]))[:4]}


def render(summary, updated_date):
    nodes = []
    colors = ["#67e8f9", "#a78bfa", "#6ee7b7", "#fbbf24"]
    total = sum(count for _, count in summary["languages"])
    for index, (language, count) in enumerate(summary["languages"]):
        x = 490 + index * 103
        width = max(4, round(84 * count / total))
        nodes.append(f'<text x="{x}" y="96" fill="#d9e4f1" font-size="12">{escape(language[:13])}</text>'
                     f'<rect x="{x}" y="110" width="84" height="4" rx="2" fill="#1e2b3c"/>'
                     f'<rect x="{x}" y="110" width="{width}" height="4" rx="2" fill="{colors[index]}"/>'
                     f'<text x="{x}" y="137" fill="#8195ad" font-size="11">{count} repo{"s" if count != 1 else ""}</text>')
    if not nodes:
        nodes.append('<text x="490" y="108" fill="#8195ad" font-size="12">Language data will appear here.</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="184" viewBox="0 0 960 184" role="img" aria-labelledby="title desc">
<title id="title">Public signal: {summary['projects']} original public repositories and {summary['stars']} stars</title>
<desc id="desc">Language counts are repositories, not lines of code. Forks and this profile are excluded. Updated {escape(updated_date)} UTC.</desc>
<rect x=".5" y=".5" width="959" height="183" rx="14" fill="#0b1220" stroke="#233047"/>
<g font-family="Consolas, monospace">
<text x="28" y="33" fill="#67e8f9" font-size="11" letter-spacing="2">PUBLIC SIGNAL</text>
<text x="930" y="33" text-anchor="end" fill="#8195ad" font-size="10">UPDATED {escape(updated_date)} UTC</text>
<path d="M28 49 H932 M451 68 V145" stroke="#233047"/>
<text x="30" y="111" fill="#f0f6ff" font-size="46" font-weight="bold">{summary['projects']:02d}</text>
<text x="30" y="136" fill="#8195ad" font-size="11">ORIGINAL PUBLIC REPOS</text>
<text x="251" y="111" fill="#f0f6ff" font-size="46" font-weight="bold">{summary['stars']:02d}</text>
<text x="251" y="136" fill="#8195ad" font-size="11">STARS ACROSS THESE REPOS</text>
{''.join(nodes)}
<text x="490" y="163" fill="#8195ad" font-size="10">PRIMARY LANGUAGE / REPOSITORY COUNT</text>
</g></svg>
'''


def main():
    summary = summarize(fetch_repositories("BuildWithRaymond"), "BuildWithRaymond")
    destination = Path(__file__).resolve().parents[1] / "assets" / "activity.svg"
    destination.write_text(render(summary, datetime.now(timezone.utc).strftime("%Y-%m-%d")), encoding="utf-8")
    print(f"Updated public signal: {summary['projects']} original public repositories")


if __name__ == "__main__":
    main()
