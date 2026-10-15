from __future__ import annotations

import argparse
import json
from pathlib import Path

from patent_defense.chart import create_chart
from patent_defense.ledger import (
    add_evidence,
    default_ledger_path,
    export_entries,
    read_entries,
    verify_entries,
)
from patent_defense.search import search_crossref


def build_parser() -> argparse.ArgumentParser:
    # --ledger is accepted both before and after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--ledger", type=Path, default=argparse.SUPPRESS,
                        help="Ledger file (default: data/evidence.jsonl or $PATENT_DEFENSE_LEDGER)")

    parser = argparse.ArgumentParser(prog="opda", description="Open Patent Defense AI research tools",
                                     parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search scholarly publication metadata via Crossref", parents=[common])
    search.add_argument("query")
    search.add_argument("--rows", type=int, default=10)

    ev = sub.add_parser("evidence", help="Manage local evidence files", parents=[common])
    evsub = ev.add_subparsers(dest="evidence_command", required=True)
    add = evsub.add_parser("add", help="Register a file with hash and provenance", parents=[common])
    add.add_argument("path", type=Path)
    add.add_argument("--source-url")
    add.add_argument("--published")
    add.add_argument("--notes")
    evsub.add_parser("list", help="List registered evidence", parents=[common])
    evsub.add_parser("verify", help="Check files against recorded hashes", parents=[common])
    exp = evsub.add_parser("export", help="Export the ledger to JSON", parents=[common])
    exp.add_argument("destination", type=Path)

    chart = sub.add_parser("chart", help="Claim-chart utilities", parents=[common])
    charts = chart.add_subparsers(dest="chart_command", required=True)
    init = charts.add_parser("init", help="Create a claim-chart template", parents=[common])
    init.add_argument("destination", type=Path)
    init.add_argument("--patent", required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    ledger = getattr(args, "ledger", None) or default_ledger_path()

    if args.command == "search":
        try:
            results = search_crossref(args.query, args.rows)
        except Exception as exc:
            raise SystemExit(f"Search failed: {exc}")
        for i, item in enumerate(results, 1):
            published = "-".join(str(p) for p in item["published"]) if item["published"] else "unknown"
            print(f"{i}. {item['title'] or '(untitled)'}")
            print(f"   Published: {published} | DOI: {item['doi'] or 'none'}")
            print(f"   URL: {item['url'] or 'none'}")
        print(f"\n{len(results)} metadata results. Verify each original source before relying on it.")

    elif args.command == "evidence":
        if args.evidence_command == "add":
            try:
                entry = add_evidence(args.path, ledger, args.source_url, args.published, args.notes)
            except FileNotFoundError as exc:
                raise SystemExit(str(exc))
            print(json.dumps(entry, indent=2))
        elif args.evidence_command == "list":
            entries = read_entries(ledger)
            if not entries:
                print("No evidence registered yet.")
            for e in entries:
                print(f"{e['id']}  {e['file_name']}  sha256={e['sha256']}  source={e.get('source_url') or '-'}")
        elif args.evidence_command == "verify":
            results = verify_entries(ledger)
            if not results:
                print("No evidence registered yet.")
            for r in results:
                print(f"{r['status'].upper():7} {r['id']} {r['file_path']}")
            if any(r["status"] != "ok" for r in results):
                raise SystemExit(1)
        elif args.evidence_command == "export":
            print(f"Exported {export_entries(args.destination, ledger)} entries to {args.destination}")

    elif args.command == "chart":
        create_chart(args.destination, args.patent)
        print(f"Created claim chart template: {args.destination}")


if __name__ == "__main__":
    main()
