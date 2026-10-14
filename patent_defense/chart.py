from __future__ import annotations

import json
from datetime import date
from pathlib import Path


def create_chart(destination: Path, patent: str) -> None:
    chart = {
        "schema_version": "1.0",
        "created_date": date.today().isoformat(),
        "patent_identifier": patent,
        "review_status": "draft",
        "disclaimer": "Research aid only. Human review and qualified patent counsel are required.",
        "limitations": [
            {
                "limitation_id": "L1",
                "claim_number": "1",
                "claim_text": "Replace with verbatim claim text.",
                "element_text": "Replace with one limitation/element.",
                "evidence": [],
                "analysis": "",
                "reviewer_notes": "",
                "status": "unreviewed",
            }
        ],
        "evidence_item_schema": {
            "source_title": "Exact document title",
            "source_url": "Stable source URL or DOI",
            "publication_date": "YYYY-MM-DD or null",
            "document_version": "Version/patent publication number",
            "page_or_paragraph": "Exact page, paragraph, column/line, or figure",
            "verbatim_excerpt": "Short exact passage copied from the source",
            "relevance_rationale": "Human-authored explanation of what the passage supports",
            "verified_by_human": False,
        },
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(chart, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
