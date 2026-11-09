"""Сравнение двух полных сетей на общих, явно условных входах."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from decimal import Decimal as D
from html import escape
from itertools import permutations
from math import asin, ceil, cos, radians, sin, sqrt
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo

from model import COSTS, allocate_sales, check_schedule, economics, instant, minutes, read_csv, read_json, require

HERE = Path(__file__).resolve().parent
TYPE = "SJ-100"
VARIANTS = {"D": "Прямые из Екатеринбурга", "H": "Новая база в Омске"}
DAYS = ("Пн", "Вт", "Ср", "Чт", "Пт")


def distance(a, b):
    x, y, z, w = map(radians, (float(a["latitude"]), float(a["longitude"]),
                                 float(b["latitude"]), float(b["longitude"])))
    return 6371 * 2 * asin(sqrt(sin((x - z) / 2) ** 2 + cos(x) * cos(z) * sin((y - w) / 2) ** 2))


def block(a, b):
    return 5 * ceil((25 + 60 * 1.1 * distance(a, b) / 700) / 5)


def inputs():
    airports = {row["airport"]: row for row in read_csv(HERE / "inputs/network_airports.csv")}
    routes = read_csv(HERE / "inputs/network_routes.csv")
    config = read_json(HERE / "inputs/network_scenarios.json")
    return airports, routes, config


def make_week(routes, airports, config, variant):
    base = routes[0]["base"]
    require(len(routes) == 10 and len({r["airport"] for r in routes}) == 10, "Нужно десять разных пар")
    require(all(r["base"] == base for r in routes), "Сеть должна иметь одну опорную точку")
    zones = {key: row["timezone"] for key, row in airports.items()}
    zone = ZoneInfo(zones[base])
    durations = {r["airport"]: block(airports[base], airports[r["airport"]]) for r in routes}
    ranked = sorted(durations, key=lambda key: (-durations[key], key))
    # Пять пар первой волны, повтор каждой пары во второй волне в другой день.
    groups = list(zip(ranked[::2], ranked[1::2]))
    def longest_day(order):
        return max(durations[a[0]] + durations[b[0]] for a, b in zip(groups, order))
    second = min((p for p in permutations(groups) if all(a != b for a, b in zip(groups, p))),
                 key=longest_day)
    start = datetime(2028, 1, 10, 7, tzinfo=zone)
    end = start + timedelta(days=7)
    planes = [{"id": f"B{i}", "type": TYPE, "origin": base, "destination": base, "from": start.isoformat(),
               "to": end.isoformat(), "reserved": i == 3} for i in range(1, 4)]
    turn = config["turn_min"]
    bank_gap = config["bank_wait_min"] if variant == "H" else turn
    flights, paths = [], []
    accumulated = Counter()

    def add(day, wave, tail, code, departure):
        rotation_id = f"{variant}-{day}-{wave}-{tail}"
        arrival = departure + timedelta(minutes=durations[code])
        back = arrival + timedelta(minutes=turn)
        home = back + timedelta(minutes=durations[code])
        for suffix, origin, dest, out, finish in (("out", base, code, departure, arrival),
                                                  ("in", code, base, back, home)):
            flights.append({"id": f"{rotation_id}-{suffix}", "tail": tail, "type": TYPE, "carrier": "Red Wings",
                            "origin": origin, "destination": dest, "day": DAYS[day], "wave": wave,
                            "departure": out.astimezone(ZoneInfo(zones[origin])).isoformat(),
                            "arrival": finish.astimezone(ZoneInfo(zones[dest])).isoformat(),
                            "seats": config["seats"], "source": "проектная неделя, время по расстоянию"})
        return rotation_id

    for day, (first, late) in enumerate(zip(groups, second)):
        matches = list(zip(first, reversed(late)))
        matches.sort(key=lambda p: -(durations[p[0]] + durations[p[1]]))
        tails = sorted(("B1", "B2"), key=lambda t: (accumulated[t], t))
        morning = start + timedelta(days=day)
        bank = morning + timedelta(minutes=2 * durations[first[0]] + turn)
        evening = bank + timedelta(minutes=bank_gap)
        arriving, leaving = [], []
        for tail, (a, b) in zip(tails, matches):
            begin = bank - timedelta(minutes=2 * durations[a] + turn)
            finish = evening + timedelta(minutes=2 * durations[b] + turn)
            require(minutes(instant(begin.isoformat()), instant(finish.isoformat()))
                    <= config["maximum_daily_aircraft_span_min"], "Слишком длинный день борта")
            arriving.append((a, add(day, 1, tail, a, begin) + "-in"))
            leaving.append((b, add(day, 2, tail, b, evening) + "-out"))
            accumulated[tail] += 2 * (durations[a] + durations[b])
        if variant == "H":
            def viable(pair):
                ((a, _), (b, _)) = pair
                return (distance(airports[a], airports[base]) + distance(airports[base], airports[b])
                        <= 1.65 * distance(airports[a], airports[b]))
            pairing = max((list(zip(arriving, order)) for order in permutations(leaving)),
                          key=lambda pairs: sum(map(viable, pairs)))
            for (a, inbound), (b, outbound) in filter(viable, pairing):
                paths.append({"origin": a, "destination": b, "legs": [inbound, outbound], "id": f"{a}-{b}-{day}"})
    require(max(accumulated.values()) <= config["maximum_weekly_block_min"], "Превышен недельный лимит борта")
    report, resource = check_schedule(flights, planes, zones, dict.fromkeys(airports, turn),
                                      config["maximum_daily_block_min"], zones[base])
    return report, paths, resource, durations, accumulated, planes


def weekly_sales(flights, connections, settings, fare, base, extra_load=0):
    occupied = settings["load_per_leg"] + extra_load
    require(occupied <= flights[0]["seats"], "Спрос превышает ёмкость")
    occupied_by_transfer = Counter()
    paths = []
    for connection in connections:
        amount = settings["connect_per_path"]
        if not amount:
            break
        occupied_by_transfer.update({key: amount for key in connection["legs"]})
        paths.append({**connection, "passengers": amount,
                      "net_ticket_rub": round(fare * D(settings["connect_fare_factor"]))})
    for leg in flights:
        paths.append({"origin": leg["origin"], "destination": leg["destination"], "legs": [leg["id"]],
                      "id": leg["id"], "passengers": occupied - occupied_by_transfer[leg["id"]], "net_ticket_rub": fare})
    rules = {base: {"min_minutes": 60, "max_minutes": 180, "protected_ticket": True,
                    "carrier_pairs": [["Red Wings", "Red Wings"]]}}
    sale = allocate_sales(paths, flights, rules)
    return sale, occupied_by_transfer


def round_money(value):
    return int(round(value))


def calculate(variant, flights, connections, config, settings, fare, airports, extra_load=0):
    base = flights[0]["origin"]
    sale, transfer = weekly_sales(flights, connections, settings, fare, base, extra_load)
    yearly, inputs = [], []
    prep = config[variant]
    first_year = next(year for year in (2027, 2028) if settings[variant][f"weeks_{year}"])
    for year in (2027, 2028):
        weeks = settings[variant][f"weeks_{year}"]
        occupied = sale["own_boardings"] * weeks
        displaced = occupied * settings["own_diversion_percent"] // 100
        gross = int(D(sale["net_ticket_rub"])) * weeks
        lost = displaced * fare
        flying = round_money(sum(row["block_minutes"] for row in flights) * weeks * D(settings["block_hour_cost"]) / 60)
        movement = len(flights) * weeks * settings["departure_cost"]
        fixed = round_money(D(prep["annual_fixed"]) * weeks / 52)
        ferry = 0
        if variant == "H" and year == first_year:
            ferry = 2 * (round_money(D(block(airports["SVX"], airports["OMS"])) * settings["block_hour_cost"] / 60)
                         + settings["departure_cost"])
        costs = dict.fromkeys(COSTS, 0)
        costs.update({"рейсы": flying + movement, "база_и_персонал": fixed, "перегоны": ferry})
        input_row = {"year": year, "new_ticket_revenue": gross, "lost_ticket_revenue": lost, "avoided_costs": 0,
                     "extra_costs": costs, "support_status": "исключена_из_расчёта",
                     "base_boardings": config["base_boardings"], "net_new_boardings": occupied - displaced,
                     "base_market": config["markets"][0], "net_market_change": 0}
        inputs.append(input_row)
        yearly.append({"год": year, "рабочих_недель": weeks, "кресла": len(flights) * weeks * config["seats"],
                       "посадки": occupied, "поездки": sale["journeys"] * weeks, "посадки_со_своих_рейсов": displaced,
                       "чистый_прирост_посадок": occupied - displaced, "выручка_новых_рейсов_руб": gross,
                       "потерянная_выручка_руб": lost, "выручка_прирост_руб": gross - lost,
                       "расходы_без_старта_руб": sum(costs.values()), "перегоны_руб": ferry,
                       "денежный_вклад_до_налогов_руб": gross - lost - sum(costs.values()),
                       **{f"прирост_пп_рынок_{market}": str(round(D(occupied - displaced) * 100 / market, 5))
                          for market in config["markets"]}})
    value = economics(inputs, prep["initial_cost"], config["discount"])
    return yearly, sale, transfer, value


def write(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def make_map(path, airports, routes, deferred):
    points = {code: (80 + (float(a["longitude"]) - 43) * 19, 330 - (float(a["latitude"]) - 55) * 34)
              for code, a in airports.items()}
    x, y = points["SVX"]
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1170" height="530" viewBox="0 0 1170 530" role="img">',
           '<rect width="1170" height="530" fill="#f8fafc"/>',
           '<g font-family="Arial, sans-serif" fill="#172a3a">',
           '<text x="40" y="44" font-size="27" font-weight="700">Выбранная сеть из Екатеринбурга</text>',
           f'<text x="40" y="72" font-size="15">Пар первой очереди — {len(routes) - len(deferred)} · условных — {len(deferred)} · по 2 дополнительных оборота в неделю</text>']
    for route in routes:
        x2, y2 = points[route["airport"]]
        style = 'stroke="#627582" stroke-dasharray="7 6"' if route["airport"] in deferred else 'stroke="#006d77"'
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" {style} stroke-width="3"/>')
    offsets = {"UFA": (-42, 32), "REN": (-35, 28), "KZN": (-26, -10), "GSV": (-20, 27),
               "GOJ": (-36, -14), "SGC": (-18, -14), "OMS": (-23, 29), "SVX": (-45, -20),
               "KEJ": (-30, -12), "BAX": (-18, 28), "ABA": (12, 5)}
    for code in [*offsets]:
        x, y = points[code]
        dx, dy = offsets[code]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{8 if code == "SVX" else 5}" fill="#006d77"/>')
        out.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="16" stroke="#f8fafc" stroke-width="4" paint-order="stroke">{escape(airports[code]["city"])}</text>')
    deferred_names = ", ".join(sorted(airports[code]["city"] for code in deferred))
    out.extend(['<text x="40" y="485" font-size="15">Кольцово — опорная точка. Сплошная линия — первая очередь.</text>',
                f'<text x="40" y="509" font-size="14">Пунктир — {escape(deferred_names)}. Частоты проектные.</text></g></svg>'])
    path.write_text("\n".join(out)+"\n", encoding="utf-8")


def rank_cities(airports):
    scored = []
    for row in read_csv(HERE / "inputs/city_screen.csv"):
        code = row["airport"]
        remote = min(distance(airports["SVX"], airports[code]) / 2000, 1)
        scale = min(int(row["minimum_pax_2025"] or 0) / 2_000_000, 1)
        proof = float(row["published_own_route_strength"])
        score = 50 * proof + 30 * scale + 20 * remote
        scored.append({"город": airports[code]["city"], "аэропорт": code,
                       "опубликованный_минимум_пассажиров_2025": row["minimum_pax_2025"],
                       "охват": "январь–ноябрь, нижняя граница 2025" if code == "IKT" else "2025",
                       "источник_потока": row["pax_source"], "проверяемость_маршрута_0_1": proof,
                       "основание": row["route_evidence"],
                       "расстояние_от_Екатеринбурга_км": round(distance(airports["SVX"], airports[code])),
                       "балл_нижняя_граница": round(score, 2),
                       "балл_верхняя_граница": round(score + (30 if not row["minimum_pax_2025"] else 0), 2),
                       "балл_если_вес_маршрута_45": round(45 * proof + 35 * scale + 20 * remote, 2),
                       "балл_если_вес_маршрута_55": round(55 * proof + 25 * scale + 20 * remote, 2)})
    ordered = sorted(scored, key=lambda row: (-row["балл_нижняя_граница"], row["город"]))
    return [{"порядок_проверки": i, **row} for i, row in enumerate(ordered, 1)]


def build(out):
    airports, routes, config = inputs()
    fare_reference = int(median(int(r["advertised_rub"]) for r in routes if r["advertised_rub"]))
    out.mkdir(parents=True, exist_ok=True)
    summary, routes_out, week_out, transfer_out = [], [], [], []
    plans, values = {}, {}
    for variant in VARIANTS:
        own = [r for r in routes if r["variant"] == variant]
        flights, connections, resource, durations, totals, planes = make_week(own, airports, config, variant)
        plans[variant] = (flights, connections)
        week_out.extend({**row, "вариант": variant} for row in flights)
        transfer_out.extend({"вариант": variant, **p, "пересадка_мин": config["bank_wait_min"]} for p in connections)
        for label, settings in config["cases"].items():
            fare = round(fare_reference * D(settings["fare_factor"]))
            years, sale, allocated, result = calculate(variant, flights, connections, config, settings, fare, airports)
            values[variant, label] = (years, result)
            for row in years:
                summary.append({"сеть": "полная 10" if variant == "D" else "альтернатива Омск",
                                "вариант": VARIANTS[variant], "сценарий": label, **row,
                                "пар": len(own), "оборотов_в_рабочую_неделю": len(flights) // 2,
                                "рабочих_бортов": resource["used_tails"], "резервных_бортов": resource["reserved_tails"],
                                "блок_минут_в_неделю": resource["block_minutes"],
                                "макс_блок_минут_на_борт_в_неделю": max(totals.values()),
                                "разовые_затраты_руб": config[variant]["initial_cost"],
                                "приведённый_вклад_2027_2028_руб": round_money(result["npv_rub"]),
                                "окупаемость_до_конца_2028": result["payback_year"] or result["payback_status"],
                                "статус": "сценарий, рыночные входы не подтверждены"})
            for r in own:
                code, base = r["airport"], r["base"]
                legs = [row for row in flights if code in (row["origin"], row["destination"])]
                require(len(legs) == 4, "Нарушена частота пары")
                occupied = sum(sale["loads"][leg["id"]] for leg in legs)
                transfer_legs = sum(allocated[leg["id"]] for leg in legs)
                hours = sum(leg["block_minutes"] for leg in legs)
                for row in years:
                    weeks = row["рабочих_недель"]
                    # Половина цены сквозного билета относится к каждому из двух плеч.
                    route_revenue = round_money(weeks * ((occupied - transfer_legs) * fare
                                      + D(transfer_legs) * round(fare * D(settings["connect_fare_factor"])) / 2))
                    route_variable = round_money(weeks * (D(hours) * settings["block_hour_cost"] / 60
                                                           + len(legs) * settings["departure_cost"]))
                    route_displaced = occupied * weeks * settings["own_diversion_percent"] // 100
                    routes_out.append({"вариант": VARIANTS[variant], "сценарий": label, "год": row["год"],
                                       "пара": f"{airports[base]['city']} — {airports[code]['city']}",
                                       "аэропорты": f"{base}–{code}", "км_по_прямой": round(distance(airports[base], airports[code])),
                                       "минут_на_перелёт": durations[code], "оборотов_в_рабочую_неделю": 2,
                                       "недель": weeks, "кресел_на_вылет": config["seats"],
                                       "загрузка_условие_процент": settings["load_per_leg"],
                                       "чистый_доход_за_прямую_посадку_сценарий_руб": fare,
                                       "посадки_на_новых_рейсах": occupied * weeks, "в_том_числе_пересадочных": transfer_legs * weeks,
                                       "чистый_прирост_посадок": occupied * weeks - route_displaced,
                                       "выручка_новых_рейсов_руб": route_revenue, "переменные_расходы_руб": route_variable,
                                       "вклад_после_переменных_затрат_и_перетока_руб": route_revenue - route_variable - route_displaced * fare,
                                       "основание_выбора": r["observation"], "первоисточник": r["source_url"],
                                       "метод": "100 кресел × заданная загрузка × 4 вылета × рабочие недели; это сценарий, не прогноз спроса"})
    deferred = {row["аэропорты"].split("–")[1] for row in routes_out if row["год"] == 2028
                and row["вариант"] == VARIANTS["D"] and row["сценарий"] == "базовый"
                and row["вклад_после_переменных_затрат_и_перетока_руб"] <= 0}
    for row in routes_out:
        code = row["аэропорты"].split("–")[1]
        row["этап"] = ("альтернатива Омск" if row["вариант"] == VARIANTS["H"]
                       else "отложено" if code in deferred else "первая очередь")
    first_stage = [leg for leg in plans["D"][0] if not deferred.intersection((leg["origin"], leg["destination"]))]
    make_map(out / "Карта.svg", airports, [route for route in routes if route["variant"] == "D"], deferred)
    stage_results = {}
    stage_resource = {
        "used_tails": len({leg["tail"] for leg in first_stage}),
        "reserved_tails": sum(plane["reserved"] for plane in planes),
        "block_minutes": sum(leg["block_minutes"] for leg in first_stage),
    }
    stage_max_block = max(
        sum(leg["block_minutes"] for leg in first_stage if leg["tail"] == tail)
        for tail in {leg["tail"] for leg in first_stage}
    )
    for label, case in config["cases"].items():
        fare = round(fare_reference * D(case["fare_factor"]))
        years, _, _, value = calculate("D", first_stage, [], config, case, fare, airports)
        stage_results[label] = {"годы": years, "приведённый_вклад_руб": round_money(value["npv_rub"]),
                                "окупаемость": value["payback_year"] or value["payback_status"]}
    for label, stage in stage_results.items():
        for row in stage["годы"]:
            summary.append({
                "сеть": "первая очередь 8",
                "вариант": VARIANTS["D"] + ", первая очередь",
                "сценарий": label,
                **row,
                "пар": len(first_stage) // 4,
                "оборотов_в_рабочую_неделю": len(first_stage) // 2,
                "рабочих_бортов": stage_resource["used_tails"],
                "резервных_бортов": stage_resource["reserved_tails"],
                "блок_минут_в_неделю": stage_resource["block_minutes"],
                "макс_блок_минут_на_борт_в_неделю": stage_max_block,
                "разовые_затраты_руб": config["D"]["initial_cost"],
                "приведённый_вклад_2027_2028_руб": stage["приведённый_вклад_руб"],
                "окупаемость_до_конца_2028": stage["окупаемость"],
                "статус": "сценарий, рыночные входы не подтверждены",
            })
    hub_thresholds = {"полная_сеть": None, "первая_очередь": None}
    settings = config["cases"]["базовый"]
    direct_years, direct_value = values["D", "базовый"]
    stage_base = stage_results["базовый"]
    for occupied in range(settings["load_per_leg"], config["seats"] + 1):
        years, _, _, value = calculate("H", *plans["H"], config, settings, fare_reference, airports,
                                       occupied - settings["load_per_leg"])
        if (hub_thresholds["полная_сеть"] is None and value["npv_rub"] >= direct_value["npv_rub"]
                and years[-1]["чистый_прирост_посадок"] >= direct_years[-1]["чистый_прирост_посадок"]):
            hub_thresholds["полная_сеть"] = occupied
        if (hub_thresholds["первая_очередь"] is None
                and value["npv_rub"] >= stage_base["приведённый_вклад_руб"]
                and years[-1]["чистый_прирост_посадок"] >= stage_base["годы"][-1]["чистый_прирост_посадок"]):
            hub_thresholds["первая_очередь"] = occupied
        if None not in hub_thresholds.values():
            break
    direct_thresholds, stage_thresholds = {}, {}
    for label, case in config["cases"].items():
        fare = round(fare_reference * D(case["fare_factor"]))
        for selected, thresholds in ((plans["D"][0], direct_thresholds), (first_stage, stage_thresholds)):
            for occupied in range(config["seats"] + 1):
                _, _, _, value = calculate("D", selected, [], config, case, fare, airports, occupied - case["load_per_leg"])
                if value["npv_rub"] >= 0:
                    thresholds[label] = occupied
                    break
            else:
                thresholds[label] = None
    write(out / "Сравнение_гипотез.csv", summary)
    write(out / "Маршруты.csv", routes_out)
    write(out / "Расписание_двух_сетей.csv", week_out)
    write(out / "Города.csv", rank_cities(airports))
    if transfer_out:
        write(out / "Пересадки_Омска.csv", transfer_out)
    result = {"медиана_витрины_руб": fare_reference, "порог_загрузки_Омска_процент": hub_thresholds["полная_сеть"],
              "порог_загрузки_Омска_против_первой_очереди": hub_thresholds["первая_очередь"],
              "порог_загрузки_Екатеринбурга_для_неотрицательного_приведённого_вклада": direct_thresholds,
              "порог_загрузки_первой_очереди_для_неотрицательного_приведённого_вклада": stage_thresholds,
              "первая_очередь_пар": len(first_stage) // 4, "отложенные_пары": sorted(deferred),
              "первая_очередь": stage_results,
              "число_путей_Омска_в_проектной_неделе": len(plans["H"][1]), "статус": "условное сравнение"}
    (out / "Порог_смены_решения.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    build(parser.parse_args().out)
