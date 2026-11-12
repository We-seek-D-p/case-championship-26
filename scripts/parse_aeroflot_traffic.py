"""Разбор локальной книги S72 без исправления опубликованных значений.

uv run --frozen --no-sync --with xlrd==2.0.2 python scripts/parse_aeroflot_traffic.py
Та же команда с --check проверяет сохранённые CSV без перезаписи.
"""
import argparse
import calendar
import csv
import math
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[1]
RAW = Path('data/raw/airlines/traffic_figures_2025_2.xls')
OUT = ROOT / 'data/processed/airlines'
BLOCKS = {
    'monthly': (0, False, False),
    'ytd': (86, True, False),
    'monthly_yoy': (43, False, True),
    'ytd_yoy': (129, True, True),
}
# Номер строки Excel, исходное название, код, единица нормализованного значения.
METRICS = [
    (5, 'Revenue Passenger Kilometers', 'revenue_passenger_kilometers', 'million_passenger_km'),
    (8, 'Revenue Tonne Kilometers', 'revenue_tonne_kilometers', 'million_tonne_km'),
    (11, 'Passengers carried', 'passengers', 'thousand_person'),
    (14, 'Mail carried', 'mail', 'tonne'),
    (17, 'Cargo carried', 'cargo', 'tonne'),
    (20, 'Cargo and mail carried', 'cargo_and_mail', 'tonne'),
    (23, 'Revenue Load Factor', 'revenue_load_factor', 'percent'),
    (26, 'Passenger Load Factor', 'passenger_load_factor', 'percent'),
    (29, 'Flight hours for fleet', 'flight_hours', 'hour'),
    (30, 'Available Tonne Kilometers', 'available_tonne_kilometers', 'million_tonne_km'),
    (33, 'Available Seat Kilometers', 'available_seat_kilometers', 'million_seat_km'),
    (36, 'Revenue Cargo Tonne Kilometers', 'revenue_cargo_tonne_kilometers', 'million_tonne_km'),
    (39, 'Revenue flights', 'revenue_flights', 'flight'),
]
FIELDS = (
    'source_id raw_path source_sheet source_row source_column source_locator '
    'source_metric source_unit source_period source_format source_cell_type '
    'entity reporting_basis period period_start period_end comparison_period '
    'metric scope value unit raw_value value_qualifier record_kind limitations'
).split()


def normalized(text):
    return ' '.join(text.split())


def period_label(text, ytd):
    name, year = normalized(text).split()
    month = int(name[:-1]) if ytd else list(calendar.month_name).index(name)
    if ytd:
        assert name == f'{month}M', text
    return int(year), month


def source_period(sheet, offset, ytd, col):
    text = sheet.cell_value(offset + 1, col)
    # DB45: соседние месяцы и все три остальных блока подтверждают июнь 2022.
    if (sheet.name, offset, col) == ('Aeroflot Airline', 43, 105):
        assert normalized(text) == 'June 2021'
        return (2022, 6), 'Исправлен период: исходный заголовок June 2021; June 2022 подтверждён DB2, DB88, DB131 и соседними месяцами; исходный заголовок сохранён в source_period'
    return period_label(text, ytd), ''


def number(value, unit, yoy):
    """Не вычисляет рост из кратности и не заменяет пропуски нулями."""
    if value == '':
        return '', unit, 'missing_blank'
    if value == '-':
        return '', unit, 'missing_dash'
    if isinstance(value, str):
        text = value.replace(',', '.')
        if text.endswith(('х', 'x')):
            return str(Decimal(text[:-1])), 'times', 'reported_multiple'
        if text.endswith('%'):
            assert yoy and unit == 'percent', (value, unit)
            return str(Decimal(text[:-1])), unit, 'reported'
        raise ValueError(f'Неизвестный текст значения: {value!r}')
    assert math.isfinite(value), value
    result = Decimal(str(value))
    if unit == 'percent':
        result *= 100
    return str(result), unit, 'reported'


def parse(book):
    assert book.sheet_names() == ['Aeroflot Group', 'Aeroflot Airline']
    result = {name: [] for name in BLOCKS}
    for sheet in book.sheets():
        basis = 'group' if sheet.name == 'Aeroflot Group' else 'airline'
        for block, (offset, ytd, yoy) in BLOCKS.items():
            title = sheet.cell_value(offset, 1)
            assert ('Cumulated' if ytd else 'Monthly') in title
            assert ('Y-O-Y Change' if yoy else 'Absolute') in title
            periods = [source_period(sheet, offset, ytd, c)[0] for c in range(4, 138)]
            assert periods == [(2014 + i // 12, i % 12 + 1) for i in range(134)]
            for base, label, metric, absolute_unit in METRICS:
                assert normalized(sheet.cell_value(base - 1 + offset, 2)) == label
                scopes = ['total'] if metric == 'flight_hours' else ['total', 'international', 'domestic']
                for index, scope in enumerate(scopes):
                    row = base - 1 + offset + index
                    if index:
                        assert normalized(sheet.cell_value(row, 2)).lower() == (
                            'incl. international' if index == 1 else 'domestic')
                    unit = ('percentage_point' if 'load_factor' in metric else 'percent') if yoy else absolute_unit
                    for col, (year, month) in enumerate(periods, 4):
                        cell = sheet.cell(row, col)
                        assert cell.ctype in (xlrd.XL_CELL_NUMBER, xlrd.XL_CELL_TEXT, xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                        value, value_unit, qualifier = number(cell.value, unit, yoy)
                        period = f'{year:04d}-{month:02d}'
                        start = f'{year:04d}-01-01' if ytd else f'{period}-01'
                        end = date(year, month, calendar.monthrange(year, month)[1]).isoformat()
                        column = xlrd.formula.colname(col)
                        record = dict(zip(FIELDS, [
                            'S72', RAW.as_posix(), sheet.name, str(row + 1), column,
                            f"'{sheet.name}'!{column}{row + 1}", sheet.cell_value(row, 2),
                            sheet.cell_value(row, 3), sheet.cell_value(offset + 1, col),
                            book.format_map[book.xf_list[cell.xf_index].format_key].format_str,
                            str(cell.ctype), sheet.name, basis, period, start, end,
                            (f'{year - 1:04d}-01/{year - 1:04d}-{month:02d}' if ytd else f'{year - 1:04d}-{month:02d}') if yoy else '',
                            metric, scope, value, value_unit, str(cell.value), qualifier, 'observation',
                            source_period(sheet, offset, ytd, col)[1],
                        ], strict=True))
                        result[block].append(record)
        # Вне прямоугольников показателей допустимы только заголовки и оформление.
        data_rows = {r for offset, _, _ in BLOCKS.values() for r in range(offset + 4, offset + 41)}
        for r in range(sheet.nrows):
            for c in range(4, sheet.ncols):
                if r not in data_rows or c >= 138:
                    if r not in {0, 1, 44, 87, 130}:
                        assert sheet.cell_value(r, c) == '', (sheet.name, r, c)
    annotate(result)
    return result


def key(row):
    return row['entity'], row['period'], row['metric'], row['scope']


def annotate(result):
    """Предметные расхождения — ограничения источника, а не исправления данных."""
    for block, rows in result.items():
        for row in rows:
            if row['value_qualifier'].startswith('missing'):
                row['limitations'] += ('; ' if row['limitations'] else '') + 'Числовое значение не опубликовано; исходный маркер сохранён'
        if block not in ('ytd', 'ytd_yoy'):
            continue
        monthly = {key(r): r for r in result[block.replace('ytd', 'monthly')]}
        for row in rows:
            other = monthly[key(row)]
            if row['period'].endswith('-01') and row['value'] and other['value'] and row['unit'] == other['unit']:
                if not math.isclose(float(row['value']), float(other['value']), rel_tol=1e-9, abs_tol=1e-7):
                    note = f"Расхождение January Monthly/YTD: {other['source_locator']}={other['raw_value']}; {row['source_locator']}={row['raw_value']}; значения не исправлены"
                    row['limitations'] = other['limitations'] = note


def verify(book, result):
    """Проверка полноты и обратная сверка каждой записи с ячейкой книги."""
    for block, rows in result.items():
        assert len(rows) == 2 * 37 * 134 == 9916
        assert len({key(r) for r in rows}) == len(rows)
        offset, ytd, yoy = BLOCKS[block]
        seen = set()
        for row in rows:
            sheet = book.sheet_by_name(row['source_sheet'])
            r = int(row['source_row']) - 1
            c = next(c for c in range(4, 138) if xlrd.formula.colname(c) == row['source_column'])
            location = (sheet.name, r, c)
            assert location not in seen
            seen.add(location)
            assert row['raw_value'] == str(sheet.cell_value(r, c))
            assert row['source_cell_type'] == str(sheet.cell_type(r, c))
            assert offset + 4 <= r < offset + 41
            year, month = source_period(sheet, offset, ytd, c)[0]
            assert row['period'] == f'{year}-{month:02d}'
            assert row['period_start'] == f'{year}-{1 if ytd else month:02d}-01'
            assert row['period_end'] == date(year, month, calendar.monthrange(year, month)[1]).isoformat()
            if row['value_qualifier'].startswith('missing'):
                assert row['value'] == '' and row['raw_value'] in ('', '-')
            else:
                assert math.isfinite(float(row['value']))
                # Независимая обратная проверка масштаба: % Excel хранятся долями,
                # п.п. и текстовые проценты уже даны в конечных единицах.
                raw = sheet.cell_value(r, c)
                if isinstance(raw, (int, float)):
                    scale = 100 if row['unit'] == 'percent' else 1
                    assert Decimal(row['value']) == Decimal(str(raw)) * scale
                else:
                    assert row['unit'] == ('times' if raw.endswith(('х', 'x')) else 'percent')
                    assert Decimal(row['value']) == Decimal(raw[:-1].replace(',', '.'))
            if 'load_factor' in row['metric']:
                assert row['unit'] == ('percentage_point' if yoy else 'percent')
                if not yoy and row['value']:
                    assert 0 <= Decimal(row['value']) <= 100
        expected = {(s.name, r, c) for s in book.sheets() for r in range(offset + 4, offset + 41) for c in range(4, 138)}
        assert seen == expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Проверить CSV без перезаписи')
    args = parser.parse_args()
    book = xlrd.open_workbook(ROOT / RAW, formatting_info=True)
    result = parse(book)
    verify(book, result)
    for block, expected in result.items():
        path = OUT / f'aeroflot_traffic_{block}.csv'
        if not args.check:
            with path.open('w', encoding='utf-8', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
                writer.writeheader()
                writer.writerows(expected)
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            assert reader.fieldnames == FIELDS
            actual = list(reader)
        assert actual == expected, f'CSV не совпадает с XLS: {path}'
        verify(book, {block: actual})
        counts = Counter(r['value_qualifier'] for r in actual)
        conflicts = sum('Расхождение' in r['limitations'] for r in actual)
        print(f'{path.name}: {len(actual)} записей; {dict(counts)}; расхождения January Monthly/YTD: {conflicts}')
    print('Проверены все 39664 ячейки, уникальность ключей, периоды, пропуски и точное совпадение CSV с разбором XLS.')


if __name__ == '__main__':
    main()
