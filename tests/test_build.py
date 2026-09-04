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
        assert f"api/v1/results/{b['id']}.json" in html


def test_zh_site_uses_translations_and_relative_paths():
    ds = _ds()
    html = build.render_site(ds, "zh")
    b = next(iter(ds.benchmarks.values()))
    assert b["description_zh"] in html
    assert b["description"] not in html
    assert 'href="../api/v1/' in html and 'href="../style.css"' in html
    assert 'hreflang="en"' in html and 'lang="zh-CN"' in html


def test_benchmarks_sorted_newest_first():
    ds = _ds()
    for layer in ("model", "agent"):
        released = [b["released"] for b in build.sort_benchmarks(ds, layer)]
        assert released == sorted(released, reverse=True), layer
