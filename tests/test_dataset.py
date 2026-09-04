"""Contract tests for scripts/dataset.py.

Each test builds a minimal valid dataset in a temp dir, breaks one invariant,
and asserts the validator names it. The real data/ directory is also checked
end-to-end so a bad commit fails here as well as in scripts/validate.py.
"""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from scripts.dataset import DATA, load, validate

TODAY = date(2026, 9, 4)

BENCH = {
    "id": "b1",
    "name": "Bench One",
    "layer": "model",
    "released": "2024-01",
    "maintainer": "Someone",
    "description": "x" * 80,
    "description_zh": "测" * 30,
    "domains": ["reasoning"],
    "metric": {"name": "accuracy", "unit": "percent", "higher_is_better": True},
    "status": "active",
    "links": {"paper": "https://arxiv.org/abs/0000.00000"},
    "splits": [{"name": "dev"}],
}
ROW = {
    "system": "M",
    "developer": "D",
    "value": 50.0,
    "date": "2025-01-01",
    "source": {"url": "https://example.com", "kind": "paper", "accessed": "2026-09-04"},
}
EVAL = {
    "id": "e1",
    "name": "Eval One",
    "kind": "framework",
    "maintainer": "Someone",
    "released": "2023-01",
    "description": "y" * 80,
    "description_zh": "评" * 30,
    "status": "active",
    "links": {"repo": "https://example.com/repo"},
    "benchmarks": ["b1"],
}


def write_ds(tmp: Path, benchmarks=(BENCH,), results=None, evaluators=(EVAL,)) -> Path:
    for kind in ("benchmarks", "results", "evaluators"):
        (tmp / kind).mkdir(parents=True, exist_ok=True)
    for b in benchmarks:
        (tmp / "benchmarks" / f"{b['id']}.json").write_text(json.dumps(b))
    if results is None:
        results = {"b1": [ROW]}
    for bid, rows in results.items():
        (tmp / "results" / f"{bid}.json").write_text(json.dumps({"benchmark": bid, "results": rows}))
    for e in evaluators:
        (tmp / "evaluators" / f"{e['id']}.json").write_text(json.dumps(e))
    return tmp


def run(tmp: Path) -> list[str]:
    errors: list[str] = []
    ds = load(tmp, errors)
    return errors + validate(ds, today=TODAY)


def test_minimal_dataset_is_valid(tmp_path):
    assert run(write_ds(tmp_path)) == []


def test_filename_must_match_id(tmp_path):
    write_ds(tmp_path)
    (tmp_path / "benchmarks" / "b1.json").rename(tmp_path / "benchmarks" / "other.json")
    errs = run(tmp_path)
    assert any("file name must equal `id`" in e for e in errs)


def test_schema_rejects_unknown_status(tmp_path):
    b = copy.deepcopy(BENCH)
    b["status"] = "active_with_contamination_concerns"
    errs = run(write_ds(tmp_path, benchmarks=(b,)))
    assert any("status" in e and "is not one of" in e for e in errs)


def test_schema_rejects_string_score(tmp_path):
    row = copy.deepcopy(ROW)
    row["value"] = "~90%"
    errs = run(write_ds(tmp_path, results={"b1": [row]}))
    assert any("value" in e and "not of type 'number'" in e for e in errs)


def test_percent_out_of_range(tmp_path):
    row = copy.deepcopy(ROW)
    row["value"] = 101
    errs = run(write_ds(tmp_path, results={"b1": [row]}))
    assert any("out of range" in e for e in errs)


def test_results_must_be_ascending(tmp_path):
    later = copy.deepcopy(ROW)
    later["date"] = "2025-06-01"
    errs = run(write_ds(tmp_path, results={"b1": [later, ROW]}))
    assert any("ascending date order" in e for e in errs)


def test_duplicate_row_rejected(tmp_path):
    errs = run(write_ds(tmp_path, results={"b1": [ROW, copy.deepcopy(ROW)]}))
    assert any("duplicate row" in e for e in errs)


def test_future_date_rejected(tmp_path):
    row = copy.deepcopy(ROW)
    row["date"] = "2027-01-01"
    row["source"]["accessed"] = "2027-01-01"
    errs = run(write_ds(tmp_path, results={"b1": [row]}))
    assert any("in the future" in e for e in errs)


def test_accessed_before_date_rejected(tmp_path):
    row = copy.deepcopy(ROW)
    row["source"]["accessed"] = "2024-01-01"
    errs = run(write_ds(tmp_path, results={"b1": [row]}))
    assert any("accessed precedes" in e for e in errs)


def test_undeclared_split_rejected(tmp_path):
    row = copy.deepcopy(ROW)
    row["conditions"] = {"split": "nope"}
    errs = run(write_ds(tmp_path, results={"b1": [row]}))
    assert any("not declared in benchmark.splits" in e for e in errs)


def test_active_benchmark_requires_ledger(tmp_path):
    errs = run(write_ds(tmp_path, results={}))
    assert any("has no results ledger" in e for e in errs)


def test_saturated_benchmark_may_lack_ledger(tmp_path):
    b = copy.deepcopy(BENCH)
    b["status"] = "saturated"
    assert run(write_ds(tmp_path, benchmarks=(b,), results={})) == []


def test_orphan_ledger_rejected(tmp_path):
    errs = run(write_ds(tmp_path, results={"b1": [ROW], "ghost": [ROW]}))
    assert any("results/ghost: no matching benchmark" in e for e in errs)


def test_dangling_supersedes(tmp_path):
    b = copy.deepcopy(BENCH)
    b["superseded_by"] = "b9"
    errs = run(write_ds(tmp_path, benchmarks=(b,)))
    assert any("superseded_by -> unknown benchmark 'b9'" in e for e in errs)


def test_supersession_must_be_symmetric(tmp_path):
    b1 = copy.deepcopy(BENCH)
    b2 = copy.deepcopy(BENCH)
    b2["id"] = "b2"
    b2["supersedes"] = "b1"
    b2["status"] = "saturated"
    errs = run(write_ds(tmp_path, benchmarks=(b1, b2)))
    assert any("b1.superseded_by != b2" in e for e in errs)
    b1["superseded_by"] = "b2"
    assert run(write_ds(tmp_path, benchmarks=(b1, b2))) == []


def test_evaluator_dangling_benchmark(tmp_path):
    e = copy.deepcopy(EVAL)
    e["benchmarks"] = ["b1", "nope"]
    errs = run(write_ds(tmp_path, evaluators=(e,)))
    assert any("evaluators/e1: benchmarks -> unknown benchmark 'nope'" in e for e in errs)


def test_sota_respects_direction_and_ties(tmp_path):
    lo = copy.deepcopy(ROW)
    hi = copy.deepcopy(ROW)
    hi["value"] = 70
    hi["date"] = "2025-02-01"
    hi2 = copy.deepcopy(hi)
    hi2["date"] = "2025-03-01"
    hi2["source"]["url"] = "https://example.com/2"
    ds = load(write_ds(tmp_path, results={"b1": [lo, hi, hi2]}))
    assert ds.sota("b1")["date"] == "2025-02-01"  # first to reach the score
    ds.benchmarks["b1"]["metric"]["higher_is_better"] = False
    assert ds.sota("b1")["value"] == 50.0
    assert ds.sota("zzz") is None


@pytest.mark.skipif(not DATA.exists(), reason="repo data missing")
def test_repository_data_is_valid():
    errors: list[str] = []
    ds = load(DATA, errors)
    errors += validate(ds)
    assert errors == []
    assert ds.benchmarks, "repository has no benchmarks"
