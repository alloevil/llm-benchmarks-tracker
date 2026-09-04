#!/usr/bin/env python3
"""Sync ledgers from machine-readable official / independent sources.

Two tiers of provenance:
  * Structured sources on the allow-list below carry the system name, score, and the
    conditions we need (harness, cost, dataset, run date). When one of them shows a score
    above our current top, the row is appended to data/results/<id>.json automatically.
    Schema validation, append-only ordering and duplicate detection still gate the write.
  * Everything else (vendor posts, aggregators, new benchmarks) stays manual.

Sources:
  arc-agi-2, arc-agi-3          arcprize.org leaderboard JSON           official-leaderboard
  bfcl                          gorilla.cs.berkeley.edu CSV             official-leaderboard
  gpqa-diamond, frontiermath, math
                                Epoch AI benchmark hub export           independent-evaluation
  aider-polyglot                aider.chat polyglot_leaderboard.yml     official-leaderboard

Exit status: 0 = nothing to do or rows written; 2 = a source failed to parse (tooling issue).
`--dry-run` prints what would be appended without touching files.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset import DATA, Dataset, load, validate  # noqa: E402

UA = {"User-Agent": "llm-benchmarks-tracker ledger sync (+https://github.com/alloevil/llm-benchmarks-tracker)"}
TIMEOUT = 30
TOLERANCE = 0.05  # points; ignore rounding noise


@dataclass
class Row:
    system: str
    developer: str
    value: float
    url: str
    kind: str
    date: str | None = None  # source-provided date if any; else first observed (today)
    conditions: dict[str, Any] = field(default_factory=dict)


def fetch(url: str, timeout: int = TIMEOUT, attempts: int = 3) -> bytes:
    last: Exception | None = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception as exc:  # noqa: BLE001 — slow hosts; retry with backoff
            last = exc
            time.sleep(5 * (i + 1))
    raise last  # type: ignore[misc]


def _developer(name: str, provider: str | None = None) -> str:
    if provider:
        return provider
    n = name.lower()
    for key, dev in (
        ("gpt", "OpenAI"), ("o1", "OpenAI"), ("o3", "OpenAI"), ("o4", "OpenAI"),
        ("claude", "Anthropic"), ("gemini", "Google DeepMind"), ("grok", "xAI"),
        ("deepseek", "DeepSeek"), ("qwen", "Alibaba"), ("llama", "Meta"), ("mistral", "Mistral AI"),
        ("kimi", "Moonshot AI"), ("glm", "Zhipu AI"), ("muse", "Meta"),
    ):
        if key in n:
            return dev
    return "unknown"


# ----------------------------------------------------------------------------- fetchers


def arc(version: int) -> Callable[[], list[Row]]:
    url = f"https://arcprize.org/media/data/leaderboard/v{version}.json"
    page = "https://arcprize.org/leaderboard"

    def go() -> list[Row]:
        doc = json.loads(fetch(url))
        out = []
        for e in doc["evaluations"]:
            if not e.get("display") or e.get("modelGroup") == "Human" or e.get("score") is None:
                continue
            cond: dict[str, Any] = {"split": "semi-private"}
            m = re.search(r"\((\w+)\)\s*$", e["modelDisplayName"])
            if m:
                cond["reasoning_effort"] = m.group(1).lower()
            if "Provider Adapter" in e["modelDisplayName"]:
                cond["scaffold"] = "Provider Adapter"
            if e.get("costPerTask") is not None:
                cond["cost_usd_per_task"] = float(e["costPerTask"])
            out.append(Row(
                e["modelDisplayName"], _developer(e["modelDisplayName"], e.get("providerDisplayName")),
                round(float(e["score"]) * 100, 1), page, "official-leaderboard", conditions=cond,
            ))
        return out

    return go


def bfcl() -> list[Row]:
    text = fetch("https://gorilla.cs.berkeley.edu/data_overall.csv").decode("utf-8")
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            v = float(r["Overall Acc"].rstrip("%"))
        except (KeyError, ValueError):
            continue
        cond: dict[str, Any] = {}
        try:
            cond["cost_usd_per_task"] = round(float(r["Total Cost ($)"]) / 4000, 4)  # ~4k test cases
        except (KeyError, ValueError, ZeroDivisionError):
            pass
        out.append(Row(r["Model"], _developer(r["Model"]), v, "https://gorilla.cs.berkeley.edu/leaderboard.html",
                       "official-leaderboard", conditions=cond))
    return out


_EPOCH: dict[str, list[dict[str, str]]] | None = None


def epoch(benchmark_key: str, page: str) -> Callable[[], list[Row]]:
    def go() -> list[Row]:
        global _EPOCH
        if _EPOCH is None:
            z = zipfile.ZipFile(io.BytesIO(fetch("https://epoch.ai/data/benchmark_data.zip", timeout=180)))
            _EPOCH = {}
            for name in z.namelist():
                if name.endswith(".csv"):
                    _EPOCH[Path(name).stem] = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8")))
        rows = _EPOCH.get(benchmark_key)
        if rows is None:
            raise KeyError(f"epoch export has no {benchmark_key!r}")
        out = []
        for r in rows:
            model, score = r.get("Model version"), r.get("Best score (across scorers)")
            if not model or not score:
                continue
            try:
                v = float(score)
            except ValueError:
                continue
            cond: dict[str, Any] = {"notes": "Epoch AI independent run (Inspect)."}
            if r.get("Log viewer"):
                cond["notes"] += f" Log: {r['Log viewer']}"
            started = (r.get("Started at") or "")[:10]
            out.append(Row(model, r.get("Organization") or _developer(model), round(v * 100, 1) if v <= 1 else v,
                           page, "independent-evaluation", date=started or None, conditions=cond))
        return out

    return go


def aider() -> list[Row]:
    raw = fetch("https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml")
    out = []
    # Minimal YAML walk: entries are "- dirname: ..." blocks with flat "key: value" lines.
    for block in re.split(r"\n(?=- )", raw.decode("utf-8")):
        kv = dict(re.findall(r"^\s*-?\s*(\w+):\s*(.+?)\s*$", block, re.M))
        try:
            v = float(kv["pass_rate_2"])
        except (KeyError, ValueError):
            continue
        name = kv.get("model", "").strip("'\"")
        cond: dict[str, Any] = {}
        if kv.get("edit_format"):
            cond["scaffold"] = f"aider {kv['edit_format'].strip()}"
        try:
            cond["cost_usd_per_task"] = round(float(kv["total_cost"]) / 225, 4)
        except (KeyError, ValueError):
            pass
        d = (kv.get("date") or "")[:10]
        out.append(Row(name, _developer(name), v, "https://aider.chat/docs/leaderboards/", "official-leaderboard",
                       date=d if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) else None, conditions=cond))
    return out


FETCHERS: dict[str, Callable[[], list[Row]]] = {
    "arc-agi-2": arc(2),
    "arc-agi-3": arc(3),
    "bfcl": bfcl,
    "gpqa-diamond": epoch("gpqa_diamond", "https://epoch.ai/benchmarks/gpqa-diamond"),
    "frontiermath": epoch("frontiermath_tiers_1_3_v2", "https://epoch.ai/benchmarks/frontiermath-tiers-1-3-v2"),
    "math": epoch("math_level_5", "https://epoch.ai/benchmarks/math-level-5"),
    "aider-polyglot": aider,
}


# ----------------------------------------------------------------------------- sync


def new_rows(ds: Dataset, today: date) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Return {benchmark_id: ledger_row} for sources that beat our current top, plus tooling errors."""
    additions: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    for bid, go in FETCHERS.items():
        b = ds.benchmarks.get(bid)
        if not b:
            continue
        try:
            rows = go()
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{bid}: fetch failed: {type(exc).__name__}: {str(exc)[:120]}")
            continue
        if not rows:
            problems.append(f"{bid}: fetcher returned no rows (source layout changed?)")
            continue
        higher = b["metric"]["higher_is_better"]
        best = max(rows, key=lambda r: r.value) if higher else min(rows, key=lambda r: r.value)
        ours = ds.sota(bid)
        gain = (best.value - ours["value"]) if higher else (ours["value"] - best.value)
        if ours is not None and gain <= TOLERANCE:
            continue
        if b["metric"]["unit"] == "percent" and not 0 <= best.value <= 100:
            problems.append(f"{bid}: out-of-range value {best.value} from {best.url}")
            continue
        row_date = best.date or today.isoformat()
        ledger = ds.results.get(bid, [])
        if ledger and row_date < ledger[-1]["date"]:
            row_date = today.isoformat()  # keep ledger ascending; note the observation date instead
            best.conditions["notes"] = (best.conditions.get("notes", "") + f" Source run date {best.date}.").strip()
        if any(r["system"] == best.system and r["value"] == best.value and r["source"]["url"] == best.url for r in ledger):
            continue
        cond = {k: v for k, v in best.conditions.items() if v not in (None, "", {})}
        cond["notes"] = (cond.get("notes", "") + " Added automatically by scripts/sync_ledgers.py.").strip()[:300]
        additions[bid] = {
            "system": best.system[:80],
            "developer": best.developer[:60],
            "value": best.value,
            "date": row_date,
            "source": {"url": best.url, "kind": best.kind, "accessed": today.isoformat()},
            "conditions": cond,
        }
    return additions, problems


def append(bid: str, row: dict[str, Any]) -> None:
    path = DATA / "results" / f"{bid}.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["results"].append(row)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    errors: list[str] = []
    ds = load(errors=errors)
    errors += validate(ds)
    if errors:
        print("data invalid before sync; aborting", file=sys.stderr)
        return 1

    today = date.today()
    additions, problems = new_rows(ds, today)
    for bid, row in additions.items():
        ours = ds.sota(bid)
        was = f"{ours['value']:g} ({ours['system']})" if ours else "none"
        print(f"{bid}: {was} -> {row['value']:g} ({row['system']}) [{row['source']['kind']}]")
        if not args.dry_run:
            append(bid, row)
    if not additions:
        print("ledgers up to date")

    if additions and not args.dry_run:
        errors = []
        ds2 = load(errors=errors)
        errors += validate(ds2)
        if errors:
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            print("appended rows failed validation; leaving working tree for inspection", file=sys.stderr)
            return 1

    Path("sync_summary.md").write_text(
        "\n".join(
            [f"## Appended ({len(additions)})", *(f"- `{b}`: {r['value']:g} — {r['system']}" for b, r in additions.items()), ""]
            + (["## Source problems", *(f"- {p}" for p in problems)] if problems else [])
        ) + "\n",
        encoding="utf-8",
    )
    if problems:
        for p in problems:
            print(f"WARN {p}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
