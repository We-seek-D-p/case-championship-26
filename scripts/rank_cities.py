"""TASK-02: local evidence only; Python 3.14, uv run python scripts/rank_cities.py.

Outputs include the report. Empty cells remain unknown. Rank envelopes are
adversarial bounds under missing criteria, not statistical confidence intervals.
"""
import csv
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
        writer = csv.DictWriter(stream, fields)
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


def main():
    assert sys.version_info[:2] == (3, 14), 'Use Python 3.14'
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    data = {k: read(k) for k in ('airports', 'route_passengers', 'current_routes', 'market')}
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
        s = min(100., float(total['value']) / CAP * 100)
        g = None if growth is None else max(0., min(100., (growth + 10) * 5))
        coverage = WEIGHT + (1 - WEIGHT if g is not None else 0)
        point = (WEIGHT * s + ((1-WEIGHT)*g if g is not None else 0)) / coverage
        # Lower/upper here are scenarios for unknown values, never imputed observations.
        s_hi = 100. if total['value_qualifier'] == 'greater_than' else s
        low = WEIGHT * s + ((1-WEIGHT)*g if g is not None else 0)
        high = WEIGHT * s_hi + (1-WEIGHT)*(g if g is not None else 100)
        codes = {r[k+'_iata'] for r in routes for k in ('origin', 'destination')
                 if r[k] == city and r[k+'_iata']}
        assert len(codes) <= 1
        limitations = []
        if g is None:
            limitations.append('нет годовой динамики')
            inputs.append(dict(city=city, input_role='growth_missing', metric='passengers_change',
                               period='2025', comparison_period='2024', value='',
                               limitations='Нет сопоставимого общего годового показателя'))
        if total['value_qualifier'] == 'greater_than':
            limitations.append('поток — нижний порог; верх неизвестен')
        limitations.append('нет полной оценки конкуренции и пересадок')
        for criterion, value, score, weight, sources in [
            ('size', float(total['value']), s, WEIGHT, ref(total)),
            ('growth', growth, g, 1-WEIGHT, growth_refs)]:
            scores.append(dict(city=city, criterion=criterion, value=value if value is not None else '',
                               unit='person' if criterion == 'size' else 'percent', period='2025',
                               comparison_period='' if criterion == 'size' else '2024',
                               score=score if score is not None else '', weight=weight,
                               status='missing' if score is None else 'observed_or_derived',
                               formula='min(100,100*P/6000000)' if criterion == 'size' else 'clip(5*(growth+10),0,100)',
                               sources=sources, value_qualifier=total['value_qualifier'] if criterion == 'size' else '',
                               basis='published threshold as point' if s_hi != s and criterion == 'size' else 'see report'))
        cities.append(dict(city=city, airport=airport, iata=next(iter(codes), ''),
                           passengers=float(total['value']), qualifier=total['value_qualifier'],
                           growth=growth, size_score=s, growth_score=g, score=point,
                           coverage=coverage, score_low=low, score_high=high,
                           confidence='низкая: предварительный отбор', limitations='; '.join(limitations),
                           total=total, growth_refs=growth_refs, routes=routes))
    cities.sort(key=lambda c: (-c['score'], c['city']))
    for rank, c in enumerate(cities, 1):
        c['rank'] = rank
        c['best_rank'] = 1 + sum(d['score_low'] > c['score_high'] for d in cities if d is not c)
        c['worst_rank'] = len(cities) - sum(d['score_high'] < c['score_low'] for d in cities if d is not c)
        for w in (.6, .9):
            c[f'score_w{int(w*100)}'] = (w*c['size_score'] + ((1-w)*c['growth_score'] if c['growth_score'] is not None else 0))/(w+(1-w if c['growth_score'] is not None else 0))
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
    fig.text(.3, .015, '«>» — опубликован нижний порог; точное значение неизвестно.', fontsize=10)
    fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(FIG/'airport_passengers.png', dpi=160); plt.close(fig)
    fig, ax = setup('Предварительные баллы и границы при неизвестных данных', 'Баллы из 100; полосы — сценарные границы, не вероятность')
    for i,c in enumerate(cities):
        ax.plot([c['score_low'],c['score_high']], [i,i], color='#a8b7c3', linewidth=7)
        ax.scatter(c['score'], i, color='#b64132', zorder=3)
        ax.text(102,i,f"{c['score']:.1f}",va='center')
    ax.set_xlim(0,110)
    fig.tight_layout(rect=(0,0,1,.97)); fig.savefig(FIG/'city_scores.png', dpi=160); plt.close(fig)
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
    fig.tight_layout(rect=(0,0,1,.97)); fig.savefig(FIG/'criteria_comparison.png', dpi=160); plt.close(fig)


def report(cities, market):
    candidate_rows = []
    evidence_rows = []
    network_rows = []
    for c in cities:
        r = c['total']
        candidate_rows.append([c['city'], c['airport'] + (' / '+c['iata'] if c['iata'] else ' / код не установлен'),
                               f"{c['passengers']:,.0f}".replace(',',' ') + ' человек; 2025; '+QUAL[c['qualifier']],
                               num(c['growth'])+'%' if c['growth'] is not None else 'нет сопоставимого 2024',
                               ref(r)])
        descriptions = []
        for rw in (True, False):
            route = next((r for r in c['routes'] if (r['airline']=='Red Wings') == rw), None)
            if route:
                descriptions.append(('Red Wings' if rw else 'Другой перевозчик')+f": {route['airline']}, {route['origin']} → {route['destination']}; {route['evidence_type']}; {route['validity_period']}. {ref(route)}")
            else:
                descriptions.append(('Red Wings' if rw else 'Другие перевозчики')+': маршрутного свидетельства в выбранной базе не найдено; присутствие неизвестно')
        evidence_rows.append([c['city'], '<br>'.join(descriptions), c['growth_refs'] or 'Годовая динамика неизвестна'])
        for r in read('airports'):
            if (r['airport'] == c['airport'] and r['period'] == '2025'
                    and r['metric'] == 'destinations' and r['scope'] == 'total'
                    and r['record_kind'] == 'observation'):
                network_rows.append([c['city'], r['value'], ref(r)])
    rank_rows = [[c['rank'],c['city'],num(c['size_score']),num(c['growth_score']),num(c['score']),
                  f"{c['coverage']:.0%}",f"{c['best_rank']}–{c['worst_rank']}",c['limitations']] for c in cities]
    sens = [[c['city'],c['rank_w60'],c['rank'],c['rank_w90']] for c in cities]
    ufa = next(c for c in cities if c['city']=='Уфа')
    text = f'''# TASK-02 — Предварительный рейтинг городов для нового хаба Red Wings

**При выбранных правилах первые три города — {', '.join(c['city'] for c in cities[:3])}.** Это приоритет для дальнейшей проверки, а не доказательство пригодности хаба. Недостающие сведения допускают изменение состава тройки. Дата интерпретации базы — 10 ноября 2026 года; новые данные не загружались.

## 1. Зачем выбираем город

Региональный хаб — аэропорт, где рейсы соединяются так, чтобы пассажир мог удобно пересесть между регионами. База — место размещения самолётов и экипажей; пересадки для неё не обязательны. Большой поток помогает заполнять рейсы местными пассажирами, но не гарантирует удобных стыковок, свободных слотов и прибыльности. Нужны расписание, экономика и спрос между конкретными городами — их здесь не моделируем. Выбор H1/H2 остаётся за пределами задачи.

Red Wings перевезла в 2025 году {float(market['value'])/1e6:.1f} млн человек всего ({ref(market)}). Это масштаб компании, а не доля или спрос отдельного города; в баллы показатель не включён.

## 2. Какие города сравниваем

Взяты все города из аэропортового блока, у которых есть общий фактический поток за полный 2025 год, кроме Екатеринбурга: по условию кейса там уже действует региональный хаб Red Wings. Получилось 10 кандидатов. Это лонглист в пределах доступной базы, а не обзор всех аэропортов России. Название аэропорта оставлено на уровне исходной записи, без дополнения официальными именами по памяти. IATA скопирован только из однозначной строки расписания данного города; для Тюмени код в заданных таблицах не установлен.

{table(['Город','Аэропорт / IATA','Поток, период и точность','Динамика 2025/2024','Источник потока'],candidate_rows)}

«Опубликованное значение» сохраняет точность источника: запись 3 570 000 не гарантирует подсчёт до человека. «Более» — нижний порог. Не восстанавливаем общий поток из суммы внутренних и международных сегментов: опубликованные суммы могут не совпадать с итогом.

Иркутск оставлен в резерве: 3 078 468 человек за январь–сентябрь 2025 года (S32, airports/metrics.csv:79, lines 5-5; точный адрес записи приведён в city_inputs.csv). Девять месяцев не год, умножения на 12/9 нет. Екатеринбург — ориентир существующего хаба: около 8 385 000 человек за 2025 год (S40; полная ссылка в city_inputs.csv). Оба не получают места в рейтинге новых городов.

Подтверждённые маршрутные примеры ниже показывают присутствие на конкретной паре в источнике, а не полную конкуренцию аэропорта. published_schedule — публикация расписания, historical_route — историческое сообщение, announced_route — анонс. Ни один тип сам по себе не подтверждает выполнение на дату анализа. Диапазоны расписаний без года сохранены дословно. Отсутствие записи об авиакомпании не означает её отсутствия.

{table(['Город','Red Wings и конкуренция: примеры свидетельств','Источники годовой динамики'],evidence_rows)}

Для части городов опубликован размер сети за полный 2025 год:

{table(['Город','Направлений, опубликованный итог 2025','Источник'],network_rows)}

Эти итоги показывают уже имеющиеся связи с другими городами. Они не доказывают возможность пересадок: неизвестны частоты и согласованность рейсов. Охват и определение направления у публикаций могут отличаться. Поэтому не переносим значения на остальные города и не используем их как третий критерий. У Омска есть доля перевозок в обход Москвы за 2024 год, но это другой период и не показатель размера сети; она остаётся контекстом во входной таблице.

Все использованные аэропортовые записи и маршрутные свидетельства сохранены в [city_inputs.csv](../results/cities/city_inputs.csv), включая периоды, исходные ограничения, source_id, source_file, source_row, source_locator и физическую строку core. «core:N» в таблицах означает строку соответствующего файла core; файл первичного извлечения указан перед ним.

## 3. Как считаем рейтинг

Размер рынка — главный доступный ориентир для местной загрузки рейсов. Динамика помогает увидеть, расширяется ли рынок, но одно изменение за год не является прогнозом. Веса — аналитическое решение, а не установленные закономерности отрасли.

| Критерий | Вес | Смысл и расчёт | Нормализация и пропуски |
|---|---|---|---|
| Общий поток аэропорта за 2025 год | 75% | Фактический размер обслуженного рынка, P человек | S = min(100, 100 × P / 6 000 000). 6 млн — круглая опорная шкала, не порог успеха. Для «более» берём опубликованный порог только как условную точку; верхняя оценка S допускает 100 |
| Общая годовая динамика 2025 к 2024 | 25% | Опубликованный общий прирост либо 100 × (P2025/P2024 − 1) для двух сопоставимых итогов | G = max(0, min(100, 5 × (g + 10))). −10% даёт 0, отсутствие роста — 50, +10% — 100. Пределы симметричны, выбраны для понятной шкалы |

Сначала используем опубликованную общую годовую динамику. При её отсутствии вычисляем её только из двух полных лет: Омск и Самара. У Самары одинаковые опубликованные округлённые итоги дают 0% **на точности публикации**. Рост международного сегмента не заменяет рост всего аэропорта. Динамика Иркутска за девять месяцев не включена в годовую шкалу.

При двух известных критериях B = 0,75 × S + 0,25 × G. При пропуске G условный балл B = S: известные веса перенормируются на их сумму. Это оценка по доступной части, она не означает нулевого или среднего роста. Покрытие — сумма исходных весов известных критериев: 100% либо 75%. Это полнота двух критериев, а не всей информации о хабе.

Дополнительно считаем нижнюю и верхнюю границы полного балла: неизвестный G может лежать от 0 до 100. Для нижних порогов потока неизвестный S может лежать от рассчитанного порога до 100. Крайние баллы используются исключительно как сценарии, в исходные пропуски не записываются. Лучшее место = 1 + число городов, чей минимальный балл выше максимального балла данного города. Худшее = число кандидатов минус число городов, чей максимальный балл ниже его минимального. Это консервативные границы внутри данных 10 кандидатов, не вероятностные интервалы. Для «более» граница может быть недостижимым пределом, что лишь расширяет диапазон. Округлённым публикациям не назначаем выдуманные интервалы ошибки; границы условны на их точности.

**Пример Уфы:** P = 4 929 715 человек, g = +4%. S = 82,16; G = 70; B = 0,75 × 82,16 + 0,25 × 70 = {ufa['score']:.2f}. Источники — S26 для обеих метрик, точные локаторы приведены выше. Расчёт ведётся без промежуточного округления.

Сеть и конкуренция не превращены в третий балл: расписания подробно покрывают только два аэропорта, а число публикаций зависит от сбора данных. Не считаем записи, направления из выборочных сообщений или число упоминаний перевозчика показателем преимущества. Региональный потенциал рассматриваем как гипотезу по имеющимся парам, без оценки необслуженного спроса. Нет сопоставимых сведений о долях конкурентов, пересадках, зоне охвата и ограничениях инфраструктуры.

## 4. Что показывают данные

![Общий пассажиропоток аэропортов за полный 2025 год, млн человек](figures/airport_passengers.png)

**Размер рынка.** У Казани крупнейший опубликованный годовой итог среди новых кандидатов с известным значением, далее Уфа. Оренбург и Нижний Новгород представлены нижними порогами, поэтому длина их столбца не устанавливает точный размер. Иркутск исключён из диаграммы из-за неполного года. Источники — строки потока из раздела 2, одинаковые с входами расчёта.

![Предварительные баллы и сценарные границы, шкала 0–100](figures/city_scores.png)

**Общая оценка.** Красная точка — условный балл по известным критериям; полоса — границы при неизвестных значениях. Широкие полосы показывают, почему позицию нельзя считать доказанной. У нижних порогов неизвестны и рост, и верх размера. Это не доверительные интервалы статистической модели.

![Раздельные оценки размера и годовой динамики, баллы из 100](figures/criteria_comparison.png)

**Отдельные критерии.** У Уфы выше оценка динамики, у Казани — размера; при базовых весах преимущество размера перевешивает. Минеральные Воды теряют баллы из-за опубликованного снижения общего потока. Пропуски роста подписаны «нет данных», столбцы с нулём для них не строятся. Все три графика программно построены из тех же объектов, которые записываются в CSV; единицы и смысл баллов различаются с исходными пассажирами.

## 5. Итоговый рейтинг

Места упорядочены по условному баллу; при равенстве — по названию города. Все позиции имеют **низкую уверенность для решения об открытии хаба**. Даже полное покрытие двух критериев не закрывает вопрос конкуренции, пересадок и затрат. Места в диапазоне относятся к базовым весам и только этим 10 городам.

{table(['Место','Город','S, баллы','G, баллы','B, баллы','Покрытие','Возможные места','Ограничения'],rank_rows)}

Машиночитаемые результаты: [критерии](../results/cities/criteria_scores.csv), [рейтинг](../results/cities/city_ranking.csv). Пустая ячейка означает неизвестность. Границы не охватывают возвращение Иркутска или добавление других городов, изменение точности публикаций и будущие качественные критерии.

## 6. Топ-3 — предварительный

**Уфа, второе место.** Высокий годовой поток сочетается с опубликованным ростом +4%. Преимущество — размер местного рынка и положительная динамика, обе метрики одного источника S26. Маршрутные примеры подтверждают публикации Red Wings и ЮТэйр на паре с Екатеринбургом (таблица выше), но не полноту сети. Риски — неизвестные доли перевозчиков, способность организовать пересадки и затраты. При уменьшении веса размера до 60% Уфа выходит на первое место. Проверка новых данных других городов тоже может изменить состав тройки.

**Казань, первое место.** Крупнейший опубликованный поток среди точечных годовых итогов кандидатов компенсирует слабый рост +0,3% (S38). Есть расписание Red Wings и ЮТэйр на отдельных парах. Преимущество — масштаб, риск — почти неизменный общий поток: он не доказывает возможность быстро нарастить новые перевозки. Неизвестны пересадочные потоки, ёмкость конкурентов и сезонность. При весе масштаба 90% Казань сохраняет первое место; при весе 60% уступает Уфе.

**Красноярск.** Поток 4 263 566 человек за 2025 год (S31) даёт высокий балл размера; общий годовой рост неизвестен и в условный балл не включён. Это наиболее уязвимая позиция тройки: перенормирование веса оставляет только размер. S31 также содержит 1 395 375 пассажиров у «России» и 857 078 у «Аэрофлота» (source_locator и source_row сохранены в city_inputs.csv), что подтверждает существенное присутствие конкурентов, но не автоматически их долю в доступном для нового хаба спросе. Наблюдения расписаний показывают отдельные пары, а присутствие Red Wings из отсутствия записи не исключается. При слабой общей динамике город может уступить другим кандидатам. Неизвестны фактические пересадки, доступная ниша и условия работы нового перевозчика.

## 7. Проверка устойчивости

Меняем долю размера с 75% до 60% и 90%; остаток отдаём динамике. Это проверка приоритета более крупного рынка против более быстрого роста. Формулы, шкалы и правило пропусков сохраняются.

{table(['Город','Место: размер 60%','Место: размер 75%','Место: размер 90%'],sens)}

При 60% размера тройка — Уфа, Казань, Красноярск. При 75% — Казань, Уфа, Красноярск. При 90% — Казань, Уфа, Минеральные Воды: Красноярск становится четвёртым. **Топ-3 неустойчив даже к изменению весов.** У городов с пропуском динамики условная оценка после перенормирования остаётся равной размеру, а у Минеральных Вод повышение веса размера уменьшает штраф за снижение потока. Это ещё одна причина проверять полноту данных до решения. Диапазоны возможных мест пересекаются, а нижние пороги потока допускают сильный пересмотр позиций. Неизвестный рост Красноярска, Тюмени, Саратова, Оренбурга и Нижнего Новгорода способен изменить состав тройки. Дополнительные критерии сети и конкуренции могут изменить результат ещё сильнее; их веса сейчас не имитируем.

## 8. Что дальше

Следующий этап должен проверить конкретные пары, а не сразу проектировать хаб:

- Уфа — Екатеринбург: в S19 есть Red Wings и ЮТэйр. Нужны календарь фактических выполнений, ёмкости и тарифы конкурентов, местный O&D и доля пересадок, чтобы понять характер конкуренции.
- Казань — Екатеринбург и Казань — Саратов: опубликованные свидетельства S19/S20 позволяют начать проверку действующих связей. Нужны актуальные частоты, помесячные потоки, O&D и расписания; наличие соединения в выборке не доказывает ни свободной ниши, ни нехватки предложения.
- Красноярск — Омск, Красноярск — Уфа: в S31 есть годовая динамика этих линий, а S58 содержит исторические маршрутные сообщения. Нужны уровни потока по тем же периодам, действующие перевозчики, ёмкости и структура пересадок. Проценты роста не заменяют размеры рынка.
- Для проверки альтернативы из Омска: Омск — Новосибирск, 106 309 человек на линии за 2025 год, S23 (точная запись в city_inputs.csv). Нужны конечные O&D, доля пересадок через Новосибирск и распределение по месяцам. Это поток линии с неизвестной стороной учёта, не прогноз спроса новой линии.

Общие недостающие данные: единый годовой ряд всех кандидатов, доли и ёмкости перевозчиков, конечные пункты поездок, фактические выполнения, инфраструктурные ограничения, условия аэропортов и субсидий. В этой задаче спрос, финансы, расписание нового хаба и H1/H2 не рассчитываются.

### Воспроизводимость и проверки

Запуск из корня: `uv run --frozen python scripts/rank_cities.py` (Python 3.14; matplotlib закреплён в uv.lock). Скрипт читает только четыре CSV core и создаёт три таблицы, три PNG и этот отчёт; исходные файлы и исследовательские отчёты не меняет. Он проверяет 10 уникальных городов, общий поток за полный 2025 год и единицы, допустимые типы наблюдений, источники до строки исходного обработанного CSV, пропуски и формулы баллов, веса и границы мест, наличие ссылок на PNG. Проверка повторяемости: повторить запуск и сравнить SHA-256 всех семи результатов. Успешное сообщение скрипта означает выполненные проверки данных; визуальное чтение PNG выполняется отдельно.
'''
    # Exact reserve provenance is generated, never typed from memory.
    irk = next(r for r in read('airports') if r['airport']=='Иркутск' and r['period']=='2025-01/2025-09' and r['scope']=='total' and r['metric']=='passengers')
    text = text.replace('S32, airports/metrics.csv:79, lines 5-5; точный адрес записи приведён в city_inputs.csv', ref(irk))
    (ROOT/'analysis/06-city-ranking.md').write_text(text,encoding='utf-8')


def validate(data, inputs, cities):
    assert len(cities) == len({c['city'] for c in cities}) == 10
    assert abs(WEIGHT + (1-WEIGHT)-1) < 1e-12
    source_cache = {}
    for r in inputs:
        if not r.get('source_file'):
            assert r.get('value','') == ''
            continue
        path = r['source_file']
        if path not in source_cache:
            with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f); source_cache[path]={}
                assert reader.fieldnames
                while True:
                    line=reader.line_num+1
                    row=next(reader,None)
                    if row is None: break
                    source_cache[path][str(line)]=row
        original=source_cache[path][r['source_row']]
        for key in ('source_id','source_locator'):
            assert r[key] == original[key], (path, r['source_row'],key)
        if r.get('original_value'):
            assert r['original_value'] == original.get('value',''), r
    # Recompute from the saved criterion table, not just objects used for charts.
    with (OUT/'criteria_scores.csv').open() as f: saved=list(csv.DictReader(f))
    for row in saved:
        if row['score'] == '':
            assert row['value'] == '' and row['status'] == 'missing'
            continue
        value = float(row['value'])
        expected = (min(100., value / CAP * 100) if row['criterion'] == 'size'
                    else max(0., min(100., (value + 10) * 5)))
        assert abs(float(row['score']) - expected) < 1e-10
    for c in cities:
        known=[r for r in saved if r['city']==c['city'] and r['score']!='']
        result=sum(float(r['score'])*float(r['weight']) for r in known)/sum(float(r['weight']) for r in known)
        assert abs(result-c['score']) < 1e-10
        assert c['score_low'] <= c['score']+1e-10 <= c['score_high']+1e-10
        assert 1 <= c['best_rank'] <= c['rank'] <= c['worst_rank'] <= 10
    report_text=(ROOT/'analysis/06-city-ranking.md').read_text()
    for name in ('airport_passengers','city_scores','criteria_comparison'):
        path=FIG/f'{name}.png'
        assert path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        assert f'(figures/{name}.png)' in report_text
    print('PASS: 10 cities; provenance; periods/units; missing values; saved scores; rank bounds; PNG links')
    for c in cities:
        print(c['rank'], c['city'], round(c['score'],2), f"range={c['best_rank']}–{c['worst_rank']}")


if __name__ == '__main__':
    main()
