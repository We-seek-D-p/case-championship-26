"""Материалы защиты из готовых результатов модели.
uv run --frozen --no-sync python scripts/build_defense.py
PDF: ReportLab из доступного Python-окружения или поставляемого runtime.
"""
import argparse
import csv
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'submission'

def read(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def table_md(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|']+['| '+' | '.join(str(x) for x in r)+' |' for r in rows])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passport-only",action="store_true",help="Собрать только комплект P0")
    args=parser.parse_args()
    if importlib.util.find_spec('reportlab') is None:
        runtime=Path(os.environ.get('RUNTIME_PYTHON',str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python')))
        if not runtime.is_file():raise SystemExit('Для сборки PDF нужен ReportLab; укажите RUNTIME_PYTHON с установленным пакетом.')
        subprocess.run([str(runtime),str(Path(__file__).resolve()),*sys.argv[1:]],check=True)
        return
    from reportlab.pdfgen import canvas
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    for name,filename in [('Body','Arial.ttf'),('Bold','Arial Bold.ttf')]:
        font_name='DejaVuSans.ttf' if name=='Body' else 'DejaVuSans-Bold.ttf'
        font=next(ROOT.glob(f'.venv/lib/python*/site-packages/matplotlib/mpl-data/fonts/ttf/{font_name}'),None)
        if font is None:font=Path('/System/Library/Fonts/Supplemental')/filename
        if not font.exists():
            import matplotlib.font_manager as fm
            font=Path(fm.findfont(fm.FontProperties(family='DejaVu Sans',weight='bold' if name=='Bold' else 'normal')))
        pdfmetrics.registerFont(TTFont(name,str(font)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Bold')
    OUT.mkdir(exist_ok=True)
    summaries=read('results/strategy/hypothesis_comparison.csv')
    def get(h,c='base',year='2028'):return next(r for r in summaries if (r['hypothesis'],r['scenario'],r['year'])==(h,c,year))
    def fmt(r,key,scale=1,digits=0):return f'{float(r[key])/scale:.{digits}f}'.replace('.',',')
    sources={r['source_id']:r for r in read('data/source_manifest.csv')}
    def source_link(sid):
        s=sources[sid];url=s['direct_url'] if s['direct_url'] not in ('not_found','not_identified','') else s['landing_url']
        return f'<link href="{escape(url, {chr(34): "&quot;"})}" color="#007F89">{sid}</link>'
    b,c=get('H2'),get('H2','cautious')
    baseline={r['entity']:r for r in read('submission/strategy-baseline.csv')}
    rw=float(baseline['Red Wings']['passengers'])
    second=float(baseline['Победа']['passengers'])
    gap=second-rw
    def num(value,digits=1):return f'{value:.{digits}f}'.replace('.',',')
    coverage=num(float(b['net_passenger_segments'])/gap*100,2)
    active=int(b['active_aircraft']);reserve=int(b['reserve_aircraft'])
    comparison=[['2028','Сегменты,\nтыс.','Билеты,\nмлрд ₽','Δ доли,\nп.п.','Результат*,\nмлн ₽']]
    for case in ('base','cautious'):
        for hyp in ('H1','H2'):
            r=get(hyp,case)
            comparison.append([hyp+' '+('база' if case=='base' else 'осторожный'),fmt(r,'net_passenger_segments',1000,1),fmt(r,'incremental_revenue_rub',1e9,2),fmt(r,'share_delta_pp',1,3),fmt(r,'contribution_rub',1e6)])
    assumptions={r['route_id']:r for r in read('results/strategy/route_assumptions.csv')}
    scenarios=read('results/strategy/route_scenarios.csv')
    routes=[]
    for r in (r for r in scenarios if (r['hypothesis'],r['scenario'],r['year'])==('H2','base','2028')):
        p=assumptions[r['route_id']]
        caution=next(x for x in scenarios if (x['route_id'],x['scenario'],x['year'])==(r['route_id'],'cautious','2028'))
        routes.append(dict(route_id=r['route_id'],origin=r['origin'],destination=r['destination'],
            status='Добавочные частоты Red Wings' if p['rw_evidence']=='True' else 'Проектируемая пара',
            added_roundtrips_week=p['added_roundtrips_week'],net_segments_base=round(float(r['net_segments'])),
            net_segments_cautious=round(float(caution['net_segments'])),net_revenue_base_rub=round(float(r['net_revenue_rub'])),
            net_revenue_cautious_rub=round(float(caution['net_revenue_rub'])),block_hours_week=2*float(p['block_h_oneway'])*int(p['added_roundtrips_week']),
            aircraft='SJ-100; общий пул 2 рабочих + 1 резервный',
            demand_method='Геометрическое среднее 27510 и 106309 по S23, 2025; захват 40%; ограничение креслами и вычет своих продаж',
            frequency_method='План +2 оборота/нед.; 20800 кресел/год; потолок загрузки 85%/72%',
            source_ref='../data/SOURCE_MANIFEST.md#s23',route_evidence_refs=p['evidence_refs']))
    with (OUT/'routes.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,list(routes[0]),lineterminator='\n');w.writeheader();w.writerows(routes)
    route_table=[[r['origin']+' → '+r['destination'],r['status'],r['added_roundtrips_week'],f"{r['net_segments_base']/1000:.1f} / {r['net_segments_cautious']/1000:.1f}",f"{r['net_revenue_base_rub']/1e6:.0f} / {r['net_revenue_cautious_rub']/1e6:.0f}",f"{r['block_hours_week']:.1f}"] for r in routes]
    (OUT/'routes.md').write_text('''# Маршруты H2

Десять прямых пар из Екатеринбурга. Для каждой добавляем два оборота в неделю.
Пассажиры и выручка — прирост после вычета переноса собственных продаж.
В числовых колонках: базовый / осторожный сценарии 2028 года.

'''+table_md(['Пара','Статус','Доп. оборотов/нед.','Сегменты, тыс./год','Выручка, млн ₽/год','Блок-ч/нед.'],route_table)+'''

Спрос: [S23](../data/SOURCE_MANIFEST.md#s23), итоги 2025 года:
Омск—Казань 27 510, Омск—Новосибирск 106 309. Геометрическое среднее ×40% —
общий ориентир 21,6 тыс. местных сегментов на пару до кресельных ограничений.
Коэффициент 40% — допущение. Далее применяются спрос, освоение и собственное замещение.
Два оборота дают 20 800 кресел за 52 недели; потолок продаж — 85%/72%.
Частота выбрана по спросу, затратам и [ротациям](../results/strategy/weekly_rotations.csv).

Ресурс: SJ-100, общий пул 2 рабочих +1 резервный, 100,8 блок-ч/неделю.
[Все параметры обеих H](../results/strategy/route_assumptions.csv),
[все маршрутные сценарии](../results/strategy/route_scenarios.csv),
[источники](../data/SOURCE_MANIFEST.md).
''',encoding='utf-8')

    body=ParagraphStyle('body',fontName='Body',fontSize=10.5,leading=14,spaceAfter=5)
    heading=ParagraphStyle('heading',parent=body,fontName='Bold',fontSize=12,leading=15,spaceBefore=7,spaceAfter=4)
    title=ParagraphStyle('title',parent=heading,fontSize=18,leading=22,spaceAfter=9)
    small=ParagraphStyle('small',parent=body,fontSize=9.2,leading=12.5)
    story=[]
    def p(text,style=body):story.append(Paragraph(text,style))
    def h(text):p(text,heading)
    def link(url,label):return f'<link href="{escape(url)}" color="#007F89">{label}</link>'
    p('Red Wings: концепция роста до №2',title)
    p('<b>Кейс №5:</b> «Новый хаб или прямые рейсы?»; уточнение 10.11.2026<br/><b>Команда:</b> WeSeekDp · <b>Контакт:</b> Автюхов Егор Юрьевич, @Morgart31')
    h('1. Команда и роли')
    p('Макаренко Константин — модель и код; Федосеев Николай — экономика и риски; Автюхов Егор — данные и источники; Алексеев Фёдор — документы и карта. Выбор стратегии и защита — совместно.')
    h('2. Какую проблему решаем')
    p(f'Рабочее определение №2 команды — число перевезённых пассажиров отдельной российской авиакомпании за год, включая внутренние и международные рейсы. В 2025: Red Wings — <b>{num(rw/1e6)} млн</b>, «Победа» (№2) — <b>{num(second/1e6)} млн</b>; разрыв — <b>{num(gap/1e6)} млн</b>. S7 — {num(float(baseline["S7"]["passengers"])/1e6)} млн, не целевой №2. Метрика и срок достижения не заданы организаторами.')
    h('3. Какое решение сделали и кому оно полезно')
    p('Концепция для руководства и коммерческой службы: <b>сеть</b> — пилот из существующей базы с последующим расширением; <b>цифровые каналы</b> — продвижение новых частот и использование существующих сервисов; <b>коммерция</b> — прямые продажи и допуслуги с отдельным учётом маржи. Каждую очередь запускаем по подтверждённому спросу, экономике и доступному флоту.')
    h('4. Где и как проверили решение')
    p('Сценарно сравнили H1 (новая база Уфа, восемь плеч и четыре пересадочные связки) и H2 (десять прямых пар из Екатеринбурга) на 2027–2028 годы. H2 выбрана по осторожной экономике и возможности начать с трёх пар. Цифровые предложения пока не испытаны на пассажирах.')
    h('5. На какие данные опираемся')
    p(f'<b>Факты 2025:</b> {source_link("S08")} — Red Wings; {link(baseline["Победа"]["source_url"],"Интерфакс, 15.01.2026")} — «Победа»; {link(baseline["S7"]["source_url"],"S7")} — сопоставление. {source_link("S03")} — рынок 108,85 млн пассажиров; {source_link("S23")} — линии Омск—Казань (27 510) и Омск—Новосибирск (106 309). Локаторы и периоды: strategy-baseline.csv и data/SOURCE_MANIFEST.md.',small)
    p('<b>Синтетические входы:</b> общий ориентир спроса обеих H — геометрическое среднее двух линий ×40%; это аналог, не измеренный O&amp;D выбранных пар. Тарифы, расходы, освоение, замещение и загрузка — допущения команды, проверенные в двух сценариях и стрессах.',small)
    h('6. Как решали задачу и использовали ИИ')
    p('Сопоставили города, спрос и конкурентов; ограничили продажи спросом и креслами, вычли перенос своих продаж, проверили ротации и чувствительность. Статистика — аналоги и сценарии; матанализ — пороги; алгоритмы и Python — ротации и расчёты. Статус освоения дисциплин командой не зафиксирован; не хватает реальных O&amp;D и данных цифровой воронки.',small)
    p('ChatGPT / Deep Research — исследования; Codex — код и обновление материалов. Проверка: публикации и локаторы, независимый пересчёт CSV и проверки кресел/ротаций, визуальная проверка PDF. Исходные исследования сохранены без изменений в research/reports/.',small)
    story.append(PageBreak())
    h('7. Полученное решение и результат')
    p(f'<b>H2, полная программа 2028: {active} рабочих SJ-100 + {reserve} резервный.</b> Десять пар; по два добавочных оборота в неделю. Первая очередь, а не решение всей задачи №2.')
    def flow_table(values,widths,font=9.5):
        styles=ParagraphStyle('cell',fontName='Body',fontSize=font,leading=font+3)
        data=[[Paragraph(escape(str(v)).replace('\n','<br/>'),styles) for v in row] for row in values]
        t=Table(data,colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EFF1')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#BFCBD0')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        return t
    story.append(flow_table(comparison,[128,77,91,77,126]))
    p(f'Результат — билетная выручка минус расходы программы, не чистая прибыль; субсидии не включены. База H2 закрывает <b>{coverage}%</b> разрыва с №2 на статичной базе 2025; это не прогноз места в 2028. H1 даёт больше сегментов, H2 лучше по денежному результату обоих сценариев.',small)
    p('<b>Цифровые инициативы:</b> продвигать пилот в существующих цифровых каналах; проверять предложения допуслуг и повторной покупки через имеющиеся сервисы Red Wings. Используем существующие управление бронированием и допуслуги.',small)
    p('<b>Оценка:</b> цифровой и коммерческий эффект отдельно не оценивался и не включён в расчёт. Для пилота предлагаем измерять конверсию поиска в оплату, долю прямых бронирований и маржу допуслуг на бронирование. База и цели пока не определены. Смена канала не создаёт пассажира; билетная выручка учитывается один раз.',small)
    p('<b>Приложения и повторение:</b> submission/README.md — рейтинг, H1/H2, карта, маршруты, источники и ИИ. Проверка: uv run --frozen --no-sync python scripts/check_strategy.py; сборка: тот же запуск scripts/build_defense.py.',small)
    h('8. Ограничения решения')
    p('Сегменты не равны уникальным людям; спрос по аналогам, тарифы и расходы требуют проверки. Падение только тарифа H2 примерно на 2% меняет базовый выбор в пользу H1. Совместное снижение спроса и тарифа при росте затрат может сделать обе программы убыточными. Сроки SJ-100, слоты, ТО, дальность и экипажи не подтверждены. Ресурс масштабирования и горизонт №2 неизвестны; гарантий достижения цели нет.',small)
    h('9. Дорожная карта: доработка, проверка, применение')
    p('<b>До конца 2026:</b> финансы/лизинг — лимит обязательств и условия поставок.<br/><b>I полугодие 2027:</b> коммерция/эксплуатация — договоры, слоты, дальность с загрузкой, ТО и экипажи.<br/><b>После передачи ВС, планово с октября 2027:</b> пилот Омск, Саратов, Минеральные Воды; 8–12 недель; один рабочий борт + резерв. При задержке — перенос. Коммерция и цифровые каналы — продвижение пилота и замер коммерческих показателей.<br/><b>2028:</b> до десяти пар при приросте продаж и покрытии затрат сети; два рабочих борта + резерв. Восемь недель отрицательного переменного вклада пары — пересмотр, ещё четыре без улучшения — снять частоты.<br/><b>Далее:</b> расширение по спросу, экономике и доступному флоту. Год достижения №2 не подтверждён.',small)
    h('10. Вопросы экспертам')
    p('Как согласовать метрику и горизонт №2? Какие данные о спросе, тарифах и стоимости флота доступны? Какие базовые показатели и бюджет цифрового теста допустимы?',small)
    def footer(can,doc):
        can.setFont('Body',8);can.setFillColor(colors.HexColor('#536A78'));can.drawString(48,25,'WeSeekDp · Red Wings · сдача 10 ноября 2026');can.drawRightString(A4[0]-48,25,str(doc.page))
    doc=SimpleDocTemplate(str(OUT/'project-passport.pdf'),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=34,bottomMargin=42,title='Red Wings: концепция роста до №2',author='WeSeekDp')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    if doc.page != 2:raise ValueError(f'Паспорт должен занимать 2 страницы A4, получено {doc.page}')
    if args.passport_only:
        print('P0: паспорт PDF и маршруты CSV/Markdown.')
        return

    width,height=960,540
    deck=canvas.Canvas(str(OUT/'presentation.pdf'),pagesize=(width,height));deck.setTitle('Red Wings — концепция роста до №2');deck.setAuthor('WeSeekDp')
    ink=colors.HexColor('#203340');accent=colors.HexColor('#007F89');muted=colors.HexColor('#536A78')
    number=0
    def paragraph(text,x,y,w,size=20,color=ink,bold=False):
        style=ParagraphStyle('slide',fontName='Bold' if bold else 'Body',fontSize=size,leading=size*1.25,textColor=color)
        obj=Paragraph(text.replace('\n','<br/>'),style);_,h=obj.wrap(w,height)
        if y+h>496 and y<500:raise ValueError(f'Текст выходит за поле слайда {number}: {text}')
        obj.drawOn(deck,x,height-y-h);return h
    def new_slide(title,source,sid=None):
        nonlocal number
        number+=1;deck.setFillColor(colors.HexColor('#F7F9FA'));deck.rect(0,0,width,height,fill=1,stroke=0)
        paragraph(title,54,34,852,28,bold=True)
        paragraph(source,54,505,815,9,color=muted)
        deck.setFont('Body',9);deck.setFillColor(muted);deck.drawRightString(905,24,str(number))
        if sid:
            s=sources[sid];deck.linkURL(s['landing_url'],(54,15,850,35),relative=0,thickness=0)
    def deck_table(values,y,widths,rowheight=39,size=15):
        style=ParagraphStyle('slidecell',fontName='Body',fontSize=size,leading=size+4,textColor=ink)
        header=ParagraphStyle('slidehead',parent=style,fontName='Bold',textColor=colors.white)
        cells=[[Paragraph(escape(str(v)),header if i==0 else style) for v in row] for i,row in enumerate(values)]
        t=Table(cells,colWidths=widths,rowHeights=[rowheight]*len(values))
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),accent),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#ECF2F4')]),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#CCD8DD')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9)]))
        t.wrapOn(deck,852,400);t.drawOn(deck,54,height-y-rowheight*len(values))

    new_slide('Стратегия роста Red Wings:<br/>прямые рейсы как первый этап','Кейс № 5 · уточнение 10.11.2026 · WeSeekDp · 13 ноября 2026')
    paragraph('Десять пар · +2 оборота в неделю на пару',54,163,852,25,color=accent)
    paragraph('2 рабочих SJ-100 + 1 резервный',54,239,852,30,bold=True)
    paragraph('Пилот трёх пар после поставки самолётов.<br/>H2 — первый шаг к цели №2, не гарантия её достижения.',54,340,852,22)
    paragraph('Рабочая метрика — пассажиры отдельной авиакомпании за год.<br/>Срок достижения №2 не подтверждён.',54,433,852,17,color=muted)
    deck.showPage()

    new_slide('Города и конкуренты','Рейтинг городов · S10/S11 · S57/S58',sid='S11')
    deck_table([['Общий топ-3','Баллы','Что учитываем'],['Казань','80,2','Уже опорный аэропорт Red Wings'],['Уфа','79,1','Выбрана для новой базы H1'],['Красноярск','71,1','Нет годовой динамики; хаб конкурента']],106,[225,100,527],38,16)
    paragraph('10 городов · 75% масштабу, 25% динамике.<br/>Топ меняется при других весах и неизвестном росте.',54,279,852,19,color=accent,bold=True)
    paragraph('S7, Новосибирск/Иркутск: стыковки и техническая поддержка.<br/>«Аэрофлот», Красноярск: базовые самолёты, ТО и экипажи.',54,370,852,19)
    deck.showPage()

    new_slide('Спрос и частота','S23 · Омский аэропорт, итоги 2025; параметры модели',sid='S23')
    paragraph('Факт: Омск—Казань — 27 510;<br/>Омск—Новосибирск — 106 309 пассажиров за 2025 год.',54,115,852,23,bold=True)
    paragraph('Для обеих H: геометрическое среднее ×40%<br/>≈21,6 тыс. местных сегментов на пару до ограничений.',54,223,852,23,color=accent)
    paragraph('Продажи ограничиваем спросом и креслами;<br/>вычитаем перенос своих пассажиров.',54,331,852,23,bold=True)
    paragraph('2 оборота/нед. =20 800 кресел/год. Потолок загрузки — 85%/72%.<br/>Тарифы, захват и затраты — сценарные параметры.',54,421,852,16,color=muted)
    deck.showPage()

    new_slide('Сравнение гипотез','2028 · 52 недели · доля на рынке 2025: 108,85 млн пассажиров',sid='S03')
    deck_table(comparison,114,[213,132,174,137,196],44,15)
    paragraph('H1 даёт больше сегментов; H2 — выше результат.<br/>Тариф только H2 ниже примерно на 2% → H1 лучше в базе.',54,366,852,21,color=accent,bold=True)
    paragraph('*Выручка минус расходы программы; субсидии =0.<br/>Сегменты — не уникальные люди.',54,447,852,15,color=muted)
    deck.showPage()

    new_slide('Десять прямых пар H2','Сеть 2028 · +2 оборота/неделю на пару · submission/routes.csv')
    deck.drawImage(str(ROOT/'analysis/figures/selected_route_map.png'),52,53,width=856,height=405,preserveAspectRatio=True,anchor='c')
    deck.showPage()

    new_slide('Флот и запуск','Недельные ротации · расчёт дополнительной программы')
    deck_table([['Полная сеть 2028','H1: Уфа','H2: Екатеринбург'],['Рабочие + резерв','2 + 1','2 + 1'],['Обороты/неделю','24','20'],['Блок-часы/неделю','116,4','100,8']],112,[360,225,267],42,18)
    paragraph('Пилот: Омск, Саратов, Минеральные Воды.<br/>Один рабочий борт и один резервный.',54,310,852,23,color=accent,bold=True)
    paragraph('Ночной возврат; до 10,5 блок-ч/день и 14 часов занятости.<br/>До продаж: дальность с загрузкой, слоты, ТО и экипажи.',54,411,852,18)
    deck.showPage()

    new_slide('Сеть, цифровые каналы и коммерция','Предложения для пилота · цифровой и коммерческий эффект отдельно не оценён')
    paragraph('Сеть: H2 добавляет частоты и перевозки.<br/>Цифровые каналы: продвижение пилота<br/>и использование существующих сервисов.<br/>Коммерция: допуслуги и повторные продажи.',54,112,852,23,color=accent)
    paragraph('Измеряем: конверсию поиска в оплату;<br/>долю прямых бронирований; маржу допуслуг на бронирование.<br/>База и целевые значения пока не определены.',54,287,852,20)
    paragraph('Эффект этих инициатив не включён в маршрутный расчёт.<br/>Смена канала не создаёт пассажира; билет учитывается один раз.',54,412,852,18,color=muted)
    deck.showPage()

    new_slide('План до 2028 года','Дорожная карта · ответственные функции · цифровые инициативы — предложения команды')
    deck_table([['Когда','Кто','Результат'],['До конца 2026','Финансы, лизинг','Лимит обязательств и условия поставок'],['I полугодие 2027','Коммерция, эксплуатация','Договоры, слоты, экипажи и ТО'],['После передачи ВС','Коммерция, OCC','Пилот 8–12 недель; 1 рабочий +1 резерв'],['2028','Коммерция, финансы','До 10 пар; 2 +1 борт; покрытие затрат']],105,[180,210,462],43,15)
    paragraph('Коммерция и цифровые каналы: продвижение пилота,<br/>замер конверсии, прямых бронирований и маржи допуслуг.',54,334,852,18)
    paragraph('H2 — проверяемый первый шаг; расширение — по результатам.<br/>Задержка SJ-100 — перенос; год достижения №2 не обещаем.',54,406,852,20,color=accent,bold=True)
    paragraph('ИИ: ChatGPT / Deep Research, Codex. Проверка: источники, CSV, ротации и PDF.',54,474,852,12,color=muted)
    deck.showPage()
    if number != 8:raise ValueError(f'Ожидалось 8 слайдов, получено {number}')
    deck.save()
    print('PDF: паспорт (2 страницы) и презентация (8 слайдов). Маршруты: CSV и Markdown.')

if __name__=='__main__':main()
