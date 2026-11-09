"""Download the original DR-01 sources to data/raw/downloaded/ using only stdlib.

This fetches documents, not 'validates' their claims. Download failures and blocked
websites are reported rather than replaced with invented source files.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/catalog/sources_dr01.csv"
OUTPUT = ROOT / "data/raw/downloaded"
DEFAULT_IDS = ("S03", "S05", "S08", "S11", "S21", "S23", "S44", "S48", "S49", "S50", "S51")
MAX_BYTES = 20 * 1024 * 1024


def extension(kind: str) -> str:
    if kind in {"pdf", "pdf_scan"}:
        return ".pdf"
    if kind in {"csv", "xlsx", "zip", "json"}:
        return "." + kind
    return ".html"


def fetch(row: dict[str, str], timeout: int) -> tuple[str, str, str]:
    url = row["direct_url"]
    kind = row["direct_type"]
    if not url.startswith(("https://", "http://")):
        return ("skipped", "", "direct_url отсутствует")
    name = row["source_id"] + extension(kind)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (RedWingsResearch/1.0)", "Accept": "*/*"})
    try:
        with urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            blob = response.read(MAX_BYTES + 1)
            if len(blob) > MAX_BYTES:
                return ("error", "", "размер файла превышает 20 МиБ")
            if kind in {"pdf", "pdf_scan"} and not blob.startswith(b"%PDF-"):
                return ("error", "", "вместо PDF получен другой ответ (возможно страница защиты)")
            if kind == "xlsx" and not blob.startswith(b"PK"):
                return ("error", "", "вместо XLSX получен другой ответ")
            if not blob:
                return ("error", "", "пустой ответ")
            target = OUTPUT / name
            target.write_bytes(blob)
            return ("downloaded", str(target.relative_to(ROOT)), content_type)
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return ("error", "", f"{type(error).__name__}: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Скачать открытые первоисточники DR-01 без фиктивной верификации")
    parser.add_argument("--all", action="store_true", help="все 71 записи, где указан URL")
    parser.add_argument("--ids", nargs="+", metavar="SOURCE_ID", help="например --ids S21 S48")
    parser.add_argument("--timeout", type=int, default=20, help="тайм-аут одного запроса, секунды")
    parser.add_argument("--list", action="store_true", help="только показать очередь")
    args = parser.parse_args()
    with CATALOG.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    requested = set(args.ids or ([] if args.all else DEFAULT_IDS))
    selected = [row for row in rows if args.all or row["source_id"] in requested]
    unknown = requested - {row["source_id"] for row in selected}
    if unknown:
        parser.error("неизвестные source_id: " + ", ".join(sorted(unknown)))
    if args.list:
        for row in selected:
            print(row["source_id"], row["direct_url"])
        return
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = OUTPUT / "download_manifest.csv"
    successes = errors = 0
    with manifest.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["source_id", "landing_url", "direct_url", "saved_path", "fetched_at_utc", "result", "detail"])
        for row in selected:
            result, path, detail = fetch(row, args.timeout)
            writer.writerow([row["source_id"], row["landing_url"], row["direct_url"], path, datetime.now(timezone.utc).isoformat(), result, detail])
            print(f"{row['source_id']}: {result}: {path or detail}")
            if result == "downloaded":
                successes += 1
            elif result == "error":
                errors += 1
    print(f"Скачано: {successes}; ошибок: {errors}; лог: {manifest}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
