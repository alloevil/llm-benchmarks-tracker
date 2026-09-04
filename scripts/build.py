#!/usr/bin/env python3
"""Generate every derived artifact from data/.

  dist/index.html          static site
  dist/api/v1/*.json       machine-readable export
  dist/schema/*.json       published schemas
  README.md                tables between <!-- gen:* --> markers

`--check` exits 1 if README.md would change (CI drift guard).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset import ROOT, SCHEMA, Dataset, load, validate  # noqa: E402

DIST = ROOT / "dist"
TEMPLATE = ROOT / "templates" / "index.html"
README = ROOT / "README.md"
SITE = "https://alloevil.github.io/llm-benchmarks-tracker"

STATUS_ORDER = {"active": 0, "saturating": 1, "saturated": 2, "retired": 3}
KIND_LABEL = {
    "official-leaderboard": "official",
    "developer-report": "self-reported",
    "independent-evaluation": "independent",
    "paper": "paper",
    "aggregator": "aggregator",
}


def fmt_value(b: dict[str, Any], value: float) -> str:
    unit = b["metric"]["unit"]
    if unit == "percent":
        return f"{value:g}%"
    return f"{value:g}"


def sort_benchmarks(ds: Dataset, layer: str) -> list[dict[str, Any]]:
    rows = [b for b in ds.benchmarks.values() if b["layer"] == layer]
    return sorted(rows, key=lambda b: (STATUS_ORDER[b["status"]], b["released"], b["id"]), reverse=False)


def md_link(text: str, url: str | None) -> str:
    return f"[{text}]({url})" if url else text


def best_link(b: dict[str, Any]) -> str | None:
    links = b["links"]
    return links.get("leaderboard") or links.get("website") or links.get("paper")


# --------------------------------------------------------------------------- README


def readme_benchmark_table(ds: Dataset, layer: str) -> str:
    out = ["| Benchmark | Released | Domains | Status | Top score | System | Source |", "|---|---|---|---|---|---|---|"]
    for b in sort_benchmarks(ds, layer):
        sota = ds.sota(b["id"])
        if sota:
            score = fmt_value(b, sota["value"])
            system = sota["system"]
            src = md_link(KIND_LABEL[sota["source"]["kind"]], sota["source"]["url"])
        else:
            score = system = src = "—"
        out.append(
            f"| {md_link(b['name'], best_link(b))} | {b['released']} | {', '.join(b['domains'])} | "
            f"{b['status']} | {score} | {system} | {src} |"
        )
    return "\n".join(out)


def readme_evaluator_table(ds: Dataset) -> str:
    out = ["| Evaluator | Kind | Maintainer | Methodology | Status |", "|---|---|---|---|---|"]
    order = {"framework": 0, "leaderboard": 1, "independent-evaluator": 2, "aggregator": 3}
    for e in sorted(ds.evaluators.values(), key=lambda e: (order[e["kind"]], e["name"].lower())):
        url = e["links"].get("website") or e["links"].get("repo")
        method = e.get("methodology", "—")
        out.append(f"| {md_link(e['name'], url)} | {e['kind']} | {e['maintainer']} | {method} | {e['status']} |")
    return "\n".join(out)


def readme_timeline(ds: Dataset) -> str:
    by_year: dict[str, list[str]] = {}
    for b in ds.benchmarks.values():
        by_year.setdefault(b["released"][:4], []).append(b["name"])
    for e in ds.evaluators.values():
        by_year.setdefault(e["released"][:4], []).append(f"{e['name']} ({e['kind']})")
    lines = []
    for year in sorted(by_year):
        lines.append(f"- **{year}** — {', '.join(sorted(by_year[year], key=str.lower))}")
    return "\n".join(lines)


def readme_stats(ds: Dataset) -> str:
    n_results = sum(len(v) for v in ds.results.values())
    model = sum(1 for b in ds.benchmarks.values() if b["layer"] == "model")
    agent = len(ds.benchmarks) - model
    return (
        f"**{model}** model benchmarks · **{agent}** agent benchmarks · "
        f"**{len(ds.evaluators)}** evaluators · **{n_results}** sourced results · "
        f"updated {date.today().isoformat()}"
    )


def render_readme(ds: Dataset, text: str) -> str:
    blocks = {
        "stats": readme_stats(ds),
        "model": readme_benchmark_table(ds, "model"),
        "agent": readme_benchmark_table(ds, "agent"),
        "evaluators": readme_evaluator_table(ds),
        "timeline": readme_timeline(ds),
    }
    for name, body in blocks.items():
        pattern = re.compile(rf"(<!-- gen:{name} -->)\n(?:.*?\n)?(<!-- /gen:{name} -->)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"README.md is missing <!-- gen:{name} --> markers")
        text = pattern.sub(lambda m, body=body: f"{m.group(1)}\n{body}\n{m.group(2)}", text)
    return text


# --------------------------------------------------------------------------- API


def write_api(ds: Dataset) -> None:
    api = DIST / "api" / "v1"
    api.mkdir(parents=True, exist_ok=True)
    generated = date.today().isoformat()

    def dump(name: str, payload: Any) -> None:
        (api / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    benchmarks = []
    for b in sorted(ds.benchmarks.values(), key=lambda b: b["id"]):
        row = dict(b)
        row["sota"] = ds.sota(b["id"])
        row["result_count"] = len(ds.results.get(b["id"], []))
        benchmarks.append(row)
    dump("benchmarks.json", {"generated": generated, "count": len(benchmarks), "benchmarks": benchmarks})
    evaluators = sorted(ds.evaluators.values(), key=lambda e: e["id"])
    dump("evaluators.json", {"generated": generated, "count": len(evaluators), "evaluators": evaluators})
    results_dir = api / "results"
    results_dir.mkdir(exist_ok=True)
    for bid, rows in ds.results.items():
        payload = {"generated": generated, "benchmark": bid, "results": rows}
        (results_dir / f"{bid}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    dump(
        "index.json",
        {
            "generated": generated,
            "benchmarks": f"{SITE}/api/v1/benchmarks.json",
            "evaluators": f"{SITE}/api/v1/evaluators.json",
            "results": {bid: f"{SITE}/api/v1/results/{bid}.json" for bid in sorted(ds.results)},
            "schema": {name: f"{SITE}/schema/{name}" for name in sorted(p.name for p in SCHEMA.glob("*.json"))},
        },
    )


# --------------------------------------------------------------------------- site


def _e(s: Any) -> str:
    return html.escape(str(s), quote=True)


def html_benchmark_rows(ds: Dataset, layer: str) -> str:
    rows = []
    for b in sort_benchmarks(ds, layer):
        sota = ds.sota(b["id"])
        hb = b.get("human_baseline")
        if sota:
            kind = sota["source"]["kind"]
            score_cell = (
                f'<span class="score">{_e(fmt_value(b, sota["value"]))}</span> '
                f'<span class="system">{_e(sota["system"])}</span><br>'
                f'<a class="src src-{kind}" href="{_e(sota["source"]["url"])}" rel="noopener">{KIND_LABEL[kind]}</a> '
                f'<span class="muted">{_e(sota["date"])}</span>'
            )
        else:
            score_cell = '<span class="muted">no sourced result</span>'
        human = f'{hb["value"]:g}% <span class="muted">{_e(hb["population"])}</span>' if hb else "—"
        risk = b.get("contamination_risk")
        risk_cell = f'<span class="pill risk-{risk}">{risk}</span>' if risk else "—"
        n = len(ds.results.get(b["id"], []))
        rows.append(
            "<tr>"
            f'<td><a href="{_e(best_link(b))}" rel="noopener"><strong>{_e(b["name"])}</strong></a>'
            f'<div class="muted small" title="{_e(b["description"])}">{_e(b["description"])}</div></td>'
            f'<td class="nowrap">{_e(b["released"])}</td>'
            f'<td>{" ".join(f"<span class=\"pill domain\">{_e(d)}</span>" for d in b["domains"])}</td>'
            f'<td><span class="pill status-{b["status"]}">{b["status"]}</span></td>'
            f"<td>{risk_cell}</td>"
            f"<td>{score_cell}</td>"
            f"<td>{human}</td>"
            f'<td class="nowrap"><a href="api/v1/results/{b["id"]}.json">{n} rows</a></td>'
            "</tr>"
        )
    return "\n".join(rows)


def html_evaluator_rows(ds: Dataset) -> str:
    order = {"framework": 0, "leaderboard": 1, "independent-evaluator": 2, "aggregator": 3}
    rows = []
    for e in sorted(ds.evaluators.values(), key=lambda e: (order[e["kind"]], e["name"].lower())):
        url = e["links"].get("website") or e["links"].get("repo")
        rows.append(
            "<tr>"
            f'<td><a href="{_e(url)}" rel="noopener"><strong>{_e(e["name"])}</strong></a>'
            f'<div class="muted small" title="{_e(e["description"])}">{_e(e["description"])}</div></td>'
            f'<td><span class="pill kind-{e["kind"]}">{e["kind"]}</span></td>'
            f'<td>{_e(e["maintainer"])}</td>'
            f'<td>{_e(e.get("methodology", "—"))}</td>'
            f'<td><span class="pill status-{e["status"]}">{e["status"]}</span></td>'
            "</tr>"
        )
    return "\n".join(rows)


def html_timeline(ds: Dataset) -> str:
    by_year: dict[str, list[tuple[str, str, str]]] = {}
    for b in ds.benchmarks.values():
        by_year.setdefault(b["released"][:4], []).append((b["released"], b["name"], b["layer"]))
    for e in ds.evaluators.values():
        by_year.setdefault(e["released"][:4], []).append((e["released"], e["name"], "evaluator"))
    out = []
    for year in sorted(by_year):
        items = "".join(
            f'<span class="pill tl-{kind}" title="{_e(rel)}">{_e(name)}</span>'
            for rel, name, kind in sorted(by_year[year])
        )
        out.append(f'<div class="tl-row"><div class="tl-year">{year}</div><div class="tl-items">{items}</div></div>')
    return "\n".join(out)


def render_site(ds: Dataset) -> str:
    n_results = sum(len(v) for v in ds.results.values())
    model = sum(1 for b in ds.benchmarks.values() if b["layer"] == "model")
    ctx = {
        "GENERATED": date.today().isoformat(),
        "N_MODEL": str(model),
        "N_AGENT": str(len(ds.benchmarks) - model),
        "N_EVALUATORS": str(len(ds.evaluators)),
        "N_RESULTS": str(n_results),
        "MODEL_ROWS": html_benchmark_rows(ds, "model"),
        "AGENT_ROWS": html_benchmark_rows(ds, "agent"),
        "EVALUATOR_ROWS": html_evaluator_rows(ds),
        "TIMELINE": html_timeline(ds),
    }
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in ctx.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if leftover:
        raise SystemExit(f"template placeholders left unrendered: {leftover}")
    return text


# --------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if README.md is out of date; write nothing")
    args = ap.parse_args()

    errors: list[str] = []
    ds = load(errors=errors)
    errors += validate(ds)
    if errors:
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        print(f"{len(errors)} validation error(s); refusing to build", file=sys.stderr)
        return 1

    current = README.read_text(encoding="utf-8")
    rendered = render_readme(ds, current)
    if args.check:
        if rendered != current:
            print("README.md is stale: run `python scripts/build.py`", file=sys.stderr)
            return 1
        print("README.md up to date")
        return 0

    if rendered != current:
        README.write_text(rendered, encoding="utf-8")
        print("README.md updated")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "index.html").write_text(render_site(ds), encoding="utf-8")
    (DIST / ".nojekyll").touch()
    shutil.copytree(SCHEMA, DIST / "schema")
    write_api(ds)
    print(f"built {DIST.relative_to(ROOT)}/ ({len(ds.benchmarks)} benchmarks, {len(ds.evaluators)} evaluators)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
