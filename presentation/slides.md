---
theme: seriph
layout: deck
title: 'Кейс 5: Red Wings — WeSeekDp'
aspectRatio: '16/9'
canvasWidth: 1204
fonts:
  sans: Arial
  weights: '400,600,700'
  webfonts: false
info: |
  Презентация Red Wings. Оформление по референсу: светлый фон, красные акценты и открытая табличная сетка.
---

<div class="rw-slide redwings-cover">
  <div class="redwings-cover__heading">
    <div class="redwings-cover__team">Команда <strong>WeSeekDp</strong></div>
    <h1><span>Кейс 5:</span> Red Wings</h1>
  </div>
  <img class="redwings-cover__photo" src="/images/red-wings-cover.jpg" alt="Красный самолёт Red Wings на полосе на закате" />
</div>


<!-- Фото: https://flyredwings.com/upload/information_system_24/5/6/6/item_5661/item_5661.jpg -->

---
layout: deck
---

<div class="rw-slide fleet-slide company-overview">
  <h1>Red Wings: положение на рынке и ресурсы</h1>
  <div class="company-overview__metrics">
    <section><h2>Пассажиры · 2025</h2><strong>2,7 млн</strong><p>2,48% российского авиарынка.<br>До масштаба «Победы» — ×5,11.</p></section>
    <section><h2>Развитие сети · 2025</h2><strong>25 направлений</strong><p>Новых: 17 внутренних<br>и 8 международных.</p></section>
    <section><h2>Sky Gates · март 2025</h2><strong>3 грузовых ВС</strong><p>2 Ил-96-400Т + 1 Ил-76ТД.<br>Отдельно от пассажирского парка.</p></section>
    <section><h2>Авиация / ж/д · 2025</h2><strong>≈2×</strong><p>По пассажирообороту:<br>284,4 / 142,4 млрд пасс.-км.</p></section>
  </div>
  <div class="fleet-slide__tables">
    <section>
      <h2>Пассажирский парк Red Wings · 2026</h2>
      <table>
        <thead><tr><th>Тип самолёта</th><th>Бортов</th></tr></thead>
        <tbody>
          <tr class="fleet-slide__focus"><td>SSJ100 · SaM146</td><td>20</td></tr>
          <tr><td>SJ-100 · ПД-8</td><td>0</td></tr>
          <tr><td>Ту-204</td><td>2</td></tr>
          <tr><td>Ту-214</td><td>3</td></tr>
          <tr><td>Boeing 777</td><td>3</td></tr>
          <tr class="fleet-slide__total"><td>Всего пассажирских</td><td>28</td></tr>
        </tbody>
      </table>
    </section>
    <section>
      <h2>Поставки · сценарий 2027–2030</h2>
      <table>
        <thead><tr><th>Период</th><th>SJ-100</th><th>Ту-214</th></tr></thead>
        <tbody>
          <tr><td>I–III кв. 2027</td><td>0</td><td>0</td></tr>
          <tr class="fleet-slide__focus"><td>IV кв. 2027</td><td>+1</td><td>+1</td></tr>
          <tr><td>2028</td><td>+4</td><td>+2</td></tr>
          <tr><td>2029</td><td>+6</td><td>+3</td></tr>
          <tr><td>2030</td><td>+4</td><td>+5</td></tr>
          <tr class="fleet-slide__total"><td>Всего новых</td><td>15</td><td>11</td></tr>
        </tbody>
      </table>
      <p class="fleet-slide__outlook">Парк с учётом выбытия: <strong>30</strong> бортов к концу 2027 → <strong>43</strong> к концу 2030</p>
    </section>
  </div>
</div>


<!--
Источники: data/redwings_research/RED_WINGS_FLEET.md (парк и сценарий поставок),
analysis/HUB_STRATEGY.md (99 кресел, 2 рабочих SSJ100 и 1 резервный).
Исходный парк: https://flyredwings.com/about/park/
Индивидуальные сроки и количество SJ-100 для Red Wings не подтверждены.
Срез 13.11.2026. Поставки — сценарий, не подтверждённый график.
Наличие в парке не означает доступность для новых рейсов.
-->

<!--
Источники: data/redwings_research/market_position_2025/:
01_PASSENGERS_AND_RANKINGS.md: 2,7 млн / 108,85 млн × 100 = 2,48%;
13,8 млн («Победа») / 2,7 млн = 5,11. Сравнение масштабов за 2025 год.
02_REGIONAL_NETWORK_AND_AIRPORTS.md: 25 новых направлений, 17 ВВЛ и 8 МВЛ;
премия в номинации «Лидер развития маршрутной сети» по итогам 2025 года.
03_CARGO_AND_FLEET.md: Sky Gates — отдельный грузовой оператор;
2 Ил-96-400Т и 1 Ил-76ТД на 28.03.2025, не пассажирский парк Red Wings.
04_AVIATION_AND_RAIL.md: 284,4 / 142,4 = 2,00 по пассажирообороту;
это контекст видов транспорта, не показатель Red Wings и не число пассажиров.
Первоисточники:
https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/
https://old.favt.gov.ru/novosti-novosti?id=17763&version=print
https://www.flypobeda.ru/news/pobeda-perevezla-13-8-mln-klientov-po-itogam-2025-goda
https://flyredwings.com/press/news/red-wings-poluchila-dve-nagrady-naczionalnoj-aviaczionnoj-premii-krylya-rossii/
https://flyredwings.com/press/news/dochernyaya-gruzovaya-aviakompaniya-sky-gates-popolnila-svoj-flot-samolyotom-il-96-400t/
https://www.consultant.ru/document/cons_doc_LAW_545186/a2f5da1b183b9a1fc0220801bde8f66dd784d12b/
https://apimarket.ru/2026/01/12/za-2025-god-rzhd-perevezli-13-mlrd-passazhirov/
-->

---
layout: deck
---

<div class="rw-slide hub-method">
  <h1>Как сравнивали хаб и прямые рейсы</h1>
  <div class="hub-method__columns">
    <aside>
      <h2>Хаб</h2>
      <p>Узел пересадок с согласованными волнами рейсов.</p>
      <p>Добавляет связи между городами и объединяет спрос.</p>
      <p class="hub-method__accent">В модели: пересадочная скидка и расходы новой базы.</p>
    </aside>
    <section>
      <h2>Общая модель для 24 аэропортов</h2>
      <p class="hub-method__inputs">4 направления · 4 оборота в неделю · 52 недели · 100 кресел · загрузка 82%</p>
      <div class="hub-method__formulas">
        <p><strong>P = 4 × 2 × 4 × 52 × 100 × 82% ≈ 136 тыс.</strong> сегментов/год</p>
        <p>Выручка R = P × (тариф + 900 RUB допуслуг)</p>
        <p>Переменные расходы V = вылеты × стоимость вылета + P × 650 RUB</p>
      </div>
      <table>
        <thead><tr><th>Параметр</th><th>Прямые рейсы · MRV</th><th>Новый хаб · NUX</th></tr></thead>
        <tbody>
          <tr><td>Тариф, RUB/сегмент</td><td>T = 7 000 + 3,5 × км</td><td>0,92 × T · скидка 8%</td></tr>
          <tr><td>Потери старой сети</td><td>P × 12% × 3 000 RUB</td><td>P × 6% × 3 000 RUB</td></tr>
          <tr><td>Постоянные расходы F</td><td>245 млн RUB/год</td><td>395 млн RUB/год</td></tr>
          <tr class="hub-method__result"><td>Результат R − V − потери − F</td><td>632,2 млн RUB/год</td><td>384,1 млн RUB/год</td></tr>
        </tbody>
      </table>
      <div class="hub-method__why">
        <h2>Почему выигрывают прямые рейсы</h2>
        <p>Без пересадочной скидки, расходы базы ниже на <strong>150 млн RUB/год</strong>.<br>Хаб теряет меньше пассажиров старой сети, но это не покрывает разницу.</p>
      </div>
    </section>
  </div>
</div>


<!--
Источники: analysis/HUB_CANDIDATES.md (метод отбора, 24 аэропорта),
analysis/HUB_STRATEGY.md (S0/S1/S2, пересадочные волны, расходы),
analysis/calculate.py (routes, calc, program),
data/airport_research/documentation/METHODOLOGY.md (статистика).
Недостающие месяцы восстановлены по профилям аналогов с сохранением годовых сумм.
Поток аэропорта не используется как независимый O&D-спрос маршрута.
82% — допущение модели. Рейтинг: CM после каннибализации / рабочие борта;
второй критерий — чистые пассажирские сегменты / рабочие борта.
Потенциальный эффект хаба условен на пересадочное расписание и продажи.
-->

---
layout: deck
---

<div class="rw-slide hub-choice">
  <h1>Кандидаты и выбор стратегии</h1>
  <p class="hub-choice__subtitle">6 финалистов из 24 аэропортов · расчёт на 2028 год</p>
  <div class="hub-choice__columns">
    <section>
      <h2>Итоги отбора площадок</h2>
      <table>
        <thead><tr><th>Площадка</th><th>Статус</th><th>Результат,<br>млн RUB/год</th><th>Загрузка<br>безубыт.</th></tr></thead>
        <tbody>
          <tr class="hub-choice__selected"><td>Минеральные Воды</td><td>База</td><td>632,2</td><td>48,7%</td></tr>
          <tr><td>Сочи</td><td>База</td><td>619,0</td><td>48,6%</td></tr>
          <tr><td>Санкт-Петербург</td><td>База</td><td>599,4</td><td>48,4%</td></tr>
          <tr class="hub-choice__new"><td>Новый Уренгой</td><td>Новый хаб</td><td>384,1</td><td>60,5%</td></tr>
          <tr><td>Уфа</td><td>Новый хаб</td><td>359,0</td><td>60,7%</td></tr>
          <tr><td>Саратов</td><td>Новый хаб</td><td>334,1</td><td>60,9%</td></tr>
        </tbody>
      </table>
      <div class="hub-choice__decision">
        <h2>Выбираем S1: Минеральные Воды</h2>
        <p><strong>+248,1 млн RUB/год</strong> к результату нового хаба.<br>2 рабочих борта + 1 резервный.</p>
      </div>
    </section>
    <section class="hub-choice__strategies">
      <h2>Две стратегии</h2>
      <div class="hub-choice__strategy-selected">
        <h3>S1 · Развивать действующую базу</h3>
        <p>Прямые рейсы из Минеральных Вод.<br>+632,2 млн RUB/год.</p>
      </div>
      <div>
        <h3>S2 · Открыть новый хаб</h3>
        <p>Прямые рейсы и пересадки в Новом Уренгое.<br>+384,1 млн RUB/год.</p>
      </div>
      <figure class="hub-choice__routes">
        <figcaption>Выбранные прямые маршруты</figcaption>
        <svg class="hub-choice__route-map" viewBox="0 0 420 230" role="img" aria-label="Прямые рейсы из Минеральных Вод в Нижний Новгород, Казань, Самару и Уфу. Схема по координатам аэропортов.">
          <image href="/maps/volga-caucasus.svg" width="420" height="230" />
          <g class="route-map__lines">
            <path d="M86 198 Q46 112 101 25" />
            <path d="M86 198 Q100 72 216 34" />
            <path d="M86 198 Q142 111 234 65" />
            <path d="M86 198 Q190 28 354 49" />
          </g>
          <g class="route-map__points">
            <circle cx="101" cy="25" r="3.5" />
            <circle cx="216" cy="34" r="3.5" />
            <circle cx="234" cy="65" r="3.5" />
            <circle cx="354" cy="49" r="3.5" />
            <circle cx="86" cy="198" r="5.5" />
          </g>
          <g class="route-map__labels">
            <text x="12" y="15">Нижний Новгород</text>
            <text x="207" y="24">Казань</text>
            <text x="245" y="87">Самара</text>
            <text x="364" y="45">Уфа</text>
            <text class="route-map__base" x="100" y="198">Минеральные Воды</text>
          </g>
        </svg>
      </figure>
    </section>
  </div>
</div>


<!--
Источники: analysis/HUB_CANDIDATES.md, раздел «Экономика финалистов»;
analysis/HUB_STRATEGY.md, разделы «Сравнение S0 / S1 / S2 за 2028 год»,
«Итоги всех предлагаемых маршрутов», «Почему выбранная стратегия лучше».
Все суммы — дополнительные модельные результаты относительно S0, после
переменных, постоянных расходов и потерь CM от каннибализации, до инвестиций и налогов.
Три базы и три новые площадки выбраны по CM/рабочий борт внутри своего класса.
Одинаковая загрузка 82%, четыре направления, 2 рабочих самолёта + 1 резервный.
MRV подтверждён как летняя база; круглогодичная работа — допущение модели.
Преимущество S1: 632.2 − 384.1 = 248.1 млн RUB/год.
Схема маршрутов: координаты аэропортов из data/airport_research/processed/airports.csv.
Упрощённая проекция, север сверху; маршруты — MRV–GOJ/KZN/KUF/UFA.
Берега и реки: Natural Earth 1:50m (public domain), public/maps/volga-caucasus.svg.
Рельеф Кавказа условный, не цифровая модель высот.
-->

---
layout: deck
---

<div class="rw-slide program-demo">
  <div class="program-demo__frame">
    <img class="program-demo__screenshot" src="/images/program-demo.png" alt="Интерактивная модель программы Red Wings: параметры и карта маршрутов из Минеральных Вод" />
    <a class="program-demo__qr" href="https://26b48574.nip.io" target="_blank" rel="noopener noreferrer" aria-label="Открыть маршрутный калькулятор">
      <img src="/images/program-qr.svg?v=2" alt="QR-код: https://26b48574.nip.io" />
      <strong>Открыть маршрутный калькулятор ↗</strong>
    </a>
  </div>
</div>

<!-- Скриншот предоставлен пользователем. QR: https://26b48574.nip.io -->

---
layout: deck
---

<div class="rw-slide cargo-growth">
  <h1>Грузовые перевозки — потенциал роста по России</h1>
  <p class="cargo-growth__subtitle">Дополнительная выручка на пассажирской сети Red Wings: почта, посылки и срочные B2B-грузы</p>
  <div class="cargo-growth__columns">
    <section class="cargo-growth__market">
      <h2>Масштаб рынка · 2025</h2>
      <p class="cargo-growth__value">446,3 <span>тыс. т</span></p>
      <p>грузов и почты перевезли<br>российские авиакомпании.</p>
      <p class="cargo-growth__value cargo-growth__value--secondary">311 <span>тыс. т внутри России</span></p>
      <p class="cargo-growth__market-note">Включая грузовые самолёты.</p>
    </section>
    <section class="cargo-growth__demand">
      <h2>Где искать спрос</h2>
      <div class="cargo-growth__item">
        <h3>Север и Дальний Восток</h3>
        <p>Почта, посылки, снабжение<br>удалённых территорий.</p>
      </div>
      <div class="cargo-growth__item">
        <h3>Промышленные регионы</h3>
        <p>Срочные запчасти и комплектующие<br>для предприятий.</p>
      </div>
      <div class="cargo-growth__item">
        <h3>Межрегиональные связи</h3>
        <p>Курьерские и B2B-отправления,<br>где важна скорость доставки.</p>
      </div>
    </section>
    <section class="cargo-growth__rollout">
      <h2>Как развивать Red Wings</h2>
      <div class="cargo-growth__step">
        <span>01</span>
        <div><h3>Выделить ёмкость</h3><p>Свободный отсек после багажа;<br>обработка в обоих аэропортах.</p></div>
      </div>
      <div class="cargo-growth__step">
        <span>02</span>
        <div><h3>Продать регулярность</h3><p>Агенты, почтовые операторы<br>и корпоративные контракты.</p></div>
      </div>
      <div class="cargo-growth__step">
        <span>03</span>
        <div><h3>Расширять по сети</h3><p>Пилот на 1–2 парах, затем<br>масштабирование по марже.</p></div>
      </div>
    </section>
  </div>
  <div class="cargo-growth__takeaway">
    <h2>Масштабируем S1: 24 направления на шести базах к 2036 году</h2>
    <div class="cargo-growth__case">
      <p><strong>24 направления · 14 976 вылетов</strong><br>60–100 кг/вылет × 100 RUB/кг</p>
      <p><strong>89,9–149,8 млн RUB/год</strong><br>выручка на рейсах нашей программы</p>
      <p><strong>40,4–73,4 млн RUB/год</strong><br>результат до налога по модели затрат</p>
    </div>
    <p class="cargo-growth__case-note">Расширение модели S1: 6 оборотов/неделю. Пилот MRV: ≈10 млн RUB выручки/год. Грузовая квота требует проверки.</p>
  </div>
</div>

<!--
Источники: data/cargo_research/documentation/RESEARCH.md, разделы 1–8, 10–12;
data/cargo_research/processed/market_benchmarks.csv.
446,3 тыс. т грузов и почты — весь рынок российских авиакомпаний за 2025 год,
311 тыс. т — внутренние перевозки. Общий объём включает грузовые самолёты;
это не объём доступного рынка грузов в отсеках пассажирских ВС.
Источник рынка: https://www.alta.ru/logistics_news/125303/
Север, Дальний Восток и промышленные регионы — гипотезы географии спроса,
не подтверждённые маршруты или контракты Red Wings.
Почта и курьерские отправления, запчасти — потенциальные сегменты пилота.
Масштабирование: подтверждённая ёмкость, аэропортовая обработка, договоры,
положительная дополнительная маржа и надёжность пассажирской перевозки.
Потенциал относится к пассажирской сети, отдельно от грузового оператора Sky Gates.
Продолжение S1 к2036:6баз*4уникальных направления*6оборотов*2плеча*52недели=14976вылетов.
Ресурсные базы MRV,AER,LED,SVX,KZN,KUF; это существующее присутствие, не6новых баз.
60–100кг оплаченного груза на плечо по100RUB/кг:89856–149760тыс.RUB выручки.
Обработка20RUB/кг,масса10RUB/кг,агент15%,фиксированные6*1.5млн=9млнRUB:
результат40.4208–73.368млнRUB до налога. Допущения, не доказанный спрос/прибыль.
Масса груза не подтверждена при пассажирском LF88%; требуется проверка совместимости.
Пилот MRV сохранён как ориентир: estimates/scenarios.csv, строка base; assumptions.csv.
1 664 вылета = 4 направления × 4 оборота × 2 плеча × 52 недели.
99 840 кг × 100 RUB/кг = 9 984 000 RUB выручки.
Обработка 20 RUB/кг, масса 10 RUB/кг, агент 15% выручки,
фиксированные расходы 1,5 млн RUB/год: результат 3 991 200 RUB/год.
Это условный пример для MRV, не оценка всей России; в итог S1 не включён.
Рынок в 2025 снизился примерно на 9%; «рост» — возможность продукта Red Wings,
а не утверждение об историческом росте национального рынка.
-->

---
layout: deck
---

<div class="rw-slide multimodal">
  <h1>Мультимодальность: перелёт + трансфер + отель</h1>
  <p class="multimodal__subtitle">Одна бронь и согласованная поездка до курорта — больше сервиса для клиента и дохода с поездки</p>
  <div class="multimodal__journey">
    <div><span>01 · Red Wings</span><strong>Перелёт в Минеральные Воды</strong></div>
    <span class="multimodal__arrow">→</span>
    <div><span>02 · Автобусный партнёр</span><strong>Трансфер в Кисловодск</strong></div>
    <span class="multimodal__arrow">→</span>
    <div><span>03 · Отель-партнёр</span><strong>3 ночи на курорте</strong></div>
  </div>
  <div class="multimodal__columns">
    <section>
      <h2>Экономика клиента · модель, RUB</h2>
      <p>Билет <strong>12 000</strong> − затраты рейса <strong>10 500</strong><br>= <strong>1 500</strong> маржи до общих расходов.</p>
      <p>Комиссии: автобус <strong>300</strong> + отель <strong>1 200</strong>.<br>Сервис пакета: <strong>−200</strong>.</p>
      <p>Общие расходы: <strong>−300</strong> на пассажира.<br>Условный налог на прибыль: <strong>25%</strong>.</p>
      <p class="multimodal__service">Чистая прибыль с клиента:<br><strong>900 RUB</strong> за перелёт → <strong>1 875 RUB</strong> с пакетом.</p>
    </section>
    <section class="multimodal__chart">
      <h2>Чистая прибыль на 10 000 пассажиров</h2>
      <div class="multimodal__bar-label"><span>Только перелёт</span><strong>9,00 млн RUB</strong></div>
      <div class="multimodal__bar multimodal__bar--flight"></div>
      <div class="multimodal__bar-label"><span>20% пассажиров берут пакет</span><strong>10,95 млн RUB</strong></div>
      <div class="multimodal__bar multimodal__bar--bundle"></div>
      <p class="multimodal__uplift">+1,95 млн RUB <span>или +21,7%</span></p>
      <p class="multimodal__attach">Выручка Red Wings: <strong>120 → 123 млн RUB</strong>.<br>Чистая маржа: <strong>7,5% → 8,9%</strong> от выручки.</p>
    </section>
  </div>
  <div class="multimodal__proof">
    <section>
      <h2>Реальный пример: easyJet holidays</h2>
      <p>Прибыль до налога: <strong>122 → 190 млн GBP.</strong><br>2023 → 2024 · <strong>+56%</strong> (скорректированная).</p>
    </section>
    <section>
      <h2>Что берём для Red Wings</h2>
      <p>Автобус расширяет охват аэропорта.<br>Отель добавляет комиссию, единый сервис — удобство.</p>
    </section>
  </div>
  <p class="multimodal__note">Модель: 10 000 пассажиров, 20% пакетов; выручка партнёров учитывается только в виде комиссий. Все ставки условные.</p>
</div>

<!--
Пример Red Wings — предложение продукта, не существующая услуга или договор.
Модельная группа из 10000 путешественников, пакеты покупают 2000.
Выручка билета 12000 RUB, затраты рейса на клиента 10500, маржа 1500.
Трансфер 1500*20%=300 комиссии; отель 12000*10%=1200 комиссии.
Сервис пакета 200 RUB, распределённые общие расходы 300 RUB на каждого пассажира.
Условная ставка налога 25% — допущение модели; применимость к Red Wings не проверялась.
Чистая прибыль на клиента: (1500-300)*0.75=900 без пакета,
(1500+300+1200-200-300)*0.75=1875 с пакетом.
База: выручка 10000*12000=120 млн RUB, чистая прибыль 9 млн RUB, маржа 7.5%.
Пакеты: выручка 120 млн + 2000*1500=123 млн RUB (агентская модель),
прибыль 8000*900+2000*1875=10.95 млн RUB; маржа 10.95/123=8.9024%.
Прирост 1.95 млн RUB или 21.6667%; это результат группы пассажиров, не всей авиакомпании.
Расходы модели условные, не фактические затраты или налоговая отчётность Red Wings.
Полная стоимость отеля и трансфера не включается в выручку Red Wings.
Факт easyJet holidays: headline profit before tax 2024 GBP190m, 2023 GBP122m, +56%.
Реальный туроператор — аналог продукта, не свидетельство эффекта для Red Wings.
Источник: https://corporate.easyjet.com/files/doc_downloads/2024/12/easyJet_AR24_web.pdf
-->

---
src: ./slides/growth-2036.md
---
