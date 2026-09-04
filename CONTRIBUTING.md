# Contributing

Thanks for helping keep this accurate. The bar is simple: **every fact must be traceable to a URL you actually opened.**

## What is automated

`scripts/sync_ledgers.py` runs twice a week and appends a row when an allow-listed structured source (ARC Prize, BFCL, Epoch AI, Aider) shows a score above our current top for that benchmark. Rows it writes are marked `Added automatically by scripts/sync_ledgers.py` in `conditions.notes`. To add a source, write a fetcher returning `Row`s with honest `kind` and the conditions the source exposes; sources that only give a number (vendor blogs, aggregator tables) do not qualify.

## Adding or updating a result

1. Open `data/results/<benchmark>.json` (create it if missing; `benchmark` must equal the file name and a file in `data/benchmarks/`).
2. **Append** a row — never edit or delete an existing one. Ledgers are historical.
3. Fill in:
   - `system`: the name exactly as the source prints it, including variant (`"o3 (high)"`, `"Claude Opus 4.1 + SWE-agent"`).
   - `value`: a number. Percent metrics are 0–100.
   - `date`: when the score was published (`YYYY-MM-DD`). If only a month is known, use the 1st and say so in `conditions.notes`.
   - `source.url`: where you saw it. `source.kind`: be honest — a vendor blog is `developer-report`, a site that republishes vendor numbers is `aggregator`.
   - `conditions`: only what the source states. Omit unknown keys.
4. Run `python scripts/validate.py`.

## Adding a benchmark

1. Create `data/benchmarks/<id>.json` following `schema/benchmark.schema.json`. Look at `swe-bench-verified.json` and `gpqa-diamond.json` as templates.
2. Verify the arXiv id by opening `https://arxiv.org/abs/<id>` and checking the title. Wrong ids have been the most common error in this repo.
3. Set `status` and `contamination_risk` per the definitions in the README, and link `supersedes` / `superseded_by` both ways.
4. Write `description_zh` (Simplified Chinese; keep names, metrics and numbers as in the English). If you cannot, say so in the PR and a maintainer will add it.
5. Add a results ledger if `status` is `active` (the validator requires it).
6. Run `python scripts/validate.py && python scripts/build.py` and commit the regenerated `README.md` and `README.zh-CN.md`.

## Adding an evaluator

`data/evaluators/<id>.json`. `kind` distinguishes frameworks you run, maintainer-run leaderboards, independent evaluators that re-run models themselves, and aggregators. `benchmarks` may only list ids that exist in `data/benchmarks/`.

## What gets rejected

- Numbers without a source, or with a source that does not show the number.
- `source.kind` that overstates independence.
- arXiv ids that resolve to a different paper.
- Edits to existing ledger rows (open an issue if a row is wrong; we add a correcting row and note it).
- Descriptions containing score claims (those live in the ledger).
- Stale `README.md` / `README.zh-CN.md` tables: CI runs `python scripts/build.py --check`.

## Local setup

```bash
pip install -e ".[dev]"
python scripts/validate.py
pytest
python scripts/build.py && python -m http.server -d dist
```
