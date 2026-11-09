"""Lossless-ish table import from DR-01 Markdown; no external fact verification."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reports/NEW-DR-01-REPORT-RU.md"
OUT = ROOT / "data/catalog"
REVIEW = "report_extracted_not_independently_verified"
REPORT_NAME = "research/reports/NEW-DR-01-REPORT-RU.md"


def table(lines: list[str], key: str) -> tuple[list[str], list[list[str]]]:
    header_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith(f"| {key} |")),
        None,
    )
    if header_idx is None:
        raise ValueError(f"missing Markdown table: {key}")
    headers = [cell.strip() for cell in lines[header_idx].split("|")[1:-1]]
    rows: list[list[str]] = []
    for line in lines[header_idx + 2 :]:
        if not line.strip().startswith("|"):
            break
        row = [cell.strip() for cell in line.split("|")[1:-1]]
        if len(row) != len(headers):
            raise ValueError(f"{key}: expected {len(headers)} columns, got {len(row)}")
        rows.append(row)
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError(f"{key}: duplicate IDs")
    return headers, rows


def export(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow([*headers, "review_status", "report_file"])
        writer.writerows([*row, REVIEW, REPORT_NAME] for row in rows)


def main() -> None:
    lines = REPORT.read_text(encoding="utf-8").splitlines()
    sh, sr = table(lines, "source_id")
    oh, od = table(lines, "observation_id")
    if len(sr) != 71 or len(od) != 109:
        raise ValueError(f"unexpected report table sizes: {len(sr)} sources, {len(od)} observations")
    ids = {row[sh.index("source_id")] for row in sr}
    if any(row[oh.index("source_id")] not in ids for row in od):
        raise ValueError("observation with unknown source_id")
    OUT.mkdir(parents=True, exist_ok=True)
    export(OUT / "sources_dr01.csv", sh, sr)
    export(OUT / "observations_dr01.csv", oh, od)
    print(f"Imported {len(sr)} source records and {len(od)} observations (NOT independently verified)")


if __name__ == "__main__":
    main()
