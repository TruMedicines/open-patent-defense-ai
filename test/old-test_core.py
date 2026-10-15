import json
from pathlib import Path

import pytest

from patent_defense.chart import create_chart
from patent_defense.cli import main
from patent_defense.ledger import add_evidence, export_entries, read_entries, verify_entries
from patent_defense.search import parse_items


def test_evidence_hash_detects_change(tmp_path: Path):
    file = tmp_path / "ref.txt"; file.write_text("original")
    ledger = tmp_path / "ledger.jsonl"
    add_evidence(file, ledger)
    assert verify_entries(ledger)[0]["status"] == "ok"
    file.write_text("changed")
    assert verify_entries(ledger)[0]["status"] == "changed"


def test_missing_evidence_detected(tmp_path: Path):
    file = tmp_path / "ref.txt"; file.write_text("original")
    ledger = tmp_path / "ledger.jsonl"
    add_evidence(file, ledger); file.unlink()
    assert verify_entries(ledger)[0]["status"] == "missing"


def test_multiple_entries_one_per_line(tmp_path: Path):
    ledger = tmp_path / "ledger.jsonl"
    for name in ("a.txt", "b.txt", "c.txt"):
        f = tmp_path / name; f.write_text(name)
        add_evidence(f, ledger)
    raw = ledger.read_text().splitlines()
    assert len(raw) == 3
    assert "\\n" not in ledger.read_text()  # no literal backslash-n
    assert [e["file_name"] for e in read_entries(ledger)] == ["a.txt", "b.txt", "c.txt"]
    assert len(verify_entries(ledger)) == 3


def test_export_and_claim_chart(tmp_path: Path):
    file = tmp_path / "ref.txt"; file.write_text("source")
    ledger = tmp_path / "ledger.jsonl"; add_evidence(file, ledger)
    out = tmp_path / "export.json"
    assert export_entries(out, ledger) == 1
    assert json.loads(out.read_text())[0]["file_name"] == "ref.txt"
    chart = tmp_path / "chart.json"; create_chart(chart, "US1234567B2")
    assert json.loads(chart.read_text())["patent_identifier"] == "US1234567B2"


def test_parse_items_date_fallback():
    items = [{"title": ["T"], "DOI": "10/x", "issued": {"date-parts": [[2018, 4]]},
              "published": {"date-parts": [[None]]}}]
    assert parse_items(items)[0]["published"] == [2018, 4]
    assert parse_items([{"title": ["T"]}])[0]["published"] is None


@pytest.mark.parametrize("flag_first", [True, False])
def test_cli_ledger_flag_either_position(tmp_path: Path, capsys, flag_first):
    f = tmp_path / "x.txt"; f.write_text("x")
    ledger = tmp_path / "l.jsonl"
    argv = ["evidence", "add", str(f)]
    argv = (["--ledger", str(ledger)] + argv) if flag_first else (argv + ["--ledger", str(ledger)])
    main(argv)
    assert len(read_entries(ledger)) == 1


def test_cli_verify_exits_nonzero_on_change(tmp_path: Path):
    f = tmp_path / "x.txt"; f.write_text("x")
    ledger = tmp_path / "l.jsonl"
    main(["evidence", "add", str(f), "--ledger", str(ledger)])
    f.write_text("y")
    with pytest.raises(SystemExit) as exc:
        main(["evidence", "verify", "--ledger", str(ledger)])
    assert exc.value.code == 1
