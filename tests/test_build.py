"""Build pipeline tests: README rendering is deterministic and idempotent; site template renders fully."""

from __future__ import annotations

from scripts import build
from scripts.dataset import DATA, load, validate


def _ds():
    errors: list[str] = []
    ds = load(DATA, errors)
    errors += validate(ds)
    assert errors == []
    return ds


def test_readme_render_is_idempotent():
    ds = _ds()
    text = build.README.read_text(encoding="utf-8")
    once = build.render_readme(ds, text)
    assert build.render_readme(ds, once) == once
    for name in ("stats", "model", "agent", "evaluators", "timeline"):
        assert f"<!-- gen:{name} -->" in once and f"<!-- /gen:{name} -->" in once


def test_readme_tables_cover_every_entity():
    ds = _ds()
    text = build.render_readme(ds, build.README.read_text(encoding="utf-8"))
    for b in ds.benchmarks.values():
        assert f"[{b['name']}]" in text or f"| {b['name']} |" in text, b["id"]
    for e in ds.evaluators.values():
        assert e["name"] in text, e["id"]


def test_site_renders_without_placeholders():
    ds = _ds()
    html = build.render_site(ds)
    assert "{{" not in html
    for b in ds.benchmarks.values():
        assert f"api/v1/results/{b['id']}.json" in html
