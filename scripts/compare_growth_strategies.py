"""Scenario decision, not an O&D forecast. Python 3.14; no network/raw access.
uv run --frozen --no-sync python scripts/compare_growth_strategies.py
"""
import csv
import json
import math
import re
import sys
from statistics import geometric_mean
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/strategy'
FIG = ROOT / 'analysis/figures'
# All coordinates, block times, fares and market multipliers below are planning
# assumptions, not additional sources. Fare: RUB per passenger per one-way segment.
# destination, block h, fare, analog multiplier, assumed marginal capture share, lon, lat
H2 = [
    ('Омск', 2.0, 10500, 1.0, .28, 73.37, 54.99),
    ('Саратов', 2.0, 11500, .9, .28, 46.03, 51.53),
    ('Нижний Новгород', 2.1, 11500, 1.0, .28, 44.00, 56.33),
    ('Оренбург', 1.6, 9000, .75, .28, 55.10, 51.77),
    ('Самара', 2.1, 11000, 1.0, .30, 50.15, 53.20),
    ('Абакан', 3.0, 15000, .9, .27, 91.43, 53.72),
    ('Минеральные Воды', 3.6, 16500, 1.0, .16, 43.13, 44.21),
    ('Новокузнецк', 2.7, 13500, .9, .27, 87.11, 53.76),
    ('Томск', 2.6, 13500, .9, .27, 84.97, 56.49),
    ('Ставрополь', 3.5, 16000, 1.0, .27, 41.97, 45.04),
]
H1 = [
    ('Нижний Новгород', 1.8, 9500, 1.1, .60, 44., 56.33),
    ('Красноярск', 3.4, 15500, 1.2, .60, 92.87, 56.01),
    ('Саратов', 1.6, 9000, 1.0, .60, 46.03, 51.53),
    ('Абакан', 3.5, 15500, .9, .60, 91.43, 53.72),
    ('Самара', 1.0, 7000, 1.1, .60, 50.15, 53.20),
    ('Новосибирск', 2.9, 14000, 1.1, .60, 82.92, 55.03),
    ('Минеральные Воды', 2.8, 13500, 1.0, .45, 43.13, 44.21),
    ('Омск', 2.4, 12500, 1.1, .60, 73.37, 54.99),
]
CASES = {
    'base': dict(label='Базовый', demand=1., load=.85, fare=1.,
                 existing_displacement=.20, new_displacement=.08, transfer_displacement=.15,
                 transfer_demand=1., weeks_2027=13, ramp_2027=.65, ramp_2028=1., start='2027-10-01'),
    'cautious': dict(label='Осторожный', demand=.75, load=.72, fare=.90,
                     existing_displacement=.35, new_displacement=.15, transfer_displacement=.30,
                     transfer_demand=.55, weeks_2027=4, ramp_2027=.50, ramp_2028=.90, start='2027-12-01'),
}
POLICY = dict(seats=100, H1_added_roundtrips_week=3, H2_added_roundtrips_week=2, weeks_2028=52,
              destination_turn_h=.75, base_turn_h=1., max_block_day=10.5,
              max_elapsed_day=14., spare_aircraft=1, fixed_aircraft_rub_year=75_000_000,
              variable_rub_block_h=130_000, airport_rub_departure=20_000,
              H1_fixed_rub_year=120_000_000, H2_fixed_rub_year=20_000_000,
              H1_startup_rub=150_000_000, H2_startup_rub=20_000_000,
              transfer_fare_factor=.75, common_capture=.40)


def read(p):
    with (ROOT / p).open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f); assert reader.fieldnames
        rows=[]
        while True:
            line=reader.line_num+1; r=next(reader,None)
            if r is None:break
            rows.append(dict(r,csv_file=p,csv_row=line))
        return rows


def write(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '|'+ '|'.join('---' for _ in headers)+'|']+
                     ['| '+' | '.join(str(v) for v in r)+' |' for r in rows])


def clock(hours):
    minutes = round(hours * 60)
    return f'{minutes // 60:02}:{minutes % 60:02}'


def great_circle_km(lon1,lat1,lon2,lat2):
    """Geographic screen only; rounded city coordinates, not flown distance."""
    x1,y1,x2,y2=map(math.radians,(lon1,lat1,lon2,lat2))
    a=math.sin((y2-y1)/2)**2+math.cos(y1)*math.cos(y2)*math.sin((x2-x1)/2)**2
    return 6371*2*math.asin(math.sqrt(a))


def inputs(demand_method='common'):
    catalog={r['source_id']:r for r in read('data/source_manifest.csv')}
    facts = read('data/processed/core/route_passengers.csv')
    routes = read('data/processed/core/current_routes.csv')
    market = read('data/processed/core/market.csv')
    rw = next(r for r in market if r['entity']=='Red Wings' and r['metric']=='passengers'
              and r['scope']=='total' and r['period']=='2025')
    national = next(r for r in market if r['source_id']=='S03' and r['metric']=='airline_passengers'
                    and r['value']=='108.85')
    records=[]; used_facts={}
    for h, base, rows in [('H1','Уфа',H1),('H2','Екатеринбург',H2)]:
        for n,(dest,block,fare,mult,capture,lon,lat) in enumerate(rows,1):
            # Analogs are published LINE volumes, not O&D. Cross-city scaling and
            # marginal capture are explicit judgments, not inferred observations.
            if h=='H2':
                analog = next(r for r in facts if r['destination']==('Минеральные Воды' if dest=='Минеральные Воды' else 'Новосибирск')
                              and r['origin']==('Екатеринбург (Кольцово)' if dest=='Минеральные Воды' else 'Омск'))
            else:
                target = 'Минеральные Воды' if dest=='Минеральные Воды' else 'Казань'
                analog = next(r for r in facts if r['destination']==target and
                              r['origin']==('Самара (Курумоч)' if target=='Минеральные Воды' else 'Омск') and r['period']=='2025')
            evidence=[r for r in routes if {r['origin'],r['destination']}=={base,dest}]
            existing=any(r['airline']=='Red Wings' for r in evidence)
            records.append(dict(route_id=f'{h}-{n:02}', hypothesis=h, origin=base,destination=dest,
                                block_h_oneway=block, fare_rub_oneway=fare, lon=lon,lat=lat,
                                great_circle_km=great_circle_km(55.97 if h=='H1' else 60.60,54.74 if h=='H1' else 56.84,lon,lat),
                                added_roundtrips_week=POLICY[h+'_added_roundtrips_week'], rw_evidence=existing,
                                baseline_frequency='not_assumed; addition_only',
                                analog_passengers=float(analog['passengers']),analog_period=analog['period'],
                                analog_unit=analog['unit'],analog_pair=analog['origin']+' — '+analog['destination'],
                                analog_source_id=analog['source_id'],analog_file=analog['source_file'],
                                analog_row=analog['source_row'],analog_locator=analog['source_locator'],
                                analog_multiplier=mult, marginal_capture=capture,
                                annual_local_target=float(analog['passengers'])*mult*capture,
                                evidence_refs=json.dumps([{k:r[k] for k in ('source_id','source_file','source_row','source_locator','evidence_type','validity_period','airline')} for r in evidence],ensure_ascii=False),
                                input_status='analog_passengers is observed line traffic; coefficients, fare, time, coordinates and added frequency are assumptions'))
            used_facts[analog['csv_file'],analog['csv_row']]=analog
    fact_rows=[]
    for r in [rw,national]+list(used_facts.values()):
        fact_rows.append(dict(entity=r.get('entity',r.get('origin','')+' — '+r.get('destination','')),
                              value=r.get('passengers',r.get('value')),unit=r['unit'],period=r['period'],
                              value_qualifier=r['value_qualifier'],source_id=r['source_id'],source_file=r['source_file'],
                              source_row=r['source_row'],source_locator=r['source_locator'],source_url=catalog[r['source_id']]['landing_url'],
                              source_ref=f"../../data/SOURCE_MANIFEST.md#{r['source_id'].lower()}",
                              core_file=r['csv_file'],core_row=r['csv_row'],limitations=r['limitations']))
    if demand_method=='common':
        # A neutral scenario anchor, NOT an estimate of unserved O&D. The same
        # two observed lines and coefficient apply to every local market.
        pool=[r for r in facts if r['origin']=='Омск' and r['destination'] in ('Казань','Новосибирск') and r['period']=='2025']
        anchor=geometric_mean(float(r['passengers']) for r in pool)
        for r in records:
            r['legacy_local_target']=r['annual_local_target']
            for key in tuple(r):
                if key.startswith('analog_') or key=='marginal_capture':r['legacy_'+key]=r.pop(key)
            r['demand_method']='common geometric midpoint of S23 Omsk-Kazan and Omsk-Novosibirsk; scenario, not O&D'
            r['common_analog_passengers']=anchor
            r['common_anchor_status']='calculated geometric midpoint of two observed line volumes, not another observation'
            r['common_capture']=POLICY['common_capture']
            r['annual_local_target']=anchor*POLICY['common_capture']
            r['local_target_status']='scenario; before seat cap, ramp and own displacement'
            r['input_status']='legacy analogs are observed line volumes; common anchor is calculated; target, capture, fare, block time, frequency and coordinates are assumptions'
            r['common_evidence_refs']=json.dumps([{k:p[k] for k in ('source_id','source_file','source_row','source_locator','source_url','passengers','period','unit')} for p in pool],ensure_ascii=False)
    write('fact_references.csv',fact_rows)
    return records, float(rw['value']),float(national['value'])*1e6


def rotations(records):
    result=[]
    for h in ('H1','H2'):
        rr=[r for r in records if r['hypothesis']==h]
        if h=='H1':
            # Four west/east (last pair south/east) bundles; three service days.
            # Each bundle has one feasible 60-min connection at Ufa. Alternating
            # order allows both journey directions across the weekly pattern.
            days=[(0,2,4),(1,3,5),(0,3,6),(1,4,6)]
            jobs=defaultdict(list)
            for i in range(4):
                for j,d in enumerate(days[i]):
                    pair=rr[2*i:2*i+2]
                    jobs[d].append(pair if j%2==0 else pair[::-1])
            for d, bundles in sorted(jobs.items()):
                for tail,bundle in enumerate(bundles,1):
                    t=6.
                    assert sum(2*r['block_h_oneway'] for r in bundle)<=POLICY['max_block_day']
                    for r in bundle:
                        arrival=t+2*r['block_h_oneway']+POLICY['destination_turn_h']
                        result.append(dict(hypothesis=h,day=d+1,tail=tail,route_id=r['route_id'],
                                           departure_base_h=t,arrival_base_h=arrival,
                                           departure_base_clock=clock(t),arrival_base_clock=clock(arrival),
                                           roundtrip_block_h=2*r['block_h_oneway'],
                                           origin=r['origin'],destination=r['destination'],status='synthetic_rotation'))
                        t=arrival+POLICY['base_turn_h']
                    assert t-POLICY['base_turn_h']-6<=POLICY['max_elapsed_day']
        else:
            # Greedy balance of marginal RTs over days/tails; explicit elapsed and
            # block limits. Does not assert optimality or slot/crew approval.
            bins=defaultdict(lambda:dict(elapsed=0.,block=0.,dest=set()))
            for r in sorted(rr,key=lambda r:-r['block_h_oneway']):
                for _ in range(r['added_roundtrips_week']):
                    options=[]
                    for d in range(1,8):
                        for tail in range(1,5):
                            b=bins[d,tail]
                            dur=2*r['block_h_oneway']+POLICY['destination_turn_h']+(POLICY['base_turn_h'] if b['elapsed'] else 0.)
                            if (r['destination'] not in b['dest'] and b['elapsed']+dur<=POLICY['max_elapsed_day'] and b['block']+2*r['block_h_oneway']<=POLICY['max_block_day']
                                and not any(x['hypothesis']==h and x['day']==d and x['route_id']==r['route_id'] for x in result)):
                                options.append((tail,max([bins[d,t]['elapsed'] for t in range(1,tail+1)]),d,dur))
                    tail,_,d,dur=min(options)
                    b=bins[d,tail]; start=6+b['elapsed']+(POLICY['base_turn_h'] if b['elapsed'] else 0.)
                    end=start+2*r['block_h_oneway']+POLICY['destination_turn_h']
                    result.append(dict(hypothesis=h,day=d,tail=tail,route_id=r['route_id'],departure_base_h=start,
                                       arrival_base_h=end,departure_base_clock=clock(start),arrival_base_clock=clock(end),
                                       roundtrip_block_h=2*r['block_h_oneway'],origin=r['origin'],destination=r['destination'],status='synthetic_rotation'))
                    b['elapsed']+=dur;b['block']+=2*r['block_h_oneway'];b['dest'].add(r['destination'])
    return sorted(result,key=lambda r:(r['hypothesis'],r['day'],r['tail'],r['departure_base_h']))


def calculate(records, rot, rw, market, case, year, fare_factor=1., demand_factor=1., block_cost=None, full_network=False):
    c=CASES[case]; weeks=POLICY['weeks_2028'] if year==2028 else c['weeks_2027']
    ramp=c['ramp_2028'] if year==2028 else c['ramp_2027']
    # Three-route H2 pilot in 2027; all ten routes in 2028.
    effective=[r for r in records if year==2028 or full_network or r['hypothesis']=='H1' or
               r['destination'] in ('Омск','Саратов','Минеральные Воды')]
    operating_rot=rot if year==2028 else rotations(effective)
    output=[]; transfers=[]
    for r in effective:
        cap=2*r['added_roundtrips_week']*weeks*POLICY['seats']
        local=min(cap*c['load'],r['annual_local_target']*weeks/52*c['demand']*ramp*demand_factor)
        displacement=c['existing_displacement'] if r['rw_evidence'] else c['new_displacement']
        output.append(dict(hypothesis=r['hypothesis'],scenario=case,year=year,route_id=r['route_id'],
                           origin=r['origin'],destination=r['destination'],weeks=weeks,
                           incremental_departures=2*r['added_roundtrips_week']*weeks,seats=cap,local_segments=local,transfer_segments=0.,
                           net_segments=local*(1-displacement),net_revenue_rub=local*(1-displacement)*r['fare_rub_oneway']*c['fare']*fare_factor,
                           fare_rub=r['fare_rub_oneway']*c['fare']*fare_factor,displacement_fraction=displacement))
    byid={r['route_id']:r for r in output}
    # Assign a transfer trip to one of four actually connected bundles. Three
    # one-way connections/week (2 in one direction, 1 reverse). No all-to-all hub.
    for i in range(4):
        a,b=records[2*i:2*i+2]; ra,rb=byid[a['route_id']],byid[b['route_id']]
        target=27510*.35*weeks/52*c['transfer_demand']*ramp*demand_factor
        # Direction with only one weekly connection limits total at symmetric
        # directional demand: no more than 2*100*weeks at the load ceiling.
        p=min(target,*(2*weeks*(POLICY['seats']*c['load']-r['local_segments']/(r['incremental_departures'])) for r in (ra,rb)))
        p=max(0.,p)
        net=p*(1-c['transfer_displacement'])
        revenue=0.
        for r,inp in ((ra,a),(rb,b)):
            rev=net*inp['fare_rub_oneway']*c['fare']*fare_factor*POLICY['transfer_fare_factor']
            r['transfer_segments']+=p;r['net_segments']+=net;r['net_revenue_rub']+=rev;revenue+=rev
        transfers.append(dict(scenario=case,year=year,origin=a['destination'],via='Уфа',destination=b['destination'],
                              gross_oneway_journeys=p,net_journeys=net,net_revenue_rub=revenue,
                              demand_basis='S23 Omsk-Kazan 2025 27510 persons * assumed .35; seasonal/OD proxy',
                              status='scenario; symmetric directional demand; capacity checked'))
    summary=[]
    for h in ('H1','H2'):
        rr=[r for r in output if r['hypothesis']==h]
        weekly=[r for r in operating_rot if r['hypothesis']==h]
        active=max(r['tail'] for r in weekly); fleet=active+POLICY['spare_aircraft']
        block=sum(r['roundtrip_block_h'] for r in weekly)*weeks
        departures=sum(r['incremental_departures'] for r in rr)
        variable=block*(block_cost or POLICY['variable_rub_block_h'])+departures*POLICY['airport_rub_departure']
        fixed=(fleet*POLICY['fixed_aircraft_rub_year']+POLICY[h+'_fixed_rub_year'])*weeks/52
        startup=POLICY[h+'_startup_rub'] if year==2027 else 0
        net=sum(r['net_segments'] for r in rr); revenue=sum(r['net_revenue_rub'] for r in rr)
        journeys=sum(t['net_journeys'] for t in transfers) if h=='H1' else 0
        summary.append(dict(hypothesis=h,scenario=case,year=year,weeks=weeks,start_date=c['start'] if year==2027 else '2028 planning year; 52 weeks',
                            gross_segments=sum(r['local_segments']+r['transfer_segments'] for r in rr),
                            net_passenger_segments=net,net_oneway_journeys=net-journeys,
                            transfer_net_journeys=journeys,incremental_revenue_rub=revenue,
                            share_delta_pp=100*net/market,share_after_percent=100*(rw+net)/market,
                            share_delta_pp_denominator_plus_increment=100*(rw+net)/(market+net)-100*rw/market,
                            block_hours=block,departures=departures,active_aircraft=active,reserve_aircraft=POLICY['spare_aircraft'],total_aircraft=fleet,
                            net_segments_per_aircraft=net/fleet,variable_cost_rub=variable,fixed_cost_rub=fixed,startup_rub=startup,
                            contribution_rub=revenue-variable-fixed-startup,
                            break_even_fare_multiplier=(variable+fixed+startup)/revenue if revenue else None,
                            period_unit='calendar year scenario; RUB nominal planning prices; passengers counted as segments'))
    return output,summary,transfers


def main():
    assert sys.version_info[:2]==(3,14)
    OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
    records,rw,market=inputs(); rot=rotations(records)
    write('route_assumptions.csv',records);write('weekly_rotations.csv',rot)
    pilot=[r for r in records if r['hypothesis']=='H1' or r['destination'] in ('Омск','Саратов','Минеральные Воды')]
    write('pilot_2027_rotations.csv',[r for r in rotations(pilot) if r['hypothesis']=='H2'])
    def unit(k):
        if 'rub_year' in k:return 'RUB/year'
        if 'block_h' in k and 'rub' in k:return 'RUB/block-hour'
        if 'rub_departure' in k:return 'RUB/departure'
        if k.endswith('_rub'):return 'RUB one-off'
        if k=='max_block_day':return 'block-hours/aircraft/day'
        if k=='max_elapsed_day':return 'hours/aircraft/day'
        if k.endswith('_h'):return 'hours/turn'
        if 'weeks' in k:return 'weeks'
        if k.endswith('added_roundtrips_week'):return 'roundtrips/route/week'
        if k=='spare_aircraft':return 'aircraft'
        if k=='seats':return 'seats/departure'
        if k=='start':return 'date YYYY-MM-DD'
        if k=='label':return 'text'
        return 'fraction 0..1'
    assumptions=[dict(parameter=k,value=v,unit=unit(k),status='assumption',period='2027-2028') for k,v in POLICY.items()]
    assumptions += [dict(parameter=f'{s}.{k}',value=v,unit=unit(k),status='assumption',period='2027-2028') for s,c in CASES.items() for k,v in c.items()]
    write('assumptions.csv',assumptions)
    outputs=[];summaries=[];transfers=[]
    for case in CASES:
        for year in (2027,2028):
            r,s,t=calculate(records,rot,rw,market,case,year);outputs+=r;summaries+=s;transfers+=t
    write('route_scenarios.csv',outputs);write('hypothesis_comparison.csv',summaries);write('transfer_scenarios.csv',transfers)
    sens=[]
    for name,f,d,cost in [('reference',1,1,130000),('fare_minus_20pct',.8,1,130000),('fare_plus_20pct',1.2,1,130000),
                          ('demand_minus_25pct',1,.75,130000),('demand_plus_25pct',1,1.25,130000),
                          ('block_cost_100k',1,1,100000),('block_cost_160k',1,1,160000),('block_cost_190k',1,1,190000)]:
        _,ss,_=calculate(records,rot,rw,market,'base',2028,f,d,cost)
        sens += [dict(test=name,fare_factor=f,demand_factor=d,block_cost_rub_h=cost,**r) for r in ss]
    write('sensitivity.csv',sens)
    validate(records,rot,outputs,summaries,transfers)
    controls(records,rw,market)
    figures(records,summaries)
    report(records,rot,summaries,sens,rw,market)
    for r in summaries: print(r['hypothesis'],r['scenario'],r['year'],round(r['net_passenger_segments']),round(r['incremental_revenue_rub']/1e6,1),r['total_aircraft'],round(r['contribution_rub']/1e6,1))


def validate(records,rot,outputs,summaries,transfers):
    for r in records:
        assert sum(x['route_id']==r['route_id'] for x in rot)==r['added_roundtrips_week']
    for h in ('H1','H2'):
        groups=defaultdict(list)
        for r in rot:
            if r['hypothesis']==h:groups[r['day'],r['tail']].append(r)
        for rr in groups.values():
            assert sum(r['roundtrip_block_h'] for r in rr)<=10.5+1e-9
            assert max(r['arrival_base_h'] for r in rr)-min(r['departure_base_h'] for r in rr)<=14+1e-9
            for a,b in zip(rr,rr[1:]):assert b['departure_base_h']-a['arrival_base_h']>=1.-1e-9
    for r in outputs:
        assert 0<=r['local_segments']+r['transfer_segments']<=r['seats']*CASES[r['scenario']]['load']+1e-8
        assert 0<=r['net_segments']<=r['local_segments']+r['transfer_segments']+1e-8
        if r['hypothesis']=='H1':
            assert r['local_segments']/(6*r['weeks'])+r['transfer_segments']/(2*r['weeks'])<=100*CASES[r['scenario']]['load']+1e-8
    for s in summaries:
        rr=[r for r in outputs if (r['hypothesis'],r['scenario'],r['year'])==(s['hypothesis'],s['scenario'],s['year'])]
        assert math.isclose(sum(r['net_revenue_rub'] for r in rr),s['incremental_revenue_rub'])
    for s in summaries:
        if s['hypothesis']=='H1':
            tt=[t for t in transfers if (t['scenario'],t['year'])==(s['scenario'],s['year'])]
            rr=[r for r in outputs if (r['hypothesis'],r['scenario'],r['year'])==('H1',s['scenario'],s['year'])]
            assert math.isclose(sum(r['transfer_segments'] for r in rr),2*sum(t['gross_oneway_journeys'] for t in tt))


def figures(records,summaries):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,axes=plt.subplots(1,2,figsize=(14,7))
    for ax,h,base,lon,lat in [(axes[0],'H1','Уфа',55.97,54.74),(axes[1],'H2','Екатеринбург',60.60,56.84)]:
        for i,r in enumerate(x for x in records if x['hypothesis']==h):
            ax.plot([lon,r['lon']],[lat,r['lat']],color='#346989',alpha=.6)
            ax.scatter(r['lon'],r['lat'],color='#346989',s=20)
            offset=(-82,-18) if r['destination']=='Новокузнецк' else ((5,8) if r['destination']=='Абакан' else (4,5 if i%2 else -12))
            ax.annotate(r['destination'],(r['lon'],r['lat']),xytext=offset,textcoords='offset points',fontsize=8)
        ax.scatter(lon,lat,color='#b64132',s=70,marker='s');ax.annotate(base,(lon,lat),xytext=(4,7),textcoords='offset points',fontweight='bold')
        ax.set(xlim=(38,101),ylim=(41,61),xlabel='Долгота, ° в.д.',ylabel='Широта, ° с.ш.',title=h+': планируемые пары')
        ax.grid(alpha=.2)
    fig.suptitle('Схематическая карта вариантов роста Red Wings; 2027–2028')
    fig.text(.04,.02,'Источник: results/strategy/route_assumptions.csv. Координаты округлены как допущение; линии не являются трассами полёта.\nH2: 2 дополнительных оборота/неделю на каждой из 10 пар. H1: 3 оборота/неделю на каждой из 8 пар.',fontsize=9)
    fig.tight_layout(rect=(0,.08,1,.95));fig.savefig(FIG/'strategy_route_map.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    rr=[r for r in summaries if r['year']==2028]
    labels=[r['hypothesis']+' / '+CASES[r['scenario']]['label'] for r in rr]
    bars=ax.bar(labels,[r['net_passenger_segments']/1000 for r in rr],color=['#346989','#b76a37']*2)
    ax.bar_label(bars,fmt='%.1f');ax.set_ylabel('Дополнительные пассажиро-сегменты, тыс. за 52 недели');ax.set_title('Сценарный эффект 2028 года после вычета замещения')
    fig.text(.05,.02,'Источник: hypothesis_comparison.csv. Сценарные оценки, не наблюдаемый O&D.',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1));fig.savefig(FIG/'strategy_comparison.png',dpi=160);plt.close(fig)
    from matplotlib.lines import Line2D
    fig,ax=plt.subplots(figsize=(12,7));lon,lat=60.60,56.84
    offsets={'Омск':(8,8),'Саратов':(-72,-14),'Нижний Новгород':(-92,9),
             'Оренбург':(-65,-22),'Самара':(-50,10),'Абакан':(10,10),
             'Минеральные Воды':(7,-23),'Новокузнецк':(8,-16),'Томск':(8,9),'Ставрополь':(-68,10)}
    for r in (r for r in records if r['hypothesis']=='H2'):
        ax.plot([lon,r['lon']],[lat,r['lat']],color='#b51f3b',lw=1.8,ls='-' if r['rw_evidence'] else '--',alpha=.8)
        ax.scatter(r['lon'],r['lat'],s=35,c='#263746',zorder=4)
        ax.annotate(r['destination'],(r['lon'],r['lat']),xytext=offsets[r['destination']],textcoords='offset points',fontsize=10)
    ax.scatter(lon,lat,s=90,marker='s',c='#b51f3b',zorder=5)
    ax.annotate('Екатеринбург\nсуществующая база',(lon,lat),xytext=(0,18),ha='center',textcoords='offset points',weight='bold',fontsize=12)
    ax.set(xlim=(38,98),ylim=(41,61),xlabel='Долгота, ° в.д.',ylabel='Широта, ° с.ш.',title='H2: десять прямых пар · программа 2028 года')
    ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
    ax.legend(handles=[Line2D([0],[0],color='#b51f3b',label='Есть свидетельство Red Wings; добавляем частоты'),Line2D([0],[0],color='#b51f3b',ls='--',label='Нет свидетельства в выборке; статус требует проверки')],loc='lower right',fontsize=9)
    fig.text(.08,.035,'План: +2 оборота/неделю на пару; SJ-100, 2 рабочих + 1 резерв. Линии — проект, не трассы полёта.\nИсточник: results/strategy/route_assumptions.csv; координаты округлены. Историческое свидетельство не доказывает выполнение сегодня.',fontsize=9)
    fig.tight_layout(rect=(0,.09,1,1))
    fig.savefig(FIG/'selected_route_map.png',dpi=180)
    fig.savefig(ROOT/'submission/route-map.pdf')
    plt.close(fig)
    route_pool_figure()


def route_pool_figure():
    """График исследовательского пула из сохранённой таблицы маршрутов."""
    rows=read('results/routes/route_candidates.csv')
    categories=['passengers_and_frequency','passengers_only','frequency_only',
                'single_date_only','relative_or_qualitative_only']
    labels=['Пассажиры и частота','Только пассажиры','Только частота',
            'Только одиночная дата','Относительные / качественные сведения']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig,ax=plt.subplots(figsize=(11,6.2))
    for h,shift,color in [('H1',-.18,'#346989'),('H2',.18,'#b76a37')]:
        values=[sum(r['hypothesis']==h and r['coverage_class']==c for r in rows) for c in categories]
        bars=ax.barh([i+shift for i in range(len(categories))],values,height=.33,color=color,label=h)
        ax.bar_label(bars,padding=4)
    ax.set_yticks(range(len(categories)),labels)
    ax.invert_yaxis()
    ax.set_xlim(0,max(sum(r['hypothesis']==h and r['coverage_class']==c for r in rows)
                      for h in ('H1','H2') for c in categories)+1)
    ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_xlabel('Число пар городов; категории не пересекаются')
    ax.set_title('Типы данных в исследовательском пуле маршрутов')
    ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True);ax.legend(loc='lower right')
    fig.text(.03,.025,'Источник: results/routes/route_candidates.csv. Исследовательский пул, 10.11.2026; частота — опубликованный план.',fontsize=9)
    fig.tight_layout(rect=(0,.07,1,1))
    FIG.mkdir(parents=True,exist_ok=True)
    fig.savefig(FIG/'route_evidence_coverage.png',dpi=160);plt.close(fig)

def controls(records,rw,market):
    """Counterfactuals separate analog, fleet, timing and cost effects."""
    import copy
    rows=[]
    for design in ('legacy_3RT','common_3RT','selected_2RT','matched_block_116h','low_analog','high_analog','equal_displacement','zero_transfers','H1_demand_up25_H2_down25'):
        rr=copy.deepcopy(records)
        for r in rr:
            h=r['hypothesis']
            if design=='legacy_3RT':r['annual_local_target']=r['legacy_local_target']
            if design in ('legacy_3RT','common_3RT') and h=='H2':r['added_roundtrips_week']=3
            if design=='matched_block_116h' and h=='H2' and r['destination'] in ('Омск','Саратов','Нижний Новгород','Оренбург'):r['added_roundtrips_week']=3
            if design in ('low_analog','high_analog'):r['annual_local_target']=(27510 if design=='low_analog' else 106309)*POLICY['common_capture']
            if design=='H1_demand_up25_H2_down25':r['annual_local_target']*=1.25 if h=='H1' else .75
        saved=copy.deepcopy(CASES)
        try:
            if design=='equal_displacement':
                for c in CASES.values():c['new_displacement']=c['existing_displacement']
            if design=='zero_transfers':
                for c in CASES.values():c['transfer_demand']=0
            rot=rotations(rr)
            for case in CASES:
                _,ss,_=calculate(rr,rot,rw,market,case,2028)
                rows.extend(dict(control=design,**s) for s in ss)
        finally:
            CASES.clear();CASES.update(saved)
    # Same full launch and resource basis in 2027; main comparison retains pilot.
    for c in CASES:
        _,ss,_=calculate(records,rotations(records),rw,market,c,2027,full_network=True)
        rows.extend(dict(control='same_full_launch_2027',**s) for s in ss)
    write('controlled_comparison.csv',rows)
    stress=[]
    for case in CASES:
        for name,f,d,cost,allcost,active,marketfactor in [
            ('reference',1,1,130000,1,1,1),('combined_shock',.8,.75,160000,1,1,1),
            ('all_costs_plus25',1,1,130000,1.25,1,1),('H2_fare_minus20',.8,1,130000,1,1,1),
            ('delivery_July2028',1,1,130000,1,.5,1),('market_plus5',1,1,130000,1,1,1.05),
            ('market_minus5',1,1,130000,1,1,.95),('no_aircraft_2028',1,1,130000,1,0,1)]:
            _,ss,_=calculate(records,rotations(records),rw,market,case,2028,
                                 fare_factor=f if name!='H2_fare_minus20' else 1,demand_factor=d,block_cost=cost)
            for s in ss:
                if name=='H2_fare_minus20' and s['hypothesis']=='H2':s['incremental_revenue_rub']*=f
                # Contractual annual fixed obligations remain in a delivery shock;
                # zero aircraft case incurs committed startup, but no aircraft rent.
                if active<1:
                    for k in ('net_passenger_segments','gross_segments','net_oneway_journeys','transfer_net_journeys','incremental_revenue_rub','block_hours','departures','variable_cost_rub'):s[k]*=active
                if name=='no_aircraft_2028':
                    s['fixed_cost_rub']=0;s['startup_rub']=POLICY[s['hypothesis']+'_startup_rub']
                elif name=='delivery_July2028':s['startup_rub']=POLICY[s['hypothesis']+'_startup_rub']
                costs=allcost*(s['variable_cost_rub']+s['fixed_cost_rub']+s['startup_rub'])
                s['contribution_rub']=s['incremental_revenue_rub']-costs
                s['share_after_percent']=100*(rw+s['net_passenger_segments'])/(market*marketfactor)
                s['share_delta_pp']=s['share_after_percent']-100*rw/market
                stress.append(dict(stress=name,market_factor=marketfactor,active_year_fraction=active,total_cost_rub=costs,**s))
    write('stress_tests.csv',stress)
    _,baseline,_=calculate(records,rotations(records),rw,market,'base',2028)
    _,cautious,_=calculate(records,rotations(records),rw,market,'cautious',2028)
    lo=records[0]['annual_local_target'];hi=106309*POLICY['common_capture']
    for _ in range(60):
        midpoint=(lo+hi)/2
        trial=[dict(r,annual_local_target=midpoint) for r in records]
        _,s,_=calculate(trial,rotations(trial),rw,market,'base',2028)
        if s[0]['contribution_rub']>s[1]['contribution_rub']:hi=midpoint
        else:lo=midpoint
    write('decision_thresholds.csv',[
        dict(parameter='H2_only_fare_multiplier_equal_H1_base',value=(baseline[0]['contribution_rub']+baseline[1]['variable_cost_rub']+baseline[1]['fixed_cost_rub'])/baseline[1]['incremental_revenue_rub'],unit='multiplier',condition='H1 base unchanged; H2 passengers and costs unchanged'),
        dict(parameter='common_local_target_equal_cash_base',value=(lo+hi)/2,unit='segments/route/year before capacity and displacement',condition='both hypotheses same local target; transfer demand fixed; base 2028'),
        dict(parameter='H2_cautious_block_cost_zero_cash',value=130000+cautious[1]['contribution_rub']/cautious[1]['block_hours'],unit='RUB/block-hour',condition='cautious 2028; other assumptions unchanged')])

def report(records,rot,ss,sens,rw,market):
    def get(h,c='base',y=2028):return next(r for r in ss if (r['hypothesis'],r['scenario'],r['year'])==(h,c,y))
    b1,b2,c2=get('H1'),get('H2'),get('H2','cautious')
    summary=table(['Гипотеза','Сценарий','Год','Доп. сегменты, тыс.','Выручка, млн ₽','Δ доли, п.п.','Бортов с резервом','Результат, млн ₽'],[[r['hypothesis'],CASES[r['scenario']]['label'],r['year'],f"{r['net_passenger_segments']/1000:.1f}",f"{r['incremental_revenue_rub']/1e6:.0f}",f"{r['share_delta_pp']:.3f}",r['total_aircraft'],f"{r['contribution_rub']/1e6:.0f}"] for r in ss])
    body=f'''# Стратегия Red Wings

**Выбираем H2: десять прямых пар из Екатеринбурга, по два дополнительных оборота в неделю.**
Для полной сети нужны два рабочих SJ-100 и один резервный. В 2027 году начинаем
с трёх пар — Омск, Саратов и Минеральные Воды — после фактической передачи самолётов.

В 2028 H2 даёт {b2['net_passenger_segments']/1000:.1f} тыс. дополнительных сегментов
и {b2['incremental_revenue_rub']/1e9:.2f} млрд ₽ выручки в базовом сценарии;
{c2['net_passenger_segments']/1000:.1f} тыс. и {c2['incremental_revenue_rub']/1e9:.2f} млрд ₽ — в осторожном.
H1 даёт больше сегментов, но уступает по денежному результату обоих сценариев.
При выборе мы отдаём приоритет осторожной экономике и возможности ограничиться пилотом.

## Обе гипотезы

H1 — новая база в Уфе, восемь плеч и четыре пересадочные связки.
H2 — десять прямых пар из существующей базы Екатеринбург.

{summary}

Результат — дополнительная билетная выручка минус расходы программы, включая
резерв и запуск. Это не чистая прибыль. Субсидии и дополнительные услуги не включены.
В 2027 у H2 пилот трёх пар, у H1 полный запуск: их первый год различается по масштабу.
В 2028 обе полные программы используют три самолёта с резервом.

## Данные и спрос

Входы: [data/processed/](../data/processed/README.md).
Публикации: [каталог источников](../data/SOURCE_MANIFEST.md).
[S08](../data/SOURCE_MANIFEST.md#s08): 2,7 млн пассажиров Red Wings за 2025 год;
[S03](../data/SOURCE_MANIFEST.md#s03): 108,85 млн пассажиров российских авиакомпаний.

Для обеих H взят одинаковый сценарный ориентир по двум линиям
[S23](../data/SOURCE_MANIFEST.md#s23), 2025 год: Омск—Казань — 27 510 пассажиров,
Омск—Новосибирск — 106 309. Геометрическое среднее ×40% даёт около 21,6 тыс.
местных сегментов на пару в год до ограничения креслами и вычета своих продаж.
40% — допущение команды; это не измеренный O&D выбранных пар.
В прежнем варианте H1 и H2 получали разные аналоги; его расчёт сохранён в контрольной таблице.

Для пары: кресла = 2 × обороты в неделю × рабочие недели ×100.
Продажи = минимум спроса с освоением и кресел с потолком загрузки.
Затем вычитается перенос пассажиров с других рейсов Red Wings.

| Параметр | Базовый | Осторожный |
|---|---:|---:|
| Спрос относительно ориентира | 100% | 75% |
| Потолок загрузки | 85% | 72% |
| Тариф относительно базового | 100% | 90% |
| Освоение полной программы 2028 | 100% | 90% |
| Свои пассажиры на парах Red Wings | 20% | 35% |
| Свои пассажиры на остальных парах | 8% | 15% |

На всех парах H2 считаются только добавленные частоты. Загрузка нового рейса
сама по себе не доказывает прирост: на пилоте сравниваем все продажи компании
на паре с сопоставимым сезоном, включая прежние частоты и собственные пересадки.

## Пересадки и доля рынка

H1 соединяет через Уфу Нижний Новгород—Красноярск, Саратов—Абакан,
Самару—Новосибирск и Минеральные Воды—Омск. В каждой связке две стыковки
одного направления и одна обратного в неделю; время стыка — 60 минут.
Местные продажи имеют приоритет, редкое направление ограничивает трансфер.

Одна поездка занимает два кресла на разных сегментах и приносит один сквозной
билет: 75% суммы тарифов двух плеч. Цель связки — 27 510 ×35% поездок в год;
осторожно — ×0,55. Собственное замещение пересадок — 15%/30%.
Предполагается, что перенесённые свои поездки тоже занимали два сегмента.
[Расчёт пересадок](../results/strategy/transfer_scenarios.csv).

Прирост доли = дополнительные перевезённые сегменты /108,85 млн ×100 п.п.
Это сравнение на фиксированном рынке 2025 года. Сегменты и поездки не означают
уникальных людей. Аэропортовый поток не используется в знаменателе.
В таблицах также есть растущий знаменатель и изменение рынка на ±5%.

## Флот и расходы

H1: 116,4 блок-ч/неделю; H2: 100,8. Обе сети: два рабочих борта и один резерв.
В контрольном варианте H2 с третьим оборотом на четырёх коротких парах —
116,2 блок-ч/неделю при том же флоте. Три оборота на всех десяти парах требуют
четырёх бортов с резервом и ухудшают осторожную экономику.

[Недельные ротации](../results/strategy/weekly_rotations.csv): возврат в базу
на ночь, до 10,5 блок-ч и 14 часов занятости борта в день; оборот на конце
45 минут, в базе — 60 минут. Внутри программы пустые подлёты не требуются.
Дальность с загрузкой, слоты, ТО и сменные экипажи согласуются до продажи билетов.
Расчётный резерв не гарантирует выполнение при нескольких длительных отказах.

Расходы — допущения: 130 тыс. ₽/блок-ч, 20 тыс. ₽/вылет,
75 млн ₽/борт/год. База H1 — 120 млн ₽/год и 150 млн ₽ запуска;
расширение H2 — 20 млн ₽/год и 20 млн ₽ запуска. Амортизация поверх лизинга
не добавлена. Годовые фиксированные расходы при обычном запуске пропорциональны
активным неделям; стресс задержки сохраняет годовые обязательства.

## Когда выбрать H1 или отложить запуск

Базовый результат H1 — {b1['contribution_rub']/1e6:.0f} млн ₽, H2 — {b2['contribution_rub']/1e6:.0f} млн ₽.
Разрыв невелик: снижение только тарифа H2 примерно на 2% меняет денежный выбор.
Единый местный ориентир около 22,2 тыс. сегментов на пару вместо 21,6 тыс.
также выводит H1 вперёд в базе. На высоком общем аналоге H1 лучше в обоих сценариях.
Её преимущества — больший объём и дополнительные пересадочные связи;
цена — новая база и зависимость от стыковок.

На низком аналоге осторожно убыточны обе H. Совместный шок тарифа −20%, спроса
−25% и блок-часа 160 тыс. ₽ также может сделать обе программы убыточными.
Тогда сокращаем частоты или переносим запуск. При задержке до июля 2028
поток и переменные расходы сокращаются вдвое, фиксированные годовые расходы
сохраняются; без самолётов пассажирский эффект равен нулю.

[Контрольные сравнения](../results/strategy/controlled_comparison.csv),
[стрессы](../results/strategy/stress_tests.csv),
[пороги смены решения](../results/strategy/decision_thresholds.csv).

## Материалы и запуск

[Маршруты с источником и ресурсом](../submission/routes.md),
[дорожная карта и конкуренты](09-launch-roadmap.md),
[PDF для защиты](../submission/README.md).

Расчёт: `uv run --frozen --no-sync python scripts/compare_growth_strategies.py`.
Проверка арифметики и ротаций: `uv run --frozen --no-sync python scripts/check_strategy.py`.
'''
    (ROOT/'analysis/08-strategy-decision.md').write_text(body,encoding='utf-8')


if __name__=='__main__':main()
