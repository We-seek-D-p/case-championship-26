from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
BASELINE = {
    "baseline_version": "RW-S0-2026-11-08-P0-v2-sourced",
    "baseline_status": "partial",
}
VARIANTS = ("без_новой_базы", "новая_база")
ALL_VARIANTS = (*VARIANTS, "усиление_казани")
READINESS = ("aircraft", "airport", "crew_and_maintenance", "schedule_and_sales")
CASES = ("базовый", "осторожный")
COSTS = (
    "рейсы", "обслуживание_пассажиров", "перегоны", "база_и_персонал",
    "парк_и_резерв", "вытеснение_других_рейсов", "налоги_и_оборотные_средства",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows, field):
    result = {row[field]: row for row in rows}
    require(len(result) == len(rows), f"Повторяется ключ {field}")
    return result


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path, rows):
    rows = [{**BASELINE, **row} for row in rows]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def instant(value):
    result = datetime.fromisoformat(value)
    require(result.tzinfo is not None, f"Укажите смещение от всемирного времени: {value}")
    require(result.second == 0 and result.microsecond == 0, f"Укажите время с точностью до минуты: {value}")
    return result.astimezone(timezone.utc)


def local_instant(value, airport, zones):
    result = instant(value)
    require(
        result.astimezone(ZoneInfo(zones[airport])).utcoffset()
        == datetime.fromisoformat(value).utcoffset(),
        f"Неверное местное время аэропорта {airport}: {value}",
    )
    return result


def minutes(start, end):
    return int((end - start).total_seconds() // 60)


def check_schedule(flights, planes, zones, turns, daily_limit, day_zone):
    indexed = unique(flights, "id")
    fleet = unique(planes, "id")
    allocations = defaultdict(list)
    per_day = Counter()
    report = []
    for leg in indexed.values():
        start = local_instant(leg["departure"], leg["origin"], zones)
        end = local_instant(leg["arrival"], leg["destination"], zones)
        require(start < end and leg["origin"] != leg["destination"], f"Некорректный перелёт {leg['id']}")
        require(isinstance(leg["carrier"], str) and leg["carrier"].strip(), f"Не указан перевозчик {leg['id']}")
        require(leg.get("seats") is None or type(leg["seats"]) is int and leg["seats"] >= 0, f"Неверная ёмкость: {leg['id']}")
        if leg["tail"] is not None:
            plane = fleet[leg["tail"]]
            require(leg["carrier"] == "Red Wings" and not plane["reserved"], f"Борт недоступен: {leg['id']}")
            require(leg["type"] == plane["type"], f"Неверный тип борта: {leg['id']}")
            require(instant(plane["from"]) <= start < end <= instant(plane["to"]), f"Вылет вне окна борта: {leg['id']}")
            day = start.astimezone(ZoneInfo(day_zone)).date().isoformat()
            per_day[(leg["tail"], day)] += minutes(start, end)
            allocations[leg["tail"]].append((start, end, leg))
        report.append({**leg, "block_minutes": minutes(start, end)})
    elapsed = 0
    for tail, assignments in allocations.items():
        assignments.sort(key=lambda entry: entry[0])
        plane = fleet[tail]
        airport = plane["origin"]
        ready = instant(plane["from"])
        for start, end, leg in assignments:
            require(airport == leg["origin"] and ready <= start, f"Разрыв или пересечение ротации: {leg['id']}")
            turn = turns[leg["destination"]]
            require(type(turn) is int and turn >= 0, f"Неверный норматив разворота: {leg['destination']}")
            ready = end + timedelta(minutes=turn)
            airport = leg["destination"]
        require(airport == plane["destination"], f"Борт {tail} не закончил в нужном аэропорту")
        elapsed += minutes(assignments[0][0], assignments[-1][1])
    if daily_limit is not None:
        require(all(used <= daily_limit for used in per_day.values()), "Превышен суточный предел полётных минут")
    return report, {
        "used_tails": len(allocations),
        "reserved_tails": sum(plane["reserved"] for plane in planes),
        "block_minutes": sum(per_day.values()),
        "rotation_span_minutes": elapsed,
        "resource_by_tail_day": [
            {"tail": tail, "day": day, "block_minutes": count}
            for (tail, day), count in sorted(per_day.items())
        ],
    }


def inspect_path(path, flights, rules):
    legs = [flights[key] for key in path["legs"]]
    require(len(legs) in (1, 2) and len(set(path["legs"])) == len(legs), "Нужен прямой путь или одна пересадка")
    require((legs[0]["origin"], legs[-1]["destination"]) == (path["origin"], path["destination"]), "Неверная пара концов пути")
    if len(legs) == 1:
        return None, "прямой"
    inbound, outbound = legs
    airport = inbound["destination"]
    require(airport == outbound["origin"], "Пересадка между разными аэропортами")
    wait = minutes(instant(inbound["arrival"]), instant(outbound["departure"]))
    if wait <= 0:
        return wait, "не_стыкуется_по_времени"
    rule = rules.get(airport)
    if rule is None or rule.get("protected_ticket") is not True:
        return wait, "билет_и_правила_не_подтверждены"
    if [inbound["carrier"], outbound["carrier"]] not in rule["carrier_pairs"]:
        return wait, "билет_для_пары_перевозчиков_не_подтверждён"
    if not rule["min_minutes"] <= wait <= rule["max_minutes"]:
        return wait, "за_пределами_окна"
    return wait, "разрешён_в_рамках_входа"


def allocate_sales(paths, flights, rules):
    indexed = unique(flights, "id")
    unique(paths, "id")
    require(len({(p["origin"], p["destination"], tuple(p["legs"])) for p in paths}) == len(paths),
            "Один продаваемый путь указан несколько раз")
    loads = Counter()
    journeys = boardings = 0
    revenue = Decimal(0)
    for path in paths:
        _, status = inspect_path(path, indexed, rules)
        count, fare = path["passengers"], path["net_ticket_rub"]
        require(status in ("прямой", "разрешён_в_рамках_входа"), f"Продажа недопустима: {path['id']}")
        require(type(count) is int and count >= 0, "Число поездок должно быть целым и неотрицательным")
        require(fare is not None and decimal(fare) >= 0, "Нет чистой суммы билета перевозчика")
        own_legs = [key for key in path["legs"] if indexed[key]["carrier"] == "Red Wings"]
        require(own_legs, "В продаже отсутствует собственный перелёт")
        for key in path["legs"]:
            require(indexed[key].get("seats") is not None, f"Не задана ёмкость или квота: {key}")
            loads[key] += count
            require(loads[key] <= indexed[key]["seats"], f"Не хватает кресел или квоты: {key}")
        journeys += count
        boardings += count * len(own_legs)
        revenue += count * decimal(fare)
    return {"journeys": journeys, "own_boardings": boardings, "net_ticket_rub": str(revenue), "loads": dict(loads)}


def decimal(value):
    result = Decimal(str(value))
    require(result.is_finite(), "Ожидается конечное число")
    return result


def support_cash(value, allowed):
    require(allowed in (None, "неизвестна", "исключена_из_расчёта", "подтверждена"), "Неизвестный статус субсидии")
    if value is None:
        return Decimal(0) if allowed == "исключена_из_расчёта" else None
    require(allowed == "подтверждена" and decimal(value) >= 0, "Субсидия должна быть отдельно подтверждена")
    return decimal(value)


def economics(annual, initial, discount):
    """Пустой вход блокирует зависимый результат, в том числе итог за весь горизонт."""
    require(annual and all(row["year"] == annual[0]["year"] + i for i, row in enumerate(annual)),
            "Нужен непрерывный ряд лет по порядку")
    require(discount is None or decimal(discount) >= 0, "Ставка дисконтирования должна быть неотрицательной")
    require(initial is None or decimal(initial) >= 0, "Стартовые затраты должны быть неотрицательными")
    rows = []
    for row in annual:
        gross = row.get("new_ticket_revenue")
        lost = row.get("lost_ticket_revenue")
        avoided = row.get("avoided_costs")
        extra = [row.get("extra_costs", {}).get(key) for key in COSTS]
        support = support_cash(row.get("support"), row.get("support_status"))
        require(all(value is None or decimal(value) >= 0 for value in (gross, lost, avoided)),
                "Выручку и экономию вводят положительными величинами")
        require(all(value is None or decimal(value) >= 0 for key, value in zip(COSTS, extra)
                    if key != "налоги_и_оборотные_средства"), "Расходы вводят положительными величинами")
        net = None if gross is None or lost is None else decimal(gross) - decimal(lost)
        operating = None if net is None or None in [avoided, *extra] else net + decimal(avoided) - sum(map(decimal, extra))
        cash = None if operating is None or support is None else operating + support
        base_boardings, change, base_market, market_change = (
            row.get(key) for key in ("base_boardings", "net_new_boardings", "base_market", "net_market_change")
        )
        market = None
        if None not in [base_boardings, change, base_market, market_change]:
            before_company, after_company = base_boardings, base_boardings + change
            before_market, after_market = base_market, base_market + market_change
            require(0 <= before_company <= before_market and 0 <= after_company <= after_market
                    and before_market > 0 and after_market > 0, "Несогласованные показатели доли рынка")
            market = 100 * (decimal(after_company) / decimal(after_market) - decimal(before_company) / decimal(before_market))
        rows.append({"year": row["year"], "gross_ticket_revenue_rub": gross, "net_ticket_revenue_rub": net,
                     "own_net_boardings": change, "market_share_change_pp": market,
                     "cash_without_support_rub": operating, "support_in_calculation_rub": support, "cash_rub": cash})
    npv = payback_year = None
    payback_status = "нет_входов"
    if initial is not None and all(row["cash_rub"] is not None for row in rows):
        cumulative = -decimal(initial)
        if discount is not None:
            npv = cumulative + sum(row["cash_rub"] / (1 + decimal(discount)) ** i for i, row in enumerate(rows, 1))
        balances = []
        for row in rows:
            cumulative += row["cash_rub"]
            balances.append(cumulative)
        payback_year = next((row["year"] for i, row in enumerate(rows) if min(balances[i:]) >= 0), None)
        payback_status = "до_конца_горизонта" if payback_year is not None else "за_горизонтом"
        if decimal(initial) == 0 and min(balances) >= 0:
            payback_year, payback_status = None, "стартовые_затраты_отсутствуют"
    return {"annual": rows, "npv_rub": npv, "payback_year": payback_year, "payback_status": payback_status}


def pilot():
    spec = read_json(ROOT / "inputs/pilot.json")
    flights = unique(spec["flights"], "id")
    published, = [plan for plan in spec["plans"] if plan["change"] == "наблюдение"]
    baseline_minutes = sum(
        minutes(instant(leg["departure"]), instant(leg["arrival"]))
        for key in published["flights"] if (leg := flights[key])["carrier"] == "Red Wings"
    )
    schedule_rows, resource_rows, connection_rows = [], [], []
    for plan in spec["plans"]:
        chosen = [flights[key] for key in plan["flights"]]
        report, resource = check_schedule(chosen, plan["planes"], spec["zones"],
                                          spec["turn_minutes"], None, "Asia/Yekaterinburg")
        observations = [leg for leg in chosen if leg["carrier"] == "Red Wings"]
        weekly_directions = Counter((leg["origin"], leg["destination"]) for leg in observations)
        # Считаем по неделе вылета, по каждому направлению отдельно.
        resource_rows.append({
            "вариант": plan["name"], "неделя": spec["week"], "свой_Екатеринбург_Омск": weekly_directions["Кольцово", "Центральный"],
            "свой_Омск_Екатеринбург": weekly_directions["Центральный", "Кольцово"],
            "бортов_назначено_в_проверке": resource["used_tails"],
            "полётные_минуты_проверенного_оборота": resource["block_minutes"] if resource["used_tails"] else None,
            "от_первого_вылета_до_посадки_проверенного_оборота_минут": resource["rotation_span_minutes"] if resource["used_tails"] else None,
            "прирост_полётных_минут_внутри_примера": (
                sum(leg["block_minutes"] for leg in report if leg["carrier"] == "Red Wings") - baseline_minutes
            ),
            "резерв_переход_борта_допуски": "не проверены", "допуск_в_проект": "нет",
        })
        for leg in report:
            schedule_rows.append({"вариант": plan["name"], "рейс": leg["id"], "перевозчик": leg["carrier"],
                                  "откуда": leg["origin"], "куда": leg["destination"], "вылет_местный": leg["departure"],
                                  "посадка_местная": leg["arrival"], "время_минут": leg["block_minutes"],
                                  "борт_примера": leg["tail"], "основание": leg["source"]})
        path = {"origin": "Толмачёво", "destination": "Кольцово", "legs": ["Сибирь-5345", plan["connection_leg"]]}
        wait, status = inspect_path(path, unique(chosen, "id"), {})
        connection_rows.append({"вариант": plan["name"], "путь": "Новосибирск — Омск — Екатеринбург",
                                "ожидание_минут": wait, "путь_в_продаже": status, "пассажиров_не_посчитано": "нет данных",
                                "основание": "С01 и календарная проверка"})
    return schedule_rows, resource_rows, connection_rows


def earliest_service(readiness):
    dates = [readiness.get(key) for key in READINESS]
    known = [date.fromisoformat(value) for value in dates if value is not None]
    return max(known).isoformat() if len(known) == len(dates) else None


def run_plan(spec):
    require(spec["baseline_version"] == BASELINE["baseline_version"], "Неверная версия основы")
    require(spec["baseline_status"] == BASELINE["baseline_status"], "Для поставленной основы разрешён только частичный статус")
    plans = unique(spec["plans"], "variant")
    require(set(VARIANTS) <= set(plans) <= set(ALL_VARIANTS), "Нужны оба варианта кейса, Казань добавляется отдельно")
    outputs = []
    common_metrics = {}
    for variant in ALL_VARIANTS:
        if variant not in plans:
            continue
        plan = plans[variant]
        require({row["case"] for row in plan["cases"]} == set(CASES) and len(plan["cases"]) == len(CASES),
                "Нужны базовый и осторожный расчёты")
        require(bool(plan["flights"]), "Нет календаря для варианта")
        require(all(leg.get("source") for leg in plan["flights"]), "Для перелётов нужны источник или обозначенное допущение")
        # Для замены старых рейсов передаётся полный проверяемый срез с назначениями и новыми рейсами.
        require(all(leg["carrier"] != "Red Wings" or leg["tail"] is not None for leg in plan["flights"]),
                "Собственный рейс должен быть назначен на борт")
        report, resource = check_schedule(plan["flights"], spec["planes"], spec["zones"], spec["turn_minutes"],
                                          spec["daily_limit"], spec["day_zone"])
        for case in plan["cases"]:
            market_base = [(row["year"], row.get("base_boardings"), row.get("base_market")) for row in case["annual"]]
            require(common_metrics.setdefault(case["case"], market_base) == market_base, "Разная основа доли рынка у вариантов")
            outputs.append({
                "variant": variant, "case": case["case"], "resource": resource,
                "calendar_sales": allocate_sales(case["sales"], report, spec["connection_rules"]) if case["sales"] is not None else None,
                **economics(case["annual"], plan["initial_rub"], spec["discount"]),
            })
            if "readiness" in case:
                outputs[-1]["earliest_service_date"] = earliest_service(case["readiness"])
    horizons = {tuple(row["year"] for row in output["annual"]) for output in outputs}
    require(len(horizons) == 1, "Горизонт расчёта у вариантов и сценариев различается")
    return {**BASELINE, "победитель": None, "состояние": "условный_расчёт_проверить_источники", "outputs": outputs}


def audit_old_model():
    source = ROOT / "inputs/IW_reference"
    checksums = read_json(source / "checksums.json")
    with tempfile.TemporaryDirectory() as directory:
        scratch = Path(directory)
        for name in ("model.py", "routes.csv"):
            shutil.copyfile(source / name, scratch / name)
        subprocess.run([sys.executable, str(scratch / "model.py")], check=True, capture_output=True)
        for name, expected in checksums.items():
            require(hashlib.sha256((scratch / name).read_bytes()).hexdigest() == expected,
                    f"Изменился результат исходного расчёта: {name}")
        old = read_csv(scratch / "Сравнение_сценариев.csv")
    rows = []
    for case in ("Базовый", "Осторожный"):
        direct, hub = [row for row in old if row["Сценарий"] == case]
        passengers = "Пассажиры_на_новых_рейсах_модель"
        gross = "Валовая_выручка_новых_рейсов_руб"
        kept = "Чистая_дополнительная_выручка_до_затрат_руб"
        keep_pct = "Удержание_после_каннибализации_допущение"
        require(direct[passengers] == hub[passengers] and direct[gross] == hub[gross], "Исходная модель поменялась")
        rows.append({
            "сценарий_друга": case,
            "посадок_на_новых_рейсах_в_каждом_варианте": int(direct[passengers]),
            "валовая_выручка_в_каждом_варианте_руб": int(direct[gross]),
            "сохранённая_доля_без_новой_базы": direct[keep_pct],
            "сохранённая_доля_с_новой_базой": hub[keep_pct],
            "разница_посадок_от_поправки": int(direct["Чистый_прирост_пассажиров_модель"]) - int(hub["Чистый_прирост_пассажиров_модель"]),
            "разница_выручки_от_поправки_руб": int(direct[kept]) - int(hub[kept]),
            "изменение_разницы_выручки_на_один_пп_поправки_руб": int(direct[gross]) // 100,
            "разница_выручки_при_одинаковой_поправке_руб": 0,
            "назначение": "чувствительность старых допущений, без затрат и без прогноза",
        })
    return rows


def reference_sensitivity():
    references = unique(read_csv(ROOT / "inputs/reference_values.csv"), "идентификатор")
    amounts = {key: decimal(row["значение"]) for key, row in references.items()}
    return [
        {"что_проверено": "историческая доля по формуле кейса", "значение": round(100 * amounts["Б01"] / amounts["Б02"], 4),
         "единица": "процент", "основания": "Б01 Б02", "граница_применения": "2025, число перевозчика округлено"},
        {"что_проверено": "прирост для 0,01 процентного пункта", "значение": amounts["Б02"] / 10_000,
         "единица": "пассажирских перевозок", "основания": "Б02", "граница_применения": "только при фиксированном размере рынка 2025"},
        {"что_проверено": "прирост для 0,10 процентного пункта", "значение": amounts["Б02"] / 1_000,
         "единица": "пассажирских перевозок", "основания": "Б02", "граница_применения": "только при фиксированном размере рынка 2025"},
        {"что_проверено": "две строки аэропортовых сборов за одно обслуживание борта в Кольцово",
         "значение": amounts["Б03"] + amounts["Б04"], "единица": "рублей за тонну максимальной взлётной массы без НДС",
         "основания": "Б03 Б04", "граница_применения": "опубликованный прейскурант с 15.06.2026, только эти две статьи"},
    ]


def pilot_capacity():
    references = unique(read_csv(ROOT / "inputs/reference_values.csv"), "идентификатор")
    seats = int(references["С04"]["значение"])
    market = decimal(references["Б02"]["значение"])
    rows = []
    for case, rotations, load in (("базовая проверка", 52, Decimal("0.75")),
                                  ("осторожная проверка", 26, Decimal("0.50"))):
        capacity = rotations * 2 * seats
        occupied = int(capacity * load)
        rows.append({
            "проверка": case, "оборотов_за_2028": rotations, "вылетов_в_обе_стороны": rotations * 2,
            "кресел_на_вылет_верхняя_оценка": seats, "кресел_за_год": capacity,
            "доля_занятых_кресел_условие": load, "занятых_кресел_за_год_при_условии": occupied,
            "выручка_на_каждые_1000_руб_за_посадку_до_вычета_перетока_руб": occupied * 1000,
            "верхний_прирост_доли_при_фиксированном_рынке_пп": round(100 * occupied / market, 4),
            "статус": "проверка чувствительности, загрузка и выручка не наблюдались",
        })
    return rows


def verification():
    schedule, resource, connections = pilot()
    example = run_plan(read_json(ROOT / "inputs/plan_template.json"))
    return {
        **BASELINE,
        "календарь": schedule,
        "ресурс": resource,
        "стыковки": connections,
        "проверка_общего_ресурса": example,
        "чувствительность_ёмкости": pilot_capacity(),
    }


def generate():
    source = ROOT.parent / "A"
    require(not read_csv(source / "model_ready_inputs.csv"), "Состав допущенных входов изменился. Проверьте интеграцию.")
    candidates = unique(read_csv(source / "network_candidates.csv"), "candidate_id")
    supports = unique(read_csv(source / "support_points_screening.csv"), "city")
    claims = unique(read_csv(source / "claims.csv"), "claim_id")
    require(all(row["baseline_version"] == BASELINE["baseline_version"] for row in [*candidates.values(), *supports.values()]),
            "Перемешаны версии основы")
    result = ROOT / "results"
    result.mkdir(exist_ok=True)
    write_csv(result / "сравнение_2027_2028.csv", [
        {"вариант": variant, "сценарий": case, "год": year, "пассажиров_прирост": None, "выручка_прирост_руб": None,
         "доля_рынка_прирост_пп": None, "денежный_поток_руб": None, "самолётов": None, "чистая_приведённая_стоимость_руб": None,
         "год_окупаемости": None, "первая_дата_запуска": None, "состояние": "нет допущенных входов для прогноза"}
        for variant in ALL_VARIANTS for case in CASES for year in (2027, 2028)
    ])
    for row in candidates.values():
        require(all(key in claims for key in row["evidence_ids"].split()), f"Потерян источник пары {row['candidate_id']}")
    historical_flows = {
        frozenset(row["entity"].split(" — ")): row["claim_id"]
        for row in claims.values() if row["metric"] == "reported_route_passengers" and row["period"] == "2025"
    }
    write_csv(result / "пары_и_пробелы.csv", [
        {"номер": row["candidate_id"], "откуда": row["origin"], "куда": row["destination"], "вариант": variant,
         "сценарий": case, "своя_частота_наблюдение": row["RW_frequency_per_week_one_direction"],
         "период_своей_частоты": row["RW_frequency_period"], "конкурент": row["competitor"],
         "его_частота_наблюдение": row["competitor_frequency_per_week_one_direction"], "её_период": row["competitor_frequency_period"],
         "источники_наблюдения": row["evidence_ids"], "своя_ссылка": row["RW_source_url"], "ссылка_конкурента": row["competitor_source_url"],
         "пассажиров_на_линии_за_2025": row["historical_leg_passengers_2025"],
         "номер_утверждения_о_линии": historical_flows[frozenset((row["origin"], row["destination"]))] if row["historical_leg_passengers_2025"] else None,
         "ссылка_на_статистику_линии": row["historical_leg_source_url"],
         "рейсов_в_неделю_в_проекте": None, "пассажиров_в_год_в_проекте": None,
         "зачем_проверять": row["notes"], "метод_выбора_частоты": "подобрать оборот из доступных бортов по целевым поездкам",
         "метод_пассажиропотока": "направленный спрос за сезон и выбор пути с ограничением мест",
         "следующий_вход": "календарь, доступные борта, спрос и собственный переток",
         "состояние": "кандидат из А, прогноз не определён"}
        for row in candidates.values() for variant in VARIANTS for case in CASES
    ])
    write_csv(result / "опорные_города.csv", [
        {"город": row["city"], "роль": ("назван зимней опорной точкой" if row["role"] == "winter_support"
                                     else "назван на лето, зимняя роль неизвестна"),
         "выделенный_борт": None, "ссылка": row["role_source_url"],
         "условие_проверки": ("проверить несколько отдельных аэропортов" if row["city"] == "Москва"
                             else "подтвердить ресурс и допустимость для варианта без базы")}
        for row in supports.values()
    ])
    for name, rows in zip(("календарь_примера", "ресурс_примера", "стыковка_примера"), pilot()):
        write_csv(result / f"{name}.csv", rows)
    write_csv(result / "аудит_старых_допущений.csv", audit_old_model())
    write_csv(result / "финансовые_ориентиры.csv", reference_sensitivity())
    write_csv(result / "ёмкость_пилота.csv", pilot_capacity())
    example = run_plan(read_json(ROOT / "inputs/plan_template.json"))
    (result / "пример_общего_ресурса.json").write_text(
        json.dumps(example, default=str, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description="Расчёты Б и С для частичной основы Red Wings")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", type=Path, help="входной файл отдельного расчёта")
    mode.add_argument("--verify", action="store_true", help="повторить проверку из архива без сети")
    args = parser.parse_args()
    if args.verify:
        print(json.dumps(verification(), default=str, ensure_ascii=False, indent=2))
    elif args.plan:
        print(json.dumps(run_plan(read_json(args.plan)), default=str, ensure_ascii=False, indent=2))
    else:
        if not (ROOT.parent / "A").is_dir():
            parser.error("Для проверки из архива укажите --verify")
        generate()


if __name__ == "__main__":
    main()
