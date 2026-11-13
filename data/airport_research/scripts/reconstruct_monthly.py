#!/usr/bin/env python3
"""Repeat monthly constrained fit from packaged inputs. Requires numpy and scipy.

Run from any working directory. Writes CSV to stdout; does not change the dataset.
"""
import csv,json,pathlib,sys
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
R=pathlib.Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader((R/p).open(encoding='utf-8')))
annual=read('processed/airport_annual.csv');monthly=read('processed/airport_monthly.csv');lineage=read('documentation/DATA_LINEAGE.csv');est=read('estimates/estimates.csv')
PAX=['passengers_total','passengers_domestic','passengers_international']
L={(r['entity_id'],r['period'],r['metric']):r for r in lineage if r['entity_type']=='airport_monthly'}
E={(r['entity_id'],r['period'],r['metric']):r for r in est if r['entity_type']=='airport_monthly'}

def distribute(total,weights):
 raw=[total*w/sum(weights) for w in weights];v=[int(x) for x in raw]
 for j in sorted(range(len(v)),key=lambda j:(-(raw[j]-v[j]),j))[:int(total-sum(v))]:v[j]+=1
 return v

out=csv.DictWriter(sys.stdout,fieldnames=['airport_iata','year','month']+PAX);out.writeheader()
for a in annual:
 i=a['airport_iata'];y=a['year'];mrows=sorted([r for r in monthly if r['airport_iata']==i and r['year']==y],key=lambda r:int(r['month']))
 totals=[]
 for r in mrows:
  key=i,f"{y}-{int(r['month']):02}",PAX[0];e=E.get(key)
  totals.append(int(json.loads(e['input_observations']).get('profile_baseline',r[PAX[0]])) if e else int(r[PAX[0]]))
 n=132;cost=np.zeros(n);cost[36:108]=1;cost[48:72]=2;cost[84:108]=2;cost[108:]=1000
 lo=np.zeros(n);hi=np.full(n,np.inf);baseline=[];component_baselines={}
 for metric in PAX[1:]:
  missing=[j for j in range(12) if L[i,f'{y}-{j+1:02}',metric]['value_origin'] not in ['observed','derived']]
  known=sum(int(mrows[j][metric]) for j in range(12) if j not in missing)
  if missing:
   for j,v in zip(missing,distribute(int(a[metric])-known,[totals[j] for j in missing])):component_baselines[j,metric]=v
 for k,metric in enumerate(PAX):
  for m,r in enumerate(mrows):
   key=i,f'{y}-{m+1:02}',metric;l=L[key];fixed=l['value_origin'] in ['observed','derived']
   b=int(r[metric]) if fixed else totals[m] if k==0 else component_baselines[m,metric]
   baseline.append(b)
   if fixed:lo[k*12+m]=hi[k*12+m]=b
 rows=[];lower=[];upper=[];targets=[]
 for k,metric in enumerate(PAX):
  row=np.zeros(n);row[k*12:(k+1)*12]=1;allfixed=all(lo[k*12+j]==hi[k*12+j] for j in range(12));target=sum(lo[k*12:(k+1)*12]) if allfixed else int(a[metric]);rows.append(row);lower.append(target);upper.append(target);targets.append(target)
 residual=int(targets[0]-targets[1]-targets[2]);res=distribute(abs(residual),totals)
 if residual<0:res=[-v for v in res]
 for j in range(36):
  row=np.zeros(n);row[j]=1;row[36+j]=-1;row[72+j]=1;rows.append(row);lower.append(baseline[j]);upper.append(baseline[j])
 for m in range(12):
  row=np.zeros(n);row[m]=1;row[12+m]=-1;row[24+m]=-1;row[108+m]=-1;row[120+m]=1;rows.append(row);lower.append(res[m]);upper.append(res[m])
 result=milp(cost,integrality=np.r_[np.ones(36),np.zeros(96)],bounds=Bounds(lo,hi),constraints=LinearConstraint(np.array(rows),lower,upper),options={'time_limit':10})
 if not result.success:raise RuntimeError((i,y,result.message))
 for m in range(12):out.writerow(dict(airport_iata=i,year=y,month=m+1,**{metric:int(round(result.x[k*12+m])) for k,metric in enumerate(PAX)}))
