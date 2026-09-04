#!/usr/bin/env python3
"""Staleness check: compare our ledgers against machine-readable official leaderboards.

Reports only; never writes data. Exit 0 always (the CI job turns the report into an issue).

Sources (all official or independent; no vendor blogs, no aggregators):
  arc-agi-2, arc-agi-3      arcprize.org leaderboard JSON
  bfcl                      gorilla.cs.berkeley.edu CSV
  gpqa-diamond, frontiermath, math
                            Epoch AI benchmark hub export (zip of CSVs)
  aider-polyglot            aider.chat leaderboard YAML/HTML
Add a fetcher by returning list[Row]; the comparison logic is shared.

Also flags active benchmarks whose ledger has not been touched in STALE_DAYS.
(Broken links are covered separately by the weekly lychee workflow.)
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset import Dataset, load, validate  # noqa: E402

UA = {"User-Agent": "llm-benchmarks-tracker staleness check (+https://github.com/alloevil/llm-benchmarks-tracker)"}
TIMEOUT = 30
STALE_DAYS = 45
TOLERANCE = 0.05  # ignore differences below this many points (rounding)


@dataclass
class Row:
    system: str
    value: float
    url: str
    note: str = ""


def fetch(url: str, timeout: int = TIMEOUT) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


# ----------------------------------------------------------------------------- fetchers


def arc(version: int) -> Callable[[], list[Row]]:
    url = f"https://arcprize.org/media/data/leaderboard/v{version}.json"

    def go() -> list[Row]:
        doc = json.loads(fetch(url))
        out = []
        for e in doc["evaluations"]:
            if not e.get("display") or e.get("modelGroup") == "Human" or e.get("score") is None:
                continue
            out.append(Row(e["modelDisplayName"], round(float(e["score"]) * 100, 1), "https://arcprize.org/leaderboard",
                           f"{e.get('datasetDisplayName', '')} ${e.get('costPerTask', '?')}/task"))
        return out

    return go


def bfcl() -> list[Row]:
    text = fetch("https://gorilla.cs.berkeley.edu/data_overall.csv").decode("utf-8")
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        try:
            out.append(Row(r["Model"], float(r["Overall Acc"].rstrip("%")), "https://gorilla.cs.berkeley.edu/leaderboard.html"))
        except (KeyError, ValueError):
            continue
    return out


_EPOCH: dict[str, list[dict[str, str]]] | None = None


def epoch(benchmark_key: str) -> Callable[[], list[Row]]:
    def go() -> list[Row]:
        global _EPOCH
        if _EPOCH is None:
            z = zipfile.ZipFile(io.BytesIO(fetch("https://epoch.ai/data/benchmark_data.zip", timeout=180)))  # ~0.5 MB, slow host
            _EPOCH = {}
            for name in z.namelist():
                if name.endswith(".csv"):
                    _EPOCH[Path(name).stem] = list(csv.DictReader(io.TextIOWrapper(z.open(name), encoding="utf-8")))
        rows = _EPOCH.get(benchmark_key)
        if rows is None:
            raise KeyError(f"epoch export has no {benchmark_key!r}; have {sorted(_EPOCH)[:20]}")
        out = []
        for r in rows:
            model = r.get("Model version")
            score = r.get("Best score (across scorers)")
            if not model or not score:
                continue
            try:
                v = float(score)
            except ValueError:
                continue
            url = f"https://epoch.ai/benchmarks/{benchmark_key.replace('_', '-')}"
            out.append(Row(model, round(v * 100, 1) if v <= 1 else v, url))
        return out

    return go


def aider() -> list[Row]:
    html = fetch("https://aider.chat/docs/leaderboards/").decode("utf-8")
    out = []
    # rows look like: <td ...>Model</td> ... <td ...>NN.N%</td>; keep it loose on markup
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(1), re.S)]
        cells = [c for c in cells if c and c != "▶"]  # first cell is an expand toggle
        if len(cells) >= 2:
            pct = next((c for c in cells if re.fullmatch(r"\d+(\.\d+)?%", c)), None)
            if pct:
                out.append(Row(cells[0], float(pct[:-1]), "https://aider.chat/docs/leaderboards/"))
    return out


FETCHERS: dict[str, Callable[[], list[Row]]] = {
    "arc-agi-2": arc(2),
    "arc-agi-3": arc(3),
    "bfcl": bfcl,
    "gpqa-diamond": epoch("gpqa_diamond"),
    "frontiermath": epoch("frontiermath_tiers_1_3_v2"),
    "math": epoch("math_level_5"),
    "aider-polyglot": aider,
}


# ----------------------------------------------------------------------------- checks


def compare(ds: Dataset) -> list[str]:
    lines = []
    for bid, go in FETCHERS.items():
        b = ds.benchmarks.get(bid)
        if not b:
            continue
        try:
            rows = go()
        except Exception as exc:  # noqa: BLE001 — report and keep going
            lines.append(f"- **{b['name']}**: fetch failed: `{type(exc).__name__}: {str(exc)[:120]}`")
            continue
        if not rows:
            lines.append(f"- **{b['name']}**: fetcher returned no rows (page layout changed?)")
            continue
        higher = b["metric"]["higher_is_better"]
        best = max(rows, key=lambda r: r.value) if higher else min(rows, key=lambda r: r.value)
        ours = ds.sota(bid)
        if ours is None or (best.value - ours["value"] > TOLERANCE if higher else ours["value"] - best.value > TOLERANCE):
            have = f"{ours['value']:g} ({ours['system']}, {ours['date']})" if ours else "nothing"
            lines.append(
                f"- **{b['name']}**: source shows **{best.value:g}** — {best.system}"
                f"{' · ' + best.note if best.note else ''}; we have {have}. [source]({best.url})"
            )
    return lines


def stale(ds: Dataset, today: date) -> list[str]:
    cutoff = (today - timedelta(days=STALE_DAYS)).isoformat()
    lines = []
    for bid, b in sorted(ds.benchmarks.items()):
        if b["status"] != "active":
            continue
        rows = ds.results.get(bid, [])
        last = max((r["source"]["accessed"] for r in rows), default=None)
        if last is None or last < cutoff:
            lines.append(f"- **{b['name']}**: ledger last touched {last or 'never'}")
    return lines


def main() -> int:
    errors: list[str] = []
    ds = load(errors=errors)
    errors += validate(ds)
    if errors:
        print("data invalid; aborting staleness check", file=sys.stderr)
        return 1
    today = date.today()
    sections = [
        ("New or higher scores on official/independent sources", compare(ds)),
        (f"Active benchmarks with no ledger activity in {STALE_DAYS} days", stale(ds, today)),
    ]
    report = [f"Staleness check · {today.isoformat()}", ""]
    total = 0
    for title, lines in sections:
        if lines:
            total += len(lines)
            report += [f"## {title}", *lines, ""]
    if total == 0:
        report.append("Nothing to report.")
    report.append(
        "\n_Automated report. Scores are not written to the ledger automatically: verify the source, "
        "then add a row via `data/results/<id>.json` (see CONTRIBUTING.md)._"
    )
    out = "\n".join(report)
    print(out)
    Path("staleness.md").write_text(out + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
