"""sync_ledgers: only strictly better rows are appended; ordering, duplicates and ranges are enforced."""

from __future__ import annotations

import copy
from datetime import date

from scripts import sync_ledgers as s
from scripts.dataset import Dataset

B = {"id": "b1", "metric": {"unit": "percent", "higher_is_better": True}}
OLD = {"system": "A", "value": 50.0, "date": "2025-01-01", "source": {"url": "u", "kind": "paper", "accessed": "2025-01-01"}}


def _ds(rows):
    ds = Dataset()
    ds.benchmarks["b1"] = copy.deepcopy(B)
    ds.results["b1"] = copy.deepcopy(rows)
    return ds


def _with(fetcher, monkeypatch):
    monkeypatch.setattr(s, "FETCHERS", {"b1": fetcher})


def test_higher_score_is_appended_with_provenance(monkeypatch):
    _with(lambda: [s.Row("B", "Dev", 60.0, "https://x/lb", "official-leaderboard", conditions={"scaffold": "h"})], monkeypatch)
    add, problems = s.new_rows(_ds([OLD]), date(2026, 9, 4))
    assert problems == []
    row = add["b1"]
    assert row["value"] == 60.0 and row["source"]["kind"] == "official-leaderboard"
    assert row["date"] == "2026-09-04" and row["source"]["accessed"] == "2026-09-04"
    assert row["conditions"]["scaffold"] == "h" and "sync_ledgers" in row["conditions"]["notes"]


def test_equal_or_lower_is_ignored(monkeypatch):
    _with(lambda: [s.Row("B", "Dev", 50.04, "u2", "official-leaderboard"), s.Row("C", "Dev", 40, "u2", "paper")], monkeypatch)
    add, _ = s.new_rows(_ds([OLD]), date(2026, 9, 4))
    assert add == {}


def test_lower_is_better_direction(monkeypatch):
    ds = _ds([OLD])
    ds.benchmarks["b1"]["metric"]["higher_is_better"] = False
    _with(lambda: [s.Row("B", "Dev", 40.0, "u2", "official-leaderboard")], monkeypatch)
    add, _ = s.new_rows(ds, date(2026, 9, 4))
    assert add["b1"]["value"] == 40.0


def test_source_date_before_last_row_keeps_ledger_ascending(monkeypatch):
    _with(lambda: [s.Row("B", "Dev", 60.0, "u2", "independent-evaluation", date="2024-06-01")], monkeypatch)
    add, _ = s.new_rows(_ds([OLD]), date(2026, 9, 4))
    assert add["b1"]["date"] == "2026-09-04"
    assert "2024-06-01" in add["b1"]["conditions"]["notes"]


def test_out_of_range_is_reported_not_written(monkeypatch):
    _with(lambda: [s.Row("B", "Dev", 140.0, "u2", "official-leaderboard")], monkeypatch)
    add, problems = s.new_rows(_ds([OLD]), date(2026, 9, 4))
    assert add == {} and any("out-of-range" in p for p in problems)


def test_fetch_failure_is_a_problem_not_a_crash(monkeypatch):
    def boom():
        raise OSError("down")

    _with(boom, monkeypatch)
    add, problems = s.new_rows(_ds([OLD]), date(2026, 9, 4))
    assert add == {} and problems and "fetch failed" in problems[0]


def test_empty_source_is_reported(monkeypatch):
    _with(lambda: [], monkeypatch)
    add, problems = s.new_rows(_ds([OLD]), date(2026, 9, 4))
    assert add == {} and "no rows" in problems[0]
