"""Independent CSV/Decimal accounting and directed-flight capacity checks.
uv run --frozen --no-sync python scripts/check_strategy.py
No calls to the model for the independent recalculation.
"""
import csv
import math
import sys
import unittest
from collections import Counter, defaultdict
from decimal import Decimal as D
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(p):
    with (ROOT/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def near(a,b):
    assert math.isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-5),(a,b)
def check_flight_capacity(occupancy,capacity):
    if occupancy < -1e-7 or occupancy > capacity+1e-7:raise ValueError('directional seat overflow')

def main():
    assert sys.version_info[:2]==(3,14)
    inp={r['route_id']:r for r in read('results/strategy/route_assumptions.csv')}
    routes=read('results/strategy/route_scenarios.csv'); summary=read('results/strategy/hypothesis_comparison.csv')
    transfers=read('results/strategy/transfer_scenarios.csv')
    rotations=read('results/strategy/weekly_rotations.csv')
    pilots=read('results/strategy/pilot_2027_rotations.csv')
    core=read('data/processed/core/route_passengers.csv')
    anchors=[D(r['passengers']) for r in core if r['origin']=='Екатеринбург (Кольцово)' and r['destination']=='Минеральные Воды' and r['period']=='2025']
    assert len(anchors)==1 and anchors[0]==D('211000')
    target=anchors[0]*D('.4')
    for r in inp.values():
        near(r['annual_local_target'],target)
        assert r['common_source_id']=='S40' and r['common_analog_pair']=='Екатеринбург (Кольцово) — Минеральные Воды'
    for s in summary:
        h,c,y=s['hypothesis'],s['scenario'],s['year'];cautious=c=='cautious'
        ww=D(s['weeks']);load=D('.72' if cautious else '.85');demand=D('.75' if cautious else '1')
        ramp=D(('.9' if cautious else '1') if y=='2028' else ('.5' if cautious else '.65'))
        farefactor=D('.9' if cautious else '1')
        rr=[r for r in routes if (r['hypothesis'],r['scenario'],r['year'])==(h,c,y)]
        rot=[r for r in (pilots if h=='H2' and y=='2027' else rotations) if r['hypothesis']==h]
        tt=[t for t in transfers if t['scenario']==c and t['year']==y] if h=='H1' else []
        net=D(0);revenue=D(0);gross=D(0)
        for r in rr:
            p=inp[r['route_id']];f=D(p['added_roundtrips_week']);cap=2*f*ww*100
            local=min(cap*load,target*ww/52*demand*ramp)
            own=D(('.35' if cautious else '.2') if p['rw_evidence']=='True' else ('.15' if cautious else '.08'))
            near(r['seats'],cap);near(r['local_segments'],local)
            transit=[t for t in tt if p['destination'] in (t['origin'],t['destination'])]
            tseg=sum((D(t['gross_oneway_journeys']) for t in transit),D(0));near(r['transfer_segments'],tseg)
            tnet=tseg*(1-D('.30' if cautious else '.15'))
            expectednet=local*(1-own)+tnet
            expectedrev=(local*(1-own)+tnet*D('.75'))*D(p['fare_rub_oneway'])*farefactor
            near(r['net_segments'],expectednet);near(r['net_revenue_rub'],expectedrev)
            net+=expectednet;revenue+=expectedrev;gross+=local+tseg
            # Reconstruct each directed flight from rotations; allocate each
            # transfer journey only to actual 60-minute connected flight pairs.
            for rt in [x for x in rot if x['route_id']==r['route_id']]:
                for direction in ('out','in'):
                    transfer_week=D(0)
                    for t in transit:
                        # Symmetric end-to-end demand: 1/2 each direction, even
                        # across that direction's actual weekly connections.
                        for start,end in [(t['origin'],t['destination']),(t['destination'],t['origin'])]:
                            count=0;this=False
                            for first in rot:
                                if first['destination']!=start:continue
                                for second in rot:
                                    if (second['destination']==end and second['day']==first['day'] and second['tail']==first['tail'] and
                                        abs(float(second['departure_base_h'])-float(first['arrival_base_h'])-1)<1e-8):
                                        count+=1
                                        if (direction=='in' and rt==first) or (direction=='out' and rt==second):this=True
                            assert count>=1
                            if this:transfer_week+=D(t['gross_oneway_journeys'])/ww/2/count
                    occupied=local/(2*f*ww)+transfer_week
                    check_flight_capacity(float(occupied),float(load*100))
        near(s['net_passenger_segments'],net);near(s['incremental_revenue_rub'],revenue);near(s['gross_segments'],gross)
        journeys=sum(D(t['net_journeys']) for t in tt)
        near(s['net_oneway_journeys'],net-journeys)
        near(s['share_delta_pp'],net/D('108850000')*100)
        near(s['share_after_percent'],(D('2700000')+net)/D('108850000')*100)
        blocks=sum((D(r['roundtrip_block_h']) for r in rot),D(0))*ww
        departures=sum(2*int(inp[r['route_id']]['added_roundtrips_week']) for r in rr)*int(ww)
        active=max(int(r['tail']) for r in rot);fixed=((active+1)*75000000+(120000000 if h=='H1' else 20000000))*ww/52
        startup=(150000000 if h=='H1' else 20000000) if y=='2027' else 0
        near(s['block_hours'],blocks);near(s['departures'],departures)
        near(s['contribution_rub'],revenue-blocks*130000-departures*20000-fixed-startup)
        grouped=defaultdict(list)
        for r in rot:grouped[r['day'],r['tail']].append(r)
        for group in grouped.values():
            group.sort(key=lambda r:float(r['departure_base_h']))
            assert sum(float(r['roundtrip_block_h']) for r in group)<=10.5+1e-8
            assert float(group[0]['departure_base_h'])>=6
            assert float(group[-1]['arrival_base_h'])<=20+1e-8
            for a,b in zip(group,group[1:]):assert float(b['departure_base_h'])-float(a['arrival_base_h'])>=1-1e-8
        counts=Counter(r['route_id'] for r in rot)
        for r in rr:assert counts[r['route_id']]==int(inp[r['route_id']]['added_roundtrips_week'])
    # City score policy is recomputed independently from the exported criteria.
    criteria=read('results/cities/criteria_scores.csv')
    for city in read('results/cities/city_ranking.csv'):
        known=[r for r in criteria if r['city']==city['city'] and r['value']!='']
        score=D(0);weights=D(0)
        for r in known:
            v=D(r['value']);w=D(r['weight'])
            scaled=min(D(100),v/D(6000000)*100) if r['criterion']=='size' else min(D(100),max(D(0),(v+10)*5))
            score+=scaled*w;weights+=w
        near(city['score'],score/weights)
    print('Расчёты, кресла по направлениям и ротации сходятся.')

class SemanticTests(unittest.TestCase):
    def model_fixture(self):
        import compare_growth_strategies as model
        records=read('results/strategy/route_assumptions.csv')
        for r in records:
            for key in ('block_h_oneway','fare_rub_oneway','annual_local_target','common_analog_passengers'):r[key]=float(r[key])
            r['added_roundtrips_week']=int(r['added_roundtrips_week'])
            r['rw_evidence']=r['rw_evidence']=='True'
        return model,records
    def test_zero_demand_cannot_create_growth(self):
        model,records=self.model_fixture()
        _,summaries,transfers=model.calculate(records,model.rotations(records),2700000,108850000,'base',2028,demand_factor=0)
        for r in summaries:self.assertEqual(r['net_passenger_segments'],0);self.assertEqual(r['incremental_revenue_rub'],0)
        self.assertTrue(all(r['gross_oneway_journeys']==0 for r in transfers))
    def test_all_own_displacement_cannot_count_new_passengers(self):
        import copy
        model,records=self.model_fixture();saved=copy.deepcopy(model.CASES['base'])
        try:
            model.CASES['base'].update(existing_displacement=1,new_displacement=1,transfer_displacement=1)
            _,summaries,_=model.calculate(records,model.rotations(records),2700000,108850000,'base',2028)
            for r in summaries:self.assertEqual(r['net_passenger_segments'],0);self.assertEqual(r['incremental_revenue_rub'],0)
        finally:model.CASES['base']=saved
    def test_directional_bottleneck(self):
        # Aggregate 160/200 seats fits, but 90 locals+30 connections on one
        # departure does not; this catches annual-only capacity validation.
        with self.assertRaises(ValueError):check_flight_capacity(120,100)

if __name__=='__main__':
    main();unittest.main(argv=[sys.argv[0]])
