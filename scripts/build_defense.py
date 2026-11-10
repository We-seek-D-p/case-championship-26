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
    p('Концепция для руководства и коммерческой службы: <b>сеть</b> — пилот из существующей базы с последующим расширением; <b>цифровой сервис</b> — улучшение самообслуживания; <b>коммерция</b> — прямые продажи и допуслуги с отдельным учётом маржи. Каждую очередь запускаем по подтверждённому спросу, экономике и доступному флоту.')
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
    values=[['H2 · 2028','Базовый','Осторожный'],
        ['Дополнительные сегменты, тыс.',fmt(b,'net_passenger_segments',1000,1),fmt(c,'net_passenger_segments',1000,1)],
        ['Билетная выручка, млрд ₽',fmt(b,'incremental_revenue_rub',1e9,2),fmt(c,'incremental_revenue_rub',1e9,2)],
        ['После расходов программы, млн ₽',fmt(b,'contribution_rub',1e6),fmt(c,'contribution_rub',1e6)]]
    story.append(flow_table(values,[285,106,108]))
    p(f'Результат — билетная выручка минус расходы программы, не чистая прибыль. База H2 закрывает <b>{coverage}%</b> разрыва с №2 на статичной базе 2025; это не прогноз места в 2028. Δ доли: +{fmt(b,"share_delta_pp",1,3)} / +{fmt(c,"share_delta_pp",1,3)} п.п. к рынку 2025.',small)
    p('<b>Цифровые инициативы:</b> на сайте уже есть управление бронированием и допуслуги. Предлагаем проверить заявку на вынужденный возврат с предзаполнением и статусом вместо повторного ввода в письме; затем проверить понятность покупки допуслуг и оплаты. Это гипотезы улучшения, эффект и бюджет не измерены. '+link('https://flyredwings.com/change-and-refund/','Публичный процесс возврата')+' и '+link('https://flyredwings.com/','сайт')+' просмотрены 10.11.2026; реальная покупка и возврат не выполнялись.',small)
    p('<b>Оценка:</b> общий эффект = вклад сети + экономия канала + маржа допуслуг + экономия обслуживания − внедрение и поддержка. Билетную выручку учитываем один раз; смена канала не создаёт пассажира. В пилоте измеряем прирост всех продаж на паре, вклад после расходов, конверсию поиска в оплату, долю прямых продаж, маржу допуслуг и самостоятельное решение обращений. До теста фиксируем определения, базу и контрольную группу; финансовый эффект цифровых инициатив пока не рассчитан.',small)
    p('<b>Приложения и повторение:</b> submission/README.md — ссылки на рейтинг, H1/H2, карту, маршруты, источники и ИИ. Расчёт: uv run --frozen --no-sync python scripts/compare_growth_strategies.py; проверка: scripts/check_strategy.py с тем же запуском.',small)
    h('8. Ограничения решения')
    p('Сегменты не равны уникальным людям; спрос по аналогам, тарифы и расходы требуют проверки. H1 даёт больше сегментов; небольшое снижение тарифа H2 меняет базовый выбор. Сроки SJ-100, слоты, ТО, дальность и экипажи не подтверждены. Ресурс масштабирования и горизонт №2 неизвестны; гарантий достижения цели нет.',small)
    h('9. Дорожная карта: доработка, проверка, применение')
    p('<b>До конца 2026:</b> финансы/лизинг — лимит и условия поставок; IT/сервис/коммерция — аудит пути, базовые KPI, бюджет и план теста. Без согласованной экономики — no-go.<br/><b>2027 после передачи ВС:</b> эксплуатация/коммерция — Омск, Саратов, Минеральные Воды; 8–12 недель; один рабочий борт + резерв. Задержка поставки — перенос.<br/><b>2028:</b> до десяти пар при приросте продаж и покрытии затрат сети. Восемь недель отрицательного переменного вклада — пересмотр, ещё четыре без улучшения — снять частоты. IT/финансы — контролируемый тест сервиса и маржи после затрат.<br/><b>Далее:</b> руководство утверждает следующие очереди только по спросу, финансированию и флоту; ежегодно обновляет разрыв с конкурентами. Новый хаб — отдельное go/no-go.',small)
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

    new_slide('Концепция роста Red Wings до №2','Рабочая метрика команды · уточнение кейса 10.11.2026 · WeSeekDp')
    paragraph('№2 по перевезённым пассажирам<br/>отдельной российской авиакомпании за год',54,115,852,27,bold=True)
    paragraph('Сеть: пилот → расширение по спросу и флоту<br/>Сервис: проверить улучшения самообслуживания<br/>Коммерция: прямые продажи и маржа допуслуг',54,230,852,23,color=accent)
    paragraph('Долгосрочная цель; срок достижения не подтверждён.<br/>Решение о каждой очереди — после проверки экономики.',54,400,852,20)
    deck.showPage()

    new_slide('Разрыв с №2 — '+num(gap/1e6)+' млн пассажиров','2025 · strategy-baseline.csv · S08; Интерфакс, 15.01.2026; S7')
    deck_table([['Отдельная авиакомпания','Пассажиры за 2025, млн'],
        ['Победа · №2',num(second/1e6)],['S7 · для сравнения',num(float(baseline['S7']['passengers'])/1e6)],
        ['Red Wings',num(rw/1e6)]],115,[510,342],46,21)
    paragraph(f'H2 закрывает около {coverage}% исходного разрыва',54,337,852,27,color=accent,bold=True)
    paragraph('Базовый сценарий 2028 на статичной базе 2025.<br/>Это не прогноз места Red Wings в 2028.',54,413,852,21)
    deck.showPage()

    new_slide('H2 — первая очередь из существующей базы','H1/H2 · route_assumptions.csv · city_ranking.csv · selected_route_map.png')
    paragraph('H1: новая база Уфа;<br/>8 плеч, 4 связки.<br/><br/>H2: Екатеринбург;<br/>10 прямых пар,<br/>+2 оборота/неделю.',54,117,350,22)
    deck.drawImage(str(ROOT/'analysis/figures/selected_route_map.png'),420,165,width=485,height=280,preserveAspectRatio=True,anchor='c')
    paragraph('Выбор H2: осторожная экономика и малый пилот.<br/>Первые пары: Омск, Саратов, Минеральные Воды.',54,413,852,21,color=accent,bold=True)
    deck.showPage()

    new_slide('Экономика пилота зависит от спроса','2028 · hypothesis_comparison.csv · S03/S23 · расчётные сценарии',sid='S23')
    deck_table(comparison,112,[213,132,174,137,196],44,15)
    paragraph('H1 даёт больше сегментов; H2 — выше результат.<br/>Спрос по аналогам, не измеренный O&amp;D выбранных пар.',54,355,852,22,color=accent,bold=True)
    paragraph('*Билетная выручка минус расходы программы, не чистая прибыль.<br/>Δ доли к 108,85 млн пассажиров рынка 2025; сегменты ≠ уникальные люди.',54,436,852,16,color=muted)
    deck.showPage()

    new_slide('Самообслуживание: возврат и допуслуги','Публичные страницы Red Wings · просмотр 10.11.2026 · без покупки и возврата')
    paragraph('Уже опубликованы: управление бронированием,<br/>выбор места, багаж и другие допуслуги.',54,112,852,23,bold=True)
    paragraph('Предлагаем испытать: заявку на вынужденный возврат<br/>с предзаполнением и статусом; понятность оплаты и услуг.',54,213,852,23,color=accent)
    paragraph('Проверка: время решения, самостоятельные обращения,<br/>ошибки оплаты и конверсия поиска в оплату.<br/>Базовые значения, затраты и эффект пока не измерены.',54,326,852,21)
    paragraph('<link href="https://flyredwings.com/change-and-refund/" color="#007F89">Процесс возврата</link> · <link href="https://flyredwings.com/" color="#007F89">Сайт</link> · Наличие разделов не доказывает удобство полного пути.',54,456,852,14)
    deck.showPage()

    new_slide('Коммерция: эффект без двойного счёта','Предлагаемый принцип оценки · цифровая экономика пока не рассчитана')
    paragraph('Вклад сети + экономия канала + маржа допуслуг<br/>+ экономия обслуживания − внедрение и поддержка',54,116,852,26,color=accent,bold=True)
    paragraph('Смена агентского канала на прямой не создаёт пассажира.<br/>Выручка билета учитывается один раз.<br/>Допуслуга увеличивает маржу, а не число перевозок.',54,235,852,22)
    paragraph('Коммерция + IT + финансы: база → контрольный тест → решение.<br/>KPI: доля прямых продаж, маржа услуг на бронирование,<br/>общий вклад после затрат; учитывать скидки и возвраты.',54,378,852,20)
    deck.showPage()

    new_slide('Расширяем сеть после подтверждения результата','Предлагаемые этапы · ресурс из hypothesis_comparison.csv и ротаций')
    deck_table([['Срок','Владелец','Условие перехода'],
        ['До конца 2026','Финансы, IT, лизинг','Лимит, поставки, база KPI и бюджет теста'],
        ['2027 после передачи ВС','Коммерция, эксплуатация','Пилот 3 пар, 8–12 недель; 1 борт + резерв'],
        ['2028 · до 10 пар','Коммерция, финансы',f'Прирост продаж, покрытие затрат; {active} + {reserve} борта'],
        ['Следующие очереди','Руководство','Новый спрос, флот, финансирование; go/no-go']],108,[205,215,432],55,15)
    paragraph('Задержка SJ-100 → перенос запуска.<br/>Новый хаб и ресурс дальнейшего роста оцениваются отдельно.',54,412,852,21,color=accent,bold=True)
    deck.showPage()

    new_slide('Решение: начать с проверки пилота','Риски · стресс-сценарии CSV · расширение только после go/no-go')
    paragraph('Основные риски: спрос по аналогам, тариф и расходы;<br/>поставка и надёжность флота; перенос собственных продаж.',54,116,852,24,bold=True)
    paragraph('8 недель отрицательного переменного вклада — пересмотр;<br/>ещё 4 без улучшения — снять добавленные частоты.<br/>Цифровой тест масштабировать по эффекту после затрат.',54,225,852,22)
    paragraph('H2 проверяет первую очередь.<br/>Для №2 нужна отдельная программа масштабирования<br/>с ежегодным обновлением разрыва и ресурсного плана.',54,344,852,22,color=accent,bold=True)
    paragraph('ИИ: ChatGPT / Deep Research, Codex. Проверка: источники, CSV, кресла и ротации, PDF.',54,466,852,13,color=muted)
    deck.showPage()
    if number != 8:raise ValueError(f'Ожидалось 8 слайдов, получено {number}')
    deck.save()
    print('PDF: паспорт (2 страницы) и презентация (8 слайдов). Маршруты: CSV и Markdown.')

if __name__=='__main__':main()
