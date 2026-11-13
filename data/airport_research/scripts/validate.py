#!/usr/bin/env python3
"""Validate extracted package using only Python 3.10+ standard library."""
from __future__ import annotations
import csv,collections,hashlib,json,math,pathlib,re,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1] if pathlib.Path(__file__).parent.name=='scripts' else pathlib.Path('build/data/airport_research').resolve()
ERRORS=[];WARN=[];CHECK=[];TABLE={}
def check(name,condition,detail=''):
 CHECK.append((name,'PASS' if condition else 'FAIL',detail))
 if not condition:ERRORS.append(name+': '+detail)
def read(rel):
 p=ROOT/rel
 try:
  with p.open(encoding='utf-8',newline='') as f:
   reader=csv.DictReader(f);rows=list(reader);fields=reader.fieldnames
  check('CSV '+rel,bool(rows) and bool(fields) and all(None not in r and all(v is not None for v in r.values()) for r in rows),'rows='+str(len(rows)))
  TABLE[rel]=(fields,rows);return rows
 except Exception as e:ERRORS.append(rel+': '+str(e));return []
def num(v):return float(v) if v!='' else None
for p in sorted(ROOT.rglob('*.csv')):read(str(p.relative_to(ROOT)))
def table(rel):return TABLE[rel][1]
def unique(rel,cols):
 rows=table(rel);keys=[tuple(r[k] for k in cols) for r in rows];check('KEY '+rel,len(keys)==len(set(keys)),','.join(cols))
REQUIRED={'airports.csv':'airport_iata,airport_name,city,region,country,latitude,longitude,timezone','airport_inventory.csv':'input_batch,input_record,airport_iata,raw_name,canonical_airport_iata,is_duplicate,duplicate_of,notes','airport_annual.csv':'airport_iata,year,passengers_total,passengers_domestic,passengers_international,transfer_passengers,transit_passengers','airport_monthly.csv':'airport_iata,year,month,passengers_total,passengers_domestic,passengers_international','airport_operations.csv':'airport_iata,year,metric,value,unit,value_qualifier,definition,source_id,source_locator,notes','airport_cargo.csv':'airport_iata,year,cargo_tonnes,mail_tonnes,cargo_mail_total_tonnes,scope,source_id,source_locator,notes','airport_routes.csv':'origin_iata,destination_iata,year,season,valid_from,valid_to,carrier,observation_type,weekly_departures,aircraft_type,seats_per_departure,source_id,source_locator,notes','airport_infrastructure.csv':'airport_iata,as_of_date,runway_id,runway_length_m,runway_width_m,runway_surface,pcn,terminal_capacity_pax_year,stand_count,operating_hours,restrictions,source_id,source_locator,notes','airline_market_annual.csv':'airline,year,passengers,market_share_pct,scope,source_id,source_locator,notes'}
for f,cols in REQUIRED.items():check('SCHEMA '+f,TABLE.get('processed/'+f,([],))[0]==cols.split(','))
airports=table('processed/airports.csv');aa=table('processed/airport_annual.csv');mm=table('processed/airport_monthly.csv');inv=table('processed/airport_inventory.csv');codes={r['airport_iata'] for r in airports}
check('24 unique airports',len(airports)==len(codes)==24);check('30 input records',len(inv)==30);check('6 duplicate positions',sum(r['is_duplicate']=='true' for r in inv)==6)
for rel,cols in [('processed/airports.csv',['airport_iata']),('processed/airport_inventory.csv',['input_batch','input_record']),('processed/airport_annual.csv',['airport_iata','year']),('processed/airport_monthly.csv',['airport_iata','year','month']),('processed/airport_operations.csv',['airport_iata','year','metric']),('processed/airport_cargo.csv',['airport_iata','year','scope']),('processed/airport_infrastructure.csv',['airport_iata','as_of_date','runway_id']),('processed/airline_market_annual.csv',['airline','year','scope']),('sources/sources.csv',['source_id']),('estimates/estimates.csv',['estimate_id']),('documentation/DATA_LINEAGE.csv',['entity_type','entity_id','period','metric'])]:unique(rel,cols)
unique('processed/airport_routes.csv',['origin_iata','destination_iata','year','season','valid_from','valid_to','carrier','source_id'])
check('48 airport years',len(aa)==48 and {(r['airport_iata'],r['year']) for r in aa}=={(i,str(y)) for i in codes for y in [2024,2025]})
check('576 monthly rows',len(mm)==576)
for i in codes:check('24 months '+i,{(r['year'],int(r['month'])) for r in mm if r['airport_iata']==i}=={(str(y),m) for y in [2024,2025] for m in range(1,13)})
sources=table('sources/sources.csv');sids={r['source_id'] for r in sources};est=table('estimates/estimates.csv');eids={r['estimate_id'] for r in est};lineage=table('documentation/DATA_LINEAGE.csv');lk={(r['entity_type'],r['entity_id'],r['period'],r['metric']):r for r in lineage}
refs=[]
for rel,(fields,rows) in TABLE.items():
 if rel.startswith('raw/'):continue
 for r in rows:
  for f in ['source_id','source_ids']:
   if f in r:refs += [s for s in r[f].split(';') if s]
check('Source references',set(refs)<=sids,'dangling='+str(sorted(set(refs)-sids)))
check('Lineage origins',all(r['value_origin'] in ['observed','derived','estimated','scenario'] for r in lineage))
check('Estimate references',all(not r['estimate_id'] or r['estimate_id'] in eids for r in lineage))
check('Estimate range validity',all(num(r['low'])<=num(r['estimate_value'])<=num(r['high']) and math.isfinite(num(r['estimate_value'])) for r in est))
for r in est:
 try:json.loads(r['input_observations'])
 except Exception:ERRORS.append('Invalid input JSON '+r['estimate_id'])
check('Local source evidence files',all((ROOT/r['local_path']).is_file() and (ROOT/r['local_path']).stat().st_size>0 for r in sources))
for rel,(fields,rows) in TABLE.items():
 if rel.startswith('raw/'):continue
 for r in rows:
  for key in ['airport_iata','origin_iata','destination_iata','canonical_airport_iata']:
   if key in r:check('IATA '+rel+' '+r[key],bool(re.fullmatch('[A-Z]{3}',r[key])))
  if 'airport_iata' in r and rel.startswith('processed/') and rel!='processed/route_airports.csv':
   if r['airport_iata'] not in codes:ERRORS.append('Airport foreign key '+rel+' '+r['airport_iata'])
# Provenance for every nonempty main numeric measure.
for rel,etype,metrics in [('processed/airport_annual.csv','airport_annual',['passengers_total','passengers_domestic','passengers_international','transfer_passengers','transit_passengers']),('processed/airport_monthly.csv','airport_monthly',['passengers_total','passengers_domestic','passengers_international'])]:
 for r in table(rel):
  period=r['year']+(('-'+f"{int(r['month']):02}") if 'month' in r else '')
  for m in metrics:
   if r[m]!='':
    check('Lineage '+etype+' '+r['airport_iata']+' '+period+' '+m,(etype,r['airport_iata'],period,m) in lk)
    check('Nonnegative '+etype+' '+m,num(r[m])>=0)
for r in table('processed/airport_operations.csv'):check('Operation provenance '+r['airport_iata']+r['year']+r['metric'],('airport_operations',r['airport_iata'],r['year'],r['metric']) in lk)
for r in table('processed/airport_cargo.csv'):
 for m in ['cargo_tonnes','mail_tonnes','cargo_mail_total_tonnes']:
  if r[m]!='':check('Cargo provenance '+r['airport_iata']+r['year']+r['scope']+m,('airport_cargo',r['airport_iata']+'|'+r['scope'],r['year'],m) in lk)
 if r['cargo_tonnes']!='' and r['mail_tonnes']!='':check('Cargo sum '+r['airport_iata']+r['year']+r['scope'],abs(num(r['cargo_tonnes'])+num(r['mail_tonnes'])-num(r['cargo_mail_total_tonnes']))<.0011)
# Observed monthly cells must not have been moved by balancing.
inputs={o['observation_id']:o for o in table('documentation/INPUT_OBSERVATIONS.csv')}
for l in lineage:
 if l['entity_type']=='airport_monthly' and 'input_observation=' in l['notes']:
  oid=l['notes'].split('input_observation=',1)[1].split(';')[0];o=inputs[oid];y,m=l['period'].split('-');r=next(r for r in mm if r['airport_iata']==l['entity_id'] and r['year']==y and int(r['month'])==int(m))
  check('Preserved '+oid,num(r[l['metric']])==num(o['value']))
for r in aa:
 vals=[x for x in mm if x['airport_iata']==r['airport_iata'] and x['year']==r['year']]
 for m in ['passengers_total','passengers_domestic','passengers_international']:
  diff=sum(num(x[m]) for x in vals)-num(r[m])
  if diff:WARN.append(f"{r['airport_iata']} {r['year']} {m}: sum(months)-annual={diff:g}; published values preserved")
 diff=num(r['passengers_total'])-num(r['passengers_domestic'])-num(r['passengers_international'])
 if diff:WARN.append(f"{r['airport_iata']} {r['year']}: total-domestic-international={diff:g}; see PASSENGER_RECONCILIATION")
 mx=max(num(v['passengers_total']) for v in vals)/num(r['passengers_total']);check('Monthly scale '+r['airport_iata']+r['year'],mx<=.20,'max monthly share='+str(round(mx,4)))
ops={(r['airport_iata'],r['year'],r['metric']):r for r in table('processed/airport_operations.csv')}
for i,y in {(r['airport_iata'],r['year']) for r in aa}:
 mov=num(ops[i,y,'aircraft_movements']['value']);dep=num(ops[i,y,'departures']['value']);arr=num(ops[i,y,'arrivals']['value']);check('Operation balance '+i+y,mov==dep+arr)
 pax=num(next(r for r in aa if r['airport_iata']==i and r['year']==y)['passengers_total']);check('Operation scale '+i+y,40<=pax/mov<=220,'pax/movement='+str(round(pax/mov,2)))
for r in table('processed/route_capacity.csv'):
 c=2*num(r['weekly_round_trips'])*num(r['weeks'])*num(r['seats_per_departure']);check('Route capacity '+r['route_id'],abs(c-num(r['two_way_seats']))<.005)
for r in table('processed/airport_routes.csv'):
 check('Historical route '+r['origin_iata']+r['destination_iata'],r['year'] in ['2024','2025'])
 for f in ['valid_from','valid_to']:
  if r[f]:check('Route period '+r['origin_iata']+r['destination_iata'],r[f][:4]==r['year'])
 if r['weekly_departures']!='':check('Route frequency '+r['origin_iata']+r['destination_iata'],0<num(r['weekly_departures'])<=700)
 if r['seats_per_departure']!='':check('Aircraft seating '+r['origin_iata']+r['destination_iata'],1<=num(r['seats_per_departure'])<=600)
 if r['valid_from'] and r['valid_to']:check('Route dates '+r['origin_iata']+r['destination_iata'],r['valid_from']<=r['valid_to'])
mt={r['year']:num(r['passengers']) for r in table('processed/market_totals.csv')}
for r in table('processed/airline_market_annual.csv'):check('Market share '+r['airline']+r['year'],abs(num(r['passengers'])/mt[r['year']]*100-num(r['market_share_pct']))<=.00000051)
for r in table('documentation/RAW_MANIFEST.csv'):
 p=ROOT/r['path'];check('Raw integrity '+r['path'],p.stat().st_size==int(r['bytes']) and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'])
required_docs=['README.md','estimates/estimation_methods.md','sources/SOURCES.md','documentation/DATA_DICTIONARY.md','documentation/METHODOLOGY.md','documentation/DATA_GAPS.md','documentation/DATA_CONFLICTS.md']
for rel in required_docs:check('Document '+rel,(ROOT/rel).is_file() and (ROOT/rel).stat().st_size>100)
for p in ROOT.rglob('*'):
 if any(x in p.parts for x in ['.venv','node_modules','__pycache__','.git','.cache']):ERRORS.append('Unexpected directory '+str(p))
 if p.name in ['.env','id_rsa','id_ed25519']:ERRORS.append('Unexpected secret file '+str(p))
WARN += ['Историческая маршрутная сеть неполна; объявления не подтверждают фактическое выполнение.', 'Инфраструктура: справочный снимок 2026-11-13, не восстановленный AIP 2024/2025.', 'SJ-100/Ту-214: эксплуатационная совместимость не определена; геометрический фильтр не является допуском.', 'Унаследованные источники не прошли повторную независимую веб-проверку.', 'Центральные оценки и scenario требуют фильтрации через DATA_LINEAGE перед фактическим анализом.']
report={'errors':ERRORS,'warnings':WARN,'checks':len(CHECK),'passed':sum(r[1]=='PASS' for r in CHECK),'csv_files':len(TABLE)}
(ROOT/'documentation/validation_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
text='# Результаты валидации\n\n'+f"Проверок: {len(CHECK)}. Ошибок структуры/арифметики/ссылок: {len(ERRORS)}. CSV-файлов: {len(TABLE)}.\n\n"+'Число проверок включает построчные проверки ключей, происхождения и сохранения опубликованных месячных ячеек. Это проверка целостности пакета, а не сертификация достоверности первоисточников.\n\n## Ошибки\n\n'+('\n'.join('- '+x for x in ERRORS) or 'Не обнаружены.')+'\n\n## Сохранённые расхождения и ограничения\n\n'+'\n'.join('- '+x for x in WARN)+'\n\nПроверены схемы, уникальность, периоды, неотрицательность, диапазоны оценок, IATA, ссылки на источники, наличие локальных свидетельств, формулы кресельной ёмкости, баланс операций, масштабы пассажиров на операцию, груз+почта и доли рынка. Отдельная почта преимущественно scenario; её сумма с грузом проверяется как арифметика сценария.\n'
(ROOT/'documentation/VALIDATION_REPORT.md').write_text(text)
print(json.dumps(report,ensure_ascii=False,indent=2));sys.exit(bool(ERRORS))
