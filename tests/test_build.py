"""Build pipeline tests: README rendering is deterministic and idempotent; site template renders fully."""

from __future__ import annotations

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


def test_saturation_chart_covers_percent_benchmarks():
    ds = _ds()
    svg = build.saturation_chart(ds, "en", "")
    pct = [b for b in ds.benchmarks.values() if b["metric"]["unit"] == "percent" and ds.results.get(b["id"])]
    assert svg.count('class="series') == len(pct)
    for b in pct:
        assert f'data-id="{b["id"]}"' in svg
        assert f'href="b/{b["id"]}/"' in svg
    # retired series are hidden by default; live ones are not
    assert all(f'data-id="{b["id"]}"' in svg for b in pct if not build.is_live(b))
    assert svg.count('hidden="hidden"') >= sum(1 for b in pct if not build.is_live(b))
    assert svg.count('class="human-line"') == sum(1 for b in pct if b.get("human_baseline"))
