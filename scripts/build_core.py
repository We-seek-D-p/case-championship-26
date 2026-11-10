"""Build TASK-01 facts using local processed CSV only (standard library).

No raw files, network, implicit date expansion, aggregation or model estimates.
Run: uv run python scripts/build_core.py
"""

import csv
import io
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / 'data/processed/core'
AS_OF = '2026-11-10'  # Fixed task reference, never the machine's current date.
COMMON = 'period metric scope value unit value_qualifier record_kind source_id source_locator source_file limitations'.split()
TRACE = 'source_row raw_path source_url original_value original_unit comparison_period reporting_basis source_processed_file'.split()
FIELDS = {
    'airports': ['airport'] + COMMON + TRACE,
    'route_passengers': 'origin destination period passengers unit value_qualifier traffic_type source_id source_locator source_file limitations record_kind'.split() + TRACE,
    'current_routes': 'origin origin_iata destination destination_iata airline flight_number aircraft departure_local arrival_local operating_days validity_period flights_per_week evidence_type record_kind source_id source_locator source_file limitations'.split() + TRACE + 'frequency_basis start_date end_date original_airline'.split(),
    'market': ['entity'] + COMMON + TRACE,
}


def read(path):
    """Check width including surplus/missing cells; retain CSV physical row start."""
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream)
        header = next(reader)
        assert len(header) == len(set(header)), path
        rows = []
        while True:
            start = reader.line_num + 1
            values = next(reader, None)
            if values is None:
                break
            assert len(values) == len(header), (path, start)
            rows.append(dict(zip(header, values), _row=str(start)))
        return rows


def notes(*values):
    return '; '.join(v for v in values if v)


def week_days(days):
    if days == 'ежедневно':
        return '7'
    parts = [v.strip() for v in days.split(',')]
    allowed = set('пн вт ср чт пт сб вс'.split()) | set('1234567')
    return str(len(set(parts))) if parts and all(v in allowed for v in parts) else ''


def evidence(row):
    """Evidence type is not a claim that the route operates at AS_OF."""
    kind = row['record_kind']
    if kind == 'published_schedule':
        return 'published_schedule'
    if kind in {'announced_service', 'plan'}:
        return 'announced_route'
    # Historical requires reported service, not simply an expired announcement.
    if kind in {'reported_service', 'resumed_service'}:
        period = row['period']
        past_snapshot = (
            re.fullmatch(r'as_of_\d{4}-\d{2}-\d{2}', period)
            and period[6:] < AS_OF
        )
        if past_snapshot or period in {
            '2025', '2020-10', 'summer_2026', '2020-09_as_of_2020-10-13',
        }:
            return 'historical_route'
    return 'unknown_status'


def build():
    output = {name: [] for name in FIELDS}
    audit = []
    manifest = {r['source_id']: r for r in read('data/source_manifest.csv')}
    source_ids = set(manifest)
    # Local extraction registries corroborate provenance, never publisher verification.
    for block in ('airports', 'airlines', 'market'):
        path = f'data/processed/{block}/sources.csv'
        rows = read(path)
        assert all(r['source_id'] in source_ids for r in rows), path
        audit.append((path, len(rows), len(rows), 0, 0, 'Метаданные provenance; не факты и не независимая проверка'))
    audit.append(('data/source_manifest.csv', len(manifest), len(manifest), 0, 0, 'Ссылки и издатели; статусы не переинтерпретированы'))

    def base(r, path):
        assert r['source_id'] in source_ids, (path, r['_row'])
        result = {k: r[k] for k in TRACE if k in r}
        result.update(source_id=r['source_id'], source_locator=r['source_locator'],
                      source_file=path, source_row=r['_row'],
                      source_url=r.get('source_url') or manifest[r['source_id']]['landing_url'])
        if 'value' in r:
            result.update(original_value=r['value'], original_unit=r['unit'])
        return result

    def ingest(relative):
        path = 'data/processed/' + relative + '.csv'
        return path, read(path)

    path, rows = ingest('airports/metrics')
    for r in rows:
        item = base(r, path) | {k: r[k] for k in COMMON if k in r}
        if r['metric'] == 'passengers' and r['scope'].startswith('route:'):
            item.update(origin=r['airport'], destination=r['scope'][6:], passengers=r['value'], traffic_type='unspecified',
                        limitations=notes(r['limitations'], 'Перевозки на линии, не конечный O&D; сторона учёта не установлена; город назначения не определяет конкретный аэропорт; пересечения не суммировать'))
            output['route_passengers'].append(item)
        else:
            item.update(airport=r['airport'])
            output['airports'].append(item)
    audit.append((path, len(rows), len(rows), 0, 0, 'Метрики разделены между airports и route_passengers'))

    path, rows = ingest('airports/attributes')
    used_attributes = 0
    for r in rows:
        if r['attribute'] == 'maximum_takeoff_weight':
            used_attributes += 1
            output['airports'].append(base(r, path) | dict(airport=r['airport'], period=r['period'], metric=r['attribute'], scope='airport_attribute', value=r['value'], unit=r['unit'], value_qualifier='reported', record_kind=r['record_kind'], limitations=notes(r['limitations'], 'Единица в извлечении не указана; не приписывать тонны')))
    audit.append((path, len(rows), used_attributes, 0, len(rows)-used_attributes, 'Вес сохранён без единицы; коды, UTC, составные и качественные характеристики неприменимы к числовым метрикам'))
    path, rows = ingest('airports/relations')
    audit.append((path, len(rows), 0, 0, len(rows), 'Качественные упоминания изучены; не дают пассажиров, частот или расписания'))

    path, rows = ingest('flights/scheduled_departures_winter_2026_27')
    seen = set()
    for r in rows:
        key = r['source_id'], r['source_locator']
        assert key not in seen, (path, key)
        seen.add(key)
        output['current_routes'].append(base(r, path) | {k: r[k] for k in ('origin_iata', 'destination_iata', 'airline', 'flight_number', 'aircraft', 'departure_local', 'arrival_local')} | dict(
            origin=r['origin_city'], destination=r['destination_city'], original_airline=r['airline'],
            airline={'RED WINGS': 'Red Wings'}.get(r['airline'], r['airline']),
            operating_days=r['operating_days_as_published'], validity_period=r['validity_as_published'],
            flights_per_week=week_days(r['operating_days_as_published']), frequency_basis='planned_operating_days_full_week',
            evidence_type='published_schedule', record_kind=r['record_kind'],
            limitations='Строка опубликованного расписания, не выполненный рейс; годы границ не установлены; частота — дни выполнения в полной неделе, не средняя фактическая; периоды не объединять'))
    audit.append((path, len(rows), len(rows), 0, 0, 'Единственный импорт S19/S20; исходные schedules повторно не импортируются'))

    path, rows = ingest('airlines/routes')
    for r in rows:
        frequency = r['flights_per_week'] or week_days(r['days'])
        output['current_routes'].append(base(r, path) | {k: r[k] for k in ('origin', 'destination', 'flight_number', 'aircraft', 'record_kind', 'start_date', 'end_date')} | dict(
            airline=r['entity'], original_airline=r['entity'], departure_local=r['departure_time'], arrival_local=r['arrival_time'],
            operating_days=r['days'], validity_period=r['period'], flights_per_week=frequency,
            frequency_basis=('published_planned_flights_per_week' if r['flights_per_week'] else 'planned_operating_days_full_week' if frequency else ''),
            evidence_type=evidence(r), limitations=notes(r['limitations'], 'Свидетельство относится только к опубликованному периоду; выполнение на 2026-11-10 не подтверждено', 'Частота — опубликованный план, не фактические полёты' if frequency else 'Частота не указана')))
    audit.append((path, len(rows), len(rows), 0, 0, 'Сохранены все свидетельства; IATA по городам не подставляются'))

    path, rows = ingest('airlines/metrics')
    for r in rows:
        output['market'].append(base(r, path) | {k: r[k] for k in COMMON if k in r} | dict(entity=r['entity'], limitations=notes(r['limitations'], 'Области, субъекты и стандарты отчётности не суммировать и не согласовывать принудительно')))
    audit.append((path, len(rows), len(rows), 0, 0, 'Все опубликованные метрики, включая контекстные, спецификации, планы и прогноз; типы сохранены'))
    for name in ('S02', 'S03_image13'):
        path, rows = ingest('market/' + name)
        for r in rows:
            rank = r['metric'] == 'airline_rank'
            item = base(r, path) | {k: r[k] for k in ('period', 'metric', 'value', 'unit', 'record_kind')}
            item.update(entity=r['unit'] if rank else 'Аэропорты России' if r['metric'] == 'airport_passengers' else 'Российские авиакомпании',
                        scope=r['segment'] + ('; service_type=' + r['service_type'] if 'service_type' in r else ''),
                        value_qualifier='reported',
                        limitations='Опубликованная точность; исходный масштаб сохранён; сегменты и виды сообщения пересекаются, не суммировать')
            if rank:
                item.update(unit='rank', limitations='Рейтинг перевозчика, не пассажиропоток; исходное unit содержало название перевозчика, перенесённое в entity')
            if r['unit'] == '% к предыдущему году':
                item['limitations'] += '; относительный индекс (100 — уровень предыдущего года), не темп прироста'
            if r['period'] == '2024 к 2023' or 'к 2024' in r['unit']:
                item['comparison_period'] = '2023' if name == 'S02' else '2024'
            output['market'].append(item)
        audit.append((path, len(rows), len(rows), 0, 0, 'Масштабы и единицы сохранены; airline_rank отделён от пассажиров'))
    path, rows = ingest('flights/russia_domestic_flights_2025')
    for r in rows:
        output['market'].append(base(r, path) | dict(entity='Российские авиакомпании', period=r['year'], metric=r['metric'], scope=r['scope'], value=r['reported_count'], unit=r['unit'], value_qualifier=r['qualifier'], record_kind=r['record_kind'], limitations=r['limitations'], original_value=r['reported_count'], original_unit=r['unit']))
    audit.append((path, len(rows), len(rows), 0, 0, 'Общий агрегат и его часть сохранены отдельно'))
    for relative, reason in [('market/S05_pages', 'Извлечённый текст PDF, не нормализованные наблюдения'), ('market/articles', 'Тексты статей; показатели автоматически не угадываются'), ('airlines/fares', 'Рекламные цены исключены условиями TASK-01')]:
        path, rows = ingest(relative)
        audit.append((path, len(rows), 0, len(rows), 0, reason))
    validate(output)
    return output, audit


def validate(output):
    """Small semantic regression checks on the supplied local extracts."""
    sources = {}
    for name, rows in output.items():
        identities = [(r['source_file'], r['source_row']) for r in rows]
        assert len(identities) == len(set(identities)), name
        for r in rows:
            assert r['source_id'] and r['source_locator'] and r['source_row']
            assert (ROOT / r['source_file']).is_file()
            path = r['source_file']
            if path not in sources:
                sources[path] = {s['_row']: s for s in read(path)}
            original = sources[path][r['source_row']]
            for field in ('source_id', 'source_locator', 'record_kind', 'comparison_period', 'reporting_basis'):
                if field in original:
                    assert r.get(field, '') == original[field], (path, r['source_row'], field)
            if 'value' in original:
                assert r.get('passengers', r.get('value')) == original['value']
                assert r['original_unit'] == original['unit']
            if 'period' in original:
                assert r.get('period', r.get('validity_period')) == original['period']
            if 'value_qualifier' in original:
                assert r['value_qualifier'] == original['value_qualifier']
            if 'limitations' in original:
                assert original['limitations'] in r['limitations']
            value = r.get('passengers', r.get('value', ''))
            if value:
                assert Decimal(value).is_finite()
    schedules = [r for r in output['current_routes'] if r['source_id'] in {'S19', 'S20'}]
    assert Counter(r['source_id'] for r in schedules) == {'S19': 475, 'S20': 65}
    assert all(r['evidence_type'] == 'published_schedule' for r in schedules)
    assert schedules[0]['validity_period'] == '26 окт / 23 ноя'
    assert schedules[0]['flights_per_week'] == '1' and schedules[1]['flights_per_week'] == '2'
    routes = output['route_passengers']
    assert all(r['traffic_type'] == 'unspecified' for r in routes)
    assert any(r['origin'] == 'Омск' and r['destination'] == 'Москва' for r in routes)
    assert not any(r['metric'] == 'passengers' and r['scope'].startswith('route:') for r in output['airports'])
    assert all(r['evidence_type'] == 'announced_route' for r in output['current_routes'] if r['record_kind'] in {'announced_service', 'plan'})
    assert all(r['unit'] == 'rank' for r in output['market'] if r['metric'] == 'airline_rank')
    assert {r['period'] for r in output['market'] if r['source_id'] == 'S02'} == {'2023', '2024', '2024 к 2023'}
    rw = [r for r in output['market'] if r['entity'] == 'Red Wings' and r['metric'] == 'passengers' and r['period'] == '2025']
    assert any(r['scope'] == 'total' and r['value'] == '2700000' for r in rw)
    assert any(r['scope'] == 'Russian_aircraft' and r['value_qualifier'] == 'greater_than' for r in rw)


def serialize(name, rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=FIELDS[name], extrasaction='ignore', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def main():
    output, audit = build()
    CORE.mkdir(parents=True, exist_ok=True)
    for name, rows in output.items():
        (CORE / (name + '.csv')).write_bytes(serialize(name, rows))
        parsed = read(str((CORE / (name + '.csv')).relative_to(ROOT)))
        assert len(parsed) == len(rows)
        print(f'{name}.csv: {len(rows)}')
    # Compare complete bytes, without a hash-audit artifact or dependency on raw.
    repeated, repeated_audit = build()
    assert repeated_audit == audit
    for name in output:
        assert (CORE / (name + '.csv')).read_bytes() == serialize(name, repeated[name])
    print('input | total | used | excluded | not_applicable | reason')
    for path, total, used, excluded, na, reason in audit:
        assert total == used + excluded + na
        print(f'{path} | {total} | {used} | {excluded} | {na} | {reason}')
    print('OK: CSV structure, provenance, semantic checks, accounting, repeat bytes')


if __name__ == '__main__':
    main()
