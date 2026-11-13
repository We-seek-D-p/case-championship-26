"""Сценарная экономика мультимодальных B2B-заказов Red Wings.

Запуск из любой директории: python3.14 path/to/calculate.py
Без внешних зависимостей. Не изменяет входные таблицы.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def money(value: str) -> Decimal:
    return Decimal(value or "0")


def save(path: Path, fieldnames: list[str], data: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def calculate_order(row: dict[str, str]) -> dict[str, str]:
    n = int(row["passengers"])
    seats = int(row["vehicle_seats"])
    assert n > 0 and seats >= n, row["order_id"]
    price = money(row["client_price_rub"])
    assert price >= 0
    method = row["price_method"]
    if method == "hourly":
        rate = money(row["rate_rub_hour"])
        hours = money(row["billable_hours"])
        minimum = money(row["min_billable_hours"])
        assert rate >= 0 and hours > 0 and minimum > 0
        vendor = rate * max(hours, minimum)
    elif method == "fixed":
        vendor = money(row["flat_vehicle_quote_rub"])
        assert vendor > 0
    else:
        raise ValueError(f"Unknown price_method: {method}")
    extras = sum((money(row[f]) for f in ("other_transport_rub", "dispatch_rub", "risk_reserve_rub")), Decimal())
    assert extras >= 0
    cost = vendor + extras
    cm = price - cost
    margin = cm / price * 100 if price else Decimal(0)
    return dict(
        order_id=row["order_id"], status="synthetic_scenario",
        passengers=str(n), vehicle_seats=str(seats),
        client_price_rub=f"{price:.2f}", vendor_rub=f"{vendor:.2f}",
        other_costs_rub=f"{extras:.2f}", total_cost_rub=f"{cost:.2f}",
        contribution_rub=f"{cm:.2f}", contribution_per_pax_rub=f"{cm / n:.2f}",
        margin_pct=f"{margin:.2f}",
    )


def calculate_portfolio(row: dict[str, str]) -> dict[str, str]:
    count = int(row["orders_month"])
    cm = money(row["contribution_per_order_rub"])
    fixed = money(row["incremental_fixed_month_rub"])
    assert count >= 0 and fixed >= 0
    monthly_cm = cm * count
    monthly_profit = monthly_cm - fixed
    return dict(
        scenario=row["scenario"], status="synthetic_scenario",
        orders_month=str(count), contribution_per_order_rub=f"{cm:.2f}",
        total_contribution_month_rub=f"{monthly_cm:.2f}",
        incremental_fixed_month_rub=f"{fixed:.2f}",
        result_month_rub=f"{monthly_profit:.2f}",
        result_year_rub=f"{monthly_profit * 12:.2f}",
    )


def main() -> None:
    order_fields = ["order_id", "status", "passengers", "vehicle_seats", "client_price_rub", "vendor_rub", "other_costs_rub", "total_cost_rub", "contribution_rub", "contribution_per_pax_rub", "margin_pct"]
    portfolio_fields = ["scenario", "status", "orders_month", "contribution_per_order_rub", "total_contribution_month_rub", "incremental_fixed_month_rub", "result_month_rub", "result_year_rub"]
    orders = [calculate_order(r) for r in rows(INPUT / "example_orders.csv")]
    portfolio = [calculate_portfolio(r) for r in rows(INPUT / "portfolio_assumptions.csv")]
    save(OUTPUT / "order_economics.csv", order_fields, orders)
    save(OUTPUT / "portfolio_scenarios.csv", portfolio_fields, portfolio)
    for item in orders:
        print(f"{item['order_id']}: CM {item['contribution_rub']} RUB ({item['margin_pct']}%)")
    for item in portfolio:
        print(f"{item['scenario']}: annual result {item['result_year_rub']} RUB")


if __name__ == "__main__":
    main()
