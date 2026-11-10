"""Scenario decision, not an O&D forecast. Python 3.14; no network/raw access.
uv run --frozen --no-sync python scripts/compare_growth_strategies.py
"""
import csv
import json
import math
import re
import sys
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
POLICY = dict(seats=100, added_roundtrips_week=3, weeks_2028=52,
              destination_turn_h=.75, base_turn_h=1., max_block_day=10.5,
              max_elapsed_day=14., spare_aircraft=1, fixed_aircraft_rub_year=75_000_000,
              variable_rub_block_h=130_000, airport_rub_departure=20_000,
              H1_fixed_rub_year=120_000_000, H2_fixed_rub_year=20_000_000,
              H1_startup_rub=150_000_000, H2_startup_rub=20_000_000,
              transfer_fare_factor=.75)


def read(p):
    with (ROOT / p).open(encoding='utf-8-sig', newline='') as f:
        return [dict(r, csv_file=p, csv_row=i) for i, r in enumerate(csv.DictReader(f), 2)]


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


def inputs():
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
                                added_roundtrips_week=3, rw_evidence=existing,
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
                              source_row=r['source_row'],source_locator=r['source_locator'],source_url=r['source_url'],
                              core_file=r['csv_file'],core_row=r['csv_row'],limitations=r['limitations']))
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


def calculate(records, rot, rw, market, case, year, fare_factor=1., demand_factor=1., block_cost=None):
    c=CASES[case]; weeks=POLICY['weeks_2028'] if year==2028 else c['weeks_2027']
    ramp=c['ramp_2028'] if year==2028 else c['ramp_2027']
    # Three-route H2 pilot in 2027; all ten routes in 2028.
    effective=[r for r in records if year==2028 or r['hypothesis']=='H1' or
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
        assert p>=0
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
                            break_even_fare_multiplier=(variable+fixed+startup)/revenue,
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
        if k=='added_roundtrips_week':return 'roundtrips/route/week'
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
    fig.text(.04,.02,'Источник: results/strategy/route_assumptions.csv. Координаты округлены как допущение; линии не являются трассами полёта.\nH2: 3 дополнительных оборота/неделю на каждой из 10 пар. H1: 3 оборота/неделю на каждой из 8 пар.',fontsize=9)
    fig.tight_layout(rect=(0,.08,1,.95));fig.savefig(FIG/'strategy_route_map.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    rr=[r for r in summaries if r['year']==2028]
    labels=[r['hypothesis']+' / '+CASES[r['scenario']]['label'] for r in rr]
    bars=ax.bar(labels,[r['net_passenger_segments']/1000 for r in rr],color=['#346989','#b76a37']*2)
    ax.bar_label(bars,fmt='%.1f');ax.set_ylabel('Дополнительные пассажиро-сегменты, тыс. за 52 недели');ax.set_title('Сценарный эффект 2028 года после вычета замещения')
    fig.text(.05,.02,'Источник: hypothesis_comparison.csv. Сценарные оценки, не наблюдаемый O&D.',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,1));fig.savefig(FIG/'strategy_comparison.png',dpi=160);plt.close(fig)


def report(records,rot,ss,sens,rw,market):
    def row(r):
        return [r['hypothesis'],CASES[r['scenario']]['label'],r['year'],f"{r['net_passenger_segments']:,.0f}",f"{r['incremental_revenue_rub']/1e6:.1f}",f"{r['share_delta_pp']:.3f}",r['total_aircraft'],f"{r['contribution_rub']/1e6:.1f}"]
    summary=table(['Вариант','Сценарий','Год','Доп. сегменты, чел.','Доп. выручка, млн ₽','Прирост доли, п.п.','Бортов с резервом','Условный результат, млн ₽'],[row(r) for r in ss])
    route_table=table(['Вариант','Пара','Блок-часов в одну сторону*','Тариф*, ₽','Местная цель*, чел./год','Доп. оборотов/нед.'],[[r['hypothesis'],r['origin']+' — '+r['destination'],r['block_h_oneway'],r['fare_rub_oneway'],round(r['annual_local_target']),3] for r in records])
    fleet=table(['Вариант','Блок-ч/нед.','Активных','Резерв','Всего','Оборотов/нед.'],[[h,round(sum(r['roundtrip_block_h'] for r in rot if r['hypothesis']==h),1),max(r['tail'] for r in rot if r['hypothesis']==h),1,max(r['tail'] for r in rot if r['hypothesis']==h)+1,sum(r['hypothesis']==h for r in rot)] for h in ('H1','H2')])
    sensitivity=table(['Изменение к базовому 2028','H1: результат, млн ₽','H2: результат, млн ₽'],[[name]+[f"{next(r['contribution_rub'] for r in sens if r['test']==name and r['hypothesis']==h)/1e6:.1f}" for h in ('H1','H2')] for name in dict.fromkeys(r['test'] for r in sens)])
    b1=next(r for r in ss if (r['hypothesis'],r['scenario'],r['year'])==('H1','base',2028))
    b2=next(r for r in ss if (r['hypothesis'],r['scenario'],r['year'])==('H2','base',2028))
    c2=next(r for r in ss if (r['hypothesis'],r['scenario'],r['year'])==('H2','cautious',2028))
    threshold_cost=130000+c2['contribution_rub']/c2['block_hours']
    reversal=(b1['contribution_rub']+b2['variable_cost_rub']+b2['fixed_cost_rub'])/b2['incremental_revenue_rub']
    body=f'''# Решение кейса: прямые рейсы из Екатеринбурга

**Выбираем H2: десять прямых региональных линий из Екатеринбурга с добавлением частот.**
Это сценарное инвестиционное решение: H2 использует существующую базу, допускает
поэтапный запуск и отказ от слабой пары. H1 требует новой инфраструктуры и опирается
на не подтверждённые O&D стыковки. Расчёт ниже не превращает допущения в прогноз.
При отрицательном результате в осторожном сценарии полную сеть нельзя запускать
автоматически: сначала пилот и проверка порогов. Выбранная стратегия — H2, а не
безусловное обязательство выполнять все частоты при любых тарифах и затратах.

## Сравнение

{summary}

Выручка — дополнительная билетная выручка после вычета замещения собственных рейсов,
в условных номинальных рублях планирования. Не включает субсидии, ancillary и НДС-модель.
Условный результат — выручка минус заданные ниже расходы, включая стартовые затраты
только в 2027 году; это не бухгалтерская прибыль, NPV или доказанная окупаемость.
Полная детализация: [таблица сравнения](../results/strategy/hypothesis_comparison.csv).
В 2027 у H2 рассчитан пилот трёх пар (Омск, Саратов, Минеральные Воды),
а в 2028 — все десять. H1 рассчитана как запуск восьми плеч нового хаба.
Это разные траектории запуска, не равные по масштабу проекты первого квартала работы.

В базовом 2028 H2 даёт {b2['net_segments_per_aircraft']/1000:.1f} тыс. дополнительных
сегментов на борт с резервом против {b1['net_segments_per_aircraft']/1000:.1f} тыс. у H1.
Это разные бюджеты: H2 требует на один самолёт больше. В осторожном варианте H1
имеет чуть больше сегментов на борт (33,8 против 31,8 тыс.), но хуже условный
денежный результат. Выбор не основан на абсолютном объёме без учёта ресурса.

![Сценарное сравнение](figures/strategy_comparison.png)

## Факты и основа расчёта

Использованы прежние core и маршрутный пул TASK-03A; нового аудита и сбора нет.
Факты: Red Wings — {rw/1e6:.1f} млн пассажиров за 2025 год (S08, airlines/metrics.csv:5);
рынок — {market/1e6:.2f} млн человек за 2025 год (S03, market/S03_image13.csv; provenance в core/market.csv).
Исходная доля — {100*rw/market:.3f}%. ТЗ допускает оценки, определяет Екатеринбург
как существующую базу и ожидает SJ-100 не ранее второй половины 2027 года.
Это не подтверждение конкретных поставок Red Wings. Поставка нужного числа бортов — условие сценария.
Факты с периодами, единицами и прямыми ссылками — [fact_references.csv](../results/strategy/fact_references.csv).

Аналоги местного спроса — наблюдаемые потоки линий 2025 года: Омск — Новосибирск
106 309 человек (S23, airports/metrics.csv:8), Омск — Казань 27 510 (S23:13),
Самара — Минеральные Воды 47 000 (S36:127, период по содержанию с прежней оговоркой),
Екатеринбург — Минеральные Воды 211 000 (S40:174). Это не конечный O&D.
Для каждой пары исходный CSV, строка, локатор и коэффициенты записаны в
[route_assumptions.csv](../results/strategy/route_assumptions.csv).

Свидетельство Red Wings хотя бы в одном направлении/старом анонсе трактуется
консервативно как существующая линия: её полный поток не засчитывается. H2 включает
семь пар из прежнего пула плюс Новокузнецк и Томск из уже имеющегося S19 и
Ставрополь из S18; вместо непроверенных ротаций Самара — Минеральные Воды и
Омск — Новосибирск используются пары непосредственно из базы. На всех парах
моделируются только **+3 оборота/неделю**, существующие частоты не восстанавливаются.
Отсутствие Red Wings в выборке для Минеральных Вод или новых плеч Уфы не доказывает
их новизну: предусмотрен вычет замещения и чувствительность спроса.

## Сеть и спрос: все значения со звёздочкой — допущения

{route_table}

В H1 новые плечи кроме Уфа — Красноярск расширяют исследовательский пул по аналогии;
это проектируемые пары, а не обнаруженные действующие рейсы. Уфа — Екатеринбург
исключена: для нового хаба важнее западный подвоз, а не перенос работы существующей базы.
Плановые обратные сегменты здесь заданы явно как часть проекта; они не добавлены в фактическую core.

Местная годовая цель = поток аналога × масштаб × доля захвата дополнительной ёмкостью.
H2: за основу обычно взяты 106 309 человек; масштаб 0,75–1,0 и захват 27–30%,
для Минеральных Вод — собственный наблюдаемый поток ×16%. H1: менее крупный аналог
27 510 человек ×масштаб 0,9–1,2 ×60%; для Минеральных Вод — 47 000 ×45%.
Разница отражает гипотезу: добавочные частоты зрелой базы способны привлечь больше
местных поездок, чем новая база. Это уязвимое допущение; тест ±25% спроса приведён ниже.
Коэффициенты не оценены регрессией; они задают проверяемые коммерческие цели,
а не доказывают наличие необслуженного рынка. Верхний предел загрузки также не является измеренным спросом.

В базовом сценарии: 100 кресел, верх загрузки 85%, вычет перемещения с собственных
рейсов 20% на существующих линиях и 8% на остальных. Осторожный: местная цель ×0,75,
верх загрузки 72%, тариф ×0,90, вычет 35% и 15%. Для 2028 осторожного дополнительно
применён коэффициент освоения 0,90; базовый год — 1,0. Эти понижения применяются вместе.
Перемещение с рейсов конкурентов считается приростом Red Wings, с собственных — вычитается.
Тарифы 7–16,5 тыс. ₽ на сегмент — допущения по длине плеча, не извлечённые цены продажи;
это реализованный билетный доход на занятого пассажира в условном учёте модели.

## Как учтены пересадки H1

Четыре пары конечных городов: Нижний Новгород — Красноярск, Саратов — Абакан,
Самара — Новосибирск, Минеральные Воды — Омск, все через Уфу. В каждой связке
три стыковки в неделю: две одного направления и одна обратного. В модели направления
спроса симметричны; более редкое направление ограничивает общий объём. Стыковка
60 минут, минимум в допущениях 60 минут; это требует сквозного билета/багажа и
согласования MCT аэропортом. Наличие такого сервиса сейчас не заявляется.

Цель одной связки = 27 510 ×35% = 9 628,5 поездки в год до ограничений ёмкости.
В осторожном варианте ×0,55; вычет собственного замещения 15% / 30% соответственно.
Каждая поездка занимает кресло на обоих сегментах; местные пассажиры распределяются
равномерно по направлениям/дням. Модель ограничивает трансфер остатком обоих плеч
и ёмкостью более редкого направления. Это требует отдельной проверки сезонного пика.
В осторожном сценарии фактически размещённых пересадок может быть больше, чем в
базовом: снижение местной загрузки освобождает кресла на редких стыковках.
Это эффект приоритета местных пассажиров в алгоритме, не рост измеренного спроса.
Сквозной тариф = 75% суммы двух сегментных тарифов. Выручка распределяется по плечам
пропорционально тарифам и учитывается один раз на поездку. Подробности —
[transfer_scenarios.csv](../results/strategy/transfer_scenarios.csv).

В доле рынка используется прирост перевезённых пассажиро-сегментов (пересадочный
пассажир занимает два рейса), а число односторонних поездок дано отдельно. Допущение
сопоставимости с авиакомпанейской статистикой отмечено явно; аэропортовые итоги
не подставляются в знаменатель. Нельзя подавать сегменты как уникальных людей.
Прирост доли = ΔP /108,85 млн ×100 п.п. Это фиксированный рынок 2025 года как
контрольный сценарий, не прогноз 2028. В CSV также есть вариант знаменателя
108,85 млн + ΔP: весь прирост считается расширением рынка. Рост рынка на 5% при
неизменной исходной доле уменьшает показанный добавочный эффект в п.п. в 1,05 раза.

## Обороты, флот и сроки

{fleet}

Недельные плановые обороты сохранены в [weekly_rotations.csv](../results/strategy/weekly_rotations.csv).
Таблица флота выше относится к полной сети 2028 года. Пилот H2 2027 года требует
один работающий борт и один резервный; план — [pilot_2027_rotations.csv](../results/strategy/pilot_2027_rotations.csv).
Все времена в единой шкале часов базы; первый вылет не раньше 06:00, окончание
не позднее 20:00. Блок-время задано симметричным по направлениям с запасом как
сценарная инженерная оценка; его не вычисляли вычитанием местных часов расписания.
На удалённом конце 45 минут, между оборотами в базе 60 минут. Ограничения на
воздушное судно: до 10,5 блок-часа и 14 часов занятости в день. Это не норма рабочего
времени одного экипажа: длинные дни требуют сменных экипажей. Каждый борт возвращается
на ночь; резерв — ещё один SJ-100 сверх выполняющих программу. Резерв не генерирует
выручку, но его содержание включено. Свободные часы существующего парка не присвоены.
Потребность — отдельный ресурс нового проекта, не весь флот Red Wings и не число
фактически заказанных самолётов. Резерв не позволяет обещать выполнение при любой
серии отказов; календарь ТО, ограничения аэродромов, дальность с резервом топлива
и допуск конкретной модификации SJ-100 остаются предпусковыми проверками.

H1: связки выполняются на чередующихся днях; первый оборот подвозит в Уфу,
второй вывозит. Поэтому не предполагаются ежедневные стыковки всех со всеми.
H2: алгоритм размещает дополнительные обороты по дням и бортам, проверяя названные
пределы. Он даёт допустимый план, не математически доказанный минимум флота.
Обеим гипотезам предоставлен одинаковый резерв и одинаковые нормативы.

Запуск базового варианта — 01.10.2027, 13 рабочих недель, освоение спроса 65%.
Осторожного — 01.12.2027, четыре недели, освоение 50%. Это плановые даты после
второй половины 2027 года, условные на поставке и допусках. Оба варианта используют
52 недели в 2028 году: оставшиеся календарные дни не монетизируются. Полная сеть
требует весь указанный ресурс к 2028 году; в 2027 H2 начинает с двух бортов с резервом.
Сдвиг на 01.01.2028 обнуляет эффект 2027 при сохранении предпусковых затрат;
каждый потерянный рабочий месяц 2028 сокращает поток примерно на 1/12 при прочих равных.

![Карта вариантов](figures/strategy_route_map.png)

## Затраты и чувствительность решения

Все расходы — диапазонные предположения для сравнения, не котировки поставщиков:
130 тыс. ₽/блок-час (топливо, переменное ТО и переменная часть экипажей),
20 тыс. ₽/вылет (аэропорт/обслуживание), 75 млн ₽/самолёт/год (лизинг, страхование,
фиксированные расходы самолёта). Дополнительные фиксированные расходы базы:
H1 120 млн ₽/год, H2 20 млн ₽/год; включают местный персонал/сменные экипажи,
планирование и инфраструктуру. Разовые затраты H1 150 млн ₽, H2 20 млн ₽ в год запуска.
Годовые фиксированные расходы в расчёте пропорциональны активным неделям: это
предположение о поэтапных договорах, не гарантированная экономия при задержке.
Налоги, дисконтирование, финансирование, разница капитализированных и текущих
расходов не моделируются; амортизация отдельно не добавляется поверх лизинга.

{sensitivity}

В осторожном H2 результат 2028 обнуляется примерно при {threshold_cost/1000:.1f} тыс. ₽/блок-час
вместо 130 тыс. при остальных прежних условиях, либо при снижении осторожного
тарифа ещё на {(1-c2['break_even_fare_multiplier'])*100:.1f}%. Эти изменения нельзя
складывать независимо: одновременный шок потребует меньшего отклонения каждого.
Если тарифы только H2 окажутся ниже базового плана более чем на {(1-reversal)*100:.1f}%,
а все условия H1 сохранятся базовыми, H1 обойдёт H2 по условному результату.
Это конкретная граница пересмотра, а не утверждение безусловного превосходства H2.

Пороговый множитель реализованного тарифа для каждого сценария включён в CSV
(`break_even_fare_multiplier`). Он показывает тариф для покрытия принятых расходов
при неизменном объёме, а не рыночную возможность повысить цену без потери пассажиров.
Снижение спроса уменьшает доходы, но не расходы уже выставленного расписания.
Выбор H2 основан на меньшей зависимости от стыковок и новой базы и более сильном
добавочном эффекте; положительная выручка не доказывает окупаемость. Если
осторожный вариант убыточен, это основание ограничить обязательства пилотом,
пересмотреть частоты/цены или отложить расширение, сохранив выбор H2.
Субсидии не использованы как условие прибыльности. Сравнение не оптимизирует все
возможные сети: это решение между двумя конкретными воспроизводимыми проектами.

## План реализации и правило остановки

- До конца 2026: согласовать коммерческие цели, поставочный сценарий и резерв;
  запросить условия аэропортов/лизинга. Это действия внедрения, не новый сбор для текущего расчёта.
- I полугодие 2027: подготовить дополнительные экипажи и продажи, проверить дальность,
  обороты и договоры по выбранным парам. Без готовых бортов рейсы не обещать.
- С октября 2027 при поставке: пилот на трёх парах — Омск, Саратов, Минеральные Воды;
  8–12 недель контроля. При декабрьском старте контроль продолжается в I квартале 2028.
- 2028: разворачивать все десять пар только при покрытии фактических дополнительных
  расходов. На слабых парах менять сезонность/частоту, а не открывать новую базу.
- Еженедельно: дополнительные пассажиры с вычетом переноса собственных продаж,
  реализованный тариф, загрузка, выполненные блок-часы и расходы. За 8 недель
  отрицательного операционного вклада пары — пересмотр, при отсутствии улучшения
  за следующие 4 недели — снятие добавленных частот. Числа 8/4 недели — управленческое допущение.

## Воспроизводимость

`uv run --frozen --no-sync python scripts/compare_growth_strategies.py` (Python 3.14).
Исходники не меняются, сеть не используется. Параметры — [assumptions.csv](../results/strategy/assumptions.csv),
экспорт параметров генерируется из констант скрипта; для нового расчёта менять их в коде,
а не редактировать выходной CSV.
расчёты по парам — [route_scenarios.csv](../results/strategy/route_scenarios.csv),
чувствительность — [sensitivity.csv](../results/strategy/sensitivity.csv).
Скрипт проверяет частоты каждого плеча, отсутствие перекрытий бортов, обороты,
лимиты занятости/блок-часов, баланс трансферных кресел и согласование выручки.
Округление применяется только для показа; дробные пассажиры — математическое
ожидание сценария, не точные люди. Паспорт следует структуре локального шаблона,
неизвестные сведения о составе команды и контактах явно оставлены для заполнения.
'''
    (ROOT/'analysis/08-strategy-decision.md').write_text(body,encoding='utf-8')
    selected=[r for r in ss if r['hypothesis']=='H2']
    passport=f'''# Паспорт предложения: прямые региональные рейсы Red Wings

Кейс 5 «Новый хаб или прямые рейсы?». Выбор: **H2, Екатеринбург, 10 пар**.
Команда и контакт представителя: не предоставлены; заполняются участниками перед сдачей.

## 1. Команда и роли
Состав и личные роли не предоставлены. ChatGPT/Codex использован как помощник
анализа и программирования; ответственность за решение и защиту несёт команда.

## 2. Проблема
На стагнирующем рынке Red Wings нужно увеличить долю при ограниченном новом флоте.
Новый хаб требует инфраструктуры и пересадочного спроса, который пока не измерен.

## 3. Решение и пользователи
Предлагаем добавлять частоты прямых региональных рейсов из существующей базы
Екатеринбург. Результат предназначен команде кейса и экспертам для выбора стратегии
и ограничения обязательств при неопределённой поставке SJ-100.

## 4. Проверка
Сопоставлены H1 — новый хаб в Уфе (8 плеч) и H2 — 10 прямых пар из Екатеринбурга.
Проверены сценарии 2027/2028, обороты с ночным возвратом, резервный борт,
ограничения ёмкости и чувствительность выручки/затрат.

## 5. Данные
Факты: S08 — 2,7 млн пассажиров Red Wings за 2025 год; S03 — 108,85 млн пассажиров
рынка за 2025 год; S19/S20/S17/S18 — опубликованные маршрутные свидетельства;
S23/S36/S40 — потоки линий 2025 года. Источники с локаторами — в таблицах приложения.
Синтетика команды: захват дополнительного спроса по аналогам, тарифы, блок-времена,
частоты, загрузка, замещение, затраты и даты поставок. Это сценарии, не факты и не O&D-прогноз.

## 6. Метод
Пассажиры = min(доступные кресла × верх загрузки; цель по аналогу ×освоение), затем
вычитается перенос собственных пассажиров. Для H1 добавлены только четыре
стыковочные пары с ограничениями обоих плеч. Выручка — нетто-пассажиры ×тариф;
прирост доли — дополнительные сегменты /108,85 млн ×100 п.п.
Связь с учёбой: программирование (Python, CSV), моделирование, арифметика долей,
задача размещения оборотов. Статус прохождения дисциплин командой не предоставлен.

## 7. Результат и приложения
{table(['Сценарий','Год','Доп. сегменты','Выручка, млн ₽','Δ доли, п.п.','Самолётов'],[[CASES[r['scenario']]['label'],r['year'],round(r['net_passenger_segments']),round(r['incremental_revenue_rub']/1e6,1),round(r['share_delta_pp'],3),r['total_aircraft']] for r in selected])}

Выбрана H2: готовая база, гибкий запуск и меньшая зависимость от непроверенных
стыковок. В 2027 рассчитан пилот трёх пар, в 2028 полная программа десяти. Положительная
выручка не означает прибыль: условные расходы и осторожный результат приведены в отчёте.
Приложения: [сравнение](../analysis/08-strategy-decision.md),
[таблицы](strategy/hypothesis_comparison.csv), [карта](../analysis/figures/strategy_route_map.png),
[код](../scripts/compare_growth_strategies.py). Запуск: `uv run --frozen --no-sync python scripts/compare_growth_strategies.py`.

## 8. Ограничения
Нет измеренного O&D, подтверждённых поставок, коммерческих тарифов и контрактных
затрат. Недельный план не подтверждает слоты, дальность и допуски экипажей.
Риск пересмотра решения показывается сценариями и чувствительностью. При слабых
продажах или задержке самолётов полную программу не запускать.

## 9. Дорожная карта
Конец 2026: согласование допущений и поставок. I полугодие 2027: договоры,
экипажи и технические проверки. С октября 2027, после поставки: пилот Омск,
Саратов, Минеральные Воды на 8–12 недель. В 2028: расширение до 10 пар только
при подтверждении спроса и покрытия фактических дополнительных затрат.
Доработка — реальные тарифы/расходы; практическая проверка — продажи и исполнение
пилота; применение — еженедельный пересмотр дополнительных частот коммерческой службой.

## 10. Вопросы экспертам
Какие условия поставок/резерва допустимы для планирования 2027 года?
Какие затраты базы и блок-часа реалистичны для принятия инвестиционного решения?
Достаточен ли предложенный пилот для проверки дополнительности спроса?
'''
    passport=re.sub(r'(?m)^(#{1,6} .+)\n(?!\n)',r'\1\n\n',passport)
    (ROOT/'results/project-passport.md').write_text(passport,encoding='utf-8')


if __name__=='__main__':
    main()
