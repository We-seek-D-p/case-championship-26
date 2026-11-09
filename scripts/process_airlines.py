"""Reviewed extraction specifications for local airline HTML and PDF sources.

Uses Python's standard library and Poppler pdftotext. HTML anchors refer to
normalized text of an explicit article container; PDF locators use physical
page numbers, starting at one. No network requests or raw-file modifications.
"""

import csv
import hashlib
import re
import subprocess
from collections import Counter
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/airlines'
OUT = ROOT / 'data/processed/airlines'
IDS = 'S08 S09 S10 S11 S13 S14 S15 S16 S17 S18 S22 S58 S59 S60 S61 S69'.split()
REVIEWED_SHA256 = {
    'S08': '1295a0f03ee8a07354bc9006858e5410432dd6b895ad5f5858e93407c23ab6e4',
    'S09': '15a1ff20ffbb5ed7b2047fd8b9130be45bda4b2caeace19a22bbb68f3db746bf',
    'S10': 'e023449d0558f37f85f6aa8bf4ac04f142ef9648d7c62ac5724a611addd8f47b',
    'S11': 'af1257862dc77cce22a624a6fe20dd89a897c6b2ddb71cbb21a6a072d09cd5ad',
    'S13': 'e240545512d767a4956f2397b8c451d17a4926c485ea51af4c8250bfdf469909',
    'S14': '58102c6e8821c4021903872dcf8a107ead937e4a491db4e726b781308dc3f3b5',
    'S15': 'f793c7ed53294050eb2ed5d833c77b160eee898d5d6b1068d15d41c4ea450f6c',
    'S16': '5efcbab7a98add9a8b605ffb8289b257d327f4bb3ee85b16118e1d6de8f7cb93',
    'S17': 'a638facdba0f371daec1e0b510c6bd5b35c5e296c039ea49c0149a242476e54c',
    'S18': '8d497d5ad61ed297f8ea30749599143c649db5bc3e9528053699f4fe7a91a3d1',
    'S22': '7603f91b4475977d0da22ebbc60519745cc2fa2a3745894a83f8db4673ea03ca',
    'S58': '124ecc4b0c1a6b30850f10bc948ba2e834827fab320ffcdfbea6ff5858d8f48e',
    'S59': 'a92368c57c68736b8efc1833d2890d3ca27f93ef6227e0dfb24c55b8ce3046e6',
    'S60': 'f0149a802d551b6b1edcda18539320a5c6eac7e05983c10e08d9e579be451e0a',
    'S61': 'd71129b0dc150c67afa8eefc554e713c753d91ba6131b0c971e8d7de79c95f78',
    'S69': 'edc00f0779c6fd69a5567f2afc9dad4ebdcdf7b198a7ff02b50ee6af2a1ad24b',
}
PUBLISHED = dict(zip(IDS, ['2026-01-28','2024-06-24','2026-03-31','2026-10-27',
    '2026-10-30','2026-11-03','2020-10-13','2021-10-07','2024-04-23','2025-04-29',
    '', '2026-06-01','2026-04-30','2026-04-02','','2026-06-02']))
TABLES = {k: [] for k in ['metrics', 'relations', 'routes', 'fares', 'tariff_rules', 'attributes']}


def norm(text):
    return ' '.join(text.split())


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def text(self):
        return norm(' '.join(c.text() if isinstance(c, Node) else c for c in self.children))

    def find(self, *, tag=None, cls=None):
        result = []
        for child in self.children:
            if not isinstance(child, Node):
                continue
            if (tag is None or child.tag == tag) and (cls is None or cls in child.attrs.get('class', '').split()):
                result.append(child)
            result.extend(child.find(tag=tag, cls=cls))
        return result


class Parser(HTMLParser):
    VOID = set('area base br col embed hr img input link meta param source track wbr'.split())

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        if not any(n.tag in {'style', 'script'} for n in self.stack):
            self.stack[-1].children.append(data)


FILES = {}
SCOPES = {}
LOCATORS = {}
TREES = {}
PDF_PAGES = []


def load():
    global PDF_PAGES
    for p in sorted(RAW.iterdir()):
        if p.name == '.gitkeep':
            continue
        assert p.suffix in {'.html', '.pdf'} and p.name[:3] in IDS, p
        assert p.name[:3] not in FILES, 'Duplicate source ID'
        FILES[p.name[:3]] = p
    assert set(FILES) == set(IDS), 'Input coverage changed; review specifications'
    for s, p in FILES.items():
        assert hashlib.sha256(p.read_bytes()).hexdigest() == REVIEWED_SHA256[s], f'{s}: source changed; review extraction before updating hash'
        if p.suffix == '.pdf':
            result = subprocess.run(['pdftotext', '-layout', str(p), '-'], check=True, capture_output=True, text=True)
            PDF_PAGES = result.stdout.split('\f')
            if not PDF_PAGES[-1].strip():
                PDF_PAGES.pop()
            assert len(PDF_PAGES) == 65
            continue
        root = Parser(p.read_text(encoding='utf-8')).root
        cls = {'S22':'directions__list', 'S58':'news__detail',
               'S59':'t-redactor__tte-view', 'S60':'t-redactor__tte-view',
               'S69':'pr_company_text'}.get(s, 'post')
        nodes = root.find(cls=cls)
        index = 1 if cls == 'post' else 0
        node = nodes[index]
        TREES[s] = node
        SCOPES[s] = node.text()
        LOCATORS[s] = f'html class={cls}; occurrence={index+1}'


def base(s, anchor, page=None, occurrence=1):
    text = norm(PDF_PAGES[page-1]) if page else SCOPES[s]
    anchor = norm(anchor)
    matches = list(re.finditer(re.escape(anchor), text))
    assert len(matches) >= occurrence, (s, page, anchor)
    match = matches[occurrence-1]
    locator = f'pdf page={page}' if page else LOCATORS[s]
    return dict(source_id=s, raw_path=str(FILES[s].relative_to(ROOT)),
                source_locator=f'{locator}; normalized_text_chars={match.start()}:{match.end()}',
                source_excerpt=anchor)


def metric(s, anchor, period, name, value, unit, scope='total', qualifier='reported',
           kind='observation', comparison='', notes='', entity='Red Wings', basis='', page=None):
    Decimal(str(value))
    TABLES['metrics'].append(dict(**base(s,anchor,page),entity=entity,reporting_basis=basis,
        period=period,metric=name,scope=scope,value=str(value),unit=unit,
        value_qualifier=qualifier,comparison_period=comparison,record_kind=kind,limitations=notes))


def relation(s, anchor, period, name, items, *, kind='reported_relation',
             entity='Red Wings', page=None, notes=''):
    for item in items.split('|'):
        TABLES['relations'].append(dict(**base(s,anchor,page),entity=entity,period=period,
            relation=name,related_entity=item,record_kind=kind,limitations=notes))


def route(s, anchor, origin, destination, period, *, start='', end='', frequency='',
          days='', departure='', arrival='', flight='', aircraft='', duration='',
          entity='Red Wings', kind='announced_service', page=None, notes=''):
    TABLES['routes'].append(dict(**base(s,anchor,page),entity=entity,origin=origin,
        destination=destination,period=period,start_date=start,end_date=end,
        flights_per_week=str(frequency),days=days,departure_time=departure,
        arrival_time=arrival,flight_number=flight,aircraft=aircraft,duration_minutes=str(duration),
        record_kind=kind,limitations=notes))


def metrics():
    m = metric
    m('S08','24 тыс. рейсов','2025','flights',24000,'flight',scope='Russian_aircraft')
    m('S08','более 2 млн пассажиров','2025','passengers',2000000,'person',scope='Russian_aircraft',qualifier='greater_than')
    m('S08','около 1000 чартерных рейсов','2025','flights',1000,'flight',scope='Boeing-777_charter',qualifier='approximately')
    m('S08','2,7 млн пассажиров','2025','passengers',2700000,'person')
    m('S08','увеличилась на 2%','2025','load_factor_change',2,'percent_as_reported',comparison='2024',notes='Источник не уточняет: относительный рост или процентные пункты; уровень загрузки не указан')
    for scope,n in [('total',25),('domestic',17),('international',8)]:
        m('S08','25 новых регулярных направлений: 17 внутри России и 8 за рубеж','2025','new_regular_routes',n,'route',scope)
    m('S09','0,92 млн человек в 2014 году','2014','passengers',920000,'person')
    m('S09','2,66 млн человек в 2023 году','2023','passengers',2660000,'person')
    m('S09','19 самолетов','2024-06-24','fleet',19,'aircraft',scope='SSJ 100')
    m('S09','до 400 часов в месяц','as_of_2024-06-24','average_monthly_flight_hours',400,'hour/month',scope='SSJ 100',qualifier='at_most',notes='Период усреднения не указан')
    m('S09','одним обновленным Ту-204','end_2023/early_2024','fleet_additions',1,'aircraft',scope='Ту-204')
    m('S09','одним Ту-214','end_2023/early_2024','fleet_additions',1,'aircraft',scope='Ту-214')
    m('S09','на 52 кресла','as_of_2024-06-24','seats',52,'seat',scope='business_SSJ_100')
    m('S09','более 1500 лётных часов','since_2023_as_of_2024-06-24','flight_hours_gain',1500,'hour',qualifier='greater_than')
    m('S09','более 20 га','as_of_2024-06-24','tree_planting_area',20,'ha',qualifier='greater_than')
    for scope,n in [('total',118),('international',69)]:
        m('S10','118 направлениям, включая 69','summer_2026_until_2026-10-24','routes',n,'route',scope,kind='schedule_program')
    for anchor,scope,n in [('33 направления','Урал',33),('31 – на Поволжье','Поволжье',31),('7 – на Московский','Московский регион',7),('5 – на Северо-Запад','Северо-Запад',5),('8 – на юг','Юг',8),('18 – на Кавказ','Кавказ',18),('9 направлений','ДФО',9)]:
        m('S10',anchor,'summer_2026_until_2026-10-24','routes_by_region',n,'route',scope,kind='schedule_program',notes='Категории источника; не предполагается аддитивность')
    for anchor,name,scope,n in [('7 стран','international_countries','total',7),('28 направлениям','routes_with_frequency_increase','total',28),('19 из которых международные','routes_with_frequency_increase','international',19),('21 новое направление','new_routes','total',21),('20 маршрутов','resumed_routes','total',20),('14 международных','resumed_routes','international',14)]:
        m('S10',anchor,'summer_2026_until_2026-10-24',name,n,'country' if name=='international_countries' else 'route',scope,kind='schedule_program')
    for name,scope,n,anchor in [('routes','total',71,'71 направлению'),('routes','international',34,'34 международным'),('destination_cities','domestic',24,'24 города назначения')]:
        m('S11',anchor,'winter_2026_2027_until_2027-03-27',name,n,'city' if name=='destination_cities' else 'route',scope,kind='schedule_program')
    for n,scope,anchor in [(5,'international','5-е место'),(9,'domestic','9-е')]:
        m('S13',anchor,'as_of_2026-10-30','passenger_traffic_rank_Russia',n,'rank',scope,notes='Период подсчёта и методика ранжирования не указаны')
    for n,name,kind,anchor in [(6,'new_routes','announced_service','новым шести маршрутам'),(9,'regional_routes','plan','достигнет девяти'),(6,'exclusive_routes','reported_claim','шесть из девяти маршрутов уникальные')]:
        m('S15',anchor,'2020-10',name,n,'route','hub:Екатеринбург',kind=kind)
    m('S15','до 25','2021','routes',25,'route','hub:Екатеринбург',kind='plan')
    m('S15','100 кресел','as_of_2020-10-13','seats',100,'seat','SSJ100')
    m('S16','470 тыс. пассажиров','first_project_year_as_of_2021-10-07','passengers',470000,'person','hub:Кольцово',notes='Текст одновременно говорит о первом и календарном годе; точные границы неизвестны')
    m('S16','380 тыс. человек','2021-01/2021-09','passengers',380000,'person','hub:Кольцово')
    m('S16','примерно в полмиллиона пассажиров','2021','passengers',500000,'person','hub:Кольцово',qualifier='approximately',kind='forecast')
    m('S16','примерно по 30','2022','routes',30,'route','hub:Екатеринбург',qualifier='approximately',kind='plan')
    for n,name,anchor in [(5,'new_routes','5 новых направлений'),(13,'routes_with_frequency_increase','13 маршрутам'),(26,'destination_cities','26 городами')]:
        m('S17',anchor,'spring_summer_2024',name,n,'city' if name=='destination_cities' else 'route','hub:Екатеринбург',kind='schedule_program')
    m('S17','почти 7,4 миллиона пассажиров','2023','passengers',7400000,'person','airport:Кольцово',qualifier='almost',entity='Аэропорт Кольцово',notes='Аэропортовый поток; не показатель Red Wings')
    # S58: five-year hub totals, point-in-time fleet and annual company totals.
    for entity,n,anchor,qual in [('Группа Аэрофлот',8700000,'более 8,7 млн','greater_than'),('Аэрофлот',3500000,'3,5 млн','reported'),('Россия',4400000,'4,4 млн','reported'),('Победа',825000,'825 тыс.','reported')]:
        m('S58',anchor,'first_5_hub_years_as_of_2026-06-01','passengers',n,'person','hub:Красноярск',qualifier=qual,entity=entity)
    m('S58','порядка 1 млн пассажиров','first_hub_year','passengers',1000000,'person','hub:Красноярск',qualifier='approximately',entity='Группа Аэрофлот')
    m('S58','2,2 млн','2025','passengers',2200000,'person','hub:Красноярск',entity='Группа Аэрофлот')
    m('S58','в два раза','as_of_2026-06-01','route_network_ratio',2,'ratio','hub:Красноярск',comparison='first_hub_year',entity='Группа Аэрофлот')
    for n,scope in [(32,'total'),(21,'domestic')]:
        m('S58','32 направлениям, из них 21','summer_2026','routes',n,'route','hub:Красноярск:'+scope,kind='schedule_program',entity='Группа Аэрофлот')
    for n,aircraft,anchor in [(3,'Superjet 100','3 самолета Superjet 100'),(4,'Airbus A319','4 самолета Airbus A319'),(3,'Boeing 737','3 Boeing 737')]:
        m('S58',anchor,'as_of_2026-06-01','based_aircraft',n,'aircraft','hub:Красноярск:'+aircraft,entity='Россия')
    for n,entity,anchor,qual in [(130,'Аэрофлот','почти 130 человек','almost'),(70,'Аэрофлот Техникс','более 70','greater_than'),(200,'Россия','почти 200 бортпроводников','almost')]:
        m('S58',anchor,'as_of_2026-06-01','staff',n,'person','hub:Красноярск',qualifier=qual,entity=entity)
    m('S58','шесть типов','as_of_2026-06-01','approved_aircraft_types',6,'type','hub:Красноярск',entity='Аэрофлот Техникс')
    for entity,n,anchor in [('Аэрофлот',29500000,'29,5 млн'),('Группа Аэрофлот',55300000,'55,3 млн')]:
        m('S58',anchor,'2025','passengers',n,'person',entity=entity)
    # Financial tables: preserve reporting perimeter, standard and comparison units.
    for name,v25,v24,a25,a24 in [('revenue',121300000000,113300000000,'121,3','113,3'),('EBITDAR',26600000000,31200000000,'26,6','31,2'),('EBITDAR_margin',21.9,27.5,'21,9%','27,5%'),('net_profit_loss',2500000000,-7000000000,'2,5','-7,0'),('operating_result',400000000,8300000000,'0,4','8,3')]:
        for year,val,anchor in [('2025',v25,a25),('2024',v24,a24)]:
            m('S59',anchor,year,name,val,'percent' if name=='EBITDAR_margin' else 'RUB',entity='Группа ЮТэйр',basis='IFRS')
    for name,val,unit,anchor in [('revenue_change',7.1,'percent','7,1%'),('EBITDAR_change',-14.8,'percent','-14,8%'),('EBITDAR_margin_change',-5.6,'percentage_point','-5.6 п.п.'),('net_profit_loss_change',9500000000,'RUB','9,5 млрд')]:
        m('S59',anchor,'2025',name,val,unit,comparison='2024',entity='Группа ЮТэйр',basis='IFRS')
    for n,scope,anchor in [(6900000,'total','6,9 млн'),(6200000,'airplane','6,2 млн'),(700000,'helicopter','0,7 млн')]:
        m('S59',anchor,'2025','passengers',n,'person',scope,entity='Группа ЮТэйр',basis='IFRS_release')
    m('S59','264 408 часов','2025','flight_hours',264408,'hour',entity='Группа ЮТэйр',basis='IFRS_release')
    for name,n,unit,scope,anchor in [('routes',134,'route','total','134 внутренним'),('passengers',5000000,'person','domestic','5 млн человек'),('new_routes',19,'route','domestic','19 новых российских'),('new_routes',2,'route','international','2 международных маршрута'),('flight_hours',158000,'hour','total','158 тыс. часов')]:
        m('S59',anchor,'2025',name,n,unit,scope,entity='ПАО Авиакомпания ЮТэйр',basis='IFRS_release')
    m('S59','2,9%','2025','passengers_change',2.9,'percent','domestic',comparison='2024',entity='ПАО Авиакомпания ЮТэйр',basis='IFRS_release')
    for name,n,unit,anchor in [('cargo',96400,'tonne','96,4 тыс. тонн'),('cargo_change',94,'percent','+94%'),('passengers_change',6.8,'percent','6,8%'),('firefighting_helicopters_Turkey',17,'helicopter','17 вертолетов'),('flight_hours',107000,'hour','107 тыс. часов')]:
        m('S59',anchor,'2025',name,n,unit,'helicopter',comparison='2024' if name.endswith('_change') else '',entity='Группа ЮТэйр',basis='IFRS_release')
    m('S59','более 1,7 млн нормо-часов','2025','maintenance',1700000,'standard_hour',qualifier='greater_than',entity='Группа ЮТэйр')
    m('S59','367 тысяч нормо-часов','2025','maintenance',367000,'standard_hour','airplane',entity='Группа ЮТэйр')
    m('S59','10,5%','2025','maintenance_change',10.5,'percent','airplane',comparison='2024',entity='Группа ЮТэйр')
    m('S59','1,4 млн нормо-часов','2025','maintenance',1400000,'standard_hour',entity='ЮТэйр-Инжиниринг')
    m('S59','37 воздушных судов','2025','aircraft_overhauled',37,'aircraft',entity='ЮТэйр-Инжиниринг')
    m('S59','семи аэропортов','as_of_2026-04-30','managed_airports',7,'airport',entity='Группа ЮТэйр')
    m('S59','более 3 млн пассажиров','2025','passengers',3000000,'person',qualifier='greater_than',entity='АО Аэропорт Сургут и филиалы',notes='Аэропортовый поток, не перевозки группы')
    m('S59','186 программам обучения','as_of_2026-04-30','training_programs',186,'program',entity='Центр подготовки персонала ЮТэйр')
    for name,n,unit,anchor,scope,comparison in [('operating_profit_change',-14,'percent','на 14%','total','2024'),('operating_profit_change_amount',-400000000,'RUB','0,4 млрд','total','2024'),('net_profit_change_amount',3800000000,'RUB','3,8 млрд','total','2024'),('passengers',6100000,'person','6,1 млн','total',''),('passengers',4800000,'person','4,8 млн','domestic',''),('passengers_change',4,'percent','на 4%','domestic','2024'),('flight_hours',148980,'hour','148 980','total',''),('routes',134,'route','134 направлениям','total',''),('new_routes',19,'route','19 российских','domestic',''),('new_routes',2,'route','2 международных','international','')]:
        m('S60',anchor,'2025',name,n,unit,scope,comparison=comparison,entity='ПАО Авиакомпания ЮТэйр',basis='RAS')
    m('S60','186 программам обучения','as_of_2026-04-02','training_programs',186,'program',entity='Центр подготовки персонала ЮТэйр')
    for name,n,unit,anchor,qual in [('flights',18000,'flight','более 18 тыс. рейсов','greater_than'),('passengers',1600000,'person','без малого 1,6 млн.','almost'),('seat_load_factor',83,'percent','83%','reported'),('passengers_change',4,'percent','на 4%','reported')]:
        m('S69',anchor,'2025',name,n,unit,qualifier=qual,comparison='2024' if name.endswith('_change') else '',entity='Аврора')
    m('S61','2,2 миллиона','2025','passengers',2200000,'person',entity='Азимут',page=4)
    for name,n,unit,anchor,scope in [('length',29.9,'m','29,9','SSJ100'),('wingspan',27.8,'m','27,8','SSJ100'),('maximum_takeoff_mass',49.45,'tonne','49,45','SSJ100'),('cruise_speed',840,'km/h','840','SSJ100'),('maximum_altitude',12.2,'km','12,2','SSJ100'),('range',3000,'km','3000/4200','SSJ100_B100'),('range',4200,'km','3000/4200','SSJ100_LR')]:
        m('S61',anchor,'issue_2026-01',name,n,unit,scope,entity='Азимут',page=60,kind='reported_specification')
    m('S61','24 аэропортах','issue_2026-01','business_lounge_airports',24,'airport',entity='Азимут',page=11)
    m('S61','500 приветственных','issue_2026-01','loyalty_welcome_bonus',500,'A_ruble',entity='Азимут',page=8,notes='После первого перелёта; не денежная выручка')


def build_relations_and_routes():
    r = relation
    r('S08','Основу флота','as_of_2026-01-28','fleet_family','Ту-204/214|SSJ-100|Boeing-777')
    r('S08','чаще всего выбирали','2025','popular_destination','Екатеринбург|Москва|Сочи|Таиланд')
    r('S09','Белоруссию, Казахстан','as_of_2024-06-24','served_country','Белоруссия|Казахстан|Грузия|Азербайджан|Израиль')
    r('S09','Sky Gates Airlines','as_of_2024-06-24','cargo_subdivision','Sky Gates Airlines')
    r('S09','Ил-76 и Ил-96','as_of_2024-06-24','cargo_aircraft_family','Ил-76|Ил-96')
    r('S09','новые базы','2023','new_maintenance_base','Жуковский|Екатеринбург')
    r('S10','ключевых хабов','summer_2026_until_2026-10-24','hub','Москва|Санкт-Петербург|Казань|Самара|Екатеринбург|Минеральные Воды|Сочи|Махачкала')
    r('S10','Дополнительные рейсы за рубеж','summer_2026_until_2026-10-24','frequency_increase_destination','Ереван|Стамбул|Тбилиси|Батуми|Алматы|Астана|Минск|Бишкек|Бухара',kind='schedule_program')
    for origin, destinations in [('Казань','Новый Уренгой|Нижневартовск'),('Самара','Геленджик|Ургенч'),('Чита','Кемерово'),('Екатеринбург','Ургенч'),('Оренбург','Ереван'),('Новосибирск','Батуми'),('Пермь','Минск')]:
        for destination in destinations.split('|'):
            route('S10','21 новое направление',origin,destination,'summer_2026_until_2026-10-24',end='2026-10-24',notes='Объявленное новое направление; частота и дата начала не указаны')
    r('S10','чартерная программа','summer_2026_until_2026-10-24','charter_country','Турция',kind='plan')
    winter='winter_2026_2027_until_2027-03-27'
    r('S11','Международная программа',winter,'served_country','Грузия|Узбекистан|Казахстан|Беларусь|Израиль|Армения|Турция|Кыргызстан',kind='schedule_program')
    r('S11','опорных аэропортов',winter,'hub','Москва|Санкт-Петербург|Казань|Самара|Екатеринбург|Сочи|Махачкала')
    r('S11','В Поволжье',winter,'domestic_destination','Нижний Новгород|Нижнекамск|Саранск|Саратов|Оренбург|Уфа|Тюмень|Абакан|Барнаул|Кемерово|Новокузнецк|Омск|Горно-Алтайск|Томск|Чита|Улан-Удэ|Мурманск|Сыктывкар|Ярославль|Махачкала',kind='schedule_program',notes='Перечисленные города; аэропорты отправления для них не установлены')
    r('S11','Рейсы в Батуми и Тбилиси',winter,'georgia_destination','Батуми|Тбилиси',kind='schedule_program')
    r('S11','доступны из Сочи',winter,'georgia_program_origin','Сочи|Нижний Новгород|Краснодар|Самара|Казань|Санкт-Петербург|Екатеринбург|Москва',kind='schedule_program',notes='Не строить декартово произведение с двумя городами назначения без расписания')
    r('S11','В Узбекистан',winter,'international_destination','Бухара|Наманган|Ташкент|Ургенч|Алматы|Астана|Минск|Тель-Авив|Ереван|Стамбул|Бишкек',kind='schedule_program')
    r('S13','Среди приоритетных направлений развития','as_of_2026-10-30','development_priority','Уральский ФО|Дальневосточный ФО|Северо-Кавказский ФО|Южный ФО|Ближнее зарубежье|Азиатский регион',kind='plan')
    for origin,aircraft,duration in [('Москва (Жуковский)','Ту-204/214',355),('Сочи','SSJ-100',175)]:
        route('S14','Полеты из Москвы',origin,'Тель-Авив (Бен-Гурион)','2027-03-28/2027-10-24',start='2027-03-28',end='2027-10-24',aircraft=aircraft,duration=duration,notes='Открытые продажи будущего сезона; частота не указана')
    for city in 'Волгоград|Нижний Новгород|Саратов'.split('|'):
        route('S15','с середины сентября 2020 года','Екатеринбург',city,'2020-09_as_of_2020-10-13',kind='reported_service')
    for city in 'Ноябрьск|Кемерово'.split('|'):
        route('S15','Уже 9 октября','Екатеринбург',city,'2020-10',start='2020-10-09',kind='reported_service')
    for city in 'Воронеж|Махачкала|Новосибирск|Оренбург'.split('|'):
        route('S15','В ближайшие дни','Екатеринбург',city,'as_of_2020-10-13',kind='plan',notes='Точная дата запуска не указана')
    r('S16','подписано код-шер соглашение','as_of_2021-10-07','codeshare_partner','Уральские авиалинии')
    for city,date,freq in [('Ижевск','2024-04-26',3),('Архангельск','2024-05-20',1),('Владикавказ','2024-05-21',2),('Нижневартовск','2024-05-21',2),('Батуми','2024-07-09',2)]:
        route('S17','Первым из новых маршрутов','Екатеринбург',city,'spring_summer_2024',start=date,frequency=freq,notes='Год дат восстановлен по публикации; дата окончания не указана')
    for city,freq in [('Самара',7),('Казань',6),('Нижний Новгород',6),('Барнаул',6),('Алматы',5),('Новокузнецк',5),('Уфа',5),('Оренбург',5),('Омск',4),('Томск',4),('Тбилиси',4),('Кемерово',3),('Ставрополь',2)]:
        route('S17','увеличит частоту рейсов','Екатеринбург',city,'2024-04/2024-05',frequency=freq,notes='Объявленная повышенная частота; точные границы действия неизвестны; ежедневно нормализовано в 7/нед')
    for city in 'Саратов|Махачкала|Новый Уренгой|Горно-Алтайск|Ульяновск|Астана|Анталия|Бухара'.split('|'):
        route('S17','Помимо упомянутых направлений','Екатеринбург',city,'as_of_2024-04-23',kind='reported_service')
    route('S18','запускает 2 июня','Екатеринбург','Ставрополь','from_2025-06-02',start='2025-06-02',frequency=2,days='1,6',duration=120,notes='Год по дате публикации; время полёта заявленное; конечная дата не указана')
    route('S18','из Москвы в курортный Эйлат','Москва','Эйлат','as_of_2025-04-29',notes='Открыты продажи; точные даты не указаны')
    route('S18','из Санкт-Петербурга в Тель-Авив','Санкт-Петербург','Тель-Авив','as_of_2025-04-29',notes='Открыты продажи; точные даты не указаны')
    for entity,cities,anchor in [('Аэрофлот','Москва|Краснодар|Екатеринбург|Бангкок|Пхукет','Аэрофлот летает'),('Россия','Санкт-Петербург|Екатеринбург|Благовещенск|Владивосток|Иркутск|Казань|Махачкала|Минеральные Воды|Мирный|Нерюнгри|Новый Уренгой|Омск|Сочи|Сургут|Тюмень|Хабаровск|Челябинск|Чита|Алматы|Бишкек|Ош|Пекин|Санья|Ташкент|Харбин','Авиакомпания "Россия" выполняет прямые рейсы'),('Победа','Москва (Шереметьево)','Шереметьево')]:
        for city in cities.split('|'):
            route('S58',anchor,'Красноярск',city,'summer_2026',entity=entity,kind='reported_service')
    for city,date in [('Анадырь','2026-06-02'),('Шанхай','2026-06-03'),('Гуанчжоу','2026-07-04')]:
        route('S58','С 2 июня','Красноярск',city,'summer_2026',start=date,entity='Россия',notes='Перевозчик по контексту абзаца; год по публикации')
    r('S59','семи аэропортов','as_of_2026-04-30','managed_airport','Сургут|Берёзово|Игрим|Ноябрьск|Талакан|Варандей|Усть-Кут',entity='Группа ЮТэйр')
    for origin,destination in [('Владивосток','Анадырь'),('Хабаровск','Советская Гавань'),('Хабаровск','Шанхай')]:
        route('S69','новыми направлениями',origin,destination,'2025',entity='Аврора',kind='reported_service')
    for city in 'Анталья|Дубай|Ереван|Самарканд|Стамбул|Ташкент|Тбилиси|Тель-Авив'.split('|'):
        route('S61','восстановила международную','Краснодар',city,'2025',entity='Азимут',kind='resumed_service',page=4)
    r('S61','базовыми','issue_2026-01','base_airport','Минеральные Воды|Внуково|Краснодар|Сочи',entity='Азимут',page=4)
    r('S61','Горно-Алтайск, Апатиты, Сургут','2025','new_destination','Горно-Алтайск|Апатиты|Сургут',entity='Азимут',page=4)
    # Map labels, without guessing edges hidden in overlapping curves.
    r('S61','Карта маршрутов рекламная','issue_2026-01','advertised_domestic_map_node',
      'Апатиты|Сыктывкар|Киров|С.-Петербург|Пермь|Ярославль|Псков|Иваново|Екатеринбург|Чебоксары|Москва|Уфа|Калининград|Калуга|Пенза|Саранск|Ульяновск|Челябинск|Самара|Магнитогорск|Оренбург|Астрахань|Краснодар|Минеральные Воды|Ставрополь|Сочи|Махачкала',entity='Азимут',page=59,notes='Рекламная карта, возможны изменения; узлы не задают пары маршрутов; часть надписей вне видимой границы страницы')
    r('S61','Нижневартовск','issue_2026-01','advertised_domestic_map_node','Нижневартовск|Сургут|Ханты-Мансийск|Тюмень|Омск|Новосибирск|Красноярск',entity='Азимут',page=60,notes='Продолжение рекламной карты; не расписание')
    r('S61','Международные полёты','issue_2026-01','advertised_international_map_node','Санкт-Петербург|Уфа|Москва (Внуково)|Минск|Минеральные Воды|Краснодар|Сочи|Алматы|Батуми|Кутаиси|Махачкала|Тбилиси|Ташкент|Стамбул|Бухара|Ереван|Самарканд|Термез|Анталья|Тель-Авив|Дубай (Аль-Мактум)|Джидда',entity='Азимут',page=60,notes='Рекламная карта; не восстанавливать пары/частоты по списку городов')
    r('S61','авиакомпанией S7','issue_2026-01','codeshare_partner','S7',entity='Азимут',page=59)
    for origin,destination,flight,day,dep,arr in [('Краснодар','Тель-Авив','А43025','3','13:30','15:55'),('Тель-Авив','Краснодар','А43026','4','10:10','14:30'),('Краснодар','Тель-Авив','А43025','7','16:40','19:35'),('Тель-Авив','Краснодар','А43026','1','11:05','15:15')]:
        route('S61','Рейс выполняется по графику',origin,destination,'issue_2026-01',flight=flight,days=day,departure=dep,arrival=arr,entity='Азимут',kind='published_schedule',page=6,notes='Часовая основа и конечные даты расписания не указаны; возобновление направления 10–11.12.2025 не перенесено автоматически на весь график')


def build_fares_and_rules():
    # All 23 cards in the saved S22 storefront, including any hidden DOM cards.
    items = TREES['S22'].find(cls='item')
    assert len(items) == 23
    for item in items:
        text = item.text()
        match = re.fullmatch(r'(.+?) от ([\d ]+) ₽', text)
        assert match, text
        destination, amount = match.groups()
        TABLES['fares'].append(dict(**base('S22',text),entity='Red Wings',
            origin='Екатеринбург',destination=destination,flight_numbers='',
            direction_scope='listed_origin_destination',period='',amount=str(int(amount.replace(' ',''))),
            currency='RUB',value_qualifier='at_least',journey_basis='not_specified',
            additional_fees='not_specified',record_kind='advertised_fare',
            limitations='Дата снимка, даты поездки, тариф и доступность не указаны; не фактическая выручка'))
    # PDF pp.12–13: one row per quoted price and listed flight number group.
    # Both listed directions share the displayed price; this is not a round-trip price.
    data = '''7|Москва (Внуково)|Апатиты|A47025/7026|6080|both|one_way|unspecified
7|Москва (Внуково)|Санкт-Петербург|A47019/7020|6280|both|one_way|unspecified
7|Москва (Внуково)|Псков|А47033/7034|4800|both|unspecified|unspecified
7|Москва (Внуково)|Псков|А47035/7036|4800|both|unspecified|unspecified
7|Москва (Внуково)|Псков|А47037/7038|5380|both|unspecified|unspecified
7|Москва (Внуково)|Псков|А47137/7138|5380|both|unspecified|unspecified
7|Москва (Внуково)|Ереван|А47029|14833|one|unspecified|extra
7|Москва (Внуково)|Ереван|А47030|13468|one|unspecified|extra
7|Москва (Внуково)|Кутаиси|А47071/7072|15480|both|unspecified|extra
7|Москва (Внуково)|Термез|А47055|12960|one|unspecified|extra
7|Термез|Москва (Внуково)|А47056|11250|one|unspecified|extra
7|Краснодар|Тель-Авив|А43025|16745|one|unspecified|extra
7|Тель-Авив|Краснодар|А43026|16175|one|unspecified|extra
7|Краснодар|Анталья|А43051|10065|one|unspecified|extra
7|Анталья|Краснодар|А43052|8425|one|unspecified|extra
7|Краснодар|Стамбул|А43069|12905|one|unspecified|extra
7|Стамбул|Краснодар|А43070|11080|one|unspecified|extra
7|Минеральные Воды|Иваново|A46015/6016|4980|both|one_way|unspecified
7|Минеральные Воды|Иваново|A46115/6116|5580|both|one_way|unspecified
7|Минеральные Воды|Киров|A46183/6184|10080|both|unspecified|unspecified
7|Минеральные Воды|Киров|A46013/6014|7580|both|unspecified|unspecified
7|Минеральные Воды|Махачкала|A46011/6012|3780|both|one_way|unspecified
7|Минеральные Воды|Махачкала|A46111/6112|6580|both|one_way|unspecified
7|Минеральные Воды|Оренбург|A46149/6150|6680|both|unspecified|unspecified
7|Минеральные Воды|Псков|A46005/6006|5780|both|unspecified|unspecified
7|Минеральные Воды|Псков|A46125/6125|6380|both|unspecified|unspecified
7|Минеральные Воды|Самара|A46307/6308|6680|both|one_way|unspecified
7|Минеральные Воды|Сургут|A46211/6212|35980|both|unspecified|unspecified
7|Минеральные Воды|Сыктывкар|A46045/6046|7280|both|unspecified|unspecified
7|Минеральные Воды|Тюмень|A46303/6304|11480|both|unspecified|unspecified
7|Минеральные Воды|Уфа|А46021,А46121|7880|one|unspecified|unspecified
7|Минеральные Воды|Чебоксары|A46211/6212|13280|both|unspecified|unspecified
7|Минеральные Воды|Чебоксары|A46201/6202|9880|both|unspecified|unspecified
7|Минеральные Воды|Челябинск|A46023/6024|13420|both|unspecified|unspecified
7|Минеральные Воды|Челябинск|A46123/6124|14780|both|unspecified|unspecified
7|Минеральные Воды|Алматы|А46141|14790|one|unspecified|extra
7|Алматы|Минеральные Воды|А46142|13040|one|unspecified|extra
7|Минеральные Воды|Анталья|A46215|10065|one|unspecified|extra
7|Анталья|Минеральные Воды|А46216|8425|one|unspecified|extra
7|Минеральные Воды|Бухара|A46177/6178|9150|both|one_way|extra
7|Минеральные Воды|Ереван|А46029,А46031|4395|one|unspecified|extra
7|Ереван|Минеральные Воды|А46030,А46032|2290|one|unspecified|extra
7|Минеральные Воды|Минск|A46001/6002|11780|both|unspecified|extra
7|Минеральные Воды|Самарканд|A46179/6180|21018|both|one_way|extra
7|Минеральные Воды|Стамбул|А46069,А46073|13160|one|unspecified|extra
7|Стамбул|Минеральные Воды|А46070,А46074|11090|one|unspecified|extra
7|Минеральные Воды|Ташкент|А46081|18975|one|unspecified|extra
7|Ташкент|Минеральные Воды|А46082|17580|one|unspecified|extra
7|Минеральные Воды|Тель-Авив|А46025|14605|one|unspecified|extra
7|Тель-Авив|Минеральные Воды|А46026|14310|one|unspecified|extra
7|Сочи|Калуга|A45113/5114|8880|both|unspecified|unspecified
7|Сочи|Махачкала|A45007/5008|6900|both|unspecified|unspecified
8|Сочи|Махачкала|А45057/5058|7680|both|unspecified|unspecified
8|Сочи|Пенза|А45037/5038|8720|both|unspecified|unspecified
8|Сочи|Пенза|A45107/5108|12280|both|unspecified|unspecified
8|Сочи|Псков|А45135/5136|9230|both|unspecified|unspecified
8|Сочи|Псков|А45035/5036|9750|both|unspecified|unspecified
8|Сочи|Ставрополь|А45055/5056|3270|both|unspecified|unspecified
8|Сочи|Ярославль|А45015/5016|10180|both|unspecified|unspecified
8|Сочи|Ярославль|А45005/5006|10980|both|unspecified|unspecified
8|Сочи|Алматы|А45089|15745|one|unspecified|extra
8|Алматы|Сочи|А45090|13740|one|unspecified|extra
8|Сочи|Дубай|А45087|15290|one|unspecified|extra
8|Дубай|Сочи|А45088|11395|one|unspecified|extra
8|Сочи|Ереван|А45029|6370|one|unspecified|extra
8|Ереван|Сочи|А45030|4735|one|unspecified|extra
8|Сочи|Стамбул|А45069,А45071|10560|one|unspecified|extra
8|Стамбул|Сочи|А45070,А45072|8165|one|unspecified|extra
8|Сочи|Ташкент|А45091|5570|one|unspecified|extra
8|Ташкент|Сочи|А45092|19910|one|unspecified|extra
8|Сочи|Тель-Авив|А45025|15470|one|unspecified|extra
8|Тель-Авив|Сочи|А45026|13740|one|unspecified|extra
8|Сочи|Тбилиси|A45041/5042|13785|both|one_way|extra
8|Калуга|Санкт-Петербург|А44014/4013|4380|both|unspecified|unspecified
8|Псков|Калининград|А44106/4105|8580|both|unspecified|unspecified
8|Псков|Калининград|А44005/4006|7180|both|unspecified|unspecified
8|Самара|Нижневартовск|A44047/4048|5640|both|unspecified|unspecified
8|Санкт-Петербург|Тбилиси|А47039|18120|one|unspecified|extra
8|Тбилиси|Санкт-Петербург|А47040|17755|one|unspecified|extra
8|Уфа|Горно-Алтайск|А44031/4032|9280|both|unspecified|unspecified
8|Уфа|Минеральные Воды|А46022,А46122|5450|one|unspecified|unspecified
8|Чебоксары|Сургут|A46211/6212|14480|both|unspecified|unspecified
8|Чебоксары|Сургут|A46201/6202|12080|both|unspecified|unspecified
8|Самарканд|Уфа|A44040/4039|17391|both|one_way|extra'''
    for i,line in enumerate(data.splitlines(),1):
        page,origin,destination,flights,amount,direction,journey,fees=line.split('|')
        page=int(page)
        # Locate the exact printed price, allowing digit grouping spaces.
        text=norm(PDF_PAGES[page-1])
        pattern=r'(?<!\d)' + r'\s*'.join(amount) + r'\s*₽'
        match=re.search(pattern,text)
        assert match,(page,amount)
        anchor=match.group()
        qualifier='reported' if origin=='Москва (Внуково)' and destination=='Кутаиси' else 'at_least'
        p=base('S61',anchor,page)
        p['source_locator']+=f'; reviewed_offer={i}'
        notes='Минимальный рекламный тариф; даты навигации и доступность отдельных мест не указаны; номера рейсов сохранены без исправлений'
        if flights=='A46125/6125':
            notes+='; необычный номер 46125/6125 напечатан в источнике'
        if flights=='А47030':
            notes+='; в источнике для А47030 напечатано Москва–Ереван, направление не заменено предполагаемым обратным'
        TABLES['fares'].append(dict(**p,entity='Азимут',origin=origin,destination=destination,
            flight_numbers=flights,direction_scope='both_listed_directions' if direction=='both' else 'listed_origin_destination',
            period='spring_summer_2026',amount=amount,currency='RUB',value_qualifier=qualifier,
            journey_basis='one_way' if journey=='one_way' else 'not_specified',
            additional_fees='charged_extra' if fees=='extra' else 'not_specified',
            record_kind='advertised_fare',limitations=notes))
    # Fare rules: preserve the separate tables and their differing booking-code sets.
    def rule(page,brand,service,value,unit='',qualifier='reported',conditions='',anchor=None):
        anchor=anchor or ('Норма' if page==64 else 'Тарифы')
        TABLES['tariff_rules'].append(dict(**base('S61',anchor,page),entity='Азимут',
            period='issue_2026-01',brand=brand,service=service,value=str(value),unit=unit,
            value_qualifier=qualifier,conditions=conditions,record_kind='published_rule',
            limitations='Архивная публикация; текущая применимость не проверена'))
    for brand,codes,pieces,kg,hand in [('LT','U,T,X,V,Q,O,N,M,L,K,H,G,E,B',0,'',5),('FL','Q,O,N,M,L,K,H,G,E,B',1,23,5),('Нормальный','Y',1,23,10),('BS','S',2,23,10),('FR','W',2,23,10)]:
        for service,val,unit in [('booking_codes',codes,''),('included_checked_bag_pieces',pieces,'piece'),('checked_bag_weight_per_piece',kg,'kg'),('included_cabin_bag_pieces',1,'piece'),('cabin_bag_weight',hand,'kg')]:
            rule(64,brand,service,val,unit,conditions='Таблица норм багажа, печатная стр.79')
    for brand,codes,hand,pieces in [('FR','W',10,2),('BS','S',10,2),('FL','U,T,X,V,Q,O,N,M,L,K,H,G,E,B,Y',5,1),('LT','U,T,X,V,Q,O,N,M,L,K,H,G,E,B',5,0)]:
        for service,value,unit in [('booking_codes',codes,''),('included_cabin_bag_weight',hand,'kg'),('included_checked_bag_pieces',pieces,'piece')]:
            rule(65,brand,service,value,unit,conditions='Таблица тарифов, печатная стр.80')
        for service in ['refund_after_checkin','change_after_checkin']:
            rule(65,brand,service,'not_allowed',conditions='После окончания регистрации; полностью и частично неиспользованный билет')
        for service in ['refund_before_checkin','change_before_checkin']:
            if service=='refund_before_checkin' and brand=='LT':
                rule(65,brand,service,'not_allowed',conditions='До окончания регистрации')
            else:
                rule(65,brand,service,0 if brand=='FR' else 5000,'RUB',qualifier='reported' if brand=='FR' else 'at_least',conditions='До окончания регистрации; сборы по методике с 19.11.2025; для более ранних билетов прежние правила')
        rule(65,brand,'seat_selection_fee',0 if brand in {'FR','BS'} else 230,'RUB',qualifier='reported' if brand in {'FR','BS'} else 'at_least')
        if brand in {'FL','LT'}:
            for channel,fee in [('website',865),('agents',990)]:
                rule(65,brand,'extra_5kg_cabin_bag_fee',fee,'RUB','at_least',f'Канал: {channel}; суммарно не более 10 кг; 55x40x20 см')
    rule(65,'LT','checked_bag_fee',4199,'RUB','at_least','Одно место до 23 кг; сумма измерений не более 203 см')
    for service,value,unit,condition in [('checked_bag_dimension_sum',203,'cm','Одно место'),('cabin_bag_length',55,'cm',''),('cabin_bag_width',40,'cm',''),('cabin_bag_height',20,'cm',''),('infant_bag_pieces',1,'piece','Без отдельного места'),('infant_bag_weight',10,'kg','Без отдельного места'),('infant_bag_dimension_sum',115,'cm','Без отдельного места')]:
        rule(64,'all',service,value,unit,qualifier='reported' if service=='infant_bag_pieces' else 'at_most',conditions=condition)
    for category,scope,discount,condition in [('infant_without_seat','domestic',100,'До 2 лет; бесплатно'),('infant_without_seat','international',90,'До 2 лет'),('child_or_infant_with_seat','domestic',50,'2–12 лет либо до 2 лет на отдельном кресле; исключая субсидированные перевозки'),('child_or_infant_with_seat','subsidized_domestic_or_international',25,'2–12 лет либо до 2 лет на отдельном кресле')]:
        if category=='infant_without_seat' and scope=='domestic':
            rule(65,category,'ticket_price:'+scope,'free',conditions=condition)
        else:
            rule(65,category,'discount:'+scope,discount,'percent',conditions=condition)
    for service,value,unit,qual,condition in [('insurance_fee',659,'RUB','at_least','За перелёт в одну сторону'),('price_hold_fee',549,'RUB','reported','Можно оформить не позднее чем за 4 дня до вылета'),('price_hold_duration',24,'hour','reported','Фиксация цены'),('price_hold_booking_lead',4,'day','at_least','До вылета')]:
        TABLES['tariff_rules'].append(dict(**base('S61','Гарантированная цена' if service.startswith('price_hold') else '659 рублей',11),entity='Азимут',period='issue_2026-01',brand='service',service=service,value=str(value),unit=unit,value_qualifier=qual,conditions=condition,record_kind='published_rule',limitations='Архивная публикация; текущая применимость не проверена'))
    for name,value,anchor in [('cabin_configuration','100/103 кресла','100/103'),('engine','два турбореактивных двигателя SaM-146','SaM-146')]:
        TABLES['attributes'].append(dict(**base('S61',anchor,60),entity='Азимут',period='issue_2026-01',attribute=name,value=value,scope='SSJ100',record_kind='reported_specification',limitations='Типовая характеристика из журнала; не подтверждает конфигурацию конкретного борта'))


def write_outputs():
    OUT.mkdir(parents=True,exist_ok=True)
    with (ROOT/'data/source_manifest.csv').open(encoding='utf-8',newline='') as f:
        manifest={r['source_id']:r for r in csv.DictReader(f)}
    sources=[]
    for s in IDS:
        p=FILES[s]; m=manifest[s]
        counts={name+'_rows':sum(r['source_id']==s for r in rows) for name,rows in TABLES.items()}
        sources.append(dict(source_id=s,raw_path=str(p.relative_to(ROOT)),
            sha256=hashlib.sha256(p.read_bytes()).hexdigest(),publisher=m['publisher'],
            source_url=m['direct_url'],manifest_period=m['period'],
            claimed_status=m['report_claimed_status'],published_date=PUBLISHED[s],
            issue_period='2026-01' if s=='S61' else '',capture_date='',
            status_basis='Manifest label; no independent publisher verification',
            scope_locator=LOCATORS.get(s,'pdf pages 1–65; selected airline sections'),
            **counts,limitations='Дата получения неизвестна; сведения действительны в контексте публикации'))
    for rows in TABLES.values():
        assert rows and len(rows)==len({tuple(r.items()) for r in rows}), 'Exact duplicate'
        for row in rows:
            caveat={
                'S59':'Не объединять с РСБУ S60; совпадающие пассажиры и рост вертолётного сегмента из повторов текста не дублируются',
                'S60':'Не объединять с МСФО S59; опубликованные операционные показатели отличаются',
            }.get(row['source_id'],'')
            if caveat:
                row['limitations']='; '.join(filter(None,[row['limitations'],caveat]))
    for name,rows in {**TABLES,'sources':sources}.items():
        with (OUT/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
            writer.writeheader();writer.writerows(rows)
        print(name,len(rows),dict(Counter(r['source_id'] for r in rows)))


def main():
    load()
    metrics()
    build_relations_and_routes()
    build_fares_and_rules()
    write_outputs()


if __name__ == '__main__':
    main()
