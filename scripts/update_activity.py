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
    total = sum(count for _, count in summary["languages"])
    for index, (language, count) in enumerate(summary["languages"]):
        x = 492 + index * 105
        width = max(4, round(84 * count / total))
        color = "#FF6A00" if index == 0 else "#F3EEE7"
        nodes.append(f'<text x="{x}" y="114" fill="#F3EEE7" font-size="16">{escape(language[:13])}</text>'
                     f'<rect x="{x}" y="132" width="84" height="4" fill="#1F1F1F"/>'
                     f'<rect x="{x}" y="132" width="{width}" height="4" fill="{color}"/>'
                     f'<text x="{x}" y="163" fill="#BDB6AD" font-size="15">{count} repo{"s" if count != 1 else ""}</text>')
    if not nodes:
        nodes.append('<text x="492" y="132" fill="#BDB6AD" font-size="16">No primary language data reported.</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="252" viewBox="0 0 960 252" role="img" aria-labelledby="title desc">
<title id="title">Public signal: {summary['projects']} original public repositories and {summary['stars']} stars</title>
<desc id="desc">Language counts are repositories, not lines of code. Forks and this profile are excluded. Updated {escape(updated_date)} UTC.</desc>
<rect x=".5" y=".5" width="959" height="251" fill="#0B0B0B" stroke="#1F1F1F"/>
<g font-family="Inter, 'Segoe UI', Arial, sans-serif">
<text x="28" y="34" fill="#F3EEE7" font-size="14" font-weight="600" letter-spacing="2">PUBLIC SIGNAL</text>
<text x="932" y="34" text-anchor="end" fill="#BDB6AD" font-size="13">UPDATED {escape(updated_date)} UTC</text>
<path d="M28 56 H932 M458 84 V185" stroke="#1F1F1F"/>
<path d="M28 56 H76" stroke="#FF6A00" stroke-width="2"/>
<text x="28" y="136" fill="#F3EEE7" font-size="54" font-weight="700">{summary['projects']:02d}</text>
<text x="28" y="166" fill="#BDB6AD" font-size="16">Original public repositories</text>
<text x="268" y="136" fill="#F3EEE7" font-size="54" font-weight="700">{summary['stars']:02d}</text>
<text x="268" y="166" fill="#BDB6AD" font-size="16">Stars across these repos</text>
{''.join(nodes)}
<text x="492" y="214" fill="#BDB6AD" font-size="13">PRIMARY LANGUAGE / REPOSITORY COUNT</text>
<text x="28" y="214" fill="#BDB6AD" font-size="13">Public metadata. Forks and this profile excluded.</text>
</g></svg>
'''


def render_mobile(summary, updated_date):
    nodes = []
    for index, (language, count) in enumerate(summary["languages"]):
        x = 24 if index % 2 == 0 else 260
        y = 280 + (index // 2) * 72
        nodes.append(f'<text x="{x}" y="{y}" fill="#F3EEE7" font-size="22">{escape(language[:13])}</text>'
                     f'<text x="{x}" y="{y + 30}" fill="#BDB6AD" font-size="22">{count} repositor{"ies" if count != 1 else "y"}</text>')
    if not nodes:
        nodes.append('<text x="24" y="280" fill="#BDB6AD" font-size="22">No primary language data reported.</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="440" viewBox="0 0 480 440" role="img" aria-labelledby="title desc">
<title id="title">Public signal: {summary['projects']} original public repositories and {summary['stars']} stars</title>
<desc id="desc">Language counts are repositories, not lines of code. Forks and this profile are excluded. Updated {escape(updated_date)} UTC.</desc>
<rect x=".5" y=".5" width="479" height="439" fill="#0B0B0B" stroke="#1F1F1F"/>
<g font-family="Inter, 'Segoe UI', Arial, sans-serif">
<text x="24" y="38" fill="#F3EEE7" font-size="22" font-weight="600" letter-spacing="2">PUBLIC SIGNAL</text>
<path d="M24 58 H456 M24 212 H456 M24 398 H456" stroke="#1F1F1F"/>
<path d="M24 58 H72" stroke="#FF6A00" stroke-width="2"/>
<text x="24" y="132" fill="#F3EEE7" font-size="64" font-weight="700">{summary['projects']:02d}</text>
<text x="24" y="166" fill="#BDB6AD" font-size="22">Original public</text>
<text x="24" y="194" fill="#BDB6AD" font-size="22">repositories</text>
<text x="260" y="132" fill="#F3EEE7" font-size="64" font-weight="700">{summary['stars']:02d}</text>
<text x="260" y="166" fill="#BDB6AD" font-size="22">Stars across</text>
<text x="260" y="194" fill="#BDB6AD" font-size="22">these repos</text>
<text x="24" y="246" fill="#F3EEE7" font-size="22">Primary languages</text>
{''.join(nodes)}
<text x="24" y="426" fill="#BDB6AD" font-size="22">Updated {escape(updated_date)} UTC</text>
</g></svg>
'''


def write_activity(summary, updated_date, destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for name, renderer in [("activity.svg", render), ("activity-mobile.svg", render_mobile)]:
        (destination / name).write_text(renderer(summary, updated_date), encoding="utf-8")


def main():
    summary = summarize(fetch_repositories("BuildWithRaymond"), "BuildWithRaymond")
    updated_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    write_activity(summary, updated_date, Path(__file__).resolve().parents[1] / "assets")
    print(f"Updated public signal: {summary['projects']} original public repositories")


if __name__ == "__main__":
    main()

