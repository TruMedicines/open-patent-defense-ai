from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_ledger_path() -> Path:
    return Path(os.environ.get("PATENT_DEFENSE_LEDGER", "data/evidence.jsonl"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_entries(ledger: Path) -> list[dict[str, Any]]:
    if not ledger.exists():
        return []
    entries = []
    with ledger.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at {ledger}:{number}") from exc
    return entries


def add_evidence(
    file_path: Path,
    ledger: Path | None = None,
    source_url: str | None = None,
    published: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    file_path = file_path.expanduser().resolve()
    if not file_path.is_file():
        raise FileNotFoundError(f"Evidence file not found: {file_path}")
    ledger = ledger or default_ledger_path()
    now = datetime.now(timezone.utc)
    entry = {
        "id": "ev-" + now.strftime("%Y%m%dT%H%M%S%fZ"),
        "file_name": file_path.name,
        "file_path": str(file_path),
        "sha256": sha256_file(file_path),
        "source_url": source_url,
        "published_date": published,
        "collected_at": now.isoformat(),
        "notes": notes,
    }
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def verify_entries(ledger: Path | None = None) -> list[dict[str, Any]]:
    results = []
    for entry in read_entries(ledger or default_ledger_path()):
        path = Path(entry["file_path"])
        current = sha256_file(path) if path.is_file() else None
        if current is None:
            status = "missing"
        elif current == entry["sha256"]:
            status = "ok"
        else:
            status = "changed"
        results.append(
            {
                "id": entry["id"],
                "file_path": str(path),
                "status": status,
                "recorded_sha256": entry["sha256"],
                "current_sha256": current,
            }
        )
    return results


def export_entries(destination: Path, ledger: Path | None = None) -> int:
    entries = read_entries(ledger or default_ledger_path())
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(entries)
