"""Справочный анализ S72 без изменения параметров H1/H2.

uv run --frozen --no-sync python scripts/analyze_aeroflot_traffic.py
"""
import calendar
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/aeroflot'
ENTITIES = ['Aeroflot Group', 'Aeroflot Airline']
SCOPES = ['total', 'domestic', 'international']
METRICS = ['passengers', 'cargo', 'mail', 'cargo_and_mail', 'revenue_flights',
           'revenue_passenger_kilometers', 'available_seat_kilometers']
UNITS = dict(zip(METRICS, ['thousand_person', 'tonne', 'tonne', 'tonne', 'flight',
                          'million_passenger_km', 'million_seat_km']))


def read(block):
    path = f'data/processed/airlines/aeroflot_traffic_{block}.csv'
    with (ROOT / path).open(encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        reader.fieldnames
        result = []
        while True:
            line = reader.line_num + 1
            row = next(reader, None)
            if row is None:
                break
            row['source_csv'] = path
            row['source_csv_line'] = str(line)
            result.append(row)
    return result


def write(name, rows):
    assert rows
    with (OUT / f'{name}.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def provenance(rows):
    return dict(source_id='S72', source_csv=rows[0]['source_csv'],
                source_csv_lines=';'.join(r['source_csv_line'] for r in rows),
                raw_path=rows[0]['raw_path'],
                source_locators=';'.join(r['source_locator'] for r in rows))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    monthly = read('monthly')
    ytd = read('ytd')
    idx = {(r['entity'], r['period'], r['scope'], r['metric']): r for r in monthly}
    yi = {(r['entity'], r['period'], r['scope'], r['metric']): r for r in ytd}
    assert len(idx) == len(monthly)
    def cell(e, p, s, m):
        row = idx[e, p, s, m]
        assert row['value'] != '', (e, p, s, m)
        return row
    def val(e, p, s, m):
        return float(cell(e, p, s, m)['value'])

    annual, seasonal, comparisons, checks = [], [], [], []
    totals = {}
    periods = [(y, 12) for y in [2019, 2022, 2023, 2024]] + [(2024, 2), (2025, 2)]
    for e in ENTITIES:
        for year, end in periods:
            label = str(year) if end == 12 else f'{year}-2m'
            for scope in SCOPES:
                base = dict(entity=e, period=label, period_start=f'{year}-01-01',
                            period_end=f'{year}-{end:02}-{calendar.monthrange(year, end)[1]}', scope=scope)
                for metric in METRICS:
                    inputs = [cell(e, f'{year}-{m:02}', scope, metric) for m in range(1, end + 1)]
                    total = math.fsum(float(r['value']) for r in inputs)
                    totals[e, label, scope, metric] = total
                    annual.append(dict(**base, metric=metric, value=total, unit=UNITS[metric],
                                       record_kind='calculation', formula='sum_monthly', **provenance(inputs)))
                    published = yi[e, f'{year}-{end:02}', scope, metric]
                    difference = total - float(published['value'])
                    checks.append(dict(**base, metric=metric, monthly_sum=total,
                                       published_ytd=published['value'], difference=difference,
                                       unit=UNITS[metric], status='match' if abs(difference) < 1e-7 else 'source_difference',
                                       ytd_source_csv=published['source_csv'], ytd_csv_line=published['source_csv_line'],
                                       ytd_locator=published['source_locator'], **provenance(inputs)))
                rpk = totals[e, label, scope, 'revenue_passenger_kilometers']
                ask = totals[e, label, scope, 'available_seat_kilometers']
                passengers = totals[e, label, scope, 'passengers']
                assert ask > 0 and passengers > 0
                for metric, value, unit, inputs_metrics, formula in [
                    ('passenger_load_factor', 100*rpk/ask, 'percent', METRICS[-2:], '100*sum_RPK/sum_ASK'),
                    ('avg_distance', 1000*rpk/passengers, 'km', ['revenue_passenger_kilometers', 'passengers'], '1000*sum_RPK/sum_passengers'),
                ]:
                    inputs = [cell(e, f'{year}-{m:02}', scope, metric0) for metric0 in inputs_metrics for m in range(1, end+1)]
                    totals[e, label, scope, metric] = value
                    annual.append(dict(**base, metric=metric, value=value, unit=unit,
                                       record_kind='calculation', formula=formula, **provenance(inputs)))

        for year in [2023, 2024]:
            for scope in SCOPES:
                for metric in METRICS:
                    total = totals[e, str(year), scope, metric]
                    for month in range(1, 13):
                        p = f'{year}-{month:02}'
                        row = cell(e, p, scope, metric)
                        value = float(row['value'])
                        days = calendar.monthrange(year, month)[1]
                        seasonal.append(dict(entity=e, period=p, scope=scope, metric=metric, value=value,
                                             unit=UNITS[metric], days=days, value_per_day=value/days,
                                             annual_value=total, annual_share_percent=100*value/total,
                                             daily_index=100*(value/days)/(total/(366 if calendar.isleap(year) else 365)),
                                             record_kind='calculation', **provenance([row])))
                for month in range(1, 13):
                    p = f'{year}-{month:02}'
                    lf = 100*val(e, p, scope, 'revenue_passenger_kilometers')/val(e, p, scope, 'available_seat_kilometers')
                    assert math.isclose(lf, val(e, p, scope, 'passenger_load_factor'), abs_tol=1e-7)
                    assert math.isclose(val(e, p, scope, 'cargo')+val(e, p, scope, 'mail'),
                                        val(e, p, scope, 'cargo_and_mail'), abs_tol=1e-7)

        for before, after in [('2023', '2024'), ('2024-2m', '2025-2m')]:
            for scope in SCOPES:
                for metric in METRICS + ['passenger_load_factor', 'avg_distance']:
                    a, b = [totals[e, t, scope, metric] for t in [before, after]]
                    pp = metric == 'passenger_load_factor'
                    comparisons.append(dict(entity=e, comparison_period=before, period=after, scope=scope,
                                            metric=metric, before=a, after=b, absolute_change=b-a,
                                            change=b-a if pp else 100*(b/a-1), unit='percentage_point' if pp else 'percent',
                                            record_kind='calculation', source_file='results/aeroflot/period_metrics.csv',
                                            source_key=f'{e};{before}/{after};{scope};{metric}'))

    write('period_metrics', annual)
    write('seasonality', seasonal)
    write('comparisons', comparisons)
    write('source_checks', checks)
    assert len(annual) == 324 and len(seasonal) == 1008 and len(comparisons) == 108
    for records, keys in [(annual, ['entity','period','scope','metric']), (seasonal, ['entity','period','scope','metric'])]:
        assert len({tuple(r[k] for k in keys) for r in records}) == len(records)
    for e in ENTITIES:
        for year, end in periods:
            label = str(year) if end == 12 else f'{year}-2m'
            for metric in METRICS:
                assert math.isclose(totals[e,label,'total',metric],
                                    totals[e,label,'domestic',metric]+totals[e,label,'international',metric], abs_tol=1e-6)
    render(seasonal)
    report(totals, seasonal, checks)
    print(f'Сохранены: period_metrics={len(annual)}, seasonality={len(seasonal)}, comparisons={len(comparisons)}, source_checks={len(checks)}.')
    print(f'Расхождений сумм месяцев с YTD: {sum(r["status"]=="source_difference" for r in checks)}. Значения источника не исправлены.')


def render(rows):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    labels = ['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек']
    for ax, metric, title in zip(axes, ['passengers','cargo'], ['Пассажиры', 'Груз, без почты']):
        for year, style in [(2023, '--'), (2024, '-')]:
            values = [r['daily_index'] for r in rows if r['entity']=='Aeroflot Group' and r['scope']=='domestic' and r['metric']==metric and r['period'].startswith(str(year))]
            assert len(values) == 12
            ax.plot(range(12), values, style, marker='o', label=str(year))
        ax.axhline(100, color='gray', lw=1)
        ax.set_xticks(range(12), labels, rotation=45)
        ax.set_title(title)
        ax.grid(alpha=.2)
        ax.legend()
    axes[0].set_ylabel('Индекс к среднему за день года, 100 = среднее')
    fig.suptitle('Группа Аэрофлот: сезонность внутренних перевозок')
    fig.text(.02, .02, 'Источник: S72, абсолютные месячные данные; расчёт с учётом числа дней. Не коэффициенты спроса Red Wings.', fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.94))
    fig.savefig(ROOT/'analysis/figures/aeroflot_seasonality.png', dpi=160)
    plt.close(fig)


def report(t, seasonal, checks):
    def n(e,y,s,m):return t[e,str(y),s,m]
    e='Aeroflot Group'
    lines=['# Аэрофлот S72: опора для проверки H2', '',
           '**S72 подкрепляет поэтапный запуск H2 с сезонной проверкой продаж и ёмкости.** '
           'Он показывает масштаб, сезонность и структуру действующих перевозок, но не доказывает преимущество H2 перед H1. '
           'Общесетевые показатели не являются спросом на выбранных парах Red Wings.', '',
           '## Масштаб и ресурсы', '',
           '| Субъект | Пассажиры 2023 → 2024, млн | Рост ASK | Загрузка 2023 → 2024 |', '|---|---:|---:|---:|']
    for entity in ENTITIES:
        lines.append(f'| {entity} | {n(entity,2023,"total","passengers")/1000:.2f} → {n(entity,2024,"total","passengers")/1000:.2f} | {(n(entity,2024,"total","available_seat_kilometers")/n(entity,2023,"total","available_seat_kilometers")-1)*100:.1f}% | {n(entity,2023,"total","passenger_load_factor"):.2f}% → {n(entity,2024,"total","passenger_load_factor"):.2f}% |')
    lines += ['', 'Рост сопровождался увеличением провозной ёмкости и загрузки. Для масштабирования H2 нужен план рейсов и ресурсов; одной конверсией нельзя обосновать весь прирост. '
              'Это описание совместной динамики, не доказательство её причин.', '', '## Сезонность', '',
              '![Сезонность пассажиров и груза](figures/aeroflot_seasonality.png)', '',
              '| Год, внутренние перевозки группы | III квартал: доля пассажиров | III квартал: доля груза |', '|---|---:|---:|']
    for year in [2023,2024]:
        shares=[sum(r['annual_share_percent'] for r in seasonal if r['entity']==e and r['scope']=='domestic' and r['metric']==m and r['period'] in [f'{year}-{mm:02}' for mm in [7,8,9]]) for m in ['passengers','cargo']]
        lines.append(f'| {year} | {shares[0]:.1f}% | {shares[1]:.1f}% |')
    lines += ['', 'Сезонные индексы рассчитаны отдельно для 2023 и 2024 годов с поправкой на число дней. '
              'Наблюдённый поток зависит и от предложения рейсов. Индексы S72 не перенесены в маршрутный спрос Red Wings.', '',
              '**Следствие для H2:** оценивать пилот по сопоставимым сезонам, а расширение до десяти пар проверять на зимнем и летнем расписании. '
              'Пилот октября–декабря не подтверждает летний спрос и результат полного года. Гибкость частот — аргумент в пользу поэтапного запуска из существующей базы; '
              'S72 не измеряет экономию от этой гибкости и применим также для проверки сезонных рисков H1.', '',
              '## Груз и почта', '',
              '| Охват группы | Груз 2023 → 2024, тыс. т | Изменение | Почта 2024, тыс. т |', '|---|---:|---:|---:|']
    for scope in SCOPES:
        a,b=[n(e,y,scope,'cargo') for y in [2023,2024]]
        lines.append(f'| {scope} | {a/1000:.2f} → {b/1000:.2f} | {(b/a-1)*100:.1f}% | {n(e,2024,scope,"mail")/1000:.2f} |')
    lines += ['', 'Грузовой поток существует и имеет собственный сезонный профиль. Для H2 это основание проверить коммерческие договоры на груз/почту по выбранным парам '
              'и техническую возможность перевозки вместе с пассажирами. Нужны маршрутный объём, тариф, затраты обработки, ограничения массы и объёма после багажа. '
              'В S72 нет разреза по типу самолёта и способу перевозки груза. Общегрупповые тонны не считаются доступным грузом для SJ-100. '
              '**Грузовая выручка и прибыль не оценены и в расчёт H2 не добавлены.** Груз, почта и их сумма не складываются друг с другом.', '',
              '## Применимость к выбору и ограничения', '',
              '- В H2 сохраняются действующие сценарные потолки 85%/72%; загрузка S72 — RPK/ASK, а не число пассажиров на кресло. Зрелая сеть не калибрует новый региональный маршрут.',
              '- Разделять группу и авиакомпанию, внутренние и международные перевозки. Разность группы и авиакомпании не идентифицирует отдельного конкурента.',
              '- Январь–февраль 2025 сравнивается только с январём–февралём 2024. Полных итогов 2025 в S72 нет; ряд не устанавливает порог позиции №2.',
              '- Цены, прибыльность, O&D, результаты хабов и эффект цифровизации из S72 не определяются.', '',
              '## Источники, воспроизведение и проверки', '',
              '[Исходные CSV и ограничения S72](../data/processed/airlines/README.md#статистика-аэрофлота-s72). '
              'Каждая исходная запись имеет CSV-строку и локатор ячейки XLS. Числа настоящего документа строятся скриптом, а не правятся вручную.', '',
              '`uv run --frozen --no-sync python scripts/analyze_aeroflot_traffic.py`', '',
              '- [Периоды и показатели](../results/aeroflot/period_metrics.csv): суммы и отношения, единицы, формулы, исходные CSV-строки и ячейки.',
              '- [Сезонность](../results/aeroflot/seasonality.csv): месяцы, число дней, доля года и индекс среднесуточного потока.',
              '- [Сопоставления](../results/aeroflot/comparisons.csv): исходные и конечные величины, абсолютные изменения, проценты и п.п.; ключи агрегатов.',
              '- [Сверка с YTD](../results/aeroflot/source_checks.csv): опубликованный итог, сумма месяцев, разность и оба локатора.', '',
              'Выполнены проверки полноты выбранных периодов, уникальности ключей, total = domestic + international, '
              'cargo_and_mail = cargo + mail и месячной загрузки через RPK/ASK (2023–2024). '
              f'Сверка сумм месяцев с YTD: число расхождений выше 1e-7 в единице показателя — {sum(r["status"]=="source_difference" for r in checks)}. '
              'Они сохранены как ограничения источника, без исправления данных. YoY рассчитывается из абсолютных месяцев, а не из спорных YoY-блоков.']
    lines += ['', '| Показатель | Максимальная абсолютная разность суммы месяцев и YTD | Единица | Субъект / период / охват |', '|---|---:|---|---|']
    for metric in METRICS:
        row = max((r for r in checks if r['metric']==metric), key=lambda r: abs(r['difference']))
        lines.append(f'| {metric} | {abs(row["difference"]):.6f} | {row["unit"]} | {row["entity"]} / {row["period"]} / {row["scope"]} |')
    (ROOT/'analysis/13-aeroflot-benchmark.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
