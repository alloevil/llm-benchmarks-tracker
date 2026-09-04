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
        "lang_switch": '<a href="{other}" lang="zh-CN" hreflang="zh-CN">中文</a>',
        "description": "description",
        "kind_official-leaderboard": "official",
        "kind_developer-report": "self-reported",
        "kind_independent-evaluation": "independent",
        "kind_paper": "paper",
        "kind_aggregator": "aggregator",
        "human": "human",
        "supersedes": "supersedes",
        "superseded_by": "superseded by",
        "ledger": "Full ledger",
        "released": "Released",
        "domains": "Domains",
        "status": "Status",
        "risk": "Contamination",
        "top": "Top score",
        "th_system": "System",
        "th_developer": "Developer",
        "th_value": "Score",
        "th_date": "Date",
        "th_source": "Source",
        "th_conditions": "Conditions",
        "json": "JSON",
        "back": "← All benchmarks",
        "meta_desc": "{name}: {desc} Top score {score} ({system}, {kind}). {n} sourced results with conditions.",
        "meta_desc_none": "{name}: {desc}",
        "detail_title": "{name} — scores, sources, status | LLM Benchmarks Tracker",
        "maintainer": "Maintainer",
        "task_count": "Tasks",
        "metric": "Metric",
        "links": "Links",
        "paper": "paper",
        "website": "website",
        "leaderboard": "leaderboard",
        "dataset": "dataset",
        "code": "code",
        "notes": "Notes",
        "history": "Score history",
        "filter_placeholder": "Filter by name, domain, system…",
        "filter_all": "all",
        "provenance": "of top scores are official or independent",
        "sort_hint": "click to sort",
        "no_baseline": "no measured baseline",
        "last_reported": "last reported",
        "chart_title": "Top sourced score over time, per benchmark (percent metrics only)",
        "chart_excluded": "Not charted (non-percent metric)",
        "chart_hint": "Hover a line for details; click to open the benchmark. Dashed = human baseline. Arrows = superseded by.",
        "layer": "Layer",
        "divider": "Saturated or retired — no longer used to compare frontier systems. "
        "Score shown is the last one reported, not a leaderboard top.",
    },
    "zh": {
        "bench_header": "| Benchmark | 发布 | 领域 | 状态 | 最高分 | 系统 | 来源 |",
        "eval_header": "| 评测方 | 类型 | 维护者 | 方法 | 状态 |",
        "stats": "**{model}** 个模型基准 · **{agent}** 个 Agent 基准 · **{evals}** 个评测方 · "
        "**{results}** 条有来源的结果 · 更新于 {date}",
        "no_result": "暂无有来源的结果",
        "rows": "{n} 条",
        "lang_switch": '<a href="{other}" lang="en" hreflang="en">English</a>',
        "description": "description_zh",
        "kind_official-leaderboard": "官方榜单",
        "kind_developer-report": "厂商自报",
        "kind_independent-evaluation": "独立复现",
        "kind_paper": "论文",
        "kind_aggregator": "聚合站",
        "human": "人类",
        "supersedes": "取代",
        "superseded_by": "被取代",
        "ledger": "完整账本",
        "released": "发布",
        "domains": "领域",
        "status": "状态",
        "risk": "污染风险",
        "top": "最高分",
        "th_system": "系统",
        "th_developer": "开发者",
        "th_value": "分数",
        "th_date": "日期",
        "th_source": "来源",
        "th_conditions": "条件",
        "json": "JSON",
        "back": "← 全部基准",
        "meta_desc": "{name}：{desc} 最高分 {score}（{system}，{kind}）。{n} 条带条件的有来源结果。",
        "meta_desc_none": "{name}：{desc}",
        "detail_title": "{name} — 分数、来源、状态 | LLM Benchmarks Tracker",
        "maintainer": "维护者",
        "task_count": "题量",
        "metric": "指标",
        "links": "链接",
        "paper": "论文",
        "website": "官网",
        "leaderboard": "榜单",
        "dataset": "数据集",
        "code": "代码",
        "notes": "备注",
        "history": "分数历史",
        "filter_placeholder": "按名称、领域、系统筛选…",
        "filter_all": "全部",
        "provenance": "的最高分来自官方榜单或独立复现",
        "sort_hint": "点击排序",
        "no_baseline": "无实测基线",
        "last_reported": "最后报告",
        "chart_title": "各基准有来源的最高分随时间变化（仅百分制指标）",
        "chart_excluded": "未绘制（非百分制指标）",
        "chart_hint": "悬停查看详情，点击进入基准页。虚线 = 人类基线。箭头 = 被取代。",
        "layer": "层级",
        "divider": "已饱和或退役 —— 不再用于比较前沿系统。所示分数为最后一次报告值，不是榜首。",
    },
}


def lang_prefix(lang: str) -> str:
    return "" if lang == "en" else f"{lang}/"


def detail_url(lang: str, bid: str) -> str:
    """Site-absolute path of a benchmark detail page, e.g. /zh/b/mmlu/."""
    return f"/{lang_prefix(lang)}b/{bid}/"


def sparkline(b: dict[str, Any], rows: list[dict[str, Any]], width: int = 120, height: int = 28) -> str:
    """Inline SVG of value over time. Empty string when fewer than two points."""
    if len(rows) < 2:
        return ""
    pts = sorted((r["date"], r["value"]) for r in rows)
    d0 = date.fromisoformat(pts[0][0]).toordinal()
    d1 = date.fromisoformat(pts[-1][0]).toordinal()
    vals = [v for _, v in pts]
    lo, hi = (0.0, 100.0) if b["metric"]["unit"] == "percent" else (min(vals), max(vals))
    span_x = max(d1 - d0, 1)
    span_y = max(hi - lo, 1e-9)
    pad = 3
    coords = []
    for d, v in pts:
        x = pad + (date.fromisoformat(d).toordinal() - d0) / span_x * (width - 2 * pad)
        y = height - pad - (v - lo) / span_y * (height - 2 * pad)
        coords.append(f"{x:.1f},{y:.1f}")
    last = coords[-1].split(",")
    title = f"{pts[0][0]} → {pts[-1][0]}: {fmt_value(b, vals[0])} → {fmt_value(b, vals[-1])}"
    return (
        f'<svg class="spark" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
        f'aria-label="{_e(title)}"><title>{_e(title)}</title>'
        f'<polyline fill="none" stroke="currentColor" stroke-width="1.5" points="{" ".join(coords)}"/>'
        f'<circle cx="{last[0]}" cy="{last[1]}" r="2.2" fill="currentColor"/></svg>'
    )


def provenance_share(ds: Dataset) -> int:
    """Percent of benchmarks whose top score comes from an official leaderboard, paper or independent run."""
    sotas = [ds.sota(bid) for bid in ds.benchmarks if ds.sota(bid)]
    trusted = sum(1 for s in sotas if s["source"]["kind"] in ("official-leaderboard", "independent-evaluation", "paper"))
    return round(100 * trusted / len(sotas)) if sotas else 0


def kind_label(lang: str, kind: str) -> str:
    return T[lang][f"kind_{kind}"]


def fmt_value(b: dict[str, Any], value: float) -> str:
    unit = b["metric"]["unit"]
    if unit == "percent":
        return f"{value:g}%"
    return f"{value:g}"


LIVE = ("active", "saturating")


def is_live(b: dict[str, Any]) -> bool:
    return b["status"] in LIVE


def sort_benchmarks(ds: Dataset, layer: str) -> list[dict[str, Any]]:
    """Live (active/saturating) first, then saturated/retired; newest first within each group."""
    rows = [b for b in ds.benchmarks.values() if b["layer"] == layer]
    rows.sort(key=lambda b: (b["released"], b["id"]), reverse=True)
    rows.sort(key=lambda b: not is_live(b))  # stable: preserves newest-first inside each group
    return rows


def last_reported(ds: Dataset, bid: str) -> dict[str, Any] | None:
    rows = ds.results.get(bid)
    return max(rows, key=lambda r: r["date"]) if rows else None


def md_link(text: str, url: str | None) -> str:
    return f"[{text}]({url})" if url else text


def best_link(b: dict[str, Any]) -> str | None:
    links = b["links"]
    return links.get("leaderboard") or links.get("website") or links.get("paper")


# --------------------------------------------------------------------------- README


def readme_benchmark_table(ds: Dataset, layer: str, lang: str = "en") -> str:
    t = T[lang]
    out = [t["bench_header"], "|---|---|---|---|---|---|---|"]
    divider_done = False
    for b in sort_benchmarks(ds, layer):
        if not is_live(b) and not divider_done:
            out.append(f"| *{t['divider']}* | | | | | | |")
            divider_done = True
        row = ds.sota(b["id"]) if is_live(b) else last_reported(ds, b["id"])
        if row:
            score = fmt_value(b, row["value"])
            if not is_live(b):
                score = f"{t['last_reported']} {score}"
            system = row["system"]
            src = md_link(kind_label(lang, row["source"]["kind"]), row["source"]["url"])
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


def score_html(ds: Dataset, b: dict[str, Any], lang: str) -> str:
    """Top score + system + source badge + date, with the human baseline folded in."""
    t = T[lang]
    sota = ds.sota(b["id"])
    hb = b.get("human_baseline")
    if not sota:
        return f'<span class="muted">{t["no_result"]}</span>'
    kind = sota["source"]["kind"]
    human = ""
    if hb:
        human = (
            f' <span class="human" title="{_e(hb["population"])}">· {t["human"]} '
            f'<a href="{_e(hb["source"])}" rel="noopener">{hb["value"]:g}%</a></span>'
        )
    return (
        f'<span class="score">{_e(fmt_value(b, sota["value"]))}</span>{human}<br>'
        f'<span class="system">{_e(sota["system"])}</span><br>'
        f'<a class="src src-{kind}" href="{_e(sota["source"]["url"])}" rel="noopener">{kind_label(lang, kind)}</a> '
        f'<time class="muted" datetime="{_e(sota["date"])}">{_e(sota["date"])}</time>'
    )


def chain_html(ds: Dataset, b: dict[str, Any], lang: str, base: str) -> str:
    """Supersession arrows shown under the name."""
    t = T[lang]
    parts = []
    for rel, arrow in (("supersedes", "↑"), ("superseded_by", "↓")):
        target = b.get(rel)
        if target and target in ds.benchmarks:
            parts.append(
                f'<a class="chain" href="{base}b/{target}/" title="{t[rel]}">{arrow} {_e(ds.benchmarks[target]["name"])}</a>'
            )
    return " ".join(parts)


def compact_row(ds: Dataset, b: dict[str, Any], lang: str, base: str) -> str:
    """Single-line row for saturated/retired benchmarks: last reported score and successor, no SOTA framing."""
    t = T[lang]
    last = last_reported(ds, b["id"])
    risk = b.get("contamination_risk") or ""
    nxt = b.get("superseded_by")
    succ = ""
    if nxt and nxt in ds.benchmarks:
        succ = f' <a class="chain" href="{base}b/{nxt}/">→ {_e(ds.benchmarks[nxt]["name"])}</a>'
    if last:
        kind = last["source"]["kind"]
        score = (
            f'<span class="muted">{t["last_reported"]}</span> <strong>{_e(fmt_value(b, last["value"]))}</strong> '
            f'<a class="src src-{kind}" href="{_e(last["source"]["url"])}" rel="noopener">{kind_label(lang, kind)}</a> '
            f'<time class="muted" datetime="{last["date"]}">{last["date"][:7]}</time>'
        )
    else:
        score = f'<span class="muted">{t["no_result"]}</span>'
    search = " ".join([b["name"], b.get("full_name", ""), *b["domains"]]).lower()
    risk_cell = f'<span class="pill risk-{risk}">{risk}</span>' if risk else "—"
    return (
        f'<tr class="compact" data-status="{b["status"]}" data-risk="{risk}" data-domains="{_e(" ".join(b["domains"]))}" '
        f'data-released="{b["released"]}" data-score="{last["value"] if last else -1}" data-search="{_e(search)}">'
        f'<td data-label="Benchmark"><a href="{base}b/{b["id"]}/">{_e(b["name"])}</a>{succ}</td>'
        f'<td data-label="{t["released"]}" class="nowrap muted">{_e(b["released"])}</td>'
        f'<td data-label="{t["domains"]}" class="muted">{_e(", ".join(b["domains"]))}</td>'
        f'<td data-label="{t["status"]}"><span class="pill status-{b["status"]}">{b["status"]}</span></td>'
        f'<td data-label="{t["risk"]}">{risk_cell}</td>'
        f'<td data-label="{t["top"]}" colspan="2">{score}</td>'
        "</tr>"
    )


def html_benchmark_rows(ds: Dataset, layer: str, lang: str) -> str:
    t = T[lang]
    base = "../" if lang != "en" else ""
    rows = []
    divider_done = False
    for b in sort_benchmarks(ds, layer):
        if not is_live(b):
            if not divider_done:
                rows.append(f'<tr class="divider"><td colspan="7">{t["divider"]}</td></tr>')
                divider_done = True
            rows.append(compact_row(ds, b, lang, base))
            continue
        sota = ds.sota(b["id"])
        desc = b[t["description"]]
        risk = b.get("contamination_risk") or ""
        risk_cell = f'<span class="pill risk-{risk}">{risk}</span>' if risk else "—"
        results = ds.results.get(b["id"], [])
        domains = " ".join(f'<span class="pill domain">{_e(d)}</span>' for d in b["domains"])
        chain = chain_html(ds, b, lang, base)
        chain_wrap = f' <span class="chainwrap">{chain}</span>' if chain else ""
        search = " ".join([b["name"], b.get("full_name", ""), *b["domains"], sota["system"] if sota else ""]).lower()
        domains_attr = _e(" ".join(b["domains"]))
        score_attr = sota["value"] if sota else -1
        rows.append(
            f'<tr data-status="{b["status"]}" data-risk="{risk}" data-domains="{domains_attr}" '
            f'data-released="{b["released"]}" data-score="{score_attr}" data-search="{_e(search)}">'
            f'<td data-label="Benchmark"><a href="{base}b/{b["id"]}/"><strong>{_e(b["name"])}</strong></a>{chain_wrap}'
            f'<div class="muted small" title="{_e(desc)}">{_e(desc)}</div></td>'
            f'<td data-label="{t["released"]}" class="nowrap">{_e(b["released"])}</td>'
            f'<td data-label="{t["domains"]}">{domains}</td>'
            f'<td data-label="{t["status"]}"><span class="pill status-{b["status"]}">{b["status"]}</span></td>'
            f'<td data-label="{t["risk"]}">{risk_cell}</td>'
            f'<td data-label="{t["top"]}">{score_html(ds, b, lang)}</td>'
            f'<td data-label="{t["history"]}" class="sparkcell">{sparkline(b, results)}'
            f'<a class="muted small-link" href="{base}b/{b["id"]}/">{t["rows"].format(n=len(results))}</a></td>'
            "</tr>"
        )
    return "\n".join(rows)


def conditions_html(c: dict[str, Any]) -> str:
    if not c:
        return '<span class="muted">—</span>'
    parts = []
    for k, v in c.items():
        if k == "notes":
            continue
        if isinstance(v, bool):
            parts.append(f'<span class="pill cond">{k}{"" if v else ": no"}</span>')
        else:
            parts.append(f'<span class="pill cond">{_e(k)}: {_e(v)}</span>')
    out = " ".join(parts)
    if c.get("notes"):
        out += f'<div class="muted small-note">{_e(c["notes"])}</div>'
    return out


def html_ledger(ds: Dataset, b: dict[str, Any], lang: str) -> str:
    t = T[lang]
    rows = sorted(ds.results.get(b["id"], []), key=lambda r: (-r["value"], r["date"]))
    if not b["metric"]["higher_is_better"]:
        rows.sort(key=lambda r: (r["value"], r["date"]))
    if not rows:
        return f'<p class="muted">{t["no_result"]}</p>'
    body = []
    for r in rows:
        kind = r["source"]["kind"]
        body.append(
            "<tr>"
            f'<td data-label="{t["th_system"]}"><strong>{_e(r["system"])}</strong></td>'
            f'<td data-label="{t["th_developer"]}">{_e(r["developer"])}</td>'
            f'<td data-label="{t["th_value"]}" class="nowrap"><span class="score">{_e(fmt_value(b, r["value"]))}</span></td>'
            f'<td data-label="{t["th_date"]}" class="nowrap"><time datetime="{r["date"]}">{r["date"]}</time></td>'
            f'<td data-label="{t["th_source"]}"><a class="src src-{kind}" href="{_e(r["source"]["url"])}" rel="noopener">'
            f"{kind_label(lang, kind)}</a></td>"
            f'<td data-label="{t["th_conditions"]}">{conditions_html(r.get("conditions", {}))}</td>'
            "</tr>"
        )
    head = "".join(
        f'<th scope="col">{t[k]}</th>'
        for k in ("th_system", "th_developer", "th_value", "th_date", "th_source", "th_conditions")
    )
    return f'<div class="wrap"><table class="ledger"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def render_detail(ds: Dataset, b: dict[str, Any], lang: str) -> str:
    t = T[lang]
    base = "../../" if lang == "en" else "../../../"
    other_lang = "zh" if lang == "en" else "en"
    sota = ds.sota(b["id"])
    desc = b[t["description"]]
    hb = b.get("human_baseline")
    if sota:
        meta_desc = t["meta_desc"].format(
            name=b["name"], desc=desc, score=fmt_value(b, sota["value"]), system=sota["system"],
            kind=kind_label(lang, sota["source"]["kind"]), n=len(ds.results.get(b["id"], [])),
        )
    else:
        meta_desc = t["meta_desc_none"].format(name=b["name"], desc=desc)
    facts = [
        (t["released"], _e(b["released"])),
        (t["maintainer"], _e(b["maintainer"])),
        (t["status"], f'<span class="pill status-{b["status"]}">{b["status"]}</span>'),
        (t["risk"], f'<span class="pill risk-{b["contamination_risk"]}">{b["contamination_risk"]}</span>'
         if b.get("contamination_risk") else "—"),
        (t["metric"], f'{_e(b["metric"]["name"])} ({b["metric"]["unit"]}, {"↑" if b["metric"]["higher_is_better"] else "↓"})'),
        (t["task_count"], f'{b["task_count"]:,}' if b.get("task_count") else "—"),
        (t["domains"], " ".join(f'<span class="pill domain">{_e(d)}</span>' for d in b["domains"])),
        (t["human"], f'<a href="{_e(hb["source"])}" rel="noopener">{hb["value"]:g}%</a> '
         f'<span class="muted">{_e(hb["population"])}</span>' if hb else f'<span class="muted">{t["no_baseline"]}</span>'),
    ]
    links = " · ".join(
        f'<a href="{_e(url)}" rel="noopener">{t[k]}</a>' for k, url in b["links"].items() if url
    )
    chain = chain_html(ds, b, lang, base)
    ld = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": b["name"],
        "alternateName": b.get("full_name"),
        "description": desc,
        "url": f"{SITE}{detail_url(lang, b['id'])}",
        "datePublished": b["released"],
        "creator": {"@type": "Organization", "name": b["maintainer"]},
        "keywords": b["domains"],
        "isPartOf": {"@type": "Dataset", "name": "LLM Benchmarks Tracker", "url": f"{SITE}/"},
        "distribution": {"@type": "DataDownload", "encodingFormat": "application/json",
                         "contentUrl": f"{SITE}/api/v1/results/{b['id']}.json"},
    }
    if b["links"].get("paper"):
        ld["citation"] = b["links"]["paper"]
    ctx = {
        "LANG": "en" if lang == "en" else "zh-CN",
        "TITLE": t["detail_title"].format(name=b["name"]),
        "META_DESC": meta_desc,
        "SITE": SITE,
        "BASE": base,
        "PAGE_URL": f"{SITE}{detail_url(lang, b['id'])}",
        "ALT_EN": f"{SITE}{detail_url('en', b['id'])}",
        "ALT_ZH": f"{SITE}{detail_url('zh', b['id'])}",
        "LANG_SWITCH": t["lang_switch"].format(other=f"{SITE}{detail_url(other_lang, b['id'])}"),
        "JSON_LD": json.dumps({k: v for k, v in ld.items() if v is not None}, ensure_ascii=False),
        "NAME": _e(b["name"]),
        "FULL_NAME": _e(b.get("full_name") or ""),
        "DESC": _e(desc),
        "SCORE": score_html(ds, b, lang),
        "FACTS": "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts),
        "LINKS": links,
        "CHAIN": chain,
        "NOTES": f'<p class="notes"><strong>{t["notes"]}.</strong> {_e(b["notes"])}</p>' if b.get("notes") else "",
        "SPARK": sparkline(b, ds.results.get(b["id"], []), width=480, height=96),
        "LEDGER": html_ledger(ds, b, lang),
        "LEDGER_TITLE": t["ledger"],
        "HISTORY_TITLE": t["history"],
        "JSON_URL": f"{base}api/v1/results/{b['id']}.json",
        "JSON_LABEL": t["json"],
        "BACK": t["back"],
        "HOME": f"{SITE}/{lang_prefix(lang)}",
        "GENERATED": date.today().isoformat(),
    }
    text = (TEMPLATE.parent / "detail.html").read_text(encoding="utf-8")
    for key, value in ctx.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if leftover:
        raise SystemExit(f"detail.html: placeholders left unrendered: {leftover}")
    return text


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


CHART_W, CHART_H = 1000, 460
CHART_PAD = {"l": 44, "r": 110, "t": 16, "b": 36}


def saturation_chart(ds: Dataset, lang: str, base: str) -> str:
    """Score-over-time chart: one polyline per percent-metric benchmark from its earliest sourced
    result to its best, a dashed marker for the human baseline, and arrows along supersession chains.
    Pure SVG; each series is an <a> so clicking works without JS. site.js adds hover/toggles."""
    t = T[lang]
    series = [
        b for b in ds.benchmarks.values()
        if b["metric"]["unit"] == "percent" and len(ds.results.get(b["id"], [])) >= 1
    ]
    if not series:
        return ""
    all_dates = [date.fromisoformat(r["date"]) for b in series for r in ds.results[b["id"]]]
    all_dates += [date.fromisoformat(b["released"] + "-01") for b in series]
    d0 = date(min(all_dates).year, 1, 1).toordinal()
    d1 = date(max(all_dates).year + 1, 1, 1).toordinal()
    x0, x1 = CHART_PAD["l"], CHART_W - CHART_PAD["r"]
    y0, y1 = CHART_PAD["t"], CHART_H - CHART_PAD["b"]

    def X(d: str) -> float:
        return x0 + (date.fromisoformat(d if len(d) == 10 else d + "-01").toordinal() - d0) / (d1 - d0) * (x1 - x0)

    def Y(v: float) -> float:
        return y1 - max(0.0, min(100.0, v)) / 100.0 * (y1 - y0)

    out = [
        f'<svg class="chart" viewBox="0 0 {CHART_W} {CHART_H}" role="img" aria-labelledby="chart-title" '
        f'xmlns="http://www.w3.org/2000/svg">',
        f'<title id="chart-title">{t["chart_title"]}</title>',
    ]
    # grid
    for v in (0, 25, 50, 75, 100):
        y = Y(v)
        out.append(f'<line class="grid" x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}"/>')
        out.append(f'<text class="axis" x="{x0 - 8}" y="{y + 4:.1f}" text-anchor="end">{v}%</text>')
    for year in range(date.fromordinal(d0).year, date.fromordinal(d1).year + 1):
        x = X(f"{year}-01-01")
        out.append(f'<line class="grid v" x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}"/>')
        if year < date.fromordinal(d1).year:
            out.append(f'<text class="axis" x="{x + 4:.1f}" y="{y1 + 16}">{year}</text>')
    # supersession arrows (behind series)
    pos: dict[str, tuple[float, float]] = {}
    for b in series:
        rows = sorted(ds.results[b["id"]], key=lambda r: r["date"])
        pos[b["id"]] = (X(rows[0]["date"]), Y(rows[0]["value"]))
    out.append('<defs><marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto">'
               '<path d="M0,0 L8,4 L0,8 z" class="arrhead"/></marker></defs>')
    for b in series:
        nxt = b.get("superseded_by")
        if nxt in pos:
            best = ds.sota(b["id"])
            ax, ay = X(best["date"]), Y(best["value"])
            bx, by = pos[nxt]
            hid = "" if is_live(b) and is_live(ds.benchmarks[nxt]) else ' hidden="hidden"'
            out.append(f'<line class="chain-arrow" x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
                       f'marker-end="url(#arr)" data-from="{b["id"]}" data-to="{nxt}"{hid}/>')
    # label positions: greedy vertical de-overlap for active benchmarks (others get no label)
    label_y: dict[str, float] = {}
    active = sorted(
        (b for b in series if b["status"] == "active"),
        key=lambda b: Y(ds.sota(b["id"])["value"]),
    )
    prev = -1e9
    for b in active:
        y = max(Y(ds.sota(b["id"])["value"]), prev + 13)
        label_y[b["id"]] = y
        prev = y
    # series
    for b in sorted(series, key=lambda b: b["released"]):
        rows = sorted(ds.results[b["id"]], key=lambda r: r["date"])
        pts = " ".join(f"{X(r['date']):.1f},{Y(r['value']):.1f}" for r in rows)
        best = ds.sota(b["id"])
        lx, ly = X(best["date"]), Y(best["value"])
        hb = b.get("human_baseline")
        human = ""
        if hb:
            hy = Y(hb["value"])
            human = (f'<line class="human-line" x1="{X(rows[0]["date"]) - 6:.1f}" y1="{hy:.1f}" '
                     f'x2="{lx + 6:.1f}" y2="{hy:.1f}"/>')
        label = ""
        if b["id"] in label_y:
            ty = label_y[b["id"]]
            leader = ""
            if abs(ty - ly) > 6:
                leader = f'<line class="leader" x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx + 8:.1f}" y2="{ty:.1f}"/>'
            label = f'{leader}<text class="slabel" x="{lx + 10:.1f}" y="{ty + 4:.1f}">{_e(b["name"])}</text>'
        hidden = "" if is_live(b) else ' hidden="hidden"'
        kind = kind_label(lang, best["source"]["kind"])
        tip = f'{b["name"]} · {b["released"]} · {fmt_value(b, best["value"])} {best["system"]} ({kind})'
        out.append(
            f'<a href="{base}b/{b["id"]}/" class="series layer-{b["layer"]} status-{b["status"]}" '
            f'data-id="{b["id"]}" data-layer="{b["layer"]}" data-status="{b["status"]}" data-tip="{_e(tip)}"{hidden}>'
            f"<title>{_e(tip)}</title>{human}"
            f'<polyline class="hit" points="{pts}"/><polyline points="{pts}"/>'
            + "".join(f'<circle cx="{X(r["date"]):.1f}" cy="{Y(r["value"]):.1f}" r="2.5"/>' for r in rows)
            + f'<circle class="last" cx="{lx:.1f}" cy="{ly:.1f}" r="4"/>{label}</a>'
        )
    out.append("</svg>")
    others = [b for b in ds.benchmarks.values() if b["metric"]["unit"] != "percent" or b["id"] not in pos]
    note = ""
    if others:
        names = ", ".join(f'<a href="{base}b/{b["id"]}/">{_e(b["name"])}</a>' for b in sorted(others, key=lambda b: b["name"]))
        note = f'<p class="muted small-note">{t["chart_excluded"]}: {names}</p>'
    controls = (
        '<div class="chart-controls" hidden>'
        f'<span class="fgroup"><span class="flabel">{t["layer"]}</span>'
        + "".join(
            f'<button type="button" class="pill tl-{k}" data-toggle="layer" data-value="{k}" aria-pressed="true">{k}</button>'
            for k in ("model", "agent")
        )
        + "</span>"
        f'<span class="fgroup"><span class="flabel">{t["status"]}</span>'
        + "".join(
            f'<button type="button" class="pill status-{s}" data-toggle="status" data-value="{s}" '
            f'aria-pressed="{"true" if s in LIVE else "false"}">{s}</button>'
            for s in ("active", "saturating", "saturated", "retired")
        )
        + f'</span><span class="muted chart-hint">{t["chart_hint"]}</span></div>'
    )
    tooltip = '<div class="tooltip" hidden></div>'
    return f'<div class="chart-wrap">{controls}{"".join(out)}{tooltip}</div>{note}'


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



def filter_bar(ds: Dataset, layer: str, lang: str) -> str:
    """Progressive-enhancement filter controls; hidden until JS enables them."""
    t = T[lang]
    statuses = sorted({b["status"] for b in ds.benchmarks.values() if b["layer"] == layer}, key=lambda s: s)
    risks = [r for r in ("low", "medium", "high") if any(
        b.get("contamination_risk") == r for b in ds.benchmarks.values() if b["layer"] == layer)]

    def group(name: str, label: str, values: list[str], cls: str) -> str:
        btns = "".join(
            f'<button type="button" class="pill {cls}-{v}" data-filter="{name}" data-value="{v}" '
            f'aria-pressed="false">{v}</button>'
            for v in values
        )
        return f'<span class="fgroup"><span class="flabel">{label}</span>{btns}</span>'

    return (
        f'<form class="filters" data-target="{layer}" hidden>'
        f'<input type="search" placeholder="{t["filter_placeholder"]}" aria-label="{t["filter_placeholder"]}" data-search>'
        f'{group("status", t["status"], statuses, "status")}'
        f'{group("risk", t["risk"], risks, "risk")}'
        f'<output class="muted" data-count></output>'
        "</form>"
    )


def render_site(ds: Dataset, lang: str) -> str:
    n_results = sum(len(v) for v in ds.results.values())
    model = sum(1 for b in ds.benchmarks.values() if b["layer"] == "model")
    base = "../" if lang != "en" else ""
    other = f"{SITE}/zh/" if lang == "en" else f"{SITE}/"
    ctx = {
        "SITE": SITE,
        "BASE": base,
        "PAGE_URL": f"{SITE}/" if lang == "en" else f"{SITE}/{lang}/",
        "LANG_SWITCH": T[lang]["lang_switch"].format(other=other),
        "JSON_LD": json_ld(ds),
        "GENERATED": date.today().isoformat(),
        "N_MODEL": str(model),
        "N_AGENT": str(len(ds.benchmarks) - model),
        "N_BENCH": str(len(ds.benchmarks)),
        "N_EVALUATORS": str(len(ds.evaluators)),
        "N_RESULTS": str(n_results),
        "PROVENANCE": str(provenance_share(ds)),
        "PROVENANCE_LABEL": T[lang]["provenance"],
        "MODEL_FILTERS": filter_bar(ds, "model", lang),
        "AGENT_FILTERS": filter_bar(ds, "agent", lang),
        "MODEL_ROWS": html_benchmark_rows(ds, "model", lang),
        "AGENT_ROWS": html_benchmark_rows(ds, "agent", lang),
        "EVALUATOR_ROWS": html_evaluator_rows(ds, lang),
        "TIMELINE": html_timeline(ds),
        "CHART": saturation_chart(ds, lang, base),
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
    for lang in ("en", "zh"):
        out = DIST / lang_prefix(lang)
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(render_site(ds, lang), encoding="utf-8")
        for b in ds.benchmarks.values():
            d = out / "b" / b["id"]
            d.mkdir(parents=True)
            (d / "index.html").write_text(render_detail(ds, b, lang), encoding="utf-8")
    (DIST / ".nojekyll").touch()
    shutil.copytree(STATIC, DIST, dirs_exist_ok=True)
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    today = date.today().isoformat()
    urls = [(f"{SITE}/", "weekly"), (f"{SITE}/zh/", "weekly"), (f"{SITE}/api/v1/index.json", None)]
    urls += [(f"{SITE}{detail_url(lang, bid)}", "weekly") for lang in ("en", "zh") for bid in sorted(ds.benchmarks)]
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
