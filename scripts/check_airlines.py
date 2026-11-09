"""Validate source coverage, provenance, accounting scope and risky extraction cases."""

import csv
import hashlib
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

import process_airlines as extraction

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/processed/airlines'


def read(name):
    with (OUT / (name + '.csv')).open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    assert rows and all(None not in r and None not in r.values() for r in rows)
    assert len(rows) == len({tuple(r.items()) for r in rows})
    return rows


def main():
    extraction.load()
    names = ['metrics', 'relations', 'routes', 'fares', 'tariff_rules', 'attributes']
    tables = {name: read(name) for name in names}
    sources = read('sources')
    source_map = {r['source_id']: r for r in sources}
    assert len(sources) == len(source_map) == 16
    assert set(source_map) == set(extraction.IDS)
    # Every record must point to the precise text from which its evidence was selected.
    for name, rows in tables.items():
        counts = Counter(r['source_id'] for r in rows)
        for s, source in source_map.items():
            assert counts[s] == int(source[name + '_rows'])
        for r in rows:
            source = source_map[r['source_id']]
            assert r['raw_path'] == source['raw_path']
            locator = r['source_locator']
            a, b = map(int, re.search(r'normalized_text_chars=(\d+):(\d+)', locator).groups())
            page = re.search(r'^pdf page=(\d+)', locator)
            if page:
                assert r['source_id'] == 'S61'
                text = extraction.norm(extraction.PDF_PAGES[int(page[1])-1])
            else:
                assert locator.startswith(extraction.LOCATORS[r['source_id']])
                text = extraction.SCOPES[r['source_id']]
            assert text[a:b] == r['source_excerpt']
    for source in sources:
        assert hashlib.sha256((ROOT/source['raw_path']).read_bytes()).hexdigest() == source['sha256']
        assert sum(int(source[n+'_rows']) for n in names) > 0
        assert source['capture_date'] == ''
    metrics = tables['metrics']
    grain = [(r['source_id'],r['entity'],r['reporting_basis'],r['period'],r['metric'],r['scope'],r['comparison_period']) for r in metrics]
    assert len(grain) == len(set(grain))
    for r in metrics:
        Decimal(r['value'])
        assert r['unit'] and r['period'] and r['record_kind']
    def m(s, name, scope='total', period='2025', entity=None):
        rows = [r for r in metrics if r['source_id']==s and r['metric']==name
                and r['scope']==scope and r['period']==period and (entity is None or r['entity']==entity)]
        assert len(rows)==1, (s,name,scope,period)
        return rows[0]
    assert m('S08','passengers')['value']=='2700000'
    assert m('S08','passengers','Russian_aircraft')['value_qualifier']=='greater_than'
    assert m('S08','load_factor_change')['unit']=='percent_as_reported'
    assert m('S09','passengers',period='2014')['value']=='920000'
    assert m('S16','passengers','hub:Кольцово',period='2021')['record_kind']=='forecast'
    assert m('S59','net_profit_loss',period='2024')['value']=='-7000000000'
    assert m('S59','EBITDAR_margin_change')['unit']=='percentage_point'
    assert m('S59','passengers','airplane')['value']=='6200000'
    assert m('S60','passengers')['value']=='6100000'
    assert m('S59','passengers','domestic',entity='ПАО Авиакомпания ЮТэйр')['value']=='5000000'
    assert m('S60','passengers','domestic')['value']=='4800000'
    assert m('S61','passengers')['value']=='2200000'
    routes=tables['routes']
    assert sum(r['source_id']=='S17' for r in routes)==26
    assert not any(r['source_id']=='S11' for r in routes), 'Do not infer a Cartesian product'
    announced = [r for r in routes if r['source_id']=='S14']
    assert len(announced)==2 and {r['duration_minutes'] for r in announced}=={'355','175'}
    assert all(r['start_date']=='2027-03-28' and r['end_date']=='2027-10-24' for r in announced)
    schedules=[r for r in routes if r['record_kind']=='published_schedule']
    assert len(schedules)==4
    assert {(r['days'],r['departure_time'],r['arrival_time']) for r in schedules}=={
        ('3','13:30','15:55'),('4','10:10','14:30'),('7','16:40','19:35'),('1','11:05','15:15')}
    for r in routes:
        if r['flights_per_week']:
            assert Decimal(r['flights_per_week'])>0
        for field in ['departure_time','arrival_time']:
            if r[field]: assert re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d',r[field])
        for field in ['start_date','end_date']:
            if r[field]:
                from datetime import date
                date.fromisoformat(r[field])
    fares=tables['fares']
    assert Counter(r['source_id'] for r in fares)=={'S22':23,'S61':84}
    # Independently enumerate every printed currency amount on both offer pages:
    # repeated equal prices must be covered with the same multiplicity.
    for page in [7,8]:
        text=extraction.norm(extraction.PDF_PAGES[page-1])
        printed=Counter(int(re.sub(r'\s','',amount)) for amount in re.findall(r'(?<!\d)(\d[\d ]*)\s*₽',text))
        extracted=Counter(int(r['amount']) for r in fares if r['source_id']=='S61'
                          and r['source_locator'].startswith(f'pdf page={page};'))
        assert printed==extracted, (page,'Printed price coverage mismatch')
    for r in fares:
        assert int(r['amount'])>0 and r['currency']=='RUB'
        assert r['record_kind']=='advertised_fare'
        assert r['value_qualifier'] in {'at_least','reported'}
    s22=[r for r in fares if r['source_id']=='S22']
    assert len({r['destination'] for r in s22})==23
    assert min(int(r['amount']) for r in s22)==1430
    anomaly=next(r for r in fares if r['flight_numbers']=='А47030')
    assert anomaly['origin']=='Москва (Внуково)' and anomaly['destination']=='Ереван'
    assert anomaly['amount']=='13468' and 'не заменено' in anomaly['limitations']
    weird=next(r for r in fares if r['flight_numbers']=='A46125/6125')
    assert weird['amount']=='6380' and 'необычный' in weird['limitations']
    kutaisi=next(r for r in fares if r['destination']=='Кутаиси')
    assert kutaisi['value_qualifier']=='reported'
    rules=tables['tariff_rules']
    assert len(rules)==77
    fl_codes=[r for r in rules if r['brand']=='FL' and r['service']=='booking_codes']
    assert len(fl_codes)==2 and fl_codes[0]['value'] != fl_codes[1]['value']
    assert next(r for r in rules if r['brand']=='LT' and r['service']=='refund_before_checkin')['value']=='not_allowed'
    assert next(r for r in rules if r['brand']=='FR' and r['service']=='change_before_checkin')['value']=='0'
    # Scan every exported field. Source URLs may include a public appointment slug;
    # no body excerpts carry personal names, direct contacts or credentials.
    patterns=[r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',r'\+7\s*\(?\d{3}',
              r'(?i)(?:api[_-]?key|password|authorization|private key)\s*[:=]']
    for rows in [sources,*tables.values()]:
        for r in rows:
            text=' '.join(r.values())
            assert not any(re.search(p,text) for p in patterns), (r['source_id'],'sensitive pattern')
            assert not any(name in text for name in ['Сухоребрик','Ключарев','Чудновский','Теплицкий','Геннадий Абрамов','Александр Егоров'])
    print('PASS: 16 source hashes, CSV structure, coverage, unique metric grain, all evidence spans;')
    print('accounting scopes, periods, forecast kinds, schedules, 107 fares, 77 tariff rules, sensitive-pattern scan.')


if __name__=='__main__':
    main()
