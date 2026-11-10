"""TASK-03A: curated route pool, exact evidence links and coverage (Python 3.14).

Run: uv run --frozen --no-sync python scripts/build_route_candidates.py
Only route_candidates.csv and route_evidence_coverage.png are overwritten.
Selection and priorities are analyst judgments; no demand is estimated.
"""
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from build_core import read, week_days

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/routes/route_candidates.csv'
FIG = ROOT / 'analysis/figures/route_evidence_coverage.png'
AS_OF = '2026-11-10'  # Same interpretation date as TASK-01/02, not a freshness claim.
# Explicit city-level aliases only; original airport names remain in evidence.
ALIASES = {'Екатеринбург (Кольцово)': 'Екатеринбург', 'Самара (Курумоч)': 'Самара',
           'Тюмень (Рощино)': 'Тюмень', 'Саратов (Гагарин)': 'Саратов'}
# origin, destination, H1 hub (empty = H2), reason, specific gap, priority, priority reason.
SELECTION = [
    ('Казань', 'Омск', 'Казань',
     'Есть поток линии; проверка местной опоры восточного плеча Казани и возможного питания пересадок.',
     'Перевозчики, частоты, доля конечных поездок; возможные продолжения через Казань и субсидии.',
     'P1', 'Есть уровень пассажиров; можно проверить отделение местного потока от пересадочного.'),
    ('Казань', 'Саратов', 'Казань',
     'Западное плечо к Казани; есть единственный вылет ЮТэйр, пригодность для регулярного подвоза неизвестна.',
     'Регулярность за пределами единственной даты, уровень пассажиров и конкуренты на всём сезоне.',
     'P1', 'Сначала исключить ошибку: одиночная дата не устанавливает регулярную частоту.'),
    ('Казань', 'Новый Уренгой', 'Казань',
     'Анонс Red Wings даёт предметную северную пару для местного рынка и возможных пересадок через Казань.',
     'Выполнение анонса, сезонность и цель поездок, объём линии, действующее предложение и субсидии.',
     'P2', 'До оценки спроса требуется подтвердить эксплуатацию и сезон программы.'),
    ('Казань', 'Нижневартовск', 'Казань',
     'Второе северное плечо из опубликованной программы Red Wings; проверка местного и стыковочного спроса.',
     'Выполнение, местный O&D, частоты, сезонность, заменяемость другими северными плечами и субсидии.',
     'P2', 'Есть только анонс; нельзя считать дополнительный поток независимым от других плеч.'),
    ('Уфа', 'Екатеринбург', 'Уфа',
     'Связь кандидата с существующей базой; Red Wings и ЮТэйр позволяют исследовать местный рынок и конкуренцию.',
     'O&D, загрузка и ёмкости перевозчиков; наземные альтернативы и дополнительность нового хаба к Екатеринбургу.',
     'P1', 'Сравнение предложения двух перевозчиков проверяет риск перераспределения существующих пассажиров.'),
    ('Уфа', 'Красноярск', 'Уфа',
     'Рост линии в S31 подтверждает обслуженный рынок, но не размер; восточное плечо возможного хаба Уфы.',
     'Абсолютные уровни 2024/2025, перевозчик, календарь и ёмкость; конечные поездки и западные подвозящие пары.',
     'P1', 'Нужно исправить ошибочную атрибуцию S58 и получить знаменатель роста.'),
    ('Красноярск', 'Омск', 'Красноярск',
     'Есть поток линии и сообщение о России; можно проверить местный рынок и питание конкурирующих хабов.',
     'Сторона учёта и месяцы пассажиров, фактическая доля России, конечные поездки и субсидии.',
     'P1', 'Измеренный поток позволяет проверить нишу Red Wings в присутствии перевозчика группы Аэрофлот.'),
    ('Красноярск', 'Иркутск', 'Красноярск',
     'Восточное плечо из летней сети России; проверить местный рынок и возможные продолжения с Урала и из Омска.',
     'Уровень потока, текущие частоты и ёмкости России, O&D и стыковки с западными плечами.',
     'P2', 'Имеется историческое сетевое сообщение без измеренного объёма.'),
    ('Красноярск', 'Челябинск', 'Красноярск',
     'Есть рост линии и сообщение о России; ещё одно западное плечо для проверки конкуренции и местной опоры.',
     'Абсолютные уровни 2024/2025, действующее предложение, местные поездки и конкурирующие стыковки.',
     'P2', 'Процент роста без уровня не показывает размер рынка.'),
    ('Екатеринбург', 'Омск', '',
     'Прямая линия из существующей базы Red Wings; пример расширения существующей сети без нового хаба.',
     'Пассажиры пары, фактическая ёмкость и загрузка, местный O&D, тарифы и субсидии.',
     'P1', 'Есть расписание Red Wings; сравнить рост прямого местного рынка с H1 через Казань/Красноярск.'),
    ('Екатеринбург', 'Саратов', '',
     'Прямая связь базы Red Wings с регионом; в выборке есть оба направления расписания.',
     'Уровень потока, календарные годы графиков, фактическое выполнение, загрузка и субсидии.',
     'P1', 'Два независимо опубликованных направления помогают сверить предложение.'),
    ('Екатеринбург', 'Нижний Новгород', '',
     'Региональная линия Red Wings из базы; город вне топ-3 H1, несколько вариантов расписания.',
     'Уровень и сезонность потока, календарь выполнения, ёмкости всех конкурентов и субсидии.',
     'P2', 'Сетевое свидетельство есть, но измеренного пассажирского рынка нет.'),
    ('Екатеринбург', 'Оренбург', '',
     'Прямая региональная линия из базы Red Wings; позволяет проверить развитие города вне топ-3 H1.',
     'Пассажиры линии, фактическая загрузка, наземные альтернативы, действующие конкуренты и субсидии.',
     'P2', 'Расписание не показывает достаточность местного спроса.'),
    ('Екатеринбург', 'Самара', '',
     'Существующая база и опорный город Red Wings; опубликованы Red Wings и ЮТэйр.',
     'Поток пары, доли перевозчиков, местный O&D, фактические частоты и влияние расширения на существующие рейсы.',
     'P1', 'Можно проверить конкуренцию без предположения о новой базе в Самаре.'),
    ('Екатеринбург', 'Абакан', '',
     'Существующее восточное плечо Red Wings из Екатеринбурга; сравнение с западными прямыми линиями.',
     'Пассажиры, сезонность, местный O&D, фактические ёмкости и условия субсидирования.',
     'P2', 'Есть два варианта графика, нет уровня спроса.'),
    ('Екатеринбург', 'Минеральные Воды', '',
     'Измеренная региональная линия из базы; расписание конкурентов позволяет проверить вход или расширение.',
     'Помесячный O&D, ёмкости и тарифы конкурентов; присутствие Red Wings и доступная ниша не установлены.',
     'P1', 'Одновременно есть пассажиры и расписание других перевозчиков.'),
    ('Самара', 'Минеральные Воды', '',
     'Измеренная пара вне баз: проверить возможность обслуживать самолётом из Екатеринбурга без новой базы.',
     'Перевозчики и частоты; уточнение периода S36, O&D и возврат самолёта/экипажа в Екатеринбург.',
     'P2', 'Поток есть, но способ обслуживания из существующей базы и исходный период требуют проверки.'),
    ('Омск', 'Новосибирск', '',
     'Измеренная пара вне топ-3: проверить прямой местный рынок отдельно от подвоза в существующий хаб конкурента.',
     'Перевозчик и частота, доля конечного Новосибирска, наземная альтернатива; обслуживание из Екатеринбурга.',
     'P1', 'Наибольший из выбранных потоков Омска не доказывает большой местный O&D.'),
]
EVIDENCE_FIELDS = ('passenger_evidence', 'route_evidence', 'relative_change_evidence',
                   'base_access_evidence', 'context_evidence')
CATEGORIES = ['passengers_and_frequency', 'passengers_only', 'frequency_only',
              'single_date_only', 'relative_or_qualitative_only']


def city(value):
    return ALIASES.get(value, value)


def pair(a, b):
    return frozenset((city(a), city(b)))


def single_date(r):
    parts = r['validity_period'].split(' / ')
    return len(parts) == 2 and parts[0] == parts[1]


def has_frequency(routes):
    # A lone departure is not evidence of a recurring weekly service.
    return any(r['flights_per_week'] and not single_date(r) for r in routes)


def coverage(passengers, routes):
    if passengers:
        return CATEGORIES[0] if has_frequency(routes) else CATEGORIES[1]
    if has_frequency(routes):
        return CATEGORIES[2]
    return CATEGORIES[3] if any(single_date(r) for r in routes) else CATEGORIES[4]


def load(relative):
    return [dict(r, evidence_file=relative, evidence_row=r['_row'])
            for r in read(relative)]


def audit_ranking(data):
    ranking = read('results/cities/city_ranking.csv')
    criteria = read('results/cities/criteria_scores.csv')
    for r in ranking:
        ar = [a for a in data['airports'] if a['airport'] == r['airport']]
        total = next(a for a in ar if (a['metric'], a['period'], a['scope']) == ('passengers', '2025', 'total'))
        assert total['unit'] == 'person' and total['record_kind'] == 'observation'
        assert float(total['value']) == float(r['passengers'])
        growth_row = next((a for a in ar if (a['metric'], a['period'], a['scope'], a['comparison_period']) ==
                           ('passengers_change', '2025', 'total', '2024')), None)
        previous = next((a for a in ar if (a['metric'], a['period'], a['scope']) == ('passengers', '2024', 'total')), None)
        growth = float(growth_row['value']) if growth_row else (
            (float(total['value']) / float(previous['value']) - 1) * 100 if previous else None)
        s = min(100, float(total['value']) / 6_000_000 * 100)  # TASK-02 policy scale.
        g = max(0, min(100, 5 * (growth + 10))) if growth is not None else None
        score = s if g is None else .75 * s + .25 * g  # TASK-02 subjective weights.
        assert math.isclose(score, float(r['score']), abs_tol=1e-9)
        c = next(c for c in criteria if c['city'] == r['city'] and c['criterion'] == 'growth')
        assert (c['value'] == '') == (growth is None)
        if growth is not None:
            assert math.isclose(growth, float(c['value']), abs_tol=1e-9)
    assert [r['city'] for r in sorted(ranking, key=lambda r: -float(r['score']))][:3] == ['Казань', 'Уфа', 'Красноярск']
    k = next(r for r in ranking if r['city'] == 'Красноярск')
    print(f"TASK-02 formulas match; Krasnoyarsk with hypothetical G=50: {.75 * float(k['size_score']) + .25 * 50:.5f}")


def build(data, relations):
    result = []
    for n, (a, b, hub, reason, gap, priority, priority_reason) in enumerate(SELECTION, 1):
        key = pair(a, b)
        passengers = [r for r in data['route_passengers'] if pair(r['origin'], r['destination']) == key]
        routes = [r for r in data['current_routes'] if pair(r['origin'], r['destination']) == key]
        changes = [r for r in data['airports'] if r['metric'] == 'passengers_change' and
                   r['scope'].startswith('route:') and pair(r['airport'], r['scope'][6:]) == key]
        # Positioning evidence is context, never evidence of frequency on the target pair.
        access = [r for r in data['current_routes'] if not hub and 'Екатеринбург' not in key and
                  pair(r['origin'], r['destination']) == pair('Екатеринбург', a)]
        context = [r for r in relations if r['source_id'] == ('S11' if hub else 'S09') and
                   r['related_entity'] == (hub or 'Екатеринбург') and
                   r['relation'] == ('hub' if hub else 'new_maintenance_base')]
        groups = dict(zip(EVIDENCE_FIELDS, (passengers, routes, changes, access, context)))
        all_evidence = sum(groups.values(), [])
        result.append(dict(candidate_id=f'R{n:02}', origin_city=a, destination_city=b,
                           hypothesis='H1' if hub else 'H2', hub_candidate=hub,
                           operating_base='' if hub else 'Екатеринбург',
                           network_role='hub_spoke' if hub else ('base_direct' if 'Екатеринбург' in key else 'nonbase_direct'),
                           inclusion_reason=reason, missing_demand_data=gap,
                           research_priority=priority, priority_reason=priority_reason,
                           context_interpretation=(
                               'S11 relation=hub означает опорный аэропорт, не доказанную базу или пересадочный хаб.'
                               if context and hub else
                               'База Екатеринбург принята из ТЗ; S09 подтверждает лишь историческую техническую базу.'
                               if not hub else 'Статус нового базирования и пересадочного хаба не установлен.'),
                           interpretation_date=AS_OF,
                           source_ids=';'.join(sorted({r['source_id'] for r in all_evidence})),
                           has_passengers=bool(passengers), has_frequency=has_frequency(routes),
                           coverage_class=coverage(passengers, routes), **groups))
    return result


def validate(rows):
    keys = [(r['hypothesis'], pair(r['origin_city'], r['destination_city'])) for r in rows]
    assert len(keys) == len(set(keys)), 'Duplicate city pair in a hypothesis'
    originals = {}
    for r in rows:
        key = pair(r['origin_city'], r['destination_city'])
        assert len(key) == 2 and r['hypothesis'] in ('H1', 'H2')
        assert r['passenger_evidence'] or r['route_evidence'] or r['relative_change_evidence']
        for field in EVIDENCE_FIELDS:
            for e in r[field]:
                for path, line in ((e['evidence_file'], e['evidence_row']),
                                   (e.get('source_file', e['evidence_file']), e.get('source_row', e['evidence_row']))):
                    if path not in originals:
                        originals[path] = {s['_row']: s for s in read(path)}
                    original = originals[path][line]
                    assert all(original[k] == e[k] for k in ('source_id', 'source_locator'))
                original = originals[e['evidence_file']][e['evidence_row']]
                assert all(e[k] == v for k, v in original.items())
                if field in ('passenger_evidence', 'route_evidence'):
                    assert pair(e['origin'], e['destination']) == key
                if field == 'relative_change_evidence':
                    assert pair(e['airport'], e['scope'][6:]) == key
                if field == 'passenger_evidence':
                    assert e['unit'] == 'person' and e['period'] and e['record_kind'] == 'observation'
                if field in ('route_evidence', 'base_access_evidence') and e['source_id'] in ('S19', 'S20'):
                    assert e['flights_per_week'] == week_days(e['operating_days'])
        if r['network_role'] == 'nonbase_direct':
            assert r['base_access_evidence'], 'No evidence of access from the existing base'
        assert r['coverage_class'] == coverage(r['passenger_evidence'], r['route_evidence'])


def main():
    assert sys.version_info[:2] == (3, 14), 'Use Python 3.14'
    data = {n: load(f'data/processed/core/{n}.csv') for n in
            ('airports', 'route_passengers', 'current_routes', 'market')}
    relations = load('data/processed/airlines/relations.csv')
    audit_ranking(data)
    rows = build(data, relations)
    validate(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False, separators=(',', ':'))
                         if k in EVIDENCE_FIELDS else v for k, v in r.items()} for r in rows)
    saved = read(str(OUT.relative_to(ROOT)))
    for original, serialized in zip(rows, saved, strict=True):
        assert all(json.loads(serialized[k]) == original[k] for k in EVIDENCE_FIELDS)
    draw(rows)
    for h in ('H1', 'H2'):
        subset = [r for r in rows if r['hypothesis'] == h]
        print(h, 'pairs=', len(subset), 'coverage=', dict(Counter(r['coverage_class'] for r in subset)))
    print('Validated evidence provenance, direction/period preservation, units and coverage; no demand estimates.')


def draw(rows):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11})
    labels = ['Пассажиры и частота', 'Только пассажиры', 'Только частота',
              'Только одиночная дата', 'Только относительные /\nкачественные сведения']
    fig, ax = plt.subplots(figsize=(11, 6.2))
    y = list(range(len(CATEGORIES)))
    for h, shift, color in (('H1', -.18, '#346989'), ('H2', .18, '#b76a37')):
        counts = Counter(r['coverage_class'] for r in rows if r['hypothesis'] == h)
        values = [counts[c] for c in CATEGORIES]
        bars = ax.barh([i + shift for i in y], values, height=.33, color=color, label=h)
        ax.bar_label(bars, padding=4)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(Counter((r['hypothesis'], r['coverage_class']) for r in rows).values()) + 1)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel('Число пар городов; категории не пересекаются')
    totals = Counter(r['hypothesis'] for r in rows)
    ax.set_title(f"Покрытие маршрутного пула: H1 — {totals['H1']} пар, H2 — {totals['H2']} пар", pad=16)
    ax.grid(axis='x', alpha=.2)
    ax.set_axisbelow(True)
    ax.legend(loc='lower right')
    fig.text(.02, .065, 'Частота — опубликованный план на интервале, включая анонсы; не выполнение.\n'
             'Одиночная дата не считается регулярной частотой. Пассажиры — поток линии, не O&D.', fontsize=10)
    fig.text(.02, .015, 'Источник: results/routes/route_candidates.csv; локальная база TASK-01, срез интерпретации 10.11.2026.', fontsize=9)
    fig.tight_layout(rect=(0, .14, 1, 1))
    FIG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG, dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    main()
