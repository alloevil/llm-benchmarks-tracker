#!/usr/bin/env python3
"""Generate every derived artifact from data/.

  dist/index.html          static site
  dist/api/v1/*.json       machine-readable export
  dist/schema/*.json       published schemas
  dist/og.png, robots.txt, sitemap.xml
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
STATIC = ROOT / "static"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
SITE = "https://alloevil.github.io/llm-benchmarks-tracker"
REPO = "https://github.com/alloevil/llm-benchmarks-tracker"


# Per-language strings. Everything user-visible in generated output goes through T[lang].
T: dict[str, dict[str, str]] = {
    "en": {
        "bench_header": "| Benchmark | Released | Domains | Status | Top score | System | Source |",
        "eval_header": "| Evaluator | Kind | Maintainer | Methodology | Status |",
        "stats": "**{model}** model benchmarks · **{agent}** agent benchmarks · **{evals}** evaluators · "
        "**{results}** sourced results · updated {date}",
        "no_result": "no sourced result",
        "rows": "{n} rows",
        "lang_switch": '<a href="zh/" lang="zh-CN" hreflang="zh-CN">中文</a>',
        "description": "description",
        "kind_official-leaderboard": "official",
        "kind_developer-report": "self-reported",
        "kind_independent-evaluation": "independent",
        "kind_paper": "paper",
        "kind_aggregator": "aggregator",
    },
    "zh": {
        "bench_header": "| Benchmark | 发布 | 领域 | 状态 | 最高分 | 系统 | 来源 |",
        "eval_header": "| 评测方 | 类型 | 维护者 | 方法 | 状态 |",
        "stats": "**{model}** 个模型基准 · **{agent}** 个 Agent 基准 · **{evals}** 个评测方 · "
        "**{results}** 条有来源的结果 · 更新于 {date}",
        "no_result": "暂无有来源的结果",
        "rows": "{n} 条",
        "lang_switch": '<a href="../" lang="en" hreflang="en">English</a>',
        "description": "description_zh",
        "kind_official-leaderboard": "官方榜单",
        "kind_developer-report": "厂商自报",
        "kind_independent-evaluation": "独立复现",
        "kind_paper": "论文",
        "kind_aggregator": "聚合站",
    },
}


def kind_label(lang: str, kind: str) -> str:
    return T[lang][f"kind_{kind}"]


def fmt_value(b: dict[str, Any], value: float) -> str:
    unit = b["metric"]["unit"]
    if unit == "percent":
        return f"{value:g}%"
    return f"{value:g}"


def sort_benchmarks(ds: Dataset, layer: str) -> list[dict[str, Any]]:
    """Newest first; ties broken by id for determinism."""
    rows = [b for b in ds.benchmarks.values() if b["layer"] == layer]
    return sorted(rows, key=lambda b: (b["released"], b["id"]), reverse=True)


def md_link(text: str, url: str | None) -> str:
    return f"[{text}]({url})" if url else text


def best_link(b: dict[str, Any]) -> str | None:
    links = b["links"]
    return links.get("leaderboard") or links.get("website") or links.get("paper")


# --------------------------------------------------------------------------- README


def readme_benchmark_table(ds: Dataset, layer: str, lang: str = "en") -> str:
    out = [T[lang]["bench_header"], "|---|---|---|---|---|---|---|"]
    for b in sort_benchmarks(ds, layer):
        sota = ds.sota(b["id"])
        if sota:
            score = fmt_value(b, sota["value"])
            system = sota["system"]
            src = md_link(kind_label(lang, sota["source"]["kind"]), sota["source"]["url"])
        else:
            score = system = src = "—"
        out.append(
            f"| {md_link(b['name'], best_link(b))} | {b['released']} | {', '.join(b['domains'])} | "
            f"{b['status']} | {score} | {system} | {src} |"
        )
    return "\n".join(out)


def readme_evaluator_table(ds: Dataset, lang: str = "en") -> str:
    out = [T[lang]["eval_header"], "|---|---|---|---|---|"]
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


def readme_stats(ds: Dataset, lang: str = "en") -> str:
    n_results = sum(len(v) for v in ds.results.values())
    model = sum(1 for b in ds.benchmarks.values() if b["layer"] == "model")
    return T[lang]["stats"].format(
        model=model,
        agent=len(ds.benchmarks) - model,
        evals=len(ds.evaluators),
        results=n_results,
        date=date.today().isoformat(),
    )


def render_readme(ds: Dataset, text: str, lang: str = "en") -> str:
    blocks = {
        "stats": readme_stats(ds, lang),
        "model": readme_benchmark_table(ds, "model", lang),
        "agent": readme_benchmark_table(ds, "agent", lang),
        "evaluators": readme_evaluator_table(ds, lang),
        "timeline": readme_timeline(ds),
    }
    for name, body in blocks.items():
        pattern = re.compile(rf"(<!-- gen:{name} -->)\n(?:.*?\n)?(<!-- /gen:{name} -->)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"README is missing <!-- gen:{name} --> markers")
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


def html_benchmark_rows(ds: Dataset, layer: str, lang: str) -> str:
    t = T[lang]
    base = "../" if lang != "en" else ""
    rows = []
    for b in sort_benchmarks(ds, layer):
        sota = ds.sota(b["id"])
        hb = b.get("human_baseline")
        desc = b[t["description"]]
        if sota:
            kind = sota["source"]["kind"]
            label = kind_label(lang, kind)
            score_cell = (
                f'<span class="score">{_e(fmt_value(b, sota["value"]))}</span> '
                f'<span class="system">{_e(sota["system"])}</span><br>'
                f'<a class="src src-{kind}" href="{_e(sota["source"]["url"])}" rel="noopener">{label}</a> '
                f'<span class="muted">{_e(sota["date"])}</span>'
            )
        else:
            score_cell = f'<span class="muted">{t["no_result"]}</span>'
        human = f'{hb["value"]:g}% <span class="muted">{_e(hb["population"])}</span>' if hb else "—"
        risk = b.get("contamination_risk")
        risk_cell = f'<span class="pill risk-{risk}">{risk}</span>' if risk else "—"
        n = len(ds.results.get(b["id"], []))
        domains = " ".join(f'<span class="pill domain">{_e(d)}</span>' for d in b["domains"])
        rows.append(
            "<tr>"
            f'<td><a href="{_e(best_link(b))}" rel="noopener"><strong>{_e(b["name"])}</strong></a>'
            f'<div class="muted small" title="{_e(desc)}">{_e(desc)}</div></td>'
            f'<td class="nowrap">{_e(b["released"])}</td>'
            f"<td>{domains}</td>"
            f'<td><span class="pill status-{b["status"]}">{b["status"]}</span></td>'
            f"<td>{risk_cell}</td>"
            f"<td>{score_cell}</td>"
            f"<td>{human}</td>"
            f'<td class="nowrap"><a href="{base}api/v1/results/{b["id"]}.json">{t["rows"].format(n=n)}</a></td>'
            "</tr>"
        )
    return "\n".join(rows)


def html_evaluator_rows(ds: Dataset, lang: str) -> str:
    key = T[lang]["description"]
    order = {"framework": 0, "leaderboard": 1, "independent-evaluator": 2, "aggregator": 3}
    rows = []
    for e in sorted(ds.evaluators.values(), key=lambda e: (order[e["kind"]], e["name"].lower())):
        url = e["links"].get("website") or e["links"].get("repo")
        rows.append(
            "<tr>"
            f'<td><a href="{_e(url)}" rel="noopener"><strong>{_e(e["name"])}</strong></a>'
            f'<div class="muted small" title="{_e(e[key])}">{_e(e[key])}</div></td>'
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


def json_ld(ds: Dataset) -> str:
    """schema.org Dataset so search engines index this as data, not a blog post."""
    keywords = sorted({d for b in ds.benchmarks.values() for d in b["domains"]})
    keywords += sorted(b["name"] for b in ds.benchmarks.values() if b["status"] == "active")
    doc = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": "LLM Benchmarks Tracker",
        "description": (
            f"Schema-validated catalogue of {len(ds.benchmarks)} LLM and agent evaluation benchmarks and "
            f"{len(ds.evaluators)} evaluators, with {sum(len(v) for v in ds.results.values())} sourced results. "
            "Each result records the publishing URL, source kind and evaluation conditions."
        ),
        "url": f"{SITE}/",
        "sameAs": REPO,
        "license": "https://opensource.org/licenses/MIT",
        "isAccessibleForFree": True,
        "keywords": keywords,
        "dateModified": date.today().isoformat(),
        "creator": {"@type": "Organization", "name": "alloevil and contributors", "url": REPO},
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": f"{SITE}/api/v1/{name}.json"}
            for name in ("benchmarks", "evaluators")
        ],
    }
    return json.dumps(doc, ensure_ascii=False)



def render_site(ds: Dataset, lang: str) -> str:
    n_results = sum(len(v) for v in ds.results.values())
    model = sum(1 for b in ds.benchmarks.values() if b["layer"] == "model")
    base = "../" if lang != "en" else ""
    ctx = {
        "SITE": SITE,
        "BASE": base,
        "PAGE_URL": f"{SITE}/" if lang == "en" else f"{SITE}/{lang}/",
        "LANG_SWITCH": T[lang]["lang_switch"],
        "JSON_LD": json_ld(ds),
        "GENERATED": date.today().isoformat(),
        "N_MODEL": str(model),
        "N_AGENT": str(len(ds.benchmarks) - model),
        "N_BENCH": str(len(ds.benchmarks)),
        "N_EVALUATORS": str(len(ds.evaluators)),
        "N_RESULTS": str(n_results),
        "MODEL_ROWS": html_benchmark_rows(ds, "model", lang),
        "AGENT_ROWS": html_benchmark_rows(ds, "agent", lang),
        "EVALUATOR_ROWS": html_evaluator_rows(ds, lang),
        "TIMELINE": html_timeline(ds),
    }
    template = TEMPLATE if lang == "en" else TEMPLATE.with_name(f"index.{lang}.html")
    text = template.read_text(encoding="utf-8")
    for key, value in ctx.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if leftover:
        raise SystemExit(f"{template.name}: placeholders left unrendered: {leftover}")
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

    readmes = {README: render_readme(ds, README.read_text(encoding="utf-8"), "en")}
    readmes[README_ZH] = render_readme(ds, README_ZH.read_text(encoding="utf-8"), "zh")
    stale = [p for p, rendered in readmes.items() if rendered != p.read_text(encoding="utf-8")]
    if args.check:
        if stale:
            print(f"stale: {', '.join(p.name for p in stale)} — run `python scripts/build.py`", file=sys.stderr)
            return 1
        print("README files up to date")
        return 0
    for p in stale:
        p.write_text(readmes[p], encoding="utf-8")
        print(f"{p.name} updated")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST / "index.html").write_text(render_site(ds, "en"), encoding="utf-8")
    (DIST / "zh").mkdir()
    (DIST / "zh" / "index.html").write_text(render_site(ds, "zh"), encoding="utf-8")
    (DIST / ".nojekyll").touch()
    shutil.copytree(STATIC, DIST, dirs_exist_ok=True)
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    today = date.today().isoformat()
    urls = [(f"{SITE}/", "weekly"), (f"{SITE}/zh/", "weekly"), (f"{SITE}/api/v1/index.json", None)]
    entries = "".join(
        f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
        + (f"<changefreq>{freq}</changefreq>" if freq else "")
        + "</url>\n"
        for loc, freq in urls
    )
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}</urlset>\n",
        encoding="utf-8",
    )
    shutil.copytree(SCHEMA, DIST / "schema")
    write_api(ds)
    print(f"built {DIST.relative_to(ROOT)}/ ({len(ds.benchmarks)} benchmarks, {len(ds.evaluators)} evaluators)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
