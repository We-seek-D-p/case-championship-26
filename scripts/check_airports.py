"""Validate committed-format exports against local sources; no network or writes."""
import csv
import hashlib
import re
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/processed/airports'


def read(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f)
        rows=list(reader)
        assert all(None not in r and None not in r.values() for r in rows)
        return rows


def main():
    sources=read('sources.csv')
    assert len(sources)==17
    ids={s['source_id'] for s in sources}
    assert len(ids)==len(sources)
    tables={name:read(name+'.csv') for name in ['metrics','relations','attributes']}
    for s in sources:
        p=ROOT/s['raw_path']
        assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256']
        for name,rows in tables.items():
            key={'metrics':'metric_rows','relations':'relation_rows','attributes':'attribute_rows'}[name]
            assert sum(r['source_id']==s['source_id'] for r in rows)==int(s[key])
    patterns=[r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',r'\+7\s*\(?\d{3}',
              r'(?i)(?:api[_-]?key|password|authorization|private key)\s*[:=]']
    assert all(not re.search(p,' '.join(r.values())) for r in sources for p in patterns)
    for rows in tables.values():
        assert len({tuple(r.items()) for r in rows})==len(rows)
        for r in rows:
            assert r['source_id'] in ids
            first,last=map(int,re.fullmatch(r'lines (\d+)-(\d+)',r['source_locator']).groups())
            assert 1<=first<=last<=len((ROOT/r['raw_path']).read_text().splitlines())
            assert not any(re.search(p,' '.join(r.values())) for p in patterns)
            assert not any(x in ' '.join(r.values()) for x in ['Селиверстов','Кашичкин','Чуев','Хабиров','Андреев'])
    metrics=tables['metrics']
    def m(s,scope='total',period='2025',metric='passengers'):
        found=[r for r in metrics if (r['source_id'],r['scope'],r['period'],r['metric'])==(s,scope,period,metric)]
        assert len(found)==1
        return found[0]
    def val(*args,**kwargs): return Decimal(m(*args,**kwargs)['value'])
    assert val('S23')==1629761
    assert val('S25',period='2018')==1114507
    assert val('S32',period='2025-01/2025-09')==3078468
    assert val('S33',period='2026-08')==348410
    assert val('S38')==5384816
    assert val('S31')-val('S31','domestic')-val('S31','international')==55355
    assert val('S33',period='2026-summer')==val('S33','domestic','2026-summer')+val('S33','international','2026-summer')
    assert val('S36')==val('S37',period='2024')==3570000
    assert m('S35')['value_qualifier']=='greater_than'
    assert m('S41',metric='passengers_change')['value']=='-4.6'
    assert m('S41',period='2026/2028',metric='runway_reconstruction_budget')['record_kind']=='plan'
    assert all(not r['period'] for r in tables['attributes'])
    weight=next(r for r in tables['attributes'] if r['attribute']=='maximum_takeoff_weight')
    assert weight['value']=='191' and weight['unit']==''
    print('PASS: 17 sources; hashes, coverage, CSV shape, uniqueness, locators, periods,')
    print('qualifiers, plans, reconciliation, sensitive-pattern and named-person exclusions.')


if __name__=='__main__': main()
