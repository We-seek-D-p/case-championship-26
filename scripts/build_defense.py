"""Материалы защиты из готовых результатов модели.
uv run --frozen --no-sync python scripts/build_defense.py
PDF: ReportLab из доступного Python-окружения или поставляемого runtime.
"""
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
    if importlib.util.find_spec('reportlab') is None:
        runtime=Path(os.environ.get('RUNTIME_PYTHON',str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python')))
        if not runtime.is_file():raise SystemExit('Для сборки PDF нужен ReportLab; укажите RUNTIME_PYTHON с установленным пакетом.')
        subprocess.run([str(runtime),str(Path(__file__).resolve())],check=True)
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

    body=ParagraphStyle('body',fontName='Body',fontSize=10.5,leading=14,spaceAfter=6)
    heading=ParagraphStyle('heading',parent=body,fontName='Bold',fontSize=12,leading=15,spaceBefore=7,spaceAfter=4)
    title=ParagraphStyle('title',parent=heading,fontSize=19,leading=23,spaceAfter=10)
    small=ParagraphStyle('small',parent=body,fontSize=9,leading=12)
    story=[]
    def p(text,style=body):story.append(Paragraph(text,style))
    def h(text):p(text,heading)
    p('Паспорт проекта Red Wings',title)
    p('<b>Название:</b> Прямые региональные рейсы из Екатеринбурга<br/><b>Кейс:</b> № 5 «Новый хаб или прямые рейсы?»<br/><b>Команда:</b> WeSeekDp<br/><b>Контакт:</b> Автюхов Егор Юрьевич, @Morgart31')
    h('1. Команда и роли')
    p('Макаренко Константин — модель и код; Федосеев Николай — экономика и риски; Автюхов Егор — данные и источники; Алексеев Фёдор — документы и карта. Выбор стратегии и защита — совместно.')
    h('2. Какую проблему решаем')
    p('Red Wings нужно расти быстрее стагнирующего рынка при ограниченном новом флоте. Сравниваем новую базу с пересадками и дополнительные прямые рейсы из существующей базы.')
    h('3. Решение и кому оно полезно')
    p('Предлагаем H2: десять прямых пар из Екатеринбурга, по два дополнительных оборота в неделю на пару. Для полной программы нужны два рабочих SJ-100 и один резервный. Решение задаёт сеть, ресурс и условия поэтапного запуска.')
    h('4. Где и как сравнили варианты')
    p('H1 — Уфа, восемь плеч с четырьмя пересадочными связками. H2 — десять прямых пар. Рассчитаны 2027/2028 годы и базовый/осторожный сценарии; обе полные сети используют три борта с резервом. Отдельно сопоставлены близкие блок-часы и разные уровни спроса.')
    h('5. Данные')
    p(f'{source_link("S08")} — 2,7 млн пассажиров Red Wings в 2025; {source_link("S03")} — 108,85 млн пассажиров авиакомпаний РФ. {source_link("S23")} — Омск—Казань: 27 510; Омск—Новосибирск: 106 309 пассажиров за 2025. Источники: data/SOURCE_MANIFEST.md.')
    p('Сценарные параметры команды: геометрическое среднее двух линий ×40% как ориентир местного спроса; тарифы, загрузка, замещение, блок-время, расходы и сроки запуска. Одинаковое правило спроса применяется к обеим гипотезам.')
    h('6. Метод и связь с учёбой')
    p('Продажи ограничены спросом и креслами; из них вычитаем перенос своих пассажиров. Для H1 одна пересадочная поездка занимает два сегмента и приносит один сквозной билет. Выручка — дополнительные продажи ×тариф; прирост доли — дополнительные сегменты /108,85 млн ×100 п.п.')
    p('Использованы статистика — пропуски и сценарии; математический анализ — пороги тарифа и затрат; алгоритмы — ротации и граф стыковок; Python — расчёты и графики. ChatGPT помог с исследованиями, кодом и подготовкой материалов. Материалы ИИ сохранены в research/reports/.')
    story.append(PageBreak())
    h('7. Результат')
    comparison=[['2028','Сегменты,\nтыс.','Выручка,\nмлрд ₽','Δ доли,\nп.п.','Результат*,\nмлн ₽']]
    for case in ('base','cautious'):
        for hyp in ('H1','H2'):
            r=get(hyp,case);comparison.append([hyp+' '+('база' if case=='base' else 'осторожный'),fmt(r,'net_passenger_segments',1000,1),fmt(r,'incremental_revenue_rub',1e9,2),fmt(r,'share_delta_pp',1,3),fmt(r,'contribution_rub',1e6)])
    def flow_table(values,widths,font=9.5):
        styles=ParagraphStyle('cell',fontName='Body',fontSize=font,leading=font+3)
        data=[[Paragraph(escape(str(v)).replace('\n','<br/>'),styles) for v in row] for row in values]
        t=Table(data,colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EFF1')),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#BFCBD0')),('FONTNAME',(0,0),(-1,0),'Bold'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
        return t
    story.append(flow_table(comparison,[128,77,91,77,126]));story.append(Spacer(1,8))
    p('*Дополнительная выручка минус расходы программы; не чистая прибыль. Субсидии равны нулю. Доля рассчитана на фиксированном рынке 2025 года.',small)
    p('Выбираем H2 по денежному результату осторожного сценария и возможности начать с небольшого пилота. H1 даёт больше пассажирских сегментов. При одинаковом местном ориентире около 22,2 тыс. сегментов на пару H1 уже обходит H2 по базовому денежному результату.')
    p('Приложения: submission/README.md — комплект; analysis/08-strategy-decision.md — расчёт; submission/routes.csv — маршруты, частоты, выручка, источник и ресурс; research/reports/ — исследования ИИ.')
    h('8. Ограничения')
    p('Сценарный спрос не равен измеренному O&D; сегменты не означают уникальных людей. Тарифы и расходы требуют коммерческого подтверждения. Падение только тарифа H2 примерно на 2% меняет базовый денежный выбор в пользу H1. При совместном снижении тарифа и спроса и росте затрат обе программы могут быть убыточны.')
    h('9. Дорожная карта')
    p('До конца 2026 — финансы и лизинг: лимит обязательств и условия поставок. I полугодие 2027 — коммерция и эксплуатация: договоры, слоты, дальность с загрузкой, ТО и экипажи.')
    p('После передачи самолётов, планово с октября 2027 — пилот Омск, Саратов, Минеральные Воды на 8–12 недель: один рабочий борт и один резервный. При задержке SJ-100 переносим запуск.')
    p('2028 — расширение до десяти пар при подтверждённом приросте продаж и покрытии расходов сети. Восемь недель отрицательного переменного вклада пары — пересмотр; ещё четыре без улучшения — снять добавленные частоты. Ответственные: коммерция, финансы и эксплуатация.')
    h('10. Вопросы экспертам')
    p('Какие тариф и полная стоимость блок-часа следует принять для пилота? Как оценить перенос собственных продаж и достаточный резерв самолётов?')
    def footer(can,doc):
        can.setFont('Body',8);can.setFillColor(colors.HexColor('#536A78'));can.drawString(48,25,'WeSeekDp · Red Wings · 13 ноября 2026');can.drawRightString(A4[0]-48,25,str(doc.page))
    doc=SimpleDocTemplate(str(OUT/'project-passport.pdf'),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=38,bottomMargin=42,title='Паспорт проекта Red Wings',author='WeSeekDp')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)

    width,height=960,540
    deck=canvas.Canvas(str(OUT/'presentation.pdf'),pagesize=(width,height));deck.setTitle('Red Wings — прямые рейсы из Екатеринбурга');deck.setAuthor('WeSeekDp')
    ink=colors.HexColor('#203340');accent=colors.HexColor('#007F89');muted=colors.HexColor('#536A78')
    number=0
    def paragraph(text,x,y,w,size=20,color=ink,bold=False):
        style=ParagraphStyle('slide',fontName='Bold' if bold else 'Body',fontSize=size,leading=size*1.25,textColor=color)
        obj=Paragraph(text.replace('\n','<br/>'),style);_,h=obj.wrap(w,height);obj.drawOn(deck,x,height-y-h);return h
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

    new_slide('Red Wings: прямые рейсы<br/>из Екатеринбурга','Кейс № 5 · WeSeekDp · 13 ноября 2026')
    paragraph('Десять пар · +2 оборота в неделю на пару',54,163,852,25,color=accent)
    paragraph('2 рабочих SJ-100 + 1 резервный',54,239,852,30,bold=True)
    paragraph('Пилот трёх пар после поставки самолётов.<br/>Расширение — по приросту продаж и расходам сети.',54,340,852,22)
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
    paragraph('H1 даёт больше сегментов.<br/>H2 лучше по денежному результату обоих сценариев.',54,366,852,23,color=accent,bold=True)
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

    new_slide('Условия смены решения','Чувствительность тарифа, спроса и расходов')
    paragraph('Тариф только H2 ниже примерно на 2% →<br/>H1 лучше по базовому денежному результату.',54,116,852,27,color=accent,bold=True)
    paragraph('Единый местный ориентир ≥22,2 тыс. сегментов на пару<br/>до ограничения креслами также выводит H1 вперёд в базе.',54,240,852,21)
    paragraph('Тариф −20%, спрос −25%, блок-час 160 тыс. ₽:<br/>обе программы могут стать убыточными.',54,340,852,21)
    paragraph('На пилоте считаем все продажи Red Wings на паре.<br/>8 недель отрицательного вклада — пересмотр; ещё 4 — снять частоты.',54,441,852,16,color=muted)
    deck.showPage()

    new_slide('План до 2028 года','Дорожная карта · ответственные функции')
    deck_table([['Когда','Кто','Результат'],['До конца 2026','Финансы, лизинг','Лимит обязательств и условия поставок'],['I полугодие 2027','Коммерция, эксплуатация','Договоры, слоты, экипажи и ТО'],['После передачи ВС','Коммерция, OCC','Пилот 8–12 недель; 1 рабочий +1 резерв'],['2028','Коммерция, финансы','До 10 пар; 2 +1 борт; покрытие затрат']],105,[180,210,462],43,15)
    paragraph('Задержка SJ-100 → перенос или сохранение пилота.',54,348,852,23,color=accent,bold=True)
    paragraph('ChatGPT: исследования, код и подготовка материалов.<br/>Дисциплины: статистика, матанализ, алгоритмы и Python.',54,424,852,17)
    deck.showPage();deck.save()
    print('PDF: паспорт и презентация. Маршруты: CSV и Markdown.')

if __name__=='__main__':main()
