# Open Patent Defense AI

Open-source, local-first tooling to help researchers organize prior art and build auditable patent-claim evidence maps.

**Status:** early MVP. This is research software, not legal advice or an automated determination of patent validity.

Website: `https://<your-username>.github.io/open-patent-defense-ai/`

## Current capabilities
- Search Crossref metadata for scholarly publications using a technical query.
- Register local evidence files with SHA-256 hashes and provenance metadata.
- Verify whether registered files have changed or disappeared.
- Create a claim-chart JSON template that keeps each claim limitation separate and requires source/page/passage references for human review.
- Export the evidence ledger to JSON.

## Quick start

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
opda --help
```

### Search scholarly metadata

```bash
opda search "controlled release drug delivery polymer" --rows 10
```

Search results are leads, not proof of prior art. Confirm the actual document, dates, family, and disclosure in the source itself.

### Register a document

```bash
opda evidence add ./documents/paper.pdf \
  --source-url "https://doi.org/10.xxxx/example" \
  --published 2018-04-12 \
  --notes "Review disclosure relevant to limitation 1"
opda evidence list
opda evidence verify
opda evidence export evidence-index.json
```

`opda evidence verify` exits with status 1 if any file changed or went missing, so it works in scripts and CI.

### Create a claim chart

```bash
opda chart init claim-chart.json --patent "US1234567B2"
```

Edit the generated JSON. For every limitation, record the evidence source and exact page/passage, or explicitly mark it as not found. Do not allow AI-generated text to masquerade as verified evidence.

### Ledger location

The ledger defaults to `data/evidence.jsonl`. Change it with the `PATENT_DEFENSE_LEDGER` environment variable or the `--ledger` flag, which works before or after the subcommand:

```bash
opda --ledger my.jsonl evidence list
opda evidence list --ledger my.jsonl
```

## Roadmap
1. **MVP — evidence + claim chart scaffolding** (included).
2. Add official patent-office search connectors and patent-family deduplication.
3. Extract PDF text with page-level citations and OCR fallback.
4. Add a review UI for claim charts, conflicts, and reviewer notes.
5. Add reproducible evidence bundles, signed manifests, and evaluation benchmarks.

## Principles
- Local-first storage by default.
- Exact citations and source provenance over unsupported summaries.
- Human review for relevance and legal interpretation.
- Clear distinction between discovery leads and verified evidence.
- Respect source terms, rate limits, privacy, and confidentiality.

## Development

```bash
pip install -e ".[dev]"
pytest
```

See `CONTRIBUTING.md`.

## License
Apache-2.0. See `LICENSE`.
