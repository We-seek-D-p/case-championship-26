"""TASK-02: local evidence only; Python 3.14, uv run python scripts/rank_cities.py.

Outputs include the report. Empty cells remain unknown. Rank envelopes are
adversarial bounds under missing criteria, not statistical confidence intervals.
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cities'
FIG = ROOT / 'analysis/figures'
WEIGHT = .75
CAP = 6_000_000  # Policy scale, not an observed maximum or a traffic forecast.
CITIES = {
    'Омск': 'Омск', 'Уфа': 'Уфа', 'Тюмень': 'Тюмень (Рощино)',
    'Красноярск': 'Красноярск', 'Саратов': 'Саратов (Гагарин)',
    'Оренбург': 'Оренбург', 'Самара': 'Самара (Курумоч)', 'Казань': 'Казань',
    'Нижний Новгород': 'Нижний Новгород', 'Минеральные Воды': 'Минеральные Воды',
}
QUAL = {'reported': 'опубликованное значение', 'greater_than': 'более',
        'approximately': 'около', 'almost': 'почти', 'at_least': 'не менее'}


def read(name):
    path = f'data/processed/core/{name}.csv'
    with (ROOT / path).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames  # Consume header before recording physical row starts.
        rows = []
        while True:
            line = reader.line_num + 1
            r = next(reader, None)
            if r is None:
                break
            rows.append(dict(r, core_file=path, core_row=str(line)))
        return rows


def write_csv(name, rows):
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with (OUT / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def ref(r):
    return (f"{r['source_id']}: {r['source_file']}:{r['source_row']}; "
            f"{r['source_locator']} (core:{r['core_row']})")


def num(x, digits=2):
    return '—' if x is None else f'{x:.{digits}f}'


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '|' + '|'.join('---' for _ in headers) + '|'] +
                     ['| ' + ' | '.join(str(v).replace('|', '/') for v in row) + ' |' for row in rows])


def weighted_score(size, growth, weight):
    coverage = weight + (1 - weight if growth is not None else 0)
    numerator = weight * size + ((1 - weight) * growth if growth is not None else 0)
    return (numerator / coverage if coverage else None), coverage


def calculate_ranking(data, *, size_weight=WEIGHT, passenger_cap=CAP,
                      growth_min=-10, growth_max=10, city_overrides=None):
    """Use the same scoring rules for official tables and one-off scenarios."""
    settings = (size_weight, passenger_cap, growth_min, growth_max)
    if any(type(value) not in (int, float) or not math.isfinite(value) for value in settings):
        raise ValueError('Веса и границы шкал должны быть конечными числами.')
    if not 0 <= size_weight <= 1 or passenger_cap <= 0 or growth_min >= growth_max:
        raise ValueError('Вес размера должен быть от 0 до 1, потолок потока больше 0, минимум роста ниже максимума.')
    if not math.isfinite(growth_max - growth_min):
        raise ValueError('Диапазон роста слишком велик.')
    overrides = {} if city_overrides is None else city_overrides
    if not isinstance(overrides, dict) or overrides.keys() - CITIES.keys():
        raise ValueError('city_overrides должен содержать названия городов из списка.')
    airports = data['airports']
    inputs, scores, cities = [], [], []
    for city, airport in CITIES.items():
        ar = [r for r in airports if r['airport'] == airport]
        # Explicit city-to-airport mapping above; no inferred airports for city-only records.
        routes = [r for r in data['current_routes'] if city in (r['origin'], r['destination'])]
        for r in ar + routes + [r for r in data['route_passengers'] if r['origin'] == airport]:
            inputs.append(dict(city=city, input_role='context', **r))
        total = next(r for r in ar if r['period'] == '2025' and r['metric'] == 'passengers'
                     and r['scope'] == 'total' and r['record_kind'] == 'observation')
        assert total['unit'] == 'person'
        growth_row = next((r for r in ar if r['metric'] == 'passengers_change' and
                           r['period'] == '2025' and r['scope'] == 'total' and
                           r['comparison_period'] == '2024' and r['record_kind'] == 'observation'), None)
        previous = next((r for r in ar if r['metric'] == 'passengers' and r['period'] == '2024'
                         and r['scope'] == 'total' and r['record_kind'] == 'observation'), None)
        growth = None
        growth_refs = ''
        if growth_row:
            assert growth_row['unit'] == 'percent' and growth_row['value_qualifier'] == 'reported'
            growth = float(growth_row['value'])
            growth_refs = ref(growth_row)
        elif previous and total['value_qualifier'] == previous['value_qualifier'] == 'reported':
            assert previous['unit'] == 'person'
            growth = (float(total['value']) / float(previous['value']) - 1) * 100
            growth_refs = ref(total) + ' + ' + ref(previous)
        change = overrides.get(city, {})
        if not isinstance(change, dict) or change.keys() - {'passengers', 'growth'}:
            raise ValueError(f'{city}: можно менять только passengers и growth.')
        passengers = float(total['value'])
        qualifier = total['value_qualifier']
        size_refs = ref(total)
        if 'passengers' in change:
            passengers = change['passengers']
            if type(passengers) is not int or passengers < 0:
                raise ValueError(f'{city}: passengers должно быть неотрицательным целым числом.')
            qualifier = 'scenario'
            size_refs = 'Сценарная замена, исходное наблюдение: ' + size_refs
        if 'growth' in change:
            growth = change['growth']
            if growth is not None and (type(growth) not in (int, float)
                                       or not math.isfinite(growth) or growth < -100):
                raise ValueError(f'{city}: growth задаётся в процентах от −100 или null.')
            growth_refs = 'Сценарная замена. Исходное наблюдение: ' + (growth_refs or 'отсутствует')
        size = min(100., passengers / passenger_cap * 100)
        if growth is None:
            growth_score = None
        else:
            bounded_growth = min(growth_max, max(growth_min, growth))
            growth_score = 100 * ((bounded_growth - growth_min) / (growth_max - growth_min))
        point, coverage = weighted_score(size, growth_score, size_weight)
        size_hi = 100. if qualifier == 'greater_than' else size
        known_growth = (1 - size_weight) * growth_score if growth_score is not None else 0
        low = size_weight * size + known_growth
        high = size_weight * size_hi + (known_growth if growth_score is not None else (1 - size_weight) * 100)
        codes = {r[k+'_iata'] for r in routes for k in ('origin', 'destination')
                 if r[k] == city and r[k+'_iata']}
        assert len(codes) <= 1
        limitations = []
        if growth_score is None:
            limitations.append('нет годовой динамики')
            inputs.append(dict(city=city, input_role='growth_missing', metric='passengers_change',
                               period='2025', comparison_period='2024', value='',
                               limitations='Нет сопоставимого общего годового показателя'))
        if qualifier == 'greater_than':
            limitations.append('поток — нижний порог; верх неизвестен')
        limitations.append('нет полной оценки конкуренции и пересадок')
        for criterion, value, score, weight, sources, field in [
            ('size', passengers, size, size_weight, size_refs, 'passengers'),
            ('growth', growth, growth_score, 1 - size_weight, growth_refs, 'growth')]:
            formula = (f'min(100,100*P/{passenger_cap:g})' if criterion == 'size' else
                       f'clip(100*(growth-({growth_min:g}))/({growth_max:g}-({growth_min:g})),0,100)')

            if criterion == 'growth' and (growth_min, growth_max) == (-10, 10):
                formula = 'clip(5*(growth+10),0,100)'
            scores.append(dict(city=city, criterion=criterion, value=value if value is not None else '',
                               unit='person' if criterion == 'size' else 'percent', period='2025',
                               comparison_period='' if criterion == 'size' else '2024',
                               score=score if score is not None else '', weight=weight,
                               status='scenario' if field in change else 'missing' if score is None else 'observed_or_derived',
                               formula=formula,
                               sources=sources, value_qualifier=qualifier if criterion == 'size' else '',
                               basis='published threshold as point' if size_hi != size and criterion == 'size' else 'see report'))
        cities.append(dict(city=city, airport=airport, iata=next(iter(codes), ''),
                           passengers=passengers, qualifier=qualifier,
                           growth=growth, size_score=size, growth_score=growth_score, score=point,
                           coverage=coverage, score_low=low, score_high=high,
                           confidence='низкая: предварительный отбор', limitations='; '.join(limitations),
                           total=total, growth_refs=growth_refs, routes=routes))
    cities.sort(key=lambda c: (c['score'] is None, -(c['score'] or 0), c['city']))
    for rank, c in enumerate(cities, 1):
        c['rank'] = rank if c['score'] is not None else None
        c['new_hub_eligible'] = c['city'] not in ('Казань','Самара','Минеральные Воды')
        c['eligibility_basis'] = ('S10/S11: уже опорный аэропорт Red Wings; расширение не новая база' if not c['new_hub_eligible'] else 'не назван опорным в S11; статус базирования всё равно требует проверки')
        c['best_rank'] = 1 + sum(d['score_low'] > c['score_high'] for d in cities if d is not c)
        c['worst_rank'] = len(cities) - sum(d['score_high'] < c['score_low'] for d in cities if d is not c)
        for w in (.6, .9):
            c[f'score_w{int(w*100)}'], _ = weighted_score(c['size_score'], c['growth_score'], w)
    for w in (60, 90):
        for rank, c in enumerate(sorted(cities, key=lambda c: (-c[f'score_w{w}'], c['city'])), 1):
            c[f'rank_w{w}'] = rank
    # Market context is retained separately; it is not an airport metric.
    market = next(r for r in data['market'] if r['entity'] == 'Red Wings' and
                  r['metric'] == 'passengers' and r['scope'] == 'total' and r['period'] == '2025')
    inputs.append(dict(city='Контекст рынка', input_role='context', **market))
    for airport in ('Иркутск', 'Екатеринбург (Кольцово)'):
        for r in airports:
            if r['airport'] == airport:
                inputs.append(dict(city=airport, input_role='reserve_or_benchmark', **r))
    return inputs, scores, cities, market


def core_city_data():
    return {key: read(key) for key in ('airports', 'route_passengers', 'current_routes', 'market')}


def main():
    assert sys.version_info[:2] == (3, 14), 'Use Python 3.14'
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    data = core_city_data()
    inputs, scores, cities, market = calculate_ranking(data)
    write_csv('city_inputs.csv', inputs)
    write_csv('criteria_scores.csv', scores)
    ranking = [{k: ('' if v is None else v) for k, v in c.items()
                if k not in ('total', 'growth_refs', 'routes')} for c in cities]
    write_csv('city_ranking.csv', ranking)
    charts(cities)
    report(cities, market)
    validate(data, inputs, cities)


def charts(cities):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11})
    names = [c['city'] for c in cities]
    y = np.arange(len(cities))
    def setup(title, xlabel):
        fig, ax = plt.subplots(figsize=(11, 7))
        ax.set_title(title, pad=16)
        ax.set_yticks(y, names)
        ax.set_ylabel('Город-кандидат')
        ax.set_xlabel(xlabel)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=.2)
        ax.set_axisbelow(True)
        return fig, ax
    fig, ax = setup('Общий пассажиропоток аэропортов за 2025 год', 'Млн пассажиров за полный год')
    ax.barh(y, [c['passengers']/1e6 for c in cities], color='#346989')
    for i, c in enumerate(cities):
        ax.text(c['passengers']/1e6+.04, i, ('> ' if c['qualifier']=='greater_than' else '')+f"{c['passengers']/1e6:.3f}", va='center')
    ax.set_xlim(0, 6.1)
    fig.text(.3, .015, '«>» — опубликован нижний порог; точное значение неизвестно.\nИсточник: results/cities/city_ranking.csv; первичные ссылки в city_inputs.csv.', fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1)); fig.savefig(FIG/'airport_passengers.png', dpi=160); plt.close(fig)
    fig, ax = setup('Предварительные баллы и границы при неизвестных данных', 'Баллы из 100; полосы — сценарные границы, не вероятность')
    for i,c in enumerate(cities):
        ax.plot([c['score_low'],c['score_high']], [i,i], color='#a8b7c3', linewidth=7)
        ax.scatter(c['score'], i, color='#b64132', zorder=3)
        ax.text(102,i,f"{c['score']:.1f}",va='center')
    ax.set_xlim(0,110)
    fig.text(.3,.015,'Источник: results/cities/city_ranking.csv; веса 75/25; данные 2025 года.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.97)); fig.savefig(FIG/'city_scores.png', dpi=160); plt.close(fig)
    fig, ax = setup('Два критерия: масштаб рынка и годовая динамика', 'Оценка критерия, 0–100 баллов')
    ax.barh(y-.18, [c['size_score'] for c in cities], height=.34, label='Размер: 75%', color='#346989')
    for i,c in enumerate(cities):
        if c['growth_score'] is not None:
            ax.barh(i+.18,c['growth_score'],height=.34,color='#b76a37')
        else:
            ax.text(2,i+.18,'нет данных',va='center',fontsize=9)
    ax.legend(handles=[Patch(color='#346989',label='Размер: 75%'),
                       Patch(color='#b76a37',label='Динамика: 25%')], loc='lower right')
    ax.set_xlim(0,105)
    fig.text(.3,.015,'Источник: results/cities/criteria_scores.csv; исходные наблюдения 2025/2024.',fontsize=9)
    fig.tight_layout(rect=(0,.05,1,.97)); fig.savefig(FIG/'criteria_comparison.png', dpi=160); plt.close(fig)

def report(cities,market):
    rows=[[c['rank'],c['city'],f"{c['passengers']/1e6:.3f}"+('+' if c['qualifier']=='greater_than' else ''),'—' if c['growth'] is None else f"{c['growth']:.1f}",f"{c['score']:.1f}",f"{c['best_rank']}–{c['worst_rank']}",f"[{c['total']['source_id']}](../data/SOURCE_MANIFEST.md#{c['total']['source_id'].lower()})"] for c in cities]
    text='''# Рейтинг городов

**Общий топ-3 — Казань, Уфа, Красноярск. Для H1 выбираем Уфу.**
Казань уже названа опорным аэропортом Red Wings в [S11](../data/SOURCE_MANIFEST.md#s11).
Самара и Минеральные Воды также присутствуют среди опорных точек/хабов в S10/S11.
После их исключения из отбора новой базы первые три — Уфа, Красноярск, Тюмень.

В лонглисте десять городов с общим потоком за полный 2025 год. Екатеринбург —
существующая база сравнения. Веса: 75% масштабу аэропорта, 25% годовой динамике.
Это выбранный приоритет крупного рынка, а не отраслевой норматив.

'''+table(['Место','Город','Поток 2025, млн','Рост к 2024, %','Баллы','Диапазон места','Источник'],rows)+'''

«+» после потока означает опубликованный нижний порог. Пропуск роста не заменяется нулём.

## Формула

Размер S = min(100; поток /6 млн ×100).
Динамика G = max(0; min(100; 5 ×(рост в процентах +10))).
Итог =0,75S +0,25G. При неизвестном G условный балл равен S, а полный балл
считается в диапазоне от 0,75S до 0,75S +25. Для нижнего порога потока
верхняя граница S равна 100. Это границы неизвестных значений, не вероятностный интервал.

При весе размера 60% лидирует Уфа; при 75% и 90% — Казань.
При 90% Красноярск уступает место в общей тройке Минеральным Водам.
У Красноярска неизвестен рост: его место особенно зависит от правила пропусков.
Рейтинг отбирает город для расчёта H1; он не доказывает наличие пересадочного спроса.

![Пассажиропоток аэропортов](figures/airport_passengers.png)

![Баллы и границы неизвестных значений](figures/city_scores.png)

![Два критерия рейтинга](figures/criteria_comparison.png)

[Критерии и веса](../results/cities/criteria_scores.csv),
[рейтинг и альтернативные веса](../results/cities/city_ranking.csv),
[входы](../results/cities/city_inputs.csv),
[сравнение H1/H2](08-strategy-decision.md).

Расчёт: `uv run --frozen --no-sync python scripts/rank_cities.py`.
'''
    (ROOT/'analysis/06-city-ranking.md').write_text(text,encoding='utf-8')


def validate(data,inputs,cities):
    assert len(cities)==10
    for c in cities:
        assert 0<=c['score']<=100
        assert c['score_low']<=c['score']+1e-9<=c['score_high']+1e-9
        assert c['best_rank']<=c['rank']<=c['worst_rank']
    print('Рейтинг: 10 городов; баллы и границы мест рассчитаны.')


if __name__=='__main__':main()
