"""Rebuild source-backed airport extracts using only the Python standard library.

The reviewed specifications below are deliberate: numbers in news prose cannot
be assigned to periods, traffic scopes or units safely with a generic regex.
No network access; raw text is never changed.
"""

import csv
import hashlib
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/airports'
OUT = ROOT / 'data/processed/airports'
AIRPORTS = dict(zip(
    'S23 S24 S25 S26 S28 S31 S32 S33 S34 S35 S36 S37 S38 S39 S40 S41 S52'.split(),
    ['Омск'] * 3 + ['Уфа', 'Тюмень (Рощино)', 'Красноярск', 'Иркутск',
    'Иркутск', 'Саратов (Гагарин)', 'Оренбург', 'Самара (Курумоч)',
    'Самара (Курумоч)', 'Казань', 'Нижний Новгород', 'Екатеринбург (Кольцово)',
    'Минеральные Воды', 'Омск']))
FILES = {p.name[:3]: p for p in sorted(RAW.glob('*.txt'))}
assert FILES.keys() == AIRPORTS.keys(), 'Unexpected/missing input files; review coverage'
TEXT = {s: p.read_text(encoding='utf-8') for s, p in FILES.items()}
METRICS, RELATIONS, ATTRIBUTES = [], [], []


def provenance(s, first, last=None):
    lines = TEXT[s].splitlines()
    assert 1 <= first <= (last or first) <= len(lines)
    return dict(source_id=s, raw_path=str(FILES[s].relative_to(ROOT)),
                source_locator=f'lines {first}-{last or first}', airport=AIRPORTS[s])


def metric(s, line, period, name, value, unit, scope='total', precision='reported',
           comparison='', kind='observation', notes=''):
    Decimal(str(value))
    METRICS.append(dict(**provenance(s, line), period=period, metric=name,
                        scope=scope, value=str(value), unit=unit,
                        value_qualifier=precision, comparison_period=comparison,
                        record_kind=kind, limitations=notes))


def pax(s, line, value, period='2025', scope='total', precision='reported'):
    metric(s, line, period, 'passengers', value, 'person', scope, precision)


def growth(s, line, value, period='2025', scope='total', metric_name='passengers',
           comparison='2024', precision='reported'):
    metric(s, line, period, metric_name + '_change', value, 'percent', scope,
           precision, comparison)


def rel(s, line, period, relation, entities, notes=''):
    for entity in entities.split('|'):
        RELATIONS.append(dict(**provenance(s, line), period=period,
                              relation=relation, entity=entity,
                              record_kind='plan' if relation.startswith('planned_') else 'reported_relation',
                              limitations=notes))


# Passenger counts are airport traffic, never inferred O&D or unique people.
pax('S23', 3, 1629761)
metric('S23', 3, '2025', 'flights', 16000, 'flight', precision='almost')
metric('S23', 3, '2025', 'aircraft_serviced_on_apron', 7900, 'aircraft')
for line, city, value in zip(range(13, 23),
        'Москва|Санкт-Петербург|Сочи|Новосибирск|Астана|Анталья|Сургут|Новый Уренгой|Казань|Красноярск'.split('|'),
        [674175, 234510, 195927, 106309, 56405, 31093, 29964, 27762, 27510, 23192]):
    pax('S23', line, value, scope='route:' + city)
pax('S24', 6, 1726029, '2024'); pax('S24', 6, 1680206, '2023')
growth('S24', 6, 3, '2024', comparison='2023')
metric('S24', 8, '2024', 'aircraft_serviced', 8551, 'aircraft')
metric('S24', 8, '2024', 'takeoff_mass', 486737, 'tonne')
growth('S24', 8, 5, '2024', metric_name='takeoff_mass', comparison='2023')
metric('S24', 8, '2024', 'cargo_and_mail', 3438, 'tonne')
growth('S24', 8, 11, '2024', metric_name='cargo_and_mail', comparison='2023')
metric('S24', 10, '2024', 'regional_traffic_bypassing_moscow_share', 51, 'percent',
       notes='Знаменатель доли подробно не определён в источнике')
metric('S24', 11, '2025', 'subsidized_routes', 12, 'route', kind='plan')
for year, value in [(2023,1680206),(2022,1585994),(2021,1505523),(2020,942932),(2019,1383029),(2018,1114507)]:
    pax('S25', 6, value, str(year))
growth('S25', 6, 5.9, '2023', comparison='2022')
metric('S25', 8, '2023', 'regional_traffic_bypassing_moscow_share', 50, 'percent',
       precision='at_least', notes='Знаменатель доли подробно не определён в источнике')
pax('S26',4,4929715); pax('S26',6,4000000,scope='domestic'); pax('S26',6,900000,scope='international')
growth('S26',12,4)
metric('S26',8,'2025','net_profit',2000000000,'RUB',precision='greater_than')
metric('S26',8,'2025','average_salary',80000,'RUB',notes='Период начисления зарплаты не указан')
growth('S26',8,11,metric_name='average_salary'); growth('S26',8,13,metric_name='labor_productivity')
pax('S28',9,2760338); pax('S28',11,2486000,scope='domestic'); pax('S28',11,274100,scope='international')
growth('S28',11,22.5,scope='international')
for scope, value in [('total',47),('domestic',33),('CIS',7),('non_CIS_international',7)]:
    metric('S28',13,'2025','destinations',value,'destination',scope)
pax('S31',3,316329,'2025-12'); metric('S31',3,'2025-12','aircraft_departures',1495,'departure')
metric('S31',3,'2025','takeoff_operations',20120,'operation')
pax('S31',5,69158,'2025-12','international'); growth('S31',5,17,'2025-12','international',comparison='2024-12')
pax('S31',5,786939,scope='international'); growth('S31',5,5.2,scope='international')
growth('S31',7,60,scope='country:Китай',precision='greater_than')
pax('S31',9,3421272,scope='domestic'); pax('S31',11,4263566)
for city, value in zip('Омск|Улан-Удэ|Челябинск|Хабаровск|Владивосток|Уфа'.split('|'), [89,34,29,17,15,14]):
    growth('S31',9,value,scope='route:'+city)
for city, value, line in [('Россия',1395375,19),('Аэрофлот',857078,19),('NordStar',303228,21),('S7',301788,21),('КрасАвиа',278671,21),('Utair',273159,21),('Nordwind',177268,21),('Победа',141524,21),('Аврора',117079,21),('Уральские авиалинии',110187,21),('AZUR air',110124,21)]:
    pax('S31',line,value,scope='airline:'+city)
growth('S31',19,2.3,scope='airline:Россия'); growth('S31',19,18,scope='airline:Аэрофлот')
pax('S32',7,3078468,'2025-01/2025-09'); pax('S32',7,2999883,'2024-01/2024-09')
pax('S32',7,638221,'2025-01/2025-09','international'); pax('S32',7,495247,'2024-01/2024-09','international')
growth('S32',7,2.6,'2025-01/2025-09',comparison='2024-01/2024-09')
growth('S32',7,29,'2025-01/2025-09','international',comparison='2024-01/2024-09')
for line, carrier, value in [(13,'S7 Airlines',1418065),(14,'Аэрофлот',404790),(15,'ИрАэро',372248),(16,'Уральские авиалинии',131198),(17,'Россия',112894)]:
    pax('S32',line,value,'2025-01/2025-09','airline:'+carrier)
for name,value,unit in [('aircraft_departures',16753,'departure'),('cargo',6476273,'kg'),('mail',803026,'kg')]:
    metric('S32',19,'2025-01/2025-09',name,value,unit)
pax('S33',5,999558,'2026-summer'); pax('S33',6,348410,'2026-08')
metric('S33',7,'2026-summer','baggage',7252401,'kg')
pax('S33',8,815400,'2026-summer','domestic'); pax('S33',8,184158,'2026-summer','international')
for carrier,value in [('S7 Airlines',445839),('Аэрофлот',172661),('ИрАэро',169377),('Уральские авиалинии',63094),('Россия',34622)]:
    pax('S33',9,value,'2026-summer','airline:'+carrier)
metric('S33',10,'2026-summer','cargo',2000,'tonne',precision='greater_than')
metric('S33',10,'2026-summer','mail',180,'tonne')
pax('S34',1,1064000); pax('S34',1,1019000,scope='domestic'); pax('S34',1,44600,scope='international')
metric('S34',2,'2025','takeoff_landing_operations',8300,'operation',precision='greater_than')
metric('S34',2,'2025','destinations',14,'destination'); metric('S34',2,'2025','airlines',11,'airline')
pax('S35',1,951000,precision='greater_than'); pax('S35',2,885500,scope='domestic'); pax('S35',2,65600,scope='international')
metric('S35',2,'2025','domestic_passenger_share',93,'percent')
metric('S35',2,'2025','takeoff_landing_operations',8800,'operation',precision='greater_than')
metric('S35',2,'2025','cargo_and_mail',1000,'tonne',precision='greater_than')
metric('S35',3,'2025','destinations',12,'destination'); metric('S35',3,'2025','airlines',12,'airline')
pax('S36',1,3570000); pax('S36',2,2750000,scope='domestic'); pax('S36',4,822000,scope='international')
metric('S36',2,'2025','domestic_passenger_share',77,'percent'); growth('S36',4,7,scope='international')
for line, city, value, precision in [(2,'Москва',1300000,'reported'),(2,'Сочи',325000,'reported'),(2,'Санкт-Петербург',492000,'reported'),(3,'Калининград',47800,'reported'),(3,'Минеральные Воды',47000,'reported'),(4,'Анталья',249000,'reported'),(4,'Минск',19000,'greater_than'),(4,'Батуми',7000,'greater_than')]:
    pax('S36',line,value,scope='route:'+city,precision=precision)
for line,city,value in [(3,'Калининград',42),(3,'Минеральные Воды',23),(4,'Минск',84),(4,'Батуми',88)]:
    growth('S36',line,value,scope='route:'+city)
metric('S36',5,'2025','destinations',47,'destination'); metric('S36',5,'2025','airlines',28,'airline')
pax('S37',1,3570000,'2024'); pax('S37',2,2800000,'2024','domestic')
metric('S37',2,'2024','domestic_passenger_share',78,'percent')
for city,value,precision in [('Москва',1370000,'reported'),('Санкт-Петербург',510000,'reported'),('Сочи',304000,'reported'),('Ярославль',17500,'reported'),('Минск',10000,'greater_than')]:
    pax('S37',2,value,'2024','route:'+city,precision)
for city,value,precision in [('Ярославль',5,'almost'),('Казань',2,'greater_than'),('Нижний Новгород',1.5,'reported')]:
    metric('S37',2,'2024','passengers_ratio',value,'ratio','route:'+city,precision,'2023')
metric('S37',2,'2024','flights_per_week',2,'flight/week','route:Минск',notes='Red Wings; период действия внутри года не указан')
metric('S37',3,'2024','cargo_and_mail',2200,'tonne',precision='greater_than')
metric('S37',3,'2024','destinations',50,'destination'); metric('S37',3,'2024','airlines',24,'airline')
pax('S38',176,5384816); growth('S38',176,0.3)
pax('S39',1,1400000,precision='greater_than'); pax('S39',1,1100000,scope='domestic',precision='almost')
pax('S39',1,357000,scope='international'); growth('S39',1,15,scope='international')
metric('S39',1,'2025','cargo',1200,'tonne',precision='greater_than')
for scope,value in [('total',26),('domestic',16),('international',10)]:
    metric('S39',2,'2025','destinations',value,'destination',scope)
metric('S39',3,'2025','diverted_aircraft_serviced',300,'aircraft',precision='greater_than')
metric('S39',4,'2025','takeoff_landing_operations',15000,'operation',precision='greater_than')
pax('S40',1,8385000,precision='approximately'); growth('S40',1,4)
pax('S40',2,5800000,scope='domestic',precision='approximately'); pax('S40',2,2600000,scope='international')
growth('S40',2,16,scope='international'); metric('S40',3,'2025','cargo_turnover',13700,'tonne',precision='greater_than')
growth('S40',3,13,metric_name='cargo_turnover',comparison='2023')
for city,value,precision in [('Москва',2000000,'almost'),('Санкт-Петербург',700000,'approximately'),('Сочи',785000,'reported'),('Минеральные Воды',211000,'reported'),('Новосибирск',170000,'greater_than'),('Анталья',660000,'approximately'),('Дубай',211000,'reported'),('Пхукет',162000,'greater_than'),('Шарм-эль-Шейх',158000,'almost'),('Шарджа',136000,'greater_than')]:
    pax('S40',5,value,scope='route:'+city,precision=precision)
metric('S40',8,'2025','business_lounges_reconstructed',2,'lounge')
metric('S40',8,'2025','business_lounges_opened',1,'lounge','international')
pax('S41',4,4600000); growth('S41',4,-4.6)
pax('S41',5,1200000,scope='international'); growth('S41',5,8.6,scope='international')
metric('S41',9,'','international_terminal_investment',3000000000,'RUB',precision='at_most',kind='plan',notes='Дата исполнения не указана')
metric('S41',9,'','international_passengers_target_ratio',2,'ratio',kind='plan',notes='Цель проекта; не наблюдаемый поток; продолжение на строках 10–11')
metric('S41',12,'2026/2028','runway_reconstruction_budget',12000000000,'RUB',precision='approximately',kind='plan')

# Qualitative lists are reported subsets, never a complete route network.
rel('S23',5,'2025','new_destination','Камрань|Шарм-эль-Шейх|Улан-Удэ')
rel('S23',5,'2025','new_airline','Southwind Airlines')
rel('S23',5,'2025','new_aircraft_approval','Airbus A330|Boeing 737 MAX8')
rel('S24',10,'2024','new_destination','Надым|Ноябрьск|Баку|Хургада')
rel('S24',11,'2025','planned_subsidized_destination','Новый Уренгой|Ноябрьск|Надым|Салехард|Екатеринбург|Улан-Удэ|Красноярск|Казань|Уфа|Абакан|Тобольск|Ханты-Мансийск')
rel('S25',8,'2023','subsidized_destination','Абакан|Барнаул|Горно-Алтайск|Екатеринбург|Казань|Кемерово|Красноярск|Махачкала|Минеральные Воды|Новокузнецк|Самара|Тобольск|Томск|Тюмень|Уфа|Нижневартовск|Новый Уренгой|Салехард|Сургут|Ханты-Мансийск')
rel('S25',10,'2023','new_destination','Горно-Алтайск|Тобольск|Томск|Норильск|Ташкент|Пхукет|Иркутск')
rel('S25',11,'2023','popular_destination','Москва|Санкт-Петербург|Сочи|Новосибирск|Сургут|Казань|Екатеринбург|Новый Уренгой|Салехард|Ханты-Мансийск')
rel('S31',5,'2025','new_destination','Ереван|Нячанг|Шымкент')
rel('S31',5,'2025','resumed_destination','Душанбе')
rel('S31',17,'2025','new_destination','Самара|Магадан|Краснодар|Анадырь')
rel('S32',9,'2025-01/2025-09','popular_domestic_destination','Москва|Новосибирск|Санкт-Петербург|Владивосток|Красноярск')
rel('S32',9,'2025-01/2025-09','popular_international_destination','Бангкок|Пекин|Пхукет|Ташкент|Камрань')
rel('S33',8,'2026-summer','popular_domestic_destination','Москва|Новосибирск|Владивосток|Санкт-Петербург|Красноярск')
rel('S33',8,'2026-summer','popular_international_destination','Пекин|Бангкок|Камрань|Ташкент|Санья')
rel('S34',2,'2025','served_destination','Москва|Санкт-Петербург|Сочи|Казань|Калининград|Новосибирск|Минеральные Воды|Екатеринбург|Махачкала|Сургут|Новый Уренгой|Уфа|Ереван|Анталья')
rel('S34',2,'2025','regular_airline','Аэрофлот|Россия|Победа|S7 Airlines|Red Wings|Азимут|ИрАэро|Икар|Ширак Авиа|Southwind Airlines|ЮТэйр')
rel('S35',3,'2025','new_destination','Баку'); rel('S35',3,'2025','popular_destination','Москва|Санкт-Петербург')
rel('S35',3,'2025','new_airline','Corendon Airlines|ИрАэро|Азимут')
rel('S36',4,'2025','popular_international_destination','Хургада|Шарджа|Анталья')
rel('S39',2,'2025','new_domestic_destination','Мурманск|Кострома')
rel('S39',2,'2025','served_international_destination','Анталья|Ташкент|Шарм-эль-Шейх|Ереван|Хургада|Минск|Тбилиси|Батуми|Сухум')
rel('S39',2,'2025','new_international_destination','Тбилиси|Батуми|Сухум')
rel('S40',4,'2025','new_domestic_destination','Нарьян-Мар|Улан-Удэ|Абакан|Киров|Мурманск|Саранск|Элиста|Краснодар|Геленджик')
rel('S40',4,'2025','new_international_destination','Нячанг|Рас-эль-Хайма|Фукуок')
rel('S40',6,'2025','new_airline','FLYONE ARMENIA|Red Sea Airlines')
rel('S40',6,'2025','first_operator_on_sharm_route','Sky Vision Airlines')
rel('S41',5,'2025','popular_international_destination','Анталья|Стамбул|Ереван|Дубай|Шарм-эль-Шейх')
rel('S41',6,'2025','popular_domestic_destination','Москва|Санкт-Петербург|Екатеринбург|Новосибирск|Сочи')

# S52: retain ambiguous units and aircraft families literally, without expanding them.
for name, first, last in [('icao',3,3),('icao_cyrillic',4,4),('iata',6,6),('domestic_code',8,8),('location',10,10),('FIR',12,12),('authority',14,14),('reference_point',16,16),('utc_offset',18,18),('operating_hours_UTC',20,20),('accepted_aircraft',22,23),('runway',25,25),('runway_class',27,27),('runway_dimensions',29,29),('maximum_takeoff_weight',31,31),('PCN',33,33),('magnetic_landing_course',35,35),('runway_surface',37,37),('lighting',39,39)]:
    ATTRIBUTES.append(dict(**provenance('S52',first,last),period='',attribute=name,
        value=' '.join(TEXT['S52'].splitlines()[first-1:last]),unit='',
        record_kind='reported_attribute',limitations='Дата актуальности не указана' +
        ('; единица измерения не указана' if name in {'maximum_takeoff_weight','runway_dimensions'} else '')))


def write(name, rows):
    assert rows
    with (OUT / name).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'data/source_manifest.csv').open(encoding='utf-8',newline='') as f:
        manifest={r['source_id']:r for r in csv.DictReader(f)}
    sources=[]
    for s,p in FILES.items():
        m=manifest[s]
        sources.append(dict(source_id=s,airport=AIRPORTS[s],raw_path=str(p.relative_to(ROOT)),
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(),publisher=m['publisher'],
            source_url=m['direct_url'],manifest_period=m['period'],
            source_status=m['report_claimed_status'],status_basis='source_manifest; not independently verified',
            capture_format='txt',capture_date='',
            limitations='Локальная текстовая копия; исходный HTML/PDF отсутствует; дата получения неизвестна',
            metric_rows=sum(r['source_id']==s for r in METRICS),
            relation_rows=sum(r['source_id']==s for r in RELATIONS),
            attribute_rows=sum(r['source_id']==s for r in ATTRIBUTES)))
    for rows in [METRICS,RELATIONS,ATTRIBUTES]:
        assert len({tuple(r.items()) for r in rows})==len(rows), 'Exact duplicate'
        for r in rows:
            assert r['source_id'] in FILES
            assert r['source_locator'] and r['raw_path']
            caveat = {
                'S31':'Опубликованный годовой итог на 55 355 выше суммы ВВЛ и МВЛ; значения не исправлены',
                'S32':'Январь–сентябрь; не полный год; аэропорт установлен по реестру источников',
                'S33':'Лето 2026; три месяца; точные границы дат в тексте не указаны',
                'S36':'Период 2025 установлен по содержанию, заголовок реестра не соответствует тексту',
                'S38':'Из муниципального документа извлечены только показатели аэропорта',
            }.get(r['source_id'],'')
            if caveat:
                r['limitations']='; '.join(filter(None,[r['limitations'],caveat]))
    keys=[(r['source_id'],r['period'],r['metric'],r['scope'],r['comparison_period']) for r in METRICS]
    assert len(keys)==len(set(keys)), 'Duplicate metric grain'
    write('metrics.csv',METRICS); write('relations.csv',RELATIONS)
    write('attributes.csv',ATTRIBUTES); write('sources.csv',sources)
    for name,rows in [('metrics',METRICS),('relations',RELATIONS),('attributes',ATTRIBUTES)]:
        print(name,len(rows),dict(Counter(r['source_id'] for r in rows)))


if __name__=='__main__':
    main()
