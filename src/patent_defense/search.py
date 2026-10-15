from __future__ import annotations

import requests

CROSSREF_URL = "https://api.crossref.org/works"


def _first_date(item: dict) -> list | None:
    """Crossref uses several date fields; prefer the earliest-meaningful one."""
    for key in ("issued", "published", "published-print", "published-online", "created"):
        parts = (item.get(key) or {}).get("date-parts") or [[None]]
        if parts[0] and parts[0][0] is not None:
            return parts[0]
    return None


def parse_items(items: list[dict]) -> list[dict]:
    results = []
    for item in items:
        results.append(
            {
                "title": (item.get("title") or [""])[0],
                "doi": item.get("DOI"),
                "url": item.get("URL"),
                "published": _first_date(item),
                "venue": (item.get("container-title") or [""])[0],
                "type": item.get("type"),
                "authors": [
                    a.get("family", "") + (", " + a["given"] if a.get("given") else "")
                    for a in item.get("author", [])[:8]
                ],
            }
        )
    return results


def search_crossref(query: str, rows: int = 10) -> list[dict]:
    if not query.strip():
        raise ValueError("Query must not be empty")
    rows = max(1, min(int(rows), 100))
    response = requests.get(
        CROSSREF_URL,
        params={
            "query.bibliographic": query,
            "rows": rows,
            "select": "DOI,title,author,published,issued,created,URL,type,container-title",
        },
        headers={"User-Agent": "OpenPatentDefenseAI/0.2 (open-source research tool)"},
        timeout=20,
    )
    response.raise_for_status()
    return parse_items(response.json().get("message", {}).get("items", []))
