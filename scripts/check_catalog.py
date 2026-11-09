"""Structural validation of imported DR-01 tables (not a source authenticity check)."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog"
REPORT = ROOT / "research/reports/NEW-DR-01-REPORT-RU.md"
REVIEW = "report_extracted_not_independently_verified"


def read(name: str) -> list[dict[str, str]]:
    with (CATALOG / name).open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def main() -> None:
    if not REPORT.is_file():
        raise ValueError("source research report missing")
    sources = read("sources_dr01.csv")
    observations = read("observations_dr01.csv")
    assert len(sources) == 71, f"expected 71 sources, got {len(sources)}"
    assert len(observations) == 109, f"expected 109 observations, got {len(observations)}"
    source_ids = [r["source_id"] for r in sources]
    observation_ids = [r["observation_id"] for r in observations]
    assert len(source_ids) == len(set(source_ids)), "duplicate source_id"
    assert len(observation_ids) == len(set(observation_ids)), "duplicate observation_id"
    assert all(r["source_id"] in source_ids for r in observations), "unknown source_id"
    assert all(r["review_status"] == REVIEW for r in [*sources, *observations]), "unreviewed rows not clearly marked"
    assert all(r["landing_url"] for r in sources), "empty landing URL"
    assert all(r["direct_url"] for r in sources), "missing direct_url status"
    print(f"Catalog structure OK: {len(sources)} sources, {len(observations)} observations; provenance still requires manual audit")


if __name__ == "__main__":
    main()
