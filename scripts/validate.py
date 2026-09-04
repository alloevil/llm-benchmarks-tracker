#!/usr/bin/env python3
"""Validate data/ against schema/ plus cross-file invariants. Exit 1 on any error."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dataset import load, validate  # noqa: E402


def main() -> int:
    errors: list[str] = []
    ds = load(errors=errors)
    errors += validate(ds)

    n_results = sum(len(v) for v in ds.results.values())
    print(
        f"{len(ds.benchmarks)} benchmarks, {n_results} results across "
        f"{len(ds.results)} ledgers, {len(ds.evaluators)} evaluators"
    )
    if errors:
        print(f"\n{len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
