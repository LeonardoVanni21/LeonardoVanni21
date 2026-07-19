"""Fetch the public GitHub contribution calendar and store it as JSON.

No API token needed: GitHub exposes the calendar as public HTML at
    https://github.com/users/<username>/contributions
We parse it with BeautifulSoup and write data/contributions.json.
"""
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

from config import USERNAME

URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html() -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (profile-art bot)",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html",
    }
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Map each day cell id -> contribution count (from the <tool-tip> elements).
    counts = {}
    for tip in soup.find_all("tool-tip"):
        target = tip.get("for")
        if not target:
            continue
        m = re.search(r"([\d,]+)\s+contribution", tip.get_text())
        counts[target] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        level = int(td.get("data-level", 0) or 0)
        count = counts.get(td.get("id"), None)
        if count is None:
            # Older markup keeps the count on the cell itself.
            m = re.search(r"(\d+)", td.get("data-count", "") or "")
            count = int(m.group(1)) if m else 0
        days.append({"date": date, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    return {
        "username": USERNAME,
        "total": sum(d["count"] for d in days),
        "days": days,
    }


def main() -> int:
    data = parse(fetch_html())
    if not data["days"]:
        print("ERROR: no contribution days parsed — GitHub markup may have changed.",
              file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {len(data['days'])} days ({data['total']} contributions) -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
