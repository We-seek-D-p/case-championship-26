"""Независимая сверка сохранённых результатов S72 без вызова генератора.

uv run --frozen --no-sync python scripts/check_aeroflot_analysis.py
"""
import calendar
import csv
import math
from collections import defaultdict
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with (ROOT / path).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def near(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-7), (a,b)


def main():
    source = read('data/processed/airlines/aeroflot_traffic_monthly.csv')
    idx = {(r['entity'],r['period'],r['scope'],r['metric']):r for r in source}
    annual = read('results/aeroflot/period_metrics.csv')
    ai = {(r['entity'],r['period'],r['scope'],r['metric']):r for r in annual}
    season = read('results/aeroflot/seasonality.csv')
    comparisons = read('results/aeroflot/comparisons.csv')
    assert [len(annual),len(season),len(comparisons)] == [324,1008,108]
    for r in annual:
        year=int(r['period'][:4]); end=2 if r['period'].endswith('-2m') else 12
        def summed(metric):
            return sum(D(idx[r['entity'],f'{year}-{m:02}',r['scope'],metric]['value']) for m in range(1,end+1))
        if r['metric']=='passenger_load_factor':
            expected=100*summed('revenue_passenger_kilometers')/summed('available_seat_kilometers')
        elif r['metric']=='avg_distance':
            expected=1000*summed('revenue_passenger_kilometers')/summed('passengers')
        else:
            expected=summed(r['metric'])
        near(r['value'],expected)
        assert len(r['source_csv_lines'].split(';')) == len(r['source_locators'].split(';'))
    shares=defaultdict(float); weighted=defaultdict(float)
    for r in season:
        year=int(r['period'][:4]); month=int(r['period'][5:])
        days=calendar.monthrange(year,month)[1]
        assert int(r['days'])==days
        key=r['entity'],str(year),r['scope'],r['metric']
        x=idx[r['entity'],r['period'],r['scope'],r['metric']]['value']
        total=ai[key]['value']
        near(r['value'],x);near(r['annual_value'],total)
        near(r['value_per_day'],float(x)/days)
        near(r['annual_share_percent'],float(x)/float(total)*100)
        near(r['daily_index'],float(x)/days/float(total)*(366 if calendar.isleap(year) else 365)*100)
        shares[key]+=float(r['annual_share_percent'])
        weighted[key]+=float(r['daily_index'])*days/(366 if calendar.isleap(year) else 365)
    for key in shares:
        near(shares[key],100);near(weighted[key],100)
    for r in comparisons:
        a,b=[ai[r['entity'],p,r['scope'],r['metric']]['value'] for p in [r['comparison_period'],r['period']]]
        near(r['before'],a);near(r['after'],b)
        near(r['absolute_change'],float(b)-float(a))
        near(r['change'],float(b)-float(a) if r['unit']=='percentage_point' else (float(b)/float(a)-1)*100)
    checks=read('results/aeroflot/source_checks.csv')
    ytd={(r['entity'],r['period'],r['scope'],r['metric']):r for r in read('data/processed/airlines/aeroflot_traffic_ytd.csv')}
    assert len(checks)==252
    for r in checks:
        year=r['period'][:4];end='02' if r['period'].endswith('-2m') else '12'
        expected=ytd[r['entity'],f'{year}-{end}',r['scope'],r['metric']]['value']
        near(r['published_ytd'],expected)
        near(r['monthly_sum'],ai[r['entity'],r['period'],r['scope'],r['metric']]['value'])
        near(r['difference'],float(r['monthly_sum'])-float(expected))
    print('Проверены 324 агрегата, 1008 сезонных строк, 108 сопоставлений, 252 сверки с YTD; доли и взвешенные индексы сходятся к 100.')


if __name__=='__main__':
    main()
