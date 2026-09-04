"""Load and validate the data directory.

Single entry point for every consumer (validate.py, build.py, tests).
`load()` returns a `Dataset`; `validate()` returns a list of error strings.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCHEMA = ROOT / "schema"

KINDS = {
    "benchmarks": "benchmark.schema.json",
    "results": "results.schema.json",
    "evaluators": "evaluator.schema.json",
}


@dataclass
class Dataset:
    benchmarks: dict[str, dict[str, Any]] = field(default_factory=dict)
    results: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    evaluators: dict[str, dict[str, Any]] = field(default_factory=dict)

    def sota(self, benchmark_id: str) -> dict[str, Any] | None:
        """Best result for a benchmark, honouring `metric.higher_is_better`.

        Ties broken by earliest date (first to reach the score)."""
        rows = self.results.get(benchmark_id)
        if not rows:
            return None
        higher = self.benchmarks[benchmark_id]["metric"]["higher_is_better"]
        sign = 1 if higher else -1
        return min(rows, key=lambda r: (-sign * r["value"], r["date"]))


def _validators() -> dict[str, Draft202012Validator]:
    out = {}
    for kind, name in KINDS.items():
        schema = json.loads((SCHEMA / name).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        out[kind] = Draft202012Validator(schema, format_checker=FormatChecker())
    return out


def _read_json(path: Path, rel: str, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: invalid JSON: {exc}")
        return None


def load(data_dir: Path = DATA, errors: list[str] | None = None) -> Dataset:
    """Load every file. Schema violations are appended to `errors`; a file that
    fails schema validation is reported but not loaded, so cross-file checks in
    `validate()` can rely on well-typed documents."""
    if errors is None:
        errors = []
    validators = _validators()
    ds = Dataset()

    for kind, validator in validators.items():
        for path in sorted((data_dir / kind).glob("*.json")):
            rel = f"{kind}/{path.name}"
            doc = _read_json(path, rel, errors)
            if doc is None:
                continue
            schema_errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
            for err in schema_errors:
                loc = "/".join(str(p) for p in err.path) or "<root>"
                errors.append(f"{rel}: {loc}: {err.message}")
            key = "benchmark" if kind == "results" else "id"
            ident = doc.get(key) if isinstance(doc, dict) else None
            if ident != path.stem:
                errors.append(f"{rel}: file name must equal `{key}` ({ident!r})")
                continue
            if schema_errors:
                continue
            if kind == "results":
                ds.results[ident] = doc["results"]
            else:
                getattr(ds, kind)[ident] = doc
    return ds


def validate(ds: Dataset, today: date | None = None) -> list[str]:
    """Cross-file invariants that a per-file schema cannot express."""
    today = today or date.today()
    errors: list[str] = []
    bench_ids = set(ds.benchmarks)

    for bid, b in ds.benchmarks.items():
        for rel in ("supersedes", "superseded_by"):
            target = b.get(rel)
            if target and target not in bench_ids:
                errors.append(f"benchmarks/{bid}: {rel} -> unknown benchmark {target!r}")
        if b.get("supersedes") == bid or b.get("superseded_by") == bid:
            errors.append(f"benchmarks/{bid}: cannot supersede itself")
        if b["released"] > today.strftime("%Y-%m"):
            errors.append(f"benchmarks/{bid}: released {b['released']} is in the future")
        if b["status"] in ("active",) and bid not in ds.results:
            errors.append(f"benchmarks/{bid}: active benchmark has no results ledger")

    for bid, b in ds.benchmarks.items():
        sup = b.get("supersedes")
        if sup in bench_ids and ds.benchmarks[sup].get("superseded_by") != bid:
            errors.append(f"benchmarks/{bid}: supersedes {sup} but {sup}.superseded_by != {bid}")
        nxt = b.get("superseded_by")
        if nxt in bench_ids and ds.benchmarks[nxt].get("supersedes") != bid:
            errors.append(f"benchmarks/{bid}: superseded_by {nxt} but {nxt}.supersedes != {bid}")

    for bid, rows in ds.results.items():
        if bid not in bench_ids:
            errors.append(f"results/{bid}: no matching benchmark file")
            continue
        b = ds.benchmarks[bid]
        unit = b["metric"]["unit"]
        splits = {s["name"] for s in b.get("splits", [])}
        seen: set[tuple[str, str, str]] = set()
        for i, r in enumerate(rows):
            where = f"results/{bid}[{i}] {r.get('system', '?')}"
            if unit == "percent" and not 0 <= r["value"] <= 100:
                errors.append(f"{where}: percent value {r['value']} out of range")
            if r["date"] > today.isoformat():
                errors.append(f"{where}: date {r['date']} is in the future")
            if r["source"]["accessed"] < r["date"]:
                errors.append(f"{where}: source.accessed precedes result date")
            split = r.get("conditions", {}).get("split")
            if split and split not in splits:
                errors.append(f"{where}: conditions.split {split!r} not declared in benchmark.splits")
            key = (r["system"], r["date"], r["source"]["url"])
            if key in seen:
                errors.append(f"{where}: duplicate row (same system, date, source)")
            seen.add(key)
        dates = [r["date"] for r in rows]
        if dates != sorted(dates):
            errors.append(f"results/{bid}: rows must be in ascending date order (append-only ledger)")

    for eid, e in ds.evaluators.items():
        for target in e.get("benchmarks", []):
            if target not in bench_ids:
                errors.append(f"evaluators/{eid}: benchmarks -> unknown benchmark {target!r}")

    return errors
