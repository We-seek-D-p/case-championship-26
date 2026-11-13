"""Python 3.14, standard library. Run from any directory; regenerates three MD files."""
from pathlib import Path
import csv
from collections import Counter
from math import radians, sin, cos, asin, sqrt, ceil, isclose
from statistics import pstdev, mean
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/airport_research'
MARKET, RW, SECOND = 108_850_000, 2_700_000, 13_800_000
BASES = {'AER', 'KUF', 'KZN', 'LED', 'SVX', 'MRV'}
MOSCOW = {'SVO', 'VKO', 'DME', 'ZIA'}
BENCH = MOSCOW | {'OVB', 'KJA'}


def read(name):
    with (DATA / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


AIR = {r['airport_iata']: r for r in read('processed/airports.csv')}
ANNUAL = {(r['airport_iata'], int(r['year'])): float(r['passengers_total'])
          for r in read('processed/airport_annual.csv')}
MONTH = read('processed/airport_monthly.csv')
LINEAGE = read('documentation/DATA_LINEAGE.csv')
ROUTES = read('processed/airport_routes.csv')
COUNTRIES = {r['airport_iata']: r['country'] for r in read('processed/route_airports.csv')}
COUNTRIES.update({k: v['country'] for k, v in AIR.items()})


def distance(a, b):
    lat1, lon1, lat2, lon2 = [radians(float(x)) for x in
        (AIR[a]['latitude'], AIR[a]['longitude'], AIR[b]['latitude'], AIR[b]['longitude'])]
    return 6371 * 2 * asin(sqrt(sin((lat2-lat1)/2)**2
                             + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2))


@dataclass(frozen=True)
class Route:
    hub: str
    destination: str
    km: float
    bh: float
    fare: float
    cost: float
    frequency: int = 4
    weeks: int = 52
    seats: int = 99


def routes(hub):
    # Identical destination-selection rule for every airport; not demand optimization.
    pool = ['OMS', 'PEE', 'GOJ', 'VOG', 'MMK', 'NUX', 'UFA', 'CEK', 'KUF', 'SVX', 'KZN']
    eligible = [(distance(hub, d), d) for d in pool if d != hub
                and 600 <= distance(hub, d) <= 2200]
    chosen = sorted(eligible)[:4]
    return [Route(hub, d, km, .45 + km/650, 7000 + 3.5*km,
                  110000 + 120000*(.45 + km/650)) for km, d in chosen]


def calc(r, lf=.82, tariff=1., expense=1., hub=False):
    assert 0 <= lf <= 1 and r.frequency >= 0 and 0 < r.weeks <= 53
    legs = 2*r.frequency*r.weeks
    cap = legs*r.seats
    pax = cap*lf
    fare = r.fare*tariff*(.92 if hub else 1)
    rev = pax*(fare+900)
    var = legs*r.cost*expense+pax*650
    return dict(legs=legs, cap=cap, pax=pax, rev=rev, var=var, cm=rev-var,
                bh=legs*r.bh, fare=fare, unit=fare+900-650)


def program(rs, hub=False, lf=.82, tariff=1., expense=1., groups=1):
    rows = [calc(r, lf, tariff, expense, hub) for r in rs]
    sums = {k: sum(x[k] for x in rows)*groups for k in
            ('legs', 'cap', 'pax', 'rev', 'var', 'cm', 'bh')}
    # Each group uses a two-tail wave schedule, one physical spare per two groups.
    working = max(ceil(sums['bh']/2200), 2*groups)
    reserve = ceil(groups/2)
    cann = .06 if hub else .12
    lost_pax = sums['pax']*cann
    lost_cm = lost_pax*3000
    fixed = (working+reserve)*65e6 + (120e6 if hub else 20e6)*groups
    fixed += (45e6 if hub else 20e6)*groups + (35e6 if hub else 10e6)*groups
    cm = sums['cm']-lost_cm
    profit = cm-fixed
    slope = sum(x['cap']*(x['unit']-cann*3000) for x in rows)*groups
    be = (sum(x['legs']*r.cost*expense for x, r in zip(rows, rs))*groups+fixed)/slope
    out = dict(sums, net=sums['pax']-lost_pax, lost_pax=lost_pax, lost_cm=lost_cm,
               contribution=cm, fixed=fixed, profit=profit, working=working,
               reserve=reserve, allocated=working+reserve, be=be,
               E=cm/working, K=(sums['pax']-lost_pax)/working,
               share=100*(sums['pax']-lost_pax)/MARKET, slope=slope)
    assert out['net'] <= out['pax'] <= out['cap']
    assert isclose(out['cm'], out['rev']-out['var'], abs_tol=.001)
    assert isclose(profit, cm-fixed, abs_tol=.001)
    assert working*2200 >= out['bh']
    assert isclose(out['share'], 100*out['net']/MARKET)
    for r, x in zip(rs, rows):
        assert x['cap'] == x['legs']*r.seats
        assert isclose(x['rev'], x['pax']*(x['fare']+900))
        # Two rotations per tail: spoke turn .75h and base turn .75h.
        assert 4*r.bh+2*.75+.75 <= 16
    return out


def n(x): return f'{x:,.0f}'.replace(',', ' ')
def m(x): return f'{x/1e6:.1f}'
def pct(x): return f'{100*x:.1f}%'
def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |',
                      '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str, row))+' |' for row in rows])+'\n'


def network(a):
    snapshots = {}
    for r in ROUTES:
        o, d = r['origin_iata'], r['destination_iata']
        if r['year'] != '2025' or a not in (o, d) or {o, d} & MOSCOW:
            continue
        if COUNTRIES.get(o) != 'RU' or COUNTRIES.get(d) != 'RU': continue
        key = (tuple(sorted((o, d))), r['carrier'] or 'не указан')
        val = (float(r['weekly_departures'] or 0), float(r['seats_per_departure'] or 0))
        if val > snapshots.get(key, (-1, -1)): snapshots[key] = val
    carriers = Counter(k[1] for k in snapshots)
    competitor = Counter(k[1] for k in snapshots if k[1] not in ('Red Wings', 'не указан'))
    total = sum(carriers.values())
    hhi = sum((v/total)**2 for v in carriers.values()) if total else None
    return (len({k[0] for k in snapshots}), sum(v[0] for v in snapshots.values()),
            sum(v[0]*v[1] for v in snapshots.values()),
            competitor.most_common(1)[0][0] if competitor else 'нет данных', hhi)


def season(a):
    rows = [r for r in MONTH if r['airport_iata'] == a and r['year'] == '2025']
    vals = [float(r['passengers_total']) for r in rows]
    q3 = sum(float(r['passengers_total']) for r in rows if int(r['month']) in (7,8,9))
    estimated = sum(r['value_origin'] != 'observed' for r in LINEAGE
                    if r['entity_type'] == 'airport_monthly' and r['entity_id'] == a
                    and r['period'].startswith('2025') and r['metric'] == 'passengers_total')
    return q3/ANNUAL[a,2025], pstdev(vals)/mean(vals), estimated


def main():
    available = {a: routes(a) for a in AIR}
    econ = {a: program(rs, a not in BASES) for a, rs in available.items() if len(rs)==4 and a not in BENCH}
    existing = sorted((a for a in econ if a in BASES), key=lambda a: (-econ[a]['E'], -econ[a]['K'], a))
    new = sorted((a for a in econ if a not in BASES), key=lambda a: (-econ[a]['E'], -econ[a]['K'], a))
    ranked = sorted(econ, key=lambda a: (-econ[a]['E'], -econ[a]['K'], a))
    rank = {a: i+1 for i,a in enumerate(ranked)}
    s1, s2 = existing[0], new[0]
    r1, r2 = available[s1], available[s2]
    p1, p2 = econ[s1], econ[s2]
    sources = '''[Набор данных](../data/airport_research/README.md), [происхождение чисел](../data/airport_research/documentation/DATA_LINEAGE.csv),
[методика](../data/airport_research/documentation/METHODOLOGY.md), [ограничения](../data/airport_research/documentation/DATA_GAPS.md).
Дата анализа: 13.11.2026. Статистика: 2024–2025; модель: 2027–2030, постоянные рубли расчётного сценария.
Статус баз: [зима 2026/27](https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/) и
[лето 2026](https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/), проверены 13.11.2026.
Пассажиры RW: [итоги 2025](https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/).
Рынок: [сообщение Росавиации в АвиаПорт](https://www.aviaport.ru/news/rossiyskie-aviakompanii-perevezli-v-2025-godu-pochti-109-mln-passazhirov/).
Победа: [итоги 2025](https://www.flypobeda.ru/news/pobeda-perevezla-13-8-mln-klientov-po-itogam-2025-goda) — значение 13,8 млн из задания и локальной базы; сайт вернул 403 при проверке.
Коммерческие входы ниже — сценарные допущения, не тарифы и бюджеты авиакомпании.'''
    cand = ['# Отбор площадок Red Wings', '''## Метод отбора

Сравнивается одна стандартная программа: четыре ближайших направления из пула OMS, PEE, GOJ, VOG, MMK, NUX, UFA, CEK, KUF, SVX, KZN в диапазоне 600–2200 км.
По каждой паре 4 оборота в неделю, 52 недели, 99 кресел. Расстояние — ортодромия по координатам базы.
Это тест экономики при общей загрузке 82%, а не доказательство O&D. Пассажиропоток аэропорта не используется как спрос маршрута.
Главный критерий E = дополнительный CM / рабочие борта; второй K = чистые сегменты / рабочие борта.
Порядок общий для пригодных площадок; отдельно показаны лучшие внутри двух классов.
OVB и KJA оставлены конкурентными ориентирами сильных хабов; московские аэропорты исключены из новых региональных площадок.
Опорная сеть по пресс-релизу не доказывает наличие работающих пересадочных волн.

## Все 24 аэропорта

Рост рассчитан как (P2025/P2024 − 1) × 100%. Сезонность: доля Q3 / CV; «восст.» — число месяцев с происхождением, отличным от observed.
Потенциальный спрос в таблице — необходимый валовый объём программы при LF=82%, не независимая оценка рынка.
Конкурент — перевозчик с наибольшим числом уникальных пар в исторической выборке, а не установленный лидер аэропорта.
Экономический результат — годовая Π после постоянных расходов, млн ₽.''']
    rows=[]
    for a in AIR:
        q, cv, est = season(a)
        pairs, freq, seats, comp, hhi = network(a)
        status = 'ориентир' if a in BENCH else ('опорный, лето' if a=='MRV' else 'опорный' if a in BASES else 'новый')
        e = econ.get(a)
        rows.append([a+' '+AIR[a]['city'], status, n(ANNUAL[a,2025]),
                     f'{100*(ANNUAL[a,2025]/ANNUAL[a,2024]-1):+.1f}%', pairs,
                     f'{pct(q)} / {cv:.2f}; восст. {est}/12', n(e['pax']) if e else 'не оценён',
                     comp, m(e['profit']) if e else '—', rank.get(a,'—')])
    cand += [table(['Аэропорт','Статус','Пассажиры 2025','Рост','Рег. пары','Сезонность Q3 / CV','Спрос, сегм.','Конкурент выборки','Π, млн ₽','Место'], rows),
             'Махачкала (MCX) — опорный аэропорт зимы 2026/27 вне 24-строчной базы: пассажиры, рост, сезонность и экономика не оценены. Москва — опорный город, но пресс-релиз не присваивает этот статус всем четырём аэропортам московского узла.',
             '## Топ-3 новых площадок\n\n'+', '.join(a+' '+AIR[a]['city'] for a in new[:3]),
             '## Топ-3 существующих баз\n\n'+', '.join(a+' '+AIR[a]['city'] for a in existing[:3]),
             '## Экономика финалистов\n\nВсе показатели условны на принятую коммерческую модель; E включает потерю CM от каннибализации.']
    cand.append(table(['Площадка','Маршруты','CM, млн ₽','E, млн ₽/борт','K, сегм./борт','F, млн ₽','Π, млн ₽','LF BE'],
        [[a, ', '.join(r.destination for r in available[a]), m(econ[a]['contribution']), m(econ[a]['E']),
          n(econ[a]['K']), m(econ[a]['fixed']), m(econ[a]['profit']), pct(econ[a]['be'])] for a in new[:3]+existing[:3]]))
    cand += ['## Доступность региональных направлений', '''Только внутренние пары за 2025 год, без московского узла. Зеркала сведены к неупорядоченной паре + перевозчик.
Повторные и перекрывающиеся публикации не суммируются: выбирается максимум известной частоты для пары и перевозчика.
Следовательно, ниже — верхняя огибающая опубликованных снимков, а не единое действующее расписание.
Частоты считаются в одном направлении; множитель 2 здесь не применяется. Неизвестные значения не восстанавливаются повторно;
входные оценки из processed сохраняют свои ограничения. HHI — по числу свидетельств уникальных пар на перевозчика, не по реальным креслам рынка.''',
        table(['Аэропорт','Пары','Вылеты/нед., огибающая','Известные кресла/нед.','HHI пар'],
              [[a, network(a)[0], f'{network(a)[1]:.1f}', n(network(a)[2]), f'{network(a)[4]:.2f}' if network(a)[4] is not None else '—'] for a in AIR]),
        '## Причины исключения остальных\n\n'+ '; '.join(a+': '+('московский ориентир' if a in MOSCOW else 'сильный конкурентный хаб, вне шорт-листа новых баз' if a in BENCH else 'менее четырёх направлений по общему фильтру' if a not in econ else f'E={m(econ[a]["E"])} млн ₽/борт, ниже топ-3 своего класса') for a in AIR if a not in new[:3]+existing[:3])+'.',
        '## Источники\n\n'+sources]
    (ROOT/'analysis/HUB_CANDIDATES.md').write_text('\n\n'.join(cand)+'\n')
    threshold = .82+(p1['profit']-p2['profit'])/p2['slope']
    extra = (threshold-.82)*p2['cap']
    savings = (p1['profit']-p2['profit'])/sum(calc(r,hub=True)['legs']*r.cost for r in r2)
    winner = 'S1' if p1['profit'] > max(0,p2['profit']) else 'S2' if p2['profit']>0 else 'S0'
    decision = f'Выбрана стратегия {winner}: развитие существующей базы {s1} ({AIR[s1]["city"]})' if winner=='S1' else f'Выбрана стратегия {winner}'
    doc = ['# Red Wings: расчёт стратегии 2027–2030', decision+f'. В базовом 2028 году это {n(p1["net"])} дополнительных пассажирских сегментов и {m(p1["profit"])} млн ₽ годового расчётного результата против {m(p2["profit"])} млн ₽ нового хаба {s2}. Решение условно на сценарные тарифы, затраты и достижение загрузки; это не прогноз подтверждённого спроса.',
           '## Сравнение S0 / S1 / S2 за 2028 год',
           '**S0 — базовый сценарий:** действующая сеть без дополнительной программы. **S1 — развитие действующих баз:** дополнительные прямые региональные рейсы из Минеральных Вод. **S2 — новый региональный хаб:** база в Новом Уренгое, прямые рейсы и пересадочные волны с дополнительными расходами. Все показатели показывают изменение относительно S0.']
    metrics = [('Дополнительные пассажиры, тыс.','net',1000),('Выручка новой программы, млн ₽','rev',1e6),('Переменные расходы, млн ₽','var',1e6),
               ('Потерянный CM, млн ₽','lost_cm',1e6),('Дополнительный CM после потерь, млн ₽','contribution',1e6),('Постоянные расходы, млн ₽','fixed',1e6),
               ('Расчётный результат, млн ₽','profit',1e6),('Рабочих самолётов','working',1),('Выделено с резервом','allocated',1),
               ('Результат / рабочий борт, млн ₽',None,1),('Прирост доли рынка, п.п.','share',1),('LF безубыточности, %','be',.01)]
    doc.append(table(['Метрика, 2028','S0','S1: '+s1,'S2: '+s2], [[label,'—' if key=='be' else '0',
        f'{(p1[key]/div if key else p1["profit"]/p1["working"]/1e6):.3f}' if key=='share' else f'{(p1[key]/div if key else p1["profit"]/p1["working"]/1e6):.1f}',
        f'{(p2[key]/div if key else p2["profit"]/p2["working"]/1e6):.3f}' if key=='share' else f'{(p2[key]/div if key else p2["profit"]/p2["working"]/1e6):.1f}'] for label,key,div in metrics]))
    doc += ['Выручка и расходы в таблице относятся к новым рейсам; потери старой программы показаны отдельно через CM. S0 означает нулевые дополнительные значения, не нулевой бизнес RW. Инвестиции и налоги не включены; результат не равен чистой бухгалтерской прибыли.',
            '## Входные параметры и происхождение', '''Статистика аэропортов берётся из processed без перезаписи. Коммерческие параметры ниже — единые модельные предположения, не официальные цены.
Независимого O&D нет: модель показывает требуемые объёмы продаж. Не применяем общий поток аэропорта как спрос маршрута.
Расстояния и зависимость тарифа от расстояния не доказывают готовность пассажиров платить.''',
            table(['Параметр','S1','S2 / основание'],[
                ['Загрузка осторожная / база / высокая','70 / 82 / 90%','70 / 82 / 90%'],
                ['Тариф чистый за сегмент, ₽','7 000 + 3,5 × км','92% тарифа S1: общий эффект пересадочной скидки'],
                ['Допуслуги / расходы на пассажира, ₽','900 / 650','900 / 650; груз = 0'],
                ['Block hours за вылет','0,45 + км / 650','0,45 + км / 650; руление и запас включены'],
                ['Стоимость вылета, ₽','110 000 + 120 000 × BH','110 000 + 120 000 × BH'],
                ['Рабочий налёт на борт / год','2 200 BH','2 200 BH после ТО'],
                ['Обороты / недели / кресла','4 / 52 / 99','4 / 52 / 99, SSJ-100'],
                ['Каннибализация валовых сегментов','12%','6%'],
                ['Потерянный CM на ушедший сегмент, ₽','3 000','3 000'],
                ['Вытеснение из-за переброски флота','0 при дополнительном флоте','0; не утверждение о наличии бортов'],
                ['Постоянные на каждый выделенный борт, млн ₽','65','65, резерв оплачивается тоже'],
                ['База / персонал / инфраструктура, млн ₽/год','20 / 20 / 10','120 / 45 / 35'],
                ['Разовые инвестиции','не заданы, в Π не включены','нужен отдельный инвестбюджет до открытия']]),
            'Стоимость вылета уже включает топливо, экипаж, ТО, аэропорт, навигацию и handling: повторного начисления нет. Фиксированные 65 млн ₽/борт — отдельный годовой бюджет владения/лизинга и страхования. Дополнительные персонал и инфраструктура относятся к базе.',
            '## Формулы и смысл переменных', r'''Для маршрута:

$$
L=2fw,\quad C=Lq,\quad P=C\cdot LF,\quad R=P(T+A),\quad V=Lc_f+Pc_p,\quad CM=R-V,\quad BH=Lb.
$$

Здесь $f$ — обороты в неделю, $w$ — недели, $q$ — кресла, $T$ — чистый тариф за сегмент, $A$ — допуслуги, $c_f$ — переменный расход на вылет, $c_p$ — расход на пассажира, $b$ — block hours.

Для программы:

$$
\Delta P=\sum P(1-c)-P_{\mathrm{displaced}},\quad CM_{\mathrm{program}}=\sum CM-\sum(Pc\cdot3000)-CM_{\mathrm{displaced}},\quad \Pi=CM_{\mathrm{program}}-F.
$$

$c$ — доля каннибализации; потеря маржи старого рейса составляет 3 000 ₽ за сегмент.

$$
N_{\mathrm{work}}=\max\left(\left\lceil\frac{BH}{2200}\right\rceil,N_{\mathrm{peak}}\right),\quad N_{\mathrm{alloc}}=N_{\mathrm{work}}+N_{\mathrm{reserve}},\quad E=\frac{CM_{\mathrm{program}}}{N_{\mathrm{work}}},\quad K=\frac{\Delta P}{N_{\mathrm{work}}}.
$$

Распределяем $F$ пропорционально креслам. Безубыточная загрузка маршрута и программы:

$$
LF_{BE,r}=\frac{Lc_f+F_r}{C(T+A-c_p-c\cdot3000)},\qquad LF_{BE,\mathrm{program}}=\frac{\sum Lc_f+F}{\sum C(T+A-c_p-c\cdot3000)}.
$$

Знаменатели должны быть положительны. При наличии оценки O&D применяется:

$$
P=\min(C\cdot LF, OD\cdot s).
$$

Здесь $OD$ не задан, поэтому ограничение спросом не применяется.''']
    r = r1[0]; x = calc(r); fixed_r=p1['fixed']*x['cap']/p1['cap']
    be=(x['legs']*r.cost+fixed_r)/(x['cap']*(x['unit']-.12*3000))
    doc += ['## Полный числовой пример: '+s1+'–'+r.destination,
            f'Исходные данные: {r.km:.0f} км, b={r.bh:.3f} BH, f=4, w=52, q=99, LF=82%, T={r.fare:.2f} ₽, A=900 ₽, c_p=650 ₽, c_f={r.cost:.2f} ₽. В вычислениях расстояния не округлены.',
            f'$L=2\\times4\\times52={n(x["legs"])}$; $C={n(x["legs"])}\\times99={n(x["cap"])}$; $P={n(x["cap"])}\\times0{{,}}82={n(x["pax"])}$ сегментов. '
            f'$R=C\\times0{{,}}82\\times({r.fare:.2f}+900)={m(x["rev"])}$ млн ₽; $V={n(x["legs"])}\\times{r.cost:.2f}+C\\times0{{,}}82\\times650={m(x["var"])}$ млн ₽; $CM={m(x["cm"])}$ млн ₽. '
            f'Потеря $CM=C\\times0{{,}}82\\times0{{,}}12\\times3000={m(x["pax"]*.12*3000)}$ млн ₽; $F_r={m(fixed_r)}$ млн ₽; $\\Pi_r={m(x["cm"]-x["pax"]*.12*3000-fixed_r)}$ млн ₽. '
            f'$LF_{{BE}}=\\frac{{{n(x["legs"])}\\times{r.cost:.2f}+{fixed_r:.0f}}}{{{n(x["cap"])}\\times({r.fare:.2f}+900-650-360)}}={100*be:.1f}\\%$. '
            'Экономический смысл: маршрут имеет положительный результат только при достаточных продажах по принятому чистому тарифу.',
            '## Итоги всех предлагаемых маршрутов']
    route_rows=[]
    for label,rs,p,h in [('S1',r1,p1,False),('S2',r2,p2,True)]:
        for r in rs:
            x=calc(r,hub=h); c=.06 if h else .12
            fr=p['fixed']*x['cap']/p['cap']
            br=(x['legs']*r.cost+fr)/(x['cap']*(x['unit']-c*3000))
            assert br>0
            route_rows.append([label+' '+r.hub+'–'+r.destination, f'{r.km:.0f}', f'{r.bh:.2f}',
                f'{x["fare"]:.0f}', n(r.cost), n(x['cap']),n(x['pax']),m(x['rev']),m(x['var']),
                m(x['cm']),pct(br),'да' if .82>=br else 'нет'])
    doc.append(table(['Маршрут','км','BH/вылет','T, ₽','c_f, ₽','Кресла','Сегменты','R, млн','V, млн','CM до потерь, млн','LF BE','82% ≥ BE'], route_rows))
    doc += ['## Флот и физическая схема расписания',
            f'S1: {p1["bh"]:.0f} BH; ceil(BH/2 200)={ceil(p1["bh"]/2200)}, пик=2, выделяется {p1["working"]} рабочих + {p1["reserve"]} резервный. S2: {p2["bh"]:.0f} BH, {p2["working"]}+{p2["reserve"]}. Резерв не производит плановые часы.',
            '''Четыре дня: пн, вт, чт, сб. На каждом из двух бортов два оборота в день: один утренний и один дневной.
Первый вылет из базы 06:00, второй 14:00 по единому времени базы. Время стоянки в пункте 45 минут.
Утром обслуживаются направления 1 и 2, днём 3 и 4; на следующем дне порядок меняется.
Таким образом, каждый маршрут получает 4 оборота/неделю, в каждом направлении существует утренний и дневной вылет.
Программа проверяет возврат утренних бортов минимум за 75 минут до 14:00 и возврат дневных до 22:00.
Это проверка занятости бортов, не подтверждение слотов, смен экипажа и эксплуатационного допуска.''']
    sched=[]
    for label,rs in [('S1',r1),('S2',r2)]:
        for r in rs:
            arrival=6+2*r.bh+.75
            end=14+2*r.bh+.75
            assert arrival+1.25<=14 and end<=22
            sched.append([label+' '+r.hub+'–'+r.destination, f'{arrival:.2f}', f'{14-arrival:.2f}', f'{end:.2f}'])
    doc.append(table(['Оборот (часы от 00:00 базы)','Возврат утра','До 14:00, ч','Возврат дня'],sched))
    # Each spoke is in the morning bank twice and afternoon bank twice weekly.
    # Only morning inbound and afternoon outbound legs connect: half of all legs.
    transfer_rows = []
    used = Counter()
    for origins, destinations in [(r2[:2], r2[2:]), (r2[2:], r2[:2])]:
        for origin in origins:
            for dest in destinations:
                demand = .20*p2['pax']/2/8
                free_origin = 99*.82*2*52-used[origin.destination, 'in']
                free_dest = 99*.82*2*52-used[dest.destination, 'out']
                flow = min(demand, free_origin, free_dest)
                assert isclose(flow, demand)
                used[origin.destination, 'in'] += flow
                used[dest.destination, 'out'] += flow
                transfer_rows.append([origin.destination+' → '+s2+' → '+dest.destination,
                                      n(flow), n(2*flow)])
    transfer = sum(used[k] for k in used if k[1]=='in')
    assert isclose(2*transfer, .20*p2['pax'])
    assert all(v <= .4*99*.82*2*52+.001 for v in used.values())
    doc += [f'В S2 пересадка: 20% сегментов = {n(transfer)} O&D-поездок × 2 сегмента, уже внутри {n(p2["pax"])} сегментов загрузки. '
            'Условный спрос — 10 / 20 / 30% сегментов в осторожном / базовом / высоком сценарии. '
            'Это сценарий при отсутствии O&D. Потоки делятся между парами направлений утро→день и день→утро в дни смены порядка; '
            'в среднем на маршруте 20% пассажиров пересадочные, на пригодных для стыковки вылетах — 40%; оставшиеся места занимает местный спрос. Пересадки не прибавляются сверх LF. '
            'Реальная MCT аэропорта не подтверждена: 75 минут — плановый параметр, требуется сквозное оформление багажа.',
            table(['Сценарная пересадочная O&D-пара','Поездки/год','Сегменты/год'], transfer_rows),
            'Каждая O&D-пара получает одинаковую долю сценарного спроса; код ограничивает её остатком обоих плеч и учитывает только направления с волной. После распределения для местного спроса сохраняется остаток кресел. Это проверка вместимости, не измерение O&D.',
            'Используется только SSJ-100 на 99 кресел. Новые SJ-100/ПД-8 и Ту-214 не включены в доступный парк и не наследуют эти кресла и расходы. Геометрия ВПП не заменяет эксплуатационный допуск. При отсутствии дополнительных исправных бортов программа не запускается: переброска требует отдельного вычета вытесненных пассажиров и CM.',
            '## Чувствительность и условие смены решения']
    sensitivity=[]
    for dimension, values in [('LF', [.70,.82,.90]),('Тариф', [.85,1,1.15]),('Расход на вылет',[.85,1,1.15])]:
        for value in values:
            kw={'lf':value} if dimension=='LF' else {'tariff':value} if dimension=='Тариф' else {'expense':value}
            a=program(r1,**kw); b=program(r2,True,**kw)
            win=max([('S0',0),('S1',a['profit']),('S2',b['profit'])],key=lambda t:t[1])[0]
            sensitivity.append([dimension, f'{value:.2f}',m(a['profit']),m(b['profit']),win])
    a=program(r1,lf=.70,tariff=.85,expense=1.15); b=program(r2,True,lf=.70,tariff=.85,expense=1.15)
    sensitivity.append(['Совместный стресс','LF70%, T−15%, c+15%',m(a['profit']),m(b['profit']),max([('S0',0),('S1',a['profit']),('S2',b['profit'])],key=lambda t:t[1])[0]])
    doc.append(table(['Изменение','Значение / множитель','Π S1, млн ₽','Π S2, млн ₽','Победитель с S0'],sensitivity))
    doc += [f'При фиксированной S1 и остальных базовых параметрах S2 сравняется с ней при LF={pct(threshold)}: '
            f'$0{{,}}82 + (\\Pi_1-\\Pi_2)/{m(p2["slope"])}$ млн ₽ на единицу LF. Это ещё {n(extra)} валовых сегментов в год. '
            f'Для строгого превосходства порог нужно превысить. Альтернатива при LF82% — снижение полного расхода на вылет S2 более чем на {pct(savings)} '
            f'или сокращение её годовых фиксированных расходов более чем на {m(p1["profit"]-p2["profit"])} млн ₽. '+
            ('Порог загрузки выше 100%: одним заполнением кресел его достичь нельзя.' if threshold>1 else 'Это условие для проверки продажами, не прогноз достижения.'),
            'Для восстановленной сезонности проверяется общий сдвиг LF на ±5 п.п.; годовой средний LF не выводится из месячного профиля. Q3 меняется на ±25% с переносом обратного изменения на прочие месяцы при неизменном годовом потоке.']
    seas=[]
    for a in (s1,s2):
        q,cv,e=season(a)
        for factor in (.75,1,1.25):
            seas.append([a, e, pct(q*factor),pct(.82+(-.05 if factor==.75 else .05 if factor==1.25 else 0)),
                         m(program(available[a],a==s2,lf=.82+(-.05 if factor==.75 else .05 if factor==1.25 else 0))['profit'])])
    doc.append(table(['Площадка','Восст. месяцев','Q3 сценарий','LF стресс','Π, млн ₽'],seas))
    doc += ['## Масштабирование 2027–2030',
            'Этапы условны на обеспечение парка. 2027: пилот 26 недель, затем годовая программа. 2029–2030: повторение блока на следующих базах топ-3 с независимыми парами; это верхний ориентир тиражирования, не утверждённое расписание. Резерв общий. Цены постоянные, инфляция не моделируется.']
    scale=[]
    for year, groups, weeks in [(2027,1,26),(2028,1,52),(2029,2,52),(2030,3,52)]:
        rs=[Route(r.hub,r.destination,r.km,r.bh,r.fare,r.cost,weeks=weeks) for r in r1]
        p=program(rs,groups=groups)
        scale.append([year,4*groups,p['working'],p['allocated'],n(p['net']),m(p['profit'])])
    doc.append(table(['Год','Маршрутных эквивалентов','Рабочих','Всего с резервом','Δ сегменты','Π, млн ₽'],scale))
    doc += ['Масштаб 2029–2030 — ресурсный сценарий эквивалентных блоков экономики S1, а не независимый пересчёт спроса следующих баз. Перед каждым этапом требуются подтверждение продаж, поставок/аренды и ТО. Заявления о производстве не считаются поставками.',
            '## Доля рынка и разрыв до второго перевозчика',
            f'Входы 2025: рынок {n(MARKET)}, RW {n(RW)}, Победа {n(SECOND)} пассажиров. $Share_{{RW}}=2{{,}}7/108{{,}}85\\times100={100*RW/MARKET:.2f}\\%$. '
            f'$Gap=13{{,}}8-2{{,}}7={m(SECOND-RW)}$ млн; $Multiplier=13{{,}}8/2{{,}}7={SECOND/RW:.2f}$. '
            f'CAGR до фиксированного уровня Победы за 2025 за 2026–2030 (5 лет): $CAGR=(13{{,}}8/2{{,}}7)^{{1/5}}-1={100*((SECOND/RW)**.2-1):.1f}\\%$. '
            f'S1 покрывает {pct(p1["net"]/(SECOND-RW))} разрыва; доля при фиксированном рынке = {100*(RW+p1["net"])/MARKET:.3f}%, прирост {p1["share"]:.3f} п.п. '
            'Это не прогноз рыночного знаменателя и будущего места конкурента.',
            '## Почему выбранная стратегия лучше',
            f'В рамках общего теста S1 сохраняет чистый тариф без общей пересадочной скидки и требует меньших расходов базы. '
            f'Преимущество результата над S2 — {m(p1["profit"]-p2["profit"])} млн ₽/год. '
            'Рекомендация: пилот прямых региональных рейсов из выбранной действующей базы; новый хаб отложить до подтверждения коммерческого порога. '
            'Для MRV подтверждён летний статус; круглогодичная работа с заложенным бюджетом базы — отдельное допущение. Превышение её годовых расходов более чем на преимущество над альтернативой меняет выбор. '
            'В неблагоприятном совместном стрессе ориентироваться на S0, если обе программы убыточны. '
            'Рейтинг не измеряет ценовую конкуренцию и эластичность спроса; выбор города предварителен до проверки тарифов и O&D. '
            'Прежние ориентиры 97,8–143,6 тыс. и 169–877 млн ₽ в расчёт не переносились: исходного расчёта в репозитории не обнаружено.',
            '## Источники и воспроизведение\n\n'+sources,
            'Команда из корня: `python3.14 analysis/calculate.py`. Стандартная библиотека; исходные CSV не меняются. Генератор содержит проверки ёмкости, пассажиров, выручки, CM, результата, часов, пика и общего рыночного знаменателя. Таблицы создаются непосредственно из результатов.',
            'Расчётный скрипт: [calculate.py](calculate.py).']
    (ROOT/'analysis/HUB_STRATEGY.md').write_text('\n\n'.join(doc)+'\n')
    (ROOT/'README.md').write_text(f'''# Red Wings: развитие региональной сети

Расчётный кейс выбора между развитием действующих баз и новым региональным хабом, горизонт 2027–2030. Рабочая ветка `gg`.

- [Интерактивный маршрутный калькулятор](calculator/README.md).
- [Данные аэропортов](data/airport_research/README.md): 24 аэропорта, статистика 2024–2025 и исторические наблюдения маршрутов.
- [Сравнение всех аэропортов и финалистов](analysis/HUB_CANDIDATES.md).
- [Стратегия, сравнительная таблица S0/S1/S2, математика и ссылка на Python-скрипт](analysis/HUB_STRATEGY.md).

{decision}. Базовая модель 2028: **{n(p1['net'])}** дополнительных пассажирских сегментов, **{m(p1['profit'])} млн ₽** годового результата, **{p1['allocated']} борта** с резервом, **+{p1['share']:.3f} п.п.** доли при фиксированном рынке 2025. Новый хаб {s2} уступает на {m(p1['profit']-p2['profit'])} млн ₽. Коммерческие параметры сценарные; спрос и доступность флота требуют подтверждения.

Воспроизведение: `python3.14 analysis/calculate.py` из корня. Python 3.14, без зависимостей. Пересоздаются только README и два аналитических Markdown. Презентация не меняется.
''')
    print(f'PASS: 24 airports; S1={s1}, S2={s2}; top new={new[:3]}, bases={existing[:3]}')
    print(f'S1 net={p1["net"]:.0f}; profit={p1["profit"]/1e6:.1f}m; fleet={p1["working"]}+{p1["reserve"]}; S2 threshold={threshold:.4f}')


if __name__ == '__main__':
    main()
