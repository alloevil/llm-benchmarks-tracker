"""Build pipeline tests: README rendering is deterministic and idempotent; site template renders fully."""

from __future__ import annotations

import re

import pytest

from scripts import build
from scripts.dataset import DATA, load, validate


def _ds():
    errors: list[str] = []
    ds = load(DATA, errors)
    errors += validate(ds)
    assert errors == []
    return ds


LANGS = [("en", build.README), ("zh", build.README_ZH)]


@pytest.mark.parametrize(("lang", "path"), LANGS)
def test_readme_render_is_idempotent(lang, path):
    ds = _ds()
    text = path.read_text(encoding="utf-8")
    once = build.render_readme(ds, text, lang)
    assert build.render_readme(ds, once, lang) == once
    for name in ("stats", "model", "agent", "evaluators", "timeline"):
        assert f"<!-- gen:{name} -->" in once and f"<!-- /gen:{name} -->" in once


@pytest.mark.parametrize(("lang", "path"), LANGS)
def test_readme_tables_cover_every_entity(lang, path):
    ds = _ds()
    text = build.render_readme(ds, path.read_text(encoding="utf-8"), lang)
    for b in ds.benchmarks.values():
        assert f"[{b['name']}]" in text or f"| {b['name']} |" in text, b["id"]
    for e in ds.evaluators.values():
        assert e["name"] in text, e["id"]


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_site_renders_without_placeholders(lang):
    ds = _ds()
    html = build.render_site(ds, lang)
    assert "{{" not in html
    for b in ds.benchmarks.values():
        assert f'b/{b["id"]}/' in html


@pytest.mark.parametrize("lang", ["en", "zh"])
def test_detail_pages_render(lang):
    ds = _ds()
    for b in ds.benchmarks.values():
        page = build.render_detail(ds, b, lang)
        assert "{{" not in page, b["id"]
        assert f"api/v1/results/{b['id']}.json" in page
        assert f'<link rel="canonical" href="{build.SITE}{build.detail_url(lang, b["id"])}">' in page
        for r in ds.results.get(b["id"], []):
            assert r["source"]["url"] in page, (b["id"], r["system"])


def test_sparkline_shape():
    b = {"metric": {"unit": "percent", "higher_is_better": True}}
    rows = [{"date": "2024-01-01", "value": 10}, {"date": "2025-01-01", "value": 60}]
    svg = build.sparkline(b, rows)
    assert svg.startswith("<svg") and "polyline" in svg and "10% → 60%" in svg
    assert build.sparkline(b, rows[:1]) == ""


def test_supersession_chain_links_both_ways():
    ds = _ds()
    page = build.render_detail(ds, ds.benchmarks["swe-bench-verified"], "en")
    assert 'b/swe-bench/"' in page and 'b/swe-bench-pro/"' in page


def test_zh_site_uses_translations_and_relative_paths():
    ds = _ds()
    html = build.render_site(ds, "zh")
    b = next(b for b in ds.benchmarks.values() if build.is_live(b))  # compact retired rows carry no description
    assert b["description_zh"] in html
    assert b["description"] not in html
    assert 'href="../api/v1/' in html and 'href="../style.css"' in html
    assert 'hreflang="en"' in html and 'lang="zh-CN"' in html


def test_benchmarks_grouped_live_first_then_newest():
    ds = _ds()
    for layer in ("model", "agent"):
        rows = build.sort_benchmarks(ds, layer)
        live = [build.is_live(b) for b in rows]
        assert live == sorted(live, reverse=True), f"{layer}: retired rows before live rows"
        for group in (True, False):
            released = [b["released"] for b in rows if build.is_live(b) is group]
            assert released == sorted(released, reverse=True), (layer, group)


def test_retired_rows_are_compact_with_divider():
    ds = _ds()
    html = build.render_site(ds, "en")
    assert html.count('<tr class="divider">') == 2  # one per layer table
    retired = [b for b in ds.benchmarks.values() if not build.is_live(b)]
    assert retired, "fixture assumption: some benchmark is saturated/retired"
    assert html.count('<tr class="compact"') == len(retired)
    assert "last reported" in html


def test_year_groups_only_current_year_expanded():
    ds = _ds()
    html = build.render_site(ds, "en")
    heads = re.findall(r'<tr class="yhead" data-year="(live|past)-(\d{4})" data-layer="\w+" data-expanded="(true|false)"', html)
    assert heads, "no year headers"
    pat = r'<tr class="yhead" data-year="(live|past)-(\d{4})" data-layer="(\w+)" data-expanded="(true|false)"'
    heads_by_layer = re.findall(pat, html)
    for layer in ("model", "agent"):
        newest = max(b["released"][:4] for b in ds.benchmarks.values() if b["layer"] == layer and build.is_live(b))
        for kind, year, lyr, expanded in heads_by_layer:
            if lyr == layer:
                assert (expanded == "true") == (kind == "live" and year == newest), (layer, kind, year, expanded)
    # every benchmark row carries its year key
    for b in ds.benchmarks.values():
        key = f'data-year="{"live" if build.is_live(b) else "past"}-{b["released"][:4]}"'
        assert key in html, b["id"]


def test_lifespan_chart_covers_percent_benchmarks():
    ds = _ds()
    html = build.lifespan_chart(ds, "en", "")
    pct = [b for b in ds.benchmarks.values() if b["metric"]["unit"] == "percent" and ds.results.get(b["id"])]
    live = [b for b in pct if build.is_live(b)]
    assert html.count("<svg") == 4  # live/full × desktop/mobile
    live_svg, full_svg = html.split("<svg")[1:3]
    assert live_svg.count('class="row ') == len(live)
    assert full_svg.count('class="row ') == len(pct)
    for b in pct:
        assert f'data-id="{b["id"]}"' in full_svg and f'href="b/{b["id"]}/"' in full_svg
    assert full_svg.count('class="human-line"') == sum(1 for b in pct if b.get("human_baseline"))
    assert full_svg.count('class="chain-arrow"') == sum(
        1 for b in pct if b.get("superseded_by") in {x["id"] for x in pct}
    )
    assert "AgentBench" in html.split("</svg>")[-1]  # non-percent listed below the chart


def test_frontier_is_monotone_running_best():
    b = {"metric": {"unit": "percent", "higher_is_better": True}}
    rows = [{"date": "2024-01-01", "value": 40}, {"date": "2024-06-01", "value": 30},
            {"date": "2025-01-01", "value": 70}, {"date": "2025-02-01", "value": 65}]
    assert build.frontier(b, rows) == [("2024-01-01", 40), ("2025-01-01", 70)]
    b["metric"]["higher_is_better"] = False
    assert build.frontier(b, rows) == [("2024-01-01", 40), ("2024-06-01", 30)]
