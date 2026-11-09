# Первичные данные и доказательства для кейса Red Wings «Новый хаб или прямые рейсы?»

**Исследование DR-01. Дата проверки: 10 ноября 2026 года, московское время.** Период фактов: преимущественно 2023–2026 годы; планы на 2027–2028 годы выделены отдельно. Формат: один отчёт с каталогом источников и реестром извлечённых наблюдений.

## A. Краткие итоги исследования

Открытых источников достаточно, чтобы восстановить масштаб рынка и Red Wings, сформировать лонглист аэропортов, проверить существование значительной части маршрутов и начать расчёт отдельных аэропортовых расходов. **Открытые данные пока не дают доказательной полной экономики новой сети:** не установлены конечные O&D-потоки для большинства приоритетных пар, доход от проданного сегмента, расходы SSJ по конкретной программе и свободный эксплуатационный ресурс флота. Выбирать стратегию на основании заполненных вымышленной загрузкой таблиц нельзя.

В отчёте зарегистрирован **71 источник**: официальные публикации, документы, каталоги выгрузок, действующие и исторические расписания, а также явно отмеченные вторичные сообщения. Это не 71 полностью скачанный датасет. Часть официальных страниц доступна только в поисковом индексе; часть PDF открыта, но скан не прочитан. Реестр содержит **109 наблюдений**; расчёт доли рынка выделен как вычисление. Лонглист включает **20 городов**. Источники обнаружены обычным веб-поиском и проверкой документов; отчёт не является результатом обращения к закрытым авиационным базам.

Наиболее полезные результаты:

- Найден официальный омский релиз с объёмами перевозок по десяти направлениям за 2025 год, а также официальный самарский релиз с объёмами отдельных линий. Это реальные опубликованные маршрутные наблюдения, но не выделенный конечный спрос между городами.
- Получены официальный PDF зимнего расписания Омска от 05.11.2026 и HTML-расписания Кольцово и Саратова. Для всех десяти приоритетных пар из Екатеринбурга найдены строки Red Wings. Поэтому эти пары нельзя целиком записывать в «новые пассажиры» проекта.
- Проверены оба сезонных сообщения Red Wings: мартовское перечисляет восемь ключевых городов, октябрьское — семь опорных. Отличия нужно хранить по сезонам.
- Текущая страница парка расходится с цифрами справки кейса. Она не раскрывает исправность, резерв, свободные экипажи и возможность снять самолёт с действующей программы.
- Подтверждён сертификат типа ПД-8. Он не означает сертификацию всего импортозамещённого SJ-100 и не доказывает поставку конкретных самолётов Red Wings.
- Найдены прямые PDF омского прейскуранта и двух октябрьских поправок. В саратовском PDF визуально проверены основные аэропортовые ставки.
- Найдено решение Росавиации № 22-64160-00191-Р. Ссылку на постановление № 1242 необходимо сопровождать проверкой актуального порядка: правовые системы отмечают утрату им силы.

**Доступ к заданию.** Ветка rewrite рабочего репозитория открылась через авторизованное подключение. Прочитан именно файл «задание/5 кейс.md» [S01], включая требования, сроки и примечание о справочном характере чисел. Остальные CSV, расчёты и выводы репозитория не приняты за первичные наблюдения. Внесение изменений в репозиторий не выполнялось.

**Что остаётся до количественного выбора.** Нужны данные об оплаченных конечных поездках и пересадках; история выполненных, а не только объявленных рейсов; доход и расходы по направлениям; бортовой план доступности; условия поддержки и предложения аэропортов для новой базы. Ни Омск, ни Екатеринбург не назначены победителем заранее. Три лучших города в этом исследовании не выбраны: задача DR-01 — собрать доказательства для последующей модели.

### Правила статусов и доступности

| Обозначение | Смысл в этом отчёте |
| --- | --- |
| verified_primary | Утверждение найдено в содержимом первичного издателя. Если текст получен только из поискового индекса, это прямо записано в доступности; неизменность полного файла не подтверждена. |
| verified_secondary | Число или сообщение прочитано во вторичном источнике либо в перепечатке, оригинальная публикация не получена. |
| estimated_with_method | Вычисление из указанных наблюдений. Это не новое измерение. |
| scenario_assumption | Допущение будущего сценария. В фактический реестр такие числа не подставлялись. |
| unverified | Найден каталог или кандидат на источник, но нужная строка/документ не проверены. |
| conflicted | Несовпадение значений, охвата, редакций или периодов. Раздел J сохраняет версии и способ разрешения. |
| unavailable | Показатель не получен в проверенном наборе источников. Не означает, что он нигде не существует. |
| not_found / access_restricted / requires_js | Соответственно: адрес не найден; доступ ограничен; для извлечения нужен исполняемый интерфейс. Тайм-аут и HTTP 503 записываются отдельно и не объявляются отсутствием документа. |

«Проверен источник» и «проверены все значения внутри» — разные состояния. Для новостей проверялся относящийся к задаче текст; для расписаний — конкретные строки; для сканированных тарифов — указанные страницы. Автоматические метки поисковой выдачи «опубликовано N месяцев назад» не использованы как точная дата публикации.

## B. Главный каталог первоисточников и проверочных источников

Каждая строка содержит отдельные поля landing_url и direct_url. Для HTML с данными они совпадают намеренно. Если единственный найденный оригинальный объект — сам PDF, оба поля содержат его адрес, а отсутствие отдельной карточки отмечено. Это не утверждение, что независимая страница публикации найдена.

archive_url = not_found во всех строках означает, что подтверждённая внешняя архивная копия не получена. Официальная страница с архивом прейскурантов — источник редакций, а не автоматически независимая архивная копия. Срок действия документа не заменяется датой его обнаружения.

| source_id | Издатель | Название | Тип | Период | Дата | landing_url | direct_url | direct_type | archive_url | Локатор | Доступность | Статус | Применение |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Материалы кейс-чемпионата в рабочем репозитории | Кейс 5. Red Wings — Новый хаб или прямые рейсы? | api | 2027–2028 | не установлена | https://github.com/We-seek-D-p/case-championship-26/blob/rewrite/задание/5%20кейс.md | https://api.github.com/repos/We-seek-D-p/case-championship-26/contents/задание/5%20кейс.md?ref=rewrite | api | not_found | §§ 6–9; инфографика | прочитан через авторизованный доступ; ветка изменяемая | verified_primary | Требования кейса; справочные числа не считать статистикой |
| S02 | Росавиация | Статистические данные: аналитическая таблица формы № 12-ГА | embedded_html | 2023–2024 | срез 27.01.2025 | https://www.favt.gov.ru/dejatelnost-vozdushnye-perevozki-stat-dannie/?from=old-site | https://www.favt.gov.ru/dejatelnost-vozdushnye-perevozki-stat-dannie/?from=old-site | embedded_html | not_found | «ВСЕ ПРЕДПРИЯТИЯ»; строки пассажиров, пассажирооборота и занятости | найдено в индексе; прямое чтение — тайм-аут | unverified | Национальная база; значения отдельных строк требуют выгрузки |
| S03 | Росавиация | Российские авиакомпании перевезли в 2025 году почти 109 млн пассажиров | embedded_html | 2025 | 30.01.2026 | https://favt.gov.ru/novosti-novosti/?id=17763 | https://favt.gov.ru/novosti-novosti/?id=17763 | embedded_html | not_found | абзацы 1–3 основного сообщения | текст найден в индексе; прямое чтение — тайм-аут | verified_primary | Годовой рынок и знаменатель доли |
| S04 | Росавиация | Реестр открытых данных | csv_catalog | исторические ряды; свежесть не установлена | не установлена | https://www.favt.gov.ru/opendata/ | not_found | csv_catalog | not_found | наборы № 5, 7, 10 | каталог виден в индексе; файлы не получены | unverified | Получить CSV пассажиров, пассажирооборота, занятости |
| S05 | Минтранс России | Доклад о результатах деятельности за 2025 год, целях на 2026 год и плановом периоде до 2028 года | pdf | 2025; планы до 2028 | 2026; точная дата не установлена | https://mintrans.gov.ru/file/557797 | https://mintrans.gov.ru/file/557797 | pdf | not_found | физическая страница 5, раздел о воздушном транспорте | PDF прочитан; 42 страницы; карточка публикации отдельно не найдена | verified_primary | Потоки в обход Москвы; параметры программ поддержки |
| S06 | Минтранс России | Расширение географии полетов — приоритет российских авиаперевозок | embedded_html | 2025 | точная дата не установлена | https://mintrans.gov.ru/press-center/news/12560 | https://mintrans.gov.ru/press-center/news/12560 | embedded_html | not_found | последний абзац о 54,4% | текст в индексе | verified_primary | Контроль определения доли рейсов |
| S07 | Росавиация | Дмитрий Ядров доложил главе Правительства о работе авиационной отрасли | embedded_html | май–август 2026 | 29.09.2026 | https://www.favt.gov.ru/novosti-novosti/?id=19636 | https://www.favt.gov.ru/novosti-novosti/?id=19636 | embedded_html | not_found | «Итоги работы авиакомпаний»; «Итоги работы аэропортов» | текст в индексе | verified_primary | Частичный срез 2026 года |
| S08 | Red Wings | Red Wings перевезла за год на российских самолетах 2 млн пассажиров и 2 совы | embedded_html | 2025 | 28.01.2026 | https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/ | https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/ | embedded_html | not_found | абзацы о 24 тыс. рейсов, 2,7 млн пассажиров, 25 новых линиях | текст в индексе; страница на /en/ содержит русский текст | verified_primary | Пассажиры компании; разделение типов и регулярности |
| S09 | Red Wings | Российская авиакомпания Red Wings отмечает свой юбилей — 25 лет деятельности | embedded_html | 2023; парк на дату релиза | точная дата не установлена | https://flyredwings.com/en/press/news/rossijskaya-aviakompaniya-red-wings-otmechaet-svoj-yubilej-25-let-deyatelnosti/ | https://flyredwings.com/en/press/news/rossijskaya-aviakompaniya-red-wings-otmechaet-svoj-yubilej-25-let-deyatelnosti/ | embedded_html | not_found | абзац о 2,66 млн пассажиров и 19 SSJ | текст в индексе | verified_primary | Исторический уровень, не текущая доступность |
| S10 | Red Wings | Red Wings перешла на летнее расписание полетов | embedded_html | лето 2026 | 31.03.2026 | https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/ | https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/ | embedded_html | not_found | первые абзацы: 118 направлений и восемь городов | текст в индексе | verified_primary | Сезонная сеть; термин «хаб» — формулировка издателя |
| S11 | Red Wings | Red Wings перешла на осенне-зимнее расписание полетов | embedded_html | зима 2026/27 | 27.10.2026 | https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/ | https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/ | embedded_html | not_found | основной текст, строки извлечения 111–118 | страница прочитана | verified_primary | Текущая объявленная сеть и семь опорных городов |
| S12 | Red Wings | Парк самолётов | embedded_html | страница на дату проверки | не указана | https://flyredwings.com/about/park/ | https://flyredwings.com/about/park/ | embedded_html | not_found | блоки SSJ100, Ту-214, Boeing 777-200ER, Ту-204-100B; строки 115–218 | страница прочитана; нет даты актуализации | verified_primary | Заявленный состав и компоновки, не свободный резерв |
| S13 | Red Wings | Роман Чуев стал генеральным директором Red Wings | embedded_html | назначение 2026 | 30.10.2026 | https://flyredwings.com/en/press/news/roman-chuev-stal-generalnym-direktorom-red-wings/ | https://flyredwings.com/en/press/news/roman-chuev-stal-generalnym-direktorom-red-wings/ | embedded_html | not_found | первые три абзаца | текст в индексе | verified_primary | Обновить устаревшую справку об управлении |
| S14 | Red Wings | Red Wings открыла программу полетов в Израиль на летний сезон 2027 года | embedded_html | 28.03–24.10.2027 | 03.11.2026 | https://flyredwings.com/press/news/red-wings-otkryla-programmu-poletov-v-izrail-na-letny-sezon-2027-goda/ | https://flyredwings.com/press/news/red-wings-otkryla-programmu-poletov-v-izrail-na-letny-sezon-2027-goda/ | embedded_html | not_found | первые два абзаца | текст в индексе | verified_primary | Анонс существующей загрузки флота на 2027 год |
| S15 | Red Wings | Red Wings создаст транзитный хаб в Екатеринбурге | embedded_html | 2020 | 13.10.2020 | https://flyredwings.com/press/news/red-wings-sozdast-tranzitnyj-xab-v-ekaterinburge/ | https://flyredwings.com/press/news/red-wings-sozdast-tranzitnyj-xab-v-ekaterinburge/ | embedded_html | not_found | дата конференции, начальные маршруты | текст в индексе | verified_primary | История проекта, не доказательство экономики 2026 года |
| S16 | Red Wings | Red Wings: год базирования в Кольцово | embedded_html | первый год проекта; январь–сентябрь 2021 | 07.10.2021 | https://flyredwings.com/press/news/red-wings-god-bazirovaniya-v-kolczovo/ | https://flyredwings.com/press/news/red-wings-god-bazirovaniya-v-kolczovo/ | embedded_html | not_found | абзацы о финансовой поддержке и 470 тыс. пассажиров | текст в индексе | verified_primary | Исторический результат и зависимость от поддержки |
| S17 | Red Wings | Red Wings развивает новые маршруты из Екатеринбурга | embedded_html | весна–лето 2024 | 23.04.2024 | https://flyredwings.com/en/press/news/red-wings-razvivaet-novye-marshruty-iz-ekaterinburga/ | https://flyredwings.com/en/press/news/red-wings-razvivaet-novye-marshruty-iz-ekaterinburga/ | embedded_html | not_found | абзац частот по 13 городам | текст в индексе | verified_primary | Историческое предложение; не текущие частоты |
| S18 | Red Wings | Red Wings будет летать в Ставрополь из Екатеринбурга | embedded_html | 2025 | 29.04.2025 | https://flyredwings.com/press/news/red-wings-budet-letat-v-stavropol-iz-ekaterinburga/ | https://flyredwings.com/press/news/red-wings-budet-letat-v-stavropol-iz-ekaterinburga/ | embedded_html | not_found | абзац о стыковках и регистрации багажа до конечного пункта | текст в индексе | verified_primary | Подтверждение предлагаемого трансферного сервиса |
| S19 | Аэропорт Кольцово | Сезонное расписание вылетов | embedded_html | осень–зима 2026/27 | изменяемая страница | https://ar-svx.ru/schedule/ | https://ar-svx.ru/schedule/ | embedded_html | not_found | строки рейсов WZ по кодам назначения; время местное | HTML прочитан; таблица извлечена также напрямую | verified_primary | Календарь действующего предложения |
| S20 | Аэропорт Гагарин | Расписание рейсов из Саратова | embedded_html | осень–зима 2026/27 | изменяемая страница | https://ar-gsv.ru/schedule/ | https://ar-gsv.ru/schedule/ | embedded_html | not_found | WZ-5048; S7-5158; S7-7058; строки 95–156 | HTML прочитан | verified_primary | Проверка обратного плеча и предложения конкурента |
| S21 | Омский аэропорт | Сезонное расписание «Зима 2026» | pdf | зима 2026/27 | редакция 05.11.2026 | https://www.aeroomsk.ru/karta-poleta/ | https://www.aeroomsk.ru/karta-poleta/pdf/w26/w26-20261105.pdf | pdf | not_found | 3 страницы; строки парных рейсов и интервалы дат | страница и PDF прочитаны | verified_primary | Расписание альтернативного узла с точными периодами |
| S22 | Red Wings | Направления из Екатеринбурга | embedded_html | витрина на дату проверки | дата предложения не раскрыта | https://flyredwings.com/directions/ekaterinburg/ | https://flyredwings.com/directions/ekaterinburg/ | embedded_html | not_found | карточки Уфы, Саратова, Омска, Сургута | текст в индексе | verified_primary | Только рекламные цены «от» |
| S23 | Омский аэропорт | Итоги производственной деятельности за 2025 год | embedded_html | 2025 | 15.01.2026 | https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/253/ | https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/253/ | embedded_html | not_found | строки 123–140; топ-10 направлений | официальная страница прочитана | verified_primary | Реальные объёмы маршрутов; конечные O&D не выделены |
| S24 | Омский аэропорт | Пассажиропоток Омского аэропорта в 2024 году составил 1 726 029 человек | embedded_html | 2023–2024 | 09.01.2025 | https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/210/ | https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/210/ | embedded_html | not_found | первые три абзаца | текст в индексе | verified_primary | Динамика аэропорта |
| S25 | Омский аэропорт | Омский аэропорт обслужил в 2023 году 1 680 206 человек | embedded_html | 2023 | 09.01.2024 | https://aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/142/ | https://aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/142/ | embedded_html | not_found | перечень субсидируемых линий 2023 | текст в индексе | verified_primary | История региональной сети, не наличие рейсов сейчас |
| S26 | Аэропорт Уфа | Международный аэропорт «Уфа» подвел итоги 2025 года | embedded_html | 2025 | 27.01.2026 | https://www.airportufa.ru/news/2025/mezhdunarodnyy-aeroport-ufa-podvel-itogi-2025-goda/ | https://www.airportufa.ru/news/2025/mezhdunarodnyy-aeroport-ufa-podvel-itogi-2025-goda/ | embedded_html | not_found | первые абзацы о пассажирах и прибыли | текст в индексе | verified_primary | Аэропортовый масштаб и показатели оператора |
| S27 | Аэропорт Пермь, официальный канал | Итоги пассажиропотока за 2025 год | embedded_html | 2025 | точная дата сообщения не извлечена | https://t.me/s/permairport?before=347 | https://t.me/s/permairport?before=347 | embedded_html | not_found | сообщение с 2 004 861; описание канала указывает aviaperm.ru | текст официального канала в индексе; ссылка на отдельный пост не извлечена | verified_primary | Поток с отдельным учётом транзита |
| S28 | AEX / AviaStat со ссылкой на аэропорт Рощино | Пассажиропоток аэропорта Рощино за 2025 год превысил 2,76 млн человек | embedded_html | 2025 | 14.01.2026 | https://www.aex.ru/news/2026/1/14/291500/ | https://www.aex.ru/news/2026/1/14/291500/ | embedded_html | not_found | основной текст | вторичная публикация прочитана в индексе; оригинал не найден | verified_secondary | Предварительная строка по Тюмени |
| S29 | Аэропорт Челябинск, официальный канал | Итоги пассажиропотока за 2025 год | embedded_html | 2025 | точная дата сообщения не извлечена | https://t.me/s/cekport_tg/410 | https://t.me/s/cekport_tg/410 | embedded_html | not_found | сообщение с 2 166 689 пассажирами | текст канала в индексе | verified_primary | Поток с внутренним, международным и транзитным компонентами |
| S30 | Западно-Сибирское МТУ Росавиации | Итоги года аэропортов Западной Сибири | embedded_html | 2025 | 22.01.2026 | https://zs-m.favt.ru/novosti-novosti/?id=12414 | https://zs-m.favt.ru/novosti-novosti/?id=12414 | embedded_html | not_found | абзацы Толмачево, Богашево, Барнаул, Кемерово | текст в индексе; прямое чтение — тайм-аут | verified_primary | Согласованный официальный срез четырёх аэропортов |
| S31 | Аэропорт Красноярск, KJA TEAM | Производственные итоги за 2025 год | embedded_html | 2025 | 14.01.2026 | https://team.kja.aero/media/aeroport-krasnoyarsk-po-itogam-2025-goda-1-1 | https://team.kja.aero/media/aeroport-krasnoyarsk-po-itogam-2025-goda-1-1 | embedded_html | not_found | «Пассажирский трафик»; «Популярные направления и авиакомпании» | текст в индексе | verified_primary | Поток аэропорта, авиакомпании и рост отдельных пар |
| S32 | Международный аэропорт Иркутск | Подводим итоги за 9 месяцев 2025 года | embedded_html | январь–сентябрь 2025 | 19.10.2025 | https://www.iktport.ru/ru/about/novosti/726-подводим-итоги-за-9-месяцев-2025-года | https://www.iktport.ru/ru/about/novosti/726-подводим-итоги-за-9-месяцев-2025-года | embedded_html | not_found | пассажиры всего и рейтинг авиакомпаний | текст в индексе | verified_primary | Частичный период и присутствие S7 |
| S33 | Международный аэропорт Иркутск | Почти миллион пассажиров и более 7 млн кг багажа: итоги лета | embedded_html | июнь–август 2026 | 17.09.2026 | https://iktport.ru/ru/about/novosti/799-почти-миллион-пассажиров-и-более-7-млн-кг-багажа-аэропорт-иркутска-подвёл-итоги-работы-за-лето | https://iktport.ru/ru/about/novosti/799-почти-миллион-пассажиров-и-более-7-млн-кг-багажа-аэропорт-иркутска-подвёл-итоги-работы-за-лето | embedded_html | not_found | абзацы пассажиров по сегментам и авиакомпаниям | текст в индексе | verified_primary | Свежий сезонный срез |
| S34 | Аэропорт Гагарин | В 2025 году аэропорт «Гагарин» обслужил 1 млн 64 тыс. пассажиров | embedded_html | 2025 | 20.01.2026 | https://ar-gsv.ru/about/news/v-2025-godu-aeroport-gagarin-obsluzhil-1-mln-64-tys-passazhi/ | https://ar-gsv.ru/about/news/v-2025-godu-aeroport-gagarin-obsluzhil-1-mln-64-tys-passazhi/ | embedded_html | not_found | первые два абзаца; список 14 направлений и 11 перевозчиков | текст в индексе | verified_primary | Масштаб Саратова и присутствие Red Wings |
| S35 | Аэропорт Оренбург | Аэропорт Оренбург обслужил за 2025 год более 950 тысяч пассажиров | embedded_html | 2025 | 15.01.2026 | https://ar-ren.ru/about/news/aeroport-orenburg-obsluzhil-za-2025-god-bolee-950/ | https://ar-ren.ru/about/news/aeroport-orenburg-obsluzhil-za-2025-god-bolee-950/ | embedded_html | not_found | первые три абзаца | текст в индексе | verified_primary | Масштаб и структура аэропорта |
| S36 | Аэропорт Курумоч | Итоги работы в новогодние праздники — текст содержит итоги 2025 года | embedded_html | 2025 | 14.01.2026 | https://ar-kuf.ru/about/news/itogi-raboty-v-novogodnie-prazdnik/ | https://ar-kuf.ru/about/news/itogi-raboty-v-novogodnie-prazdnik/ | embedded_html | not_found | абзацы годового потока и направлений | текст в индексе; заголовок не соответствует содержанию | verified_primary | Годовые потоки Самары и отдельных линий |
| S37 | Аэропорт Курумоч | Пассажиропоток аэропорта Курумоч превысил 3,5 миллиона человек | embedded_html | 2024 | 17.01.2025 | https://ar-kuf.ru/about/news/passazhiropotok-aeroporta-kurumoch-prevysil-3-5-milliona-che/ | https://ar-kuf.ru/about/news/passazhiropotok-aeroporta-kurumoch-prevysil-3-5-milliona-che/ | embedded_html | not_found | абзацы о годовом потоке, Москве, Петербурге и Сочи | текст в индексе | verified_primary | Историческая сопоставимая база |
| S38 | Официальный портал правовой информации Татарстана | Муниципальный документ об итогах работы Казани в 2025 году; полное название не извлечено | pdf | 2025 | февраль 2026 по каталогу; точная дата не установлена | https://pravo.tatarstan.ru/file/npa/2026-02/1794855/npa_1794856.pdf | https://pravo.tatarstan.ru/file/npa/2026-02/1794855/npa_1794856.pdf | pdf | not_found | страница с печатным номером 5: туризм и аэропорт | текст PDF в индексе; прямое чтение — тайм-аут | verified_primary | Поток аэропорта и туристические прокси; не O&D |
| S39 | Аэропорт Нижнего Новгорода | За 2025 год выросло количество нижегородцев, летавших за рубеж | embedded_html | 2025 | 14.01.2026 | https://ar-goj.ru/about/news/za-2025-god-vyroslo-kolichestvo-nizhegorodtsev-letavshikh-za/ | https://ar-goj.ru/about/news/za-2025-god-vyroslo-kolichestvo-nizhegorodtsev-letavshikh-za/ | embedded_html | not_found | первые абзацы, 26 направлений и запасные посадки | текст в индексе | verified_primary | Масштаб и операционные ограничения узла |
| S40 | Аэропорт Кольцово | Развитие инфраструктуры, новые сервисы и рост пассажиропотока: итоги 2025 года | embedded_html | 2025 | 19.01.2026 | https://ar-svx.ru/about/news/razvitie-infrastruktury-novye-servisy-i-rost-passazhiropotok/ | https://ar-svx.ru/about/news/razvitie-infrastruktury-novye-servisy-i-rost-passazhiropotok/ | embedded_html | not_found | первые три абзаца | текст в индексе | verified_primary | Масштаб существующей базы |
| S41 | Финмаркет / Интерфакс, пресс-служба аэропорта | Аэропорт Минвод в 2025 году снизил пассажиропоток на 4,6% | embedded_html | 2025; инфраструктурные планы 2026–2028 | 19.01.2026 | https://www.finmarket.ru/news/6545429 | https://www.finmarket.ru/news/6545429 | embedded_html | not_found | основной текст и последний абзац | вторичная публикация в индексе; оригинал аэропорта не найден | verified_secondary | Масштаб Минеральных Вод; планы отдельно от факта |
| S42 | Росстат | Численность населения РФ по муниципальным образованиям | xlsx_catalog | на 01.01.2025; каталог также содержит 2024 | 25.04.2025 для файла 2025 по каталогу | https://rosstat.gov.ru/folder/12781?print=1&source=subscribe | not_found | xlsx_catalog | not_found | «Оперативная информация», файл 1,07 МБ | каталог в индексе; прямой XLSX не получен; HTTP 503 | unverified | Нужная выгрузка по границам муниципалитетов |
| S43 | Росстат | Россия 2025: крупнейшие города | pdf | население на 01.01.2024 | 2025; точная дата не установлена | https://rosstat.gov.ru/storage/mediabank/Rossia_2025.pdf | https://rosstat.gov.ru/storage/mediabank/Rossia_2025.pdf | pdf | not_found | таблица «Крупнейшие города России на 1 января 2024 г., тыс. человек» | таблица PDF в индексе; прямое чтение — тайм-аут; отдельная карточка не найдена | verified_primary | Историческая численность города, не агломерации |
| S44 | Росавиация | Господдержка региональных перевозок; решение № 22-64160-00191-Р, версия 7 | pdf | порядок предоставления субсидии | 26.11.2024 — дата базового решения; дата версии не установлена | https://favt.gov.ru/dejatelnost-gosudarstvennaia-podderzhka-subsidii/?id=15106 | https://favt.ru/public/materials/0/3/9/e/7/039e77a7205ca81e3070590870e45a3e.pdf | pdf | not_found | титульный лист; раздел 1; приложения нужно дочитать | карточка и начало PDF в индексе; полное чтение — тайм-аут | verified_primary | Новый порядок; конкретные ставки пока не извлечены |
| S45 | Росавиация | Региональное субсидирование перевозок: перечни 2024–2026 | embedded_html | 2024–2026 | актуализация в 2026; точная дата HTML не установлена | https://favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony/?from=old-site | https://favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony/?from=old-site | embedded_html | not_found | таблица 2026; архив приказов 899-П, 261-П, 845-П, 1187-П | таблица прочитана фрагментами в индексе, включая строки № 48 и 51; прямое чтение — тайм-аут; old/special — зеркала | verified_primary | Плановые получатели, типы, кресла, частоты, софинансирование |
| S46 | Росавиация, архив нормативных материалов | Правила по постановлению Правительства РФ от 25.12.2013 № 1242, историческая редакция | pdf | редакция включает изменения до 14.11.2018 | дата загрузки не установлена | https://old.favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony | https://old.favt.gov.ru/public/materials/0/d/2/d/a/0d2da0ba156a854e116346650116d1d5.pdf | pdf | not_found | титульная страница, список изменяющих документов | начало PDF в индексе | verified_primary | Только история регулирования; ставки не переносить |
| S47 | КонсультантПлюс | Постановление № 1242, редакция 14.10.2023: отметка об утрате силы | embedded_html | правовой статус на дату проверки | дата утраты силы не извлечена | https://www.consultant.ru/document/cons_doc_LAW_156427/ | https://www.consultant.ru/document/cons_doc_LAW_156427/ | embedded_html | not_found | статус над заголовком | текст карточки в индексе; отменяющий акт не получен | verified_secondary | Сигнал обязательной правовой перепроверки |
| S48 | АО «СарАэро-Инвест» | Прейскурант для российских потребителей по состоянию на 21.12.2025 с изменениями от 01.08.2026 | pdf_scan | редакция 01.08.2026 | дата публикации не указана | https://ar-gsv.ru/about/info/ | https://ar-gsv.ru/upload/iblock/e03/x30km5z81eqnv9f1mhqs3im92866fzqy/Preyskurant-AO-SarAero_Invest-dlya-rossiyskikh-ekspluatantov-s-21.12.2025-_s-izmeneniyami-s-01.08.2026_.pdf | pdf_scan | not_found | страницы 1–2, разделы I и II.1 | PDF скачан; 11 страниц; страницы 1–2 проверены визуально | verified_primary | Конкретные ставки Саратова без НДС |
| S49 | Омский аэропорт | Прейскурант для российских потребителей с 21.08.2026 | pdf_scan | с 21.08.2026 | дата загрузки не установлена | https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/ | https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/tarifs_rus_20260821.pdf | pdf_scan | not_found | 11 страниц; таблицы ставок | PDF доступен; текстовый слой не извлечён | verified_primary | Извлечь с поправками S50–S51; ставки пока не подтверждены |
| S50 | Омский аэропорт | Изменения к прейскуранту с 10.10.2026 | pdf_scan | с 10.10.2026 | не установлена | https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/ | https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/pr568-2026.pdf | pdf_scan | not_found | 1 страница | PDF доступен; ставки не прочитаны | verified_primary | Необходимая поправка к S49 |
| S51 | Омский аэропорт | Изменения к прейскуранту с 15.10.2026 | pdf_scan | с 15.10.2026 | не установлена | https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/ | https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/pr610-2026.pdf | pdf_scan | not_found | 1 страница | PDF доступен; ставки не прочитаны | verified_primary | Необходимая поправка к S49 |
| S52 | Омский аэропорт | Коды и характеристики | embedded_html | страница на дату проверки | не указана | https://www.aeroomsk.ru/aviakompaniyam/kody-i-kharakteristiki/ | https://www.aeroomsk.ru/aviakompaniyam/kody-i-kharakteristiki/ | embedded_html | not_found | таблица кодов, ВПП и принимаемых ВС; строки 124–144 | HTML прочитан | verified_primary | Предварительная проверка инфраструктуры Омска |
| S53 | Аэропорт Курумоч | Основные показатели ФХД СЕМ за 2025–2027 годы | pdf | 2025 — факт; 2026–2027 — прогноз | не установлена | https://ar-kuf.ru/about/info/ | https://ar-kuf.ru/upload/iblock/964/ugdj79k4p95x7qjgpy17rokry33zngn4/Osnovnye-pokazateli-FKHD-SEM-v-sfere-okazaniya-reguliruemykh-uslug-za-2025_2027-gg.pdf | pdf | not_found | таблица доходов и расходов; столбцы факт/прогноз | карточка и таблица в индексе; HTML каталога прочитан | verified_primary | Экономика аэропорта; не затраты авиакомпании |
| S54 | Аэропорт Нижнего Новгорода | Отчёт об инвестиционной программе за 2024 год, формы 3а–г | pdf | 2024 | не установлена | https://goj.aero/upload/iblock/54c/i3h4wxp5659sjwweyoixytoq5ntss6t8/Investitsionnaya-programma-otchyet-po-formam-3a_b_v_g-za-2024-g.pdf | https://goj.aero/upload/iblock/54c/i3h4wxp5659sjwweyoixytoq5ntss6t8/Investitsionnaya-programma-otchyet-po-formam-3a_b_v_g-za-2024-g.pdf | pdf | not_found | строки оборудования; отдельная карточка не найдена | таблица PDF в индексе | verified_primary | Справочник состава инфраструктуры; не бюджет новой базы |
| S55 | Росавиация | Ставки сборов за аэронавигационное обслуживание: приказ ФАС № 595/24 | embedded_html | редакция 2024 | 30.08.2024 — дата акта | https://favt.gov.ru/dejatelnost-ajeronavigacionnoe-obsluzhivanie-stavki-sborov/ | https://favt.gov.ru/dejatelnost-ajeronavigacionnoe-obsluzhivanie-stavki-sborov/ | embedded_html | not_found | приложения по разным категориям пользователей | текст в индексе; возможно устаревший | verified_primary | Историческая структура ставок; не утверждённая ставка на 2027 |
| S56 | ГАРАНТ | Приказ ФАС от 16.12.2025 № 1101/25 о ставках АНО | embedded_html | 2026 | 16.12.2025; регистрация 26.01.2026 | https://base.garant.ru/413529528/ | https://base.garant.ru/413529528/ | embedded_html | not_found | пункты 1–2; приложения 1–11 | текст в индексе; официальный опубликованный экземпляр не найден | verified_secondary | Правовая сверка замены 595/24; ставки не извлечены |
| S57 | S7 Group, официальный канал S7 Newsroom | S7 Airlines подвела итоги 2025 года | embedded_html | 2025 | точная дата сообщения не извлечена | https://t.me/s/s7newsroom/544 | https://t.me/s/s7newsroom/544 | embedded_html | not_found | сообщение об итогах 2025; 12,8 млн и потоки через три хаба | текст официального канала в индексе | verified_primary | Масштаб S7 и хабов; не трансферная доля |
| S58 | Пресс-релиз Аэрофлота, перепечатка АвиаПорт | Аэрофлот отмечает 5-летие сибирского хаба | embedded_html | 2021–2026; 2025 отдельно | июнь 2026; точный день не подтверждён | https://www.aviaport.ru/news/aeroflot-otmechaet-5-letie-sibirskogo-khaba/ | https://www.aviaport.ru/news/aeroflot-otmechaet-5-letie-sibirskogo-khaba/ | embedded_html | not_found | абзацы о 2,2 млн, 32 направлениях и 10 самолётах | найден текст перепечатки; оригинал aeroflot.ru не получен | verified_secondary | Количественный ориентир хаба с ограничением происхождения |
| S59 | ЮТэйр | Группа «ЮТэйр» выпустила отчётность по МСФО за 2025 год | embedded_html | 2025 | точная дата не извлечена | https://www.utair.ru/about/news/gruppa-yuteyr-vypustila-otchyetnost-po-msfo-za-2025-god/ | https://www.utair.ru/about/news/gruppa-yuteyr-vypustila-otchyetnost-po-msfo-za-2025-god/ | embedded_html | not_found | разделы самолётных и вертолётных перевозок | официальное сообщение в индексе; полный PDF МСФО не получен | verified_primary | Операционные данные группы по раскрытому охвату |
| S60 | ЮТэйр | «ЮТэйр» опубликовал отчётность по РСБУ за 2025 год | embedded_html | 2025 | точная дата не извлечена | https://www.utair.ru/about/news/yuteyr-opublikoval-otchetnost-po-rsbu-za-2025-god/ | https://www.utair.ru/about/news/yuteyr-opublikoval-otchetnost-po-rsbu-za-2025-god/ | embedded_html | not_found | пассажиропоток ПАО и внутренние перевозки | текст официального сообщения в индексе | verified_primary | Проверка отличия охвата РСБУ/МСФО |
| S61 | Авиакомпания Азимут | Бортовой журнал «Ваш Азимут», № 97 | pdf | итоги 2025 | выпуск к Новому 2026 году; точная дата не установлена | https://azimuth.ru/ru/about/journal | https://azimuth.ru/uploads/ckeditor/attachments/949/vash_azimut_97.pdf | pdf | not_found | обращение руководства «Уважаемые пассажиры!» | текст PDF и каталог в индексе | verified_primary | Пассажиры компании и базовые аэропорты |
| S62 | Уральские авиалинии | Двойной триумф: премия «Крылья России» | embedded_html | 2025 | 02.06.2026 | https://www.uralairlines.ru/uz/news/element/dvoynoy-triumf-uralskie-avialinii-stali-laureatami-premii-krylya-rossii-v-nominatsiyakh-aviakompaniya/ | https://www.uralairlines.ru/uz/news/element/dvoynoy-triumf-uralskie-avialinii-stali-laureatami-premii-krylya-rossii-v-nominatsiyakh-aviakompaniya/ | embedded_html | not_found | комментарий о более 8 млн пассажиров и почти 53 тыс. рейсов | текст официального сообщения в индексе; /uz/ содержит русский текст | verified_primary | Подтверждённая нижняя граница годового масштаба |
| S63 | РБК Компании | АО «Ред Вингс», ИНН 7732107883: бухгалтерские показатели | embedded_html | 2025 | дата обновления не установлена | https://companies.rbc.ru/id/1027700281091-ao-red-vings/ | https://companies.rbc.ru/id/1027700281091-ao-red-vings/ | embedded_html | not_found | блок выручки, прибыли и себестоимости за 2025 | вторичная карточка в индексе; отчёт ФНС не получен | verified_secondary | Только предварительная финансовая строка |
| S64 | Росавиация | Дмитрий Ядров вручил сертификаты типа на Ил-114-300 и ПД-8 | embedded_html | 05.06.2026 | 05.06.2026 | https://favt.gov.ru/novosti-novosti/?id=18741 | https://favt.gov.ru/novosti-novosti/?id=18741 | embedded_html | not_found | первые абзацы и «Пять фактов о двигателе ПД-8» | текст официального сообщения в индексе | verified_primary | Сертификация двигателя; не всего SJ-100 |
| S65 | Ростех / ОАК | SSJ-100 получили одобрение главного изменения типовой конструкции | embedded_html | 12.10.2026 | 12.10.2026 | https://www.rostec.ru/media/news/samolety-ssj-100-poluchili-odobrenie-glavnogo-izmeneniya-tipovoy-konstruktsii/ | https://www.rostec.ru/media/news/samolety-ssj-100-poluchili-odobrenie-glavnogo-izmeneniya-tipovoy-konstruktsii/ | embedded_html | not_found | первые три абзаца; версии с SaM146 | текст в индексе | verified_primary | Ресурс прежнего SSJ; не ресурс нового ПД-8 |
| S66 | ПАО «Яковлев» | SJ-100: продуктовая страница | embedded_html | не установлен; страница изменяемая | не указана | https://yakovlev.ru/products/sj-100/ | https://yakovlev.ru/products/sj-100/ | embedded_html | not_found | блоки вместимости, дальности, числа операторов | текст в индексе; смешение брендинга с действующим SSJ | verified_primary | Только справочная характеристика; модификацию проверить |
| S67 | Авиация России, со ссылкой на интервью «Вести» | Первые SJ-100 и МС-21 передадут авиакомпаниям во второй половине 2027 года | embedded_html | объявленный план 2027 | сообщение о выступлении 15.09.2026 | https://aviation21.ru/pervye-sj-100-i-ms-21-peredadut-aviakompaniyam-vo-vtoroj-polovine-2027-goda/ | https://aviation21.ru/pervye-sj-100-i-ms-21-peredadut-aviakompaniyam-vo-vtoroj-polovine-2027-goda/ | embedded_html | not_found | абзацы сроков, сертификации и контрактов | вторичная публикация в индексе; оригинал интервью не получен | verified_secondary | Сценарий сроков; число бортов Red Wings не подтверждено |
| S68 | Росавиация | Общественный совет оценил перспективные планы отечественного авиастроения | embedded_html | план на 2026 из 2025 года | 23.10.2025 | https://favt.gov.ru/novosti-novosti?id=17091 | https://favt.gov.ru/novosti-novosti?id=17091 | embedded_html | not_found | пункт о поставках SJ-100 в 2026 | текст официального сообщения в индексе | verified_primary | История переноса плановых сроков |
| S69 | Пресс-релиз Авроры, AVIA RU | «Аврора» — дипломант национальной авиационной премии «Крылья России» | embedded_html | 2025 | 02.06.2026 | https://www.aviaru.net/pr/76792/ | https://www.aviaru.net/pr/76792/ | embedded_html | not_found | первые два абзаца: около 1,6 млн, 18 тыс. рейсов, 83% | перепечатка с указанием издателя; оригинал не найден | verified_secondary | Ориентир отдельной авиакомпании, не группы партнёров |
| S70 | Росавиация | Итоги гражданской авиации за 2023 год | embedded_html | 2023 | март 2024; точная дата сообщения не извлечена | https://special.favt.gov.ru/novosti-novosti/?id=11187 | https://special.favt.gov.ru/novosti-novosti/?id=11187 | embedded_html | not_found | «Результаты перевозок»: 105,4 млн, международные 22,4 млн, внутренние 83 млн | текст официальной страницы в индексе; полный файл статистики не выгружен | verified_primary | Национальный годовой итог; округление сохранить |
| S71 | Росавиация | Пассажиропоток российских авиакомпаний в 2024 году вырос почти на 6% | embedded_html | 2024 | 03.02.2025 | https://www.favt.gov.ru/novosti-rossii/?id=14454 | https://www.favt.gov.ru/novosti-rossii/?id=14454 | embedded_html | not_found | первые абзацы: 111,7 млн; 84,7 млн и 27 млн | текст официальной страницы в индексе; полный файл статистики не выгружен | verified_primary | Национальный годовой итог; округление сохранить |

## C. Реестр фактических наблюдений

Ниже — нормализованный реестр. **Полная карточка наблюдения** получается однозначным соединением строки C с B по source_id: издатель, дата публикации, landing_url, direct_url и archive_url наследуются из конкретного источника. Период измерения, география, единица, точный локатор, метод, статус и допустимое использование находятся в самой строке. Это позволяет не повторять длинный URL в каждой соседней строке одного документа. Для O109 второй вход расчёта явно указан как S03 / O006.

Номер строки извлечения — вспомогательный локатор текущего чтения HTML, а не гарантированно стабильная нумерация сайта. Название раздела, рейс, год и подпись таблицы имеют приоритет.

| observation_id | Объект | Метрика | Значение | Единица | Период | География | source_id | Точный локатор | Статус | Разрешённое использование | Метод извлечения | Ограничения |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| O001 | Российские авиакомпании | перевезённые пассажиры | 105.4 | млн пассажиров | 2023 | Россия | S70 | «Результаты перевозок» | verified_primary | Исторический знаменатель | извлечение опубликованного значения | Округлено; не аэропортовый поток |
| O002 | Российские авиакомпании | внутренние пассажиры | 83 | млн пассажиров | 2023 | Россия | S70 | абзац внутренних перевозок | verified_primary | Внутренний рынок | извлечение опубликованного значения | Не уникальные люди |
| O003 | Российские авиакомпании | международные пассажиры | 22.4 | млн пассажиров | 2023 | международные линии | S70 | абзац международных перевозок | verified_primary | Полный рынок российских перевозчиков | извлечение опубликованного значения | Ограничения источника — раздел B |
| O004 | Российские авиакомпании | перевезённые пассажиры | 111.7 | млн пассажиров | 2024 | все линии | S71 | первый абзац | verified_primary | Уточнённый опубликованный годовой итог | извлечение опубликованного значения | В ранней публикации было 111,6 млн; сохранить версию |
| O005 | Российские авиакомпании | внутренние пассажиры | 84.7 | млн пассажиров | 2024 | Россия | S71 | второй абзац | verified_primary | Внутренний знаменатель | извлечение опубликованного значения | В ранней публикации — 84,6 млн |
| O006 | Российские авиакомпании | перевезённые пассажиры | 108.85 | млн пассажиров | 2025 | все линии | S03 | абзац 1 | verified_primary | Основной годовой знаменатель доли Red Wings | извлечение опубликованного значения | Ограничения источника — раздел B |
| O007 | Российские авиакомпании | внутренние пассажиры | 81.45 | млн пассажиров | 2025 | Россия | S03 | абзац 1 | verified_primary | Внутренний знаменатель; числитель Red Wings пока неизвестен | извлечение опубликованного значения | Ограничения источника — раздел B |
| O008 | Российские авиакомпании | международные пассажиры | 27.4 | млн пассажиров | 2025 | международные линии | S03 | абзац 1 | verified_primary | Проверка суммы компонентов | извлечение опубликованного значения | Ограничения источника — раздел B |
| O009 | Российские аэропорты | обслуженные пассажиры | 214.66 | млн аэропортовых обслуживаний | 2025 | Россия | S03 | абзац 1 | verified_primary | Масштаб аэропортовой системы | извлечение опубликованного значения | Не знаменатель доли перевозчика |
| O010 | Российские авиакомпании | пассажирооборот | 284.43 | млрд пассажиро-км | 2025 | все линии | S03 | абзац 2 | verified_primary | Работа транспорта в расстояниях | извлечение опубликованного значения | Не число пассажиров |
| O011 | Российские авиакомпании | занятость кресел | 89.5 | % | 2025 | все линии | S03 | абзац 2 | verified_primary | Общерыночный контроль | извлечение опубликованного значения | Не загрузка конкретной новой линии; знаменатель показателя уточнить по форме |
| O012 | Внутренние регулярные перевозки | доля рейсов/маршрутов в обход Москвы | 54.4 | % | 2025 | Россия | S05 | физическая с. 5 | verified_primary | Сетевая децентрализация | извлечение опубликованного значения | Источник употребляет «рейсов (маршрутов)»; не доля пассажиров |
| O013 | Внутренние перевозки в обход Москвы | перевезённые пассажиры | 34.4 | млн пассажиров | 2025 | без сегментов с Москвой | S05 | физическая с. 5 | verified_primary | Объём немосковских перевозок | извлечение опубликованного значения | Не O&D всех региональных пар |
| O014 | Российские авиакомпании | перевезённые пассажиры | 39.5 | млн пассажиров | май–август 2026 | все линии | S07 | «Итоги работы авиакомпаний» | verified_primary | Свежий частичный срез | извлечение опубликованного значения | Не январь–август и не весь 2026 |
| O015 | Российские авиакомпании | внутренние пассажиры | 29.6 | млн пассажиров | май–август 2026 | Россия | S07 | тот же раздел | verified_primary | Сегмент периода | извлечение опубликованного значения | Ограничения источника — раздел B |
| O016 | Российские авиакомпании | международные пассажиры | 9.9 | млн пассажиров | май–август 2026 | международные линии | S07 | тот же раздел | verified_primary | Сегмент периода | извлечение опубликованного значения | Ограничения источника — раздел B |
| O017 | Red Wings | перевезённые пассажиры | 2.7 | млн пассажиров | 2025 | все линии и типы ВС | S08 | абзац общего пассажиропотока | verified_primary | Числитель общей доли | извлечение опубликованного значения | Округлённое число; внутренние отдельно не раскрыты |
| O018 | Red Wings, российские типы | перевезённые пассажиры | >2 | млн пассажиров | 2025 | все линии на российских ВС | S08 | первый абзац | verified_primary | Масштаб отечественного парка | извлечение опубликованного значения | Не внутренние перевозки |
| O019 | Red Wings, российские типы | выполненные рейсы | около 24 000 | рейсов | 2025 | все линии на российских ВС | S08 | первый абзац | verified_primary | Историческая эксплуатационная активность | извлечение опубликованного значения | Не годовой ресурс свободного парка |
| O020 | Red Wings, Boeing 777 | чартерные рейсы | около 1 000 | рейсов | 2025 | дальние чартеры | S08 | абзац Boeing-777 | verified_primary | Отделить чартерный сегмент | извлечение опубликованного значения | Пассажиры сегмента отдельно не даны |
| O021 | Red Wings | новые регулярные направления | 25: 17 внутренних, 8 международных | направлений | 2025 | вся сеть | S08 | абзац новых маршрутов | verified_primary | Масштаб расширения | извлечение опубликованного значения | Не чистый прирост сети с учётом закрытий |
| O022 | Red Wings | перевезённые пассажиры | 2.66 | млн пассажиров | 2023 | все линии | S09 | абзац десятилетней динамики | verified_primary | История компании | извлечение опубликованного значения | Ограничения источника — раздел B |
| O023 | Red Wings | направления летней программы | 118, из них 69 международных | направлений | до 24.10.2026 | вся сеть | S10 | первый абзац | verified_primary | Объявленная сезонная сеть | извлечение опубликованного значения | Не число уникальных аэропортов и не выполненные рейсы |
| O024 | Red Wings | опорные города летней программы | Москва; Санкт-Петербург; Казань; Самара; Екатеринбург; Минеральные Воды; Сочи; Махачкала | перечень | лето 2026 | Россия | S10 | первый абзац | verified_primary | Сезонный перечень | извлечение опубликованного значения | Издатель называет их «ключевыми хабами»; операционное устройство отдельно |
| O025 | Red Wings | направления зимней программы | 71, из них 34 международных | направлений | до 27.03.2027 | вся сеть | S11 | строка 113 | verified_primary | Объявленная программа | извлечение опубликованного значения | Не размер внутреннего O&D |
| O026 | Red Wings | опорные города зимней программы | Москва; Санкт-Петербург; Казань; Самара; Екатеринбург; Сочи; Махачкала | перечень | зима 2026/27 | Россия | S11 | строка 114 | verified_primary | Текущий объявленный перечень | извлечение опубликованного значения | Минеральные Воды не включены; это не доказательство закрытия базы |
| O027 | Red Wings, SSJ100 | заявленная численность и кресла | 20; 100 | ВС; кресел/ВС | страница на дату проверки | парк | S12 | SSJ100, строки 115–147 | verified_primary | Компоновка и заявленный парк | извлечение опубликованного значения | Нет бортовых номеров и остаточного ресурса |
| O028 | Red Wings, Ту-214 | заявленная численность и кресла | 3; 194 | ВС; кресел/ВС | страница на дату проверки | парк | S12 | Ту-214, строки 151–171 | verified_primary | Заявленная компоновка | извлечение опубликованного значения | Не доступность для новой сети |
| O029 | Red Wings, Ту-204-100B | заявленная численность и кресла | 2; 210 | ВС; кресел/ВС | страница на дату проверки | парк | S12 | Ту-204-100B, строки 198–218 | verified_primary | Заявленная компоновка | извлечение опубликованного значения | Расходится со справкой кейса |
| O030 | Red Wings, Boeing 777-200ER | заявленная численность и кресла | 3; 412 | ВС; кресел/ВС | страница на дату проверки | парк | S12 | Boeing 777, строки 174–194 | verified_primary | Контроль состава | извлечение опубликованного значения | Не подтверждает эксплуатацию всех трёх |
| O031 | Red Wings | генеральный директор | Роман Чуев | назначение | с 30.10.2026 | компания | S13 | первые абзацы | verified_primary | Исправить справку | извлечение опубликованного значения | Игорь Ивлиев обозначен как предшествующий и.о. |
| O032 | Red Wings в Кольцово | перевезённые пассажиры | 470 000 | пассажиров | первый год проекта к 07.10.2021 | Екатеринбург | S16 | комментарий гендиректора | verified_primary | Исторический результат проекта | извлечение опубликованного значения | Не календарный 2021; не чистый трансфер |
| O033 | Red Wings в Кольцово | перевезённые пассажиры | 380 000 | пассажиров | январь–сентябрь 2021 | Екатеринбург | S16 | тот же комментарий | verified_primary | Исторический неполный период | извлечение опубликованного значения | Прогноз полумиллиона не включён в факт |
| O034 | Омский аэропорт | пассажиропоток | 1629761 | пассажиров | 2025 | Омск | S23 | строка 126 | verified_primary | Масштаб аэропорта | извлечение опубликованного значения | Не уникальные люди и не спрос пары |
| O035 | Омский аэропорт | пассажиропоток | 1726029 | пассажиров | 2024 | Омск | S24 | первый абзац | verified_primary | Годовая динамика | извлечение опубликованного значения | Ограничения источника — раздел B |
| O036 | Омский аэропорт | пассажиропоток | 1680206 | пассажиров | 2023 | Омск | S24 | сравнение с 2023 | verified_primary | Годовая динамика | извлечение опубликованного значения | Ограничения источника — раздел B |
| O037 | Омск — Москва | пассажиропоток направления | 674175 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O038 | Омск — Санкт-Петербург | пассажиропоток направления | 234510 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O039 | Омск — Сочи | пассажиропоток направления | 195927 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O040 | Омск — Новосибирск | пассажиропоток направления | 106309 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O041 | Омск — Астана | пассажиропоток направления | 56405 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O042 | Омск — Анталья | пассажиропоток направления | 31093 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O043 | Омск — Сургут | пассажиропоток направления | 29964 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O044 | Омск — Новый Уренгой | пассажиропоток направления | 27762 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O045 | Омск — Казань | пассажиропоток направления | 27510 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O046 | Омск — Красноярск | пассажиропоток направления | 23192 | пассажиров | 2025 | пара городов | S23 | топ-10, строки 131–140 | verified_primary | Наблюдение обслуженного направления | извлечение опубликованного значения | Направления суммирования и конечные пункты поездки не раскрыты |
| O047 | Аэропорт Уфа | пассажиропоток | 4929715 | пассажиров | 2025 | Уфа | S26 | первый абзац | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Ограничения источника — раздел B |
| O048 | Аэропорт Пермь | пассажиропоток | 2004861 | пассажиров | 2025 | Пермь | S27 | сообщение об итогах | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Ограничения источника — раздел B |
| O049 | Аэропорт Пермь | компоненты потока | 1 707 582 внутренних; 284 295 международных; 12 984 транзитных | пассажиров | 2025 | Пермь | S27 | маркированный список | verified_primary | Проверка определения итога | извлечение опубликованного значения | Сумма совпадает; транзит выделен отдельно |
| O050 | Аэропорт Рощино | пассажиропоток | 2760338 | пассажиров | 2025 | Тюмень | S28 | первый абзац | verified_secondary | Предварительный масштаб | извлечение опубликованного значения | Оригинал аэропорта не найден |
| O051 | Аэропорт Челябинск | пассажиропоток | 2166689 | пассажиров | 2025 | Челябинск | S29 | сообщение итогов | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Ограничения источника — раздел B |
| O052 | Аэропорт Челябинск | компоненты потока | 1 912 999 внутренних; 247 422 международных; 6 268 транзитных | пассажиров | 2025 | Челябинск | S29 | список компонентов | verified_primary | Проверка структуры | извлечение опубликованного значения | Транзит отдельной строкой |
| O053 | Аэропорт Толмачево | внутренний и международный поток | 7,608; 2,074 | млн пассажиров | 2025 | Новосибирск | S30 | абзац Толмачево | verified_primary | Официальный округлённый масштаб | извлечение опубликованного значения | Не сводить с неофициальными 9,5 млн без сверки |
| O054 | Аэропорт Богашево | пассажиропоток | 627.5 | тыс. пассажиров | 2025 | Томск | S30 | абзац Богашево | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Ограничения источника — раздел B |
| O055 | Аэропорт Барнаул | пассажиропоток | 792.6 | тыс. пассажиров | 2025 | Барнаул | S30 | абзац Барнаула | verified_primary | Масштаб кандидата | извлечение опубликованного значения | В ранних СМИ — 790 тыс.; не усреднять |
| O056 | Аэропорт Кемерово | пассажиропоток | 458.2 | тыс. пассажиров | 2025 | Кемерово | S30 | абзац Кемерово | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Ограничения источника — раздел B |
| O057 | Аэропорт Красноярск | пассажиропоток | 4263566 | пассажиров | 2025 | Красноярск | S31 | крупная итоговая цифра | verified_primary | Масштаб узла | извлечение опубликованного значения | Внутренние и международные строки не исчерпывают итог |
| O058 | Аэропорт Красноярск | внутренний и международный поток | 3 421 272; 786 939 | пассажиров | 2025 | Красноярск | S31 | «Пассажирский трафик» | verified_primary | Раздельные сегменты | извлечение опубликованного значения | Разница с итогом — 55 355; определение остатка не установлено |
| O059 | Аэропорт Иркутск | пассажиропоток | 3078468 | пассажиров | январь–сентябрь 2025 | Иркутск | S32 | первый абзац | verified_primary | Частичный официальный период | извлечение опубликованного значения | Не годовой итог |
| O060 | S7 в Иркутске | обслуженные пассажиры | 1418065 | пассажиров | январь–сентябрь 2025 | Иркутск | S32 | рейтинг перевозчиков | verified_primary | Присутствие конкурента | извлечение опубликованного значения | Не суммировать с хабовой статистикой S7 |
| O061 | Аэропорт Иркутск | пассажиропоток | 999558 | пассажиров | июнь–август 2026 | Иркутск | S33 | первый абзац | verified_primary | Свежий сезонный срез | извлечение опубликованного значения | Ограничения источника — раздел B |
| O062 | Аэропорт Гагарин | пассажиропоток | 1064 | тыс. пассажиров | 2025 | Саратов | S34 | первый абзац | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Округлено |
| O063 | Аэропорт Оренбург | пассажиропоток | >951 | тыс. пассажиров | 2025 | Оренбург | S35 | первый абзац | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Не превращать «превысил» в точное значение |
| O064 | Аэропорт Курумоч | пассажиропоток | 3.57 | млн пассажиров | 2025 | Самара | S36 | первый абзац | verified_primary | Масштаб существующей опорной точки | извлечение опубликованного значения | Название статьи не соответствует периоду в тексте |
| O065 | Самара — Москва | пассажиропоток направления | 1.3 | млн пассажиров | 2025 | пара городов | S36 | абзац популярных направлений | verified_primary | Наблюдение сегментного потока | извлечение опубликованного значения | Трансфер через Москву не выделен |
| O066 | Самара — Санкт-Петербург | пассажиропоток направления | 492 | тыс. пассажиров | 2025 | пара городов | S36 | тот же абзац | verified_primary | Сопоставимый маршрут | извлечение опубликованного значения | Ограничения источника — раздел B |
| O067 | Самара — Сочи | пассажиропоток направления | 325 | тыс. пассажиров | 2025 | пара городов | S36 | тот же абзац | verified_primary | Сезонный сопоставимый маршрут | извлечение опубликованного значения | Ограничения источника — раздел B |
| O068 | Самара — Калининград | пассажиропоток направления | 47.8 | тыс. пассажиров | 2025 | пара городов | S36 | абзац региональных направлений | verified_primary | Сопоставимый межрегиональный маршрут | извлечение опубликованного значения | Ограничения источника — раздел B |
| O069 | Самара — Минеральные Воды | пассажиропоток направления | 47 | тыс. пассажиров | 2025 | пара городов | S36 | тот же абзац | verified_primary | Сопоставимый межрегиональный маршрут | извлечение опубликованного значения | Ограничения источника — раздел B |
| O070 | Аэропорт Казань | пассажиропоток | 5384816 | пассажиров | 2025 | Казань | S38 | печатная с. 5, абзац аэропорта | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Значение из индексированного PDF |
| O071 | Казань | туристические посещения | 5.1 | млн посещений/туристов по формулировке документа | 2025 | город Казань | S38 | печатная с. 5, абзац туризма | verified_primary | Прокси привлекательности | извлечение опубликованного значения | Методика уникальности туриста не раскрыта; не авиапассажиры |
| O072 | Аэропорт Нижнего Новгорода | пассажиропоток | >1,4 | млн пассажиров | 2025 | Нижний Новгород | S39 | первый абзац | verified_primary | Масштаб кандидата | извлечение опубликованного значения | Округлённая нижняя граница |
| O073 | Аэропорт Нижнего Новгорода | самолёты на запасной | >300 | ВС/обслуживаний по тексту | 2025 | Нижний Новгород | S39 | абзац основного запасного Москвы | verified_primary | Операционная нагрузка | извлечение опубликованного значения | Не считать регулярным местным спросом |
| O074 | Аэропорт Кольцово | пассажиропоток | около 8,385 | млн пассажиров | 2025 | Екатеринбург | S40 | первый абзац | verified_primary | Масштаб исходной базы | извлечение опубликованного значения | Ограничения источника — раздел B |
| O075 | Аэропорт Минеральные Воды | пассажиропоток | 4.6 | млн пассажиров | 2025 | Минеральные Воды | S41 | первый абзац | verified_secondary | Предварительный масштаб | извлечение опубликованного значения | Оригинал аэропорта не получен |
| O076 | Саратов, аэропортовые сборы | взлёт–посадка | 1301 | руб./т МВМ, без НДС | редакция 01.08.2026 | GSV | S48 | с. 1, I.1 | verified_primary | Опубликованная ставка для российских потребителей | визуальная проверка сканированного PDF | Не включает прочее обслуживание |
| O077 | Саратов, аэропортовые сборы | транспортная безопасность | 1090 | руб./т МВМ, без НДС | редакция 01.08.2026 | GSV | S48 | с. 1, I.2 | verified_primary | Опубликованная ставка | визуальная проверка сканированного PDF | База — МВМ, не фактическая масса |
| O078 | Саратов, аэропортовые сборы | сверхнормативная стоянка | 5 | % сбора взлёт–посадка за час | редакция 01.08.2026 | GSV | S48 | с. 1, I.3 | verified_primary | Часовая ставка сверхнормативной стоянки | визуальная проверка сканированного PDF | Норматив бесплатного времени отдельно проверить |
| O079 | Саратов, внутренние линии | аэровокзальный комплекс | 298 | руб./пассажира, без НДС | редакция 01.08.2026 | GSV | S48 | с. 2, I.4 | verified_primary | Компонент аэропортового обслуживания | визуальная проверка сканированного PDF | Порядок включения пассажиров уточнить |
| O080 | Саратов, внутренние линии | обслуживание пассажира | 575 | руб./пассажира, без НДС | редакция 01.08.2026 | GSV | S48 | с. 2, II.1 | verified_primary | Компонент обслуживания | визуальная проверка сканированного PDF | Не средняя себестоимость пассажира |
| O081 | Омский аэропорт | ВПП | 2500 × 45 | м | страница на дату проверки | OMS | S52 | строки 138–144 | verified_primary | Предварительный инфраструктурный фильтр | извлечение опубликованного значения | Нужны действующие AIP/NOTAM и расчёт взлётных характеристик |
| O082 | Омский аэропорт | принимаемые ВС | RRJ-95 включён | допуск по перечню сайта | страница на дату проверки | OMS | S52 | строка 134 | verified_primary | Проверить пригодность SSJ | извлечение опубликованного значения | Не сертификат готовности базы ТО |
| O083 | S7 Airlines | перевезённые пассажиры | 12.8 | млн пассажиров | 2025 | все линии | S57 | сообщение итогов | verified_primary | Масштаб конкурента | извлечение опубликованного значения | Ограничения источника — раздел B |
| O084 | S7 через Новосибирск / Иркутск | обслуженные пассажиры | почти 7; 1,9 | млн пассажиров | 2025 | OVB / IKT | S57 | абзац трёх хабов | verified_primary | Масштаб узлов | извлечение опубликованного значения | Возможен повторный учёт между хабами; не доля трансфера |
| O085 | Группа Аэрофлот, Красноярск | пассажиропоток | 2.2 | млн пассажиров | 2025 | Красноярск | S58 | абзац роста хаба | verified_secondary | Масштаб узла | извлечение опубликованного значения | Перепечатка; точный охват отличается от рейтинга аэропорта |
| O086 | Группа Аэрофлот, Красноярск | базирование | 10: 3 SSJ, 4 A319, 3 B737 | ВС | лето 2026 | Красноярск | S58 | абзац базирования | verified_secondary | Состав инфраструктурного проекта | извлечение опубликованного значения | Не готовая норма флота для Red Wings |
| O087 | ЮТэйр, самолётный сегмент МСФО | пассажиры | 6,2; внутренние 5,0 | млн пассажиров | 2025 | сеть | S59 | «Пассажирские перевозки на самолётах» | verified_primary | Сопоставление в раскрытом охвате | извлечение опубликованного значения | Не смешивать с 6,9 млн вместе с вертолётами |
| O088 | ПАО ЮТэйр, сообщение РСБУ | пассажиры | 6,1; внутренние 4,8 | млн пассажиров | 2025 | сеть | S60 | абзац пассажиропотока | verified_primary | Сохранить отдельное определение | извлечение опубликованного значения | Расхождение с S59 не разрешено |
| O089 | Азимут | пассажиропоток | 2.2 | млн пассажиров | 2025 | сеть | S61 | обращение руководства | verified_primary | Региональный конкурент на SSJ | извлечение опубликованного значения | Не прибыльность конкретной базы |
| O090 | Уральские авиалинии | пассажиропоток | >8 | млн пассажиров | 2025 | сеть | S62 | комментарий руководства | verified_primary | Подтверждённая граница | извлечение опубликованного значения | Точное значение по первичной годовой форме не извлечено |
| O091 | АО Ред Вингс | выручка | 52070209000 | руб. | 2025 | юридическое лицо | S63 | финансовый блок | verified_secondary | Предварительная сверка финансов | извлечение опубликованного значения | Требуется отчёт ФНС; не регулярная внутренняя выручка |
| O092 | АО Ред Вингс | чистая прибыль | 2282120000 | руб. | 2025 | юридическое лицо | S63 | финансовый блок | verified_secondary | Предварительная сверка | извлечение опубликованного значения | Не операционная прибыль и не свободные деньги |
| O093 | Двигатель ПД-8 | сертификат типа | вручён | событие | 05.06.2026 | Россия | S64 | первые абзацы | verified_primary | Факт сертификации двигателя | извлечение опубликованного значения | Не сертификат самолёта |
| O094 | SSJ с SaM146, RRJ-95B-100/LR-100 | назначенный ресурс | 20 000 полётов; 40 000 часов; 20 лет | циклы; часы; годы | с одобрением 12.10.2026 | семейство ВС | S65 | абзац установленных значений | verified_primary | Техническое ограничение соответствующих модификаций | извлечение опубликованного значения | Не распространять автоматически на весь парк и SJ-100 |
| O095 | SJ-100 | план первых передач | вторая половина 2027 | плановый период | заявление 15.09.2026 | российские заказчики | S67 | абзац сроков | verified_secondary | Сценарный срок поставки | извлечение опубликованного значения | Не подтверждает число, контракт или ввод у Red Wings |
| O096 | Аврора | пассажиропоток и занятость | около 1,6 млн; 83% | пассажиров; % | 2025 | сеть отдельной авиакомпании | S69 | первые абзацы | verified_secondary | Ориентир регионального перевозчика | извлечение опубликованного значения | Не вся единая дальневосточная система |
| O097 | Три федеральные программы поддержки | выделенные средства | 26.7 | млрд руб. | 2025 | Россия | S05 | физическая с. 5 | verified_primary | Контекст господдержки | извлечение опубликованного значения | Не бюджет одной региональной программы; не выплаты Red Wings |
| O098 | Три федеральные программы поддержки | пассажиры по специальному тарифу | 5.5 | млн пассажиров | 2025 | Россия | S05 | физическая с. 5 | verified_primary | Результат программ | извлечение опубликованного значения | Не конечный O&D |
| O099 | Новосибирск | численность постоянного населения города | 1634 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O100 | Екатеринбург | численность постоянного населения города | 1536 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O101 | Казань | численность постоянного населения города | 1319 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O102 | Нижний Новгород | численность постоянного населения города | 1205 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O103 | Красноярск | численность постоянного населения города | 1205 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O104 | Челябинск | численность постоянного населения города | 1177 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O105 | Уфа | численность постоянного населения города | 1163 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O106 | Самара | численность постоянного населения города | 1159 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O107 | Омск | численность постоянного населения города | 1104 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O108 | Пермь | численность постоянного населения города | 1027 | тыс. человек | 01.01.2024 | город в административных границах | S43 | таблица «Крупнейшие города России» | verified_primary | Исторический демографический прокси | извлечение строки индексированного PDF | Не 2025/2026 и не агломерация; округлено до тысяч |
| O109 | Red Wings | расчёт общей доли | ≈2,48 | % | 2025 | пассажиры российских авиакомпаний, все линии | S08 | 2,7 млн / 108,85 млн из S03 × 100 | estimated_with_method | Округлённая доля общей сети | деление O017 на O006, умножение на 100 | Округлён числитель; не внутренняя доля |

## D. Каталог датасетов для скачивания и извлечения

Здесь указан следующий конкретный объект для обработки, а не обещание уже готовой выгрузки. Отдельные CSV, скрипты и архивы в рамках отчёта не создавались.

| Набор | Источники и прямой объект | Структура / охват | Способ извлечения | Частота и главный контроль |
| --- | --- | --- | --- | --- |
| Национальная статистика | S02; direct_url в B | Форма 12-ГА: показатели × период × регулярность × внутренние/международные | HTML-таблицы; при появлении файла — сохранить исходный Excel | Обычно месячные/накопленные итоги; фактическая свежесть каждой версии отдельно |
| Открытые CSV Росавиации | S04; direct_url = not_found | Каталог наборов пассажиров, пассажирооборота, занятости | Сначала получить паспорт набора и фактический файл; API не угадан | Наличие каталога не доказывает обновление до 2026 |
| Годовой доклад Минтранса | S05; https://mintrans.gov.ru/file/557797 | PDF, 42 страницы; транспортные итоги и планы | Текстовый слой; раздел авиации, физическая с. 5 | Годовой; не превращать цели до 2028 в фактический прогноз спроса |
| Перечень субсидируемых маршрутов | S45; HTML в B | Получатель × пара аэропортов × подынтервал × тип ВС × кресла × частота × парные рейсы × софинансирование | Таблица HTML; затем оригинальные приложения приказов | Приказные изменения; одна пара может занимать несколько строк |
| Решение о субсидии | S44; прямой PDF в B | Условия, результат, расчёт и приложения | Полное чтение PDF после восстановления доступа | Хранить номер версии; версия 7 найдена, актуальность на весь 2027 не установлена |
| Население муниципалитетов | S42; direct_url = not_found | Муниципалитет × дата × постоянное население | Получить XLSX из каталога и лист с кодами | Годовой срез; город, округ и агломерация раздельно |
| Население крупнейших городов | S43; PDF в B | Город × 01.01.2024, тыс. человек | Извлечь табличные строки | Историческая замена до получения нового XLSX, не данные 2026 |
| Кольцово, расписание | S19; https://ar-svx.ru/schedule/ | Направление × рейс × дни × интервал × время × тип | HTML, затем развёртывание в календарь вылетов | Изменяемая страница; фиксировать время получения и исключения |
| Саратов, расписание | S20; https://ar-gsv.ru/schedule/ | Аналогичная таблица; обратные плечи и конкуренты | HTML; объединять только непересекающиеся интервалы | Граница сезона переходит через Новый год |
| Омск, зимнее расписание | S21; https://www.aeroomsk.ru/karta-poleta/pdf/w26/w26-20261105.pdf | PDF, 3 страницы; парные и многоучастковые рейсы; дата версии 05.11.2026 | Текстовый слой + визуальная сверка сложных строк | Сезон 25.10.2026–27.03.2027; есть отдельные разовые вылеты |
| Омск, маршрутные итоги | S23; официальный HTML в B | 10 направлений за 2025 год и итог аэропорта | Маркированный перечень | Годовой; направления суммирования и трансфер не расшифрованы |
| Самара, маршрутные итоги | S36–S37; HTML в B | Избранные направления, итоги 2024/2025 | Текст с единицами и признаком округления | Заголовок S36 не отражает содержание: проверять текст |
| Саратов, тарифы | S48; прямой PDF в B | Ставка × единица × дата начала × категория потребителя | OCR скана, затем визуальная сверка | Проверена редакция 01.08.2026; текущую на дату рейса уточнить |
| Омск, тарифы | S49–S51; три PDF в B | Базовый прейскурант и отдельные изменения | OCR всех трёх документов; построить историю ставок | Поправка не заменяет весь прейскурант |
| Курумоч, ФХД | S53; прямой PDF в B | Факт 2025 и прогноз 2026/2027 по регулируемым услугам | Табличный PDF | Не смешивать расходы аэропорта с ценой обслуживания авиакомпании |
| Нижний Новгород, инвестиции | S54; прямой PDF в B | Оборудование, капитальные вложения, сроки | Таблицы форм 3а–г | Проверить, какие формы — план, какие — отчёт |
| Азимут, журнал | S61; прямой PDF в B | Авторское обращение с итогами 2025 | Текстовый слой | Контроль операционного масштаба; не финансовая отчётность |
| Отчётность Red Wings | S63; оригинальный файл ФНС не получен | Сейчас только вторичная финансовая карточка | Получить форму по ИНН 7732107883 в ГИР БО | До получения первички не использовать точность до рубля как проверенную |

### Действительно установленные технические метаданные

Для S48 непосредственно получен файл объёмом **2 714 684 байта**; SHA-256: **24ba7881efacc0decf51b598cc4aa16b67ee9130c55616c58db0551e26f3fdab**. Ответ сервера имел тип application/pdf. PDF содержит 11 страниц. Страницы 1–2 отрисованы и сверены визуально; текстовый слой этих страниц пуст, поэтому одно автоматическое извлечение текста ставок не даёт.

Для S21 установлен тип application/pdf и 3 страницы; для S49 — application/pdf и 11 страниц; для S50 и S51 — application/pdf и по одной странице. Контрольные суммы, точные размеры и HTTP Last-Modified этих объектов не устанавливались. Неизвестные метаданные не заполнены по аналогии.

## E. Рынок России и показатели Red Wings

### E.1. Согласованный масштаб и пределы сопоставимости

Основные национальные значения вынесены в O001–O016. Для 2023 года найден итог Росавиации, для 2024 — более поздняя публикация об итоговой статистике, для 2025 — официальный итоговый релиз. Срез 2026 года в реестре относится **только к маю–августу**. Он не заменяет итог за девять месяцев или год.

Для годового знаменателя в 2025 году используются пассажиры **российских авиакомпаний** [O006], а не пассажиропоток аэропортов [O009]. Аэропортовая система учитывает обслуживание в пунктах сети, а международный аэропортовый поток может включать иностранных перевозчиков. Поэтому деление пассажиров Red Wings на сумму аэропортов не измеряет её долю рынка.

Для 2024 года обнаружено реальное расхождение публикаций: раннее сообщение от 22.01.2025 приводит 111,6 млн, более позднее от 03.02.2025 — 111,7 млн [S71; проверочная ранняя публикация приведена в J]. В основной ряд внесён поздний итог. Не следует «исправлять» это округлением до удобного числа без сохранения версии.

Показатель занятости кресел [O011] — агрегат рынка. Его нельзя подставить вместо ожидаемой загрузки маршрута. Для самостоятельного расчёта необходимо получить определение формы: отношение пассажиров к креслам и отношение пассажиро-км к кресло-км могут дать разные результаты при разной длине полётов.

Пассажиры перевозчика не равны уникальным людям за год: обратная поездка и стыковочная перевозка могут порождать несколько учётных сегментов. Точный порядок заполнения формы 12-ГА нужно хранить вместе с национальной выгрузкой. В настоящем отчёте все исходные числа сохранены в единицах издателя.

### E.2. База Red Wings и доля

В O017–O022 сохранены раздельно общий поток компании, перевозки на российских самолётах, рейсы российских типов и дальние чартеры. **«Российский самолёт» не означает «внутренняя линия».** Именно поэтому нельзя принять опубликованный объём отечественных типов за числитель внутренней доли.

Расчёт O109: 2,7 / 108,85 × 100 ≈ 2,48%. Он использует округлённый общий поток компании и общий рынок российских перевозчиков за один год. Публиковать его допустимо как приблизительную общую долю. Доля Red Wings на внутренних линиях по найденным данным не рассчитана.

Для будущего проекта необходимо различать:

1. Новые для компании сегментные перевозки.
2. Перенос пассажиров между собственными маршрутами.
3. Пассажиров конкурентов, перешедших в Red Wings.
4. Новые поездки, возникшие благодаря предложению.
5. Дополнительный сегмент собственной стыковки без дополнительной конечной поездки.

При постоянном знаменателе изменение доли равно добавленным сегментам, делённым на рынок. При росте общего рынка знаменатель тоже меняется. Оба определения должны быть заданы до сценарного расчёта; знаменатель 2025 года нельзя выдавать за прогноз 2028 года.

### E.3. Перевозки в обход Москвы

Показатель O012 характеризует рейсы/маршруты, а O013 — пассажиров на немосковских участках. Это разные объекты измерения. Перелёт из региона через Новосибирск может состоять из двух немосковских сегментов; он не является прямой поездкой конечной пары. Из доли немосковских рейсов не следует доля неудовлетворённого регионального спроса.

В докладе Минтранса [S05] также найдены результаты трёх программ поддержки [O097–O098]. Их общий бюджет нельзя распределять поровну по маршрутам, а пассажиров по специальным тарифам нельзя автоматически приписывать программе региональных линий или Red Wings.

### E.4. Что не восстановлено в национальном ряду

Не получена единая машинная месячная выгрузка за 2023–2026 годы с одновременным разделением по компаниям, регулярности и географии. Не извлечены точные месячные кресла, кресло-км и выполненные рейсы Red Wings. Нет проверенного помесячного прогноза общего рынка 2027–2028 годов с методикой. Эти поля остаются пропусками, а не заполняются годовым средним или линейным продолжением четырёх летних месяцев.


## F. Лонглист городов: 20 кандидатов и полнота доказательств

Это перечень для фильтрации, **не рейтинг**. Столбец населения использует только проверенный исторический срез S43: город в административных границах на 01.01.2024, тысячи человек. Прочерк означает отсутствие извлечённого значения, а не нулевое население. Население агломераций в сопоставимых границах не получено.

Годовой поток — аэропортовый показатель 2025 года, если явно не указан другой период. Точность и статус наследуются из указанных O-строк. Нельзя ранжировать аэропорты по смешанным годовым и сезонным потокам без приведения периода.

| Город | Население города на 01.01.2024, тыс. | Доступный пассажиропоток | Что подтверждено для сети / конкурентов | Источники | Что критически не установлено |
| --- | ---: | --- | --- | --- | --- |
| Омск | 1 104 | 1 629 761 за 2025 | Маршрутные итоги, зимний PDF, присутствие S7, ЮТэйр, Ямала, Red Wings; RRJ-95 в перечне допуска | O034–O046, O081–O082; S21, S52 | Конечный O&D; стоимость и готовность новой базы ТО; свободные стоянки и экипажи |
| Уфа | 1 163 | 4 929 715 за 2025 | Действующая строка Red Wings из SVX; официальный итог аэропорта | O047; S19, S26 | Трансфер и межрегиональные пары; условия размещения базы |
| Нижний Новгород | 1 205 | Более 1,4 млн за 2025 | Собственное расписание SVX–GOJ; аэропорт обслуживает существенную запасную нагрузку Москвы | O072–O073; S19, S39 | Конечный спрос; влияние запасных бортов на слоты; тарифная редакция |
| Пермь | 1 027 | 2 004 861 за 2025 | Отдельно раскрыты внутренний, международный и транзитный компоненты | O048–O049; S27 | Трансфер по парам, частоты кандидатов, свободный ресурс инфраструктуры |
| Тюмень | — | 2 760 338 за 2025, вторичный источник | Официальный оригинал годового релиза не получен | O050; S28 | Подтверждение первички, местного и трансферного спроса, договорных ставок |
| Челябинск | 1 177 | 2 166 689 за 2025 | Компоненты потока опубликованы официальным каналом | O051–O052; S29 | География спроса, конкуренция наземного транспорта, состав доступных мощностей |
| Новосибирск | 1 634 | 7,608 млн внутренних и 2,074 млн международных за 2025 | S7 — развитый узел; официальный территориальный итог и сообщение S7 | O053, O083–O084; S30, S57 | Трансферные пары и переток; доступные слоты; экономика входа рядом с S7 |
| Красноярск | 1 205 | 4 263 566 за 2025 | Действующий проект группы Аэрофлот; операционные результаты аэропорта | O057–O058, O085–O086; S31, S58 | Точный сопоставимый охват хаба; доля трансфера; экономика конкуренции |
| Иркутск | — | 3 078 468 за 9 месяцев 2025; 999 558 за лето 2026 | Сильное присутствие S7 подтверждено самим аэропортом | O059–O061; S32–S33 | Годовой сопоставимый итог, стыковочные направления, база и ограничения мощностей |
| Томск | — | 627,5 тыс. за 2025 | Итог МТУ; Red Wings присутствует в расписании Кольцово | O054; S19, S30 | Маршрутные объёмы; сезонность; реальные мощности нового терминала |
| Саратов | — | 1,064 млн за 2025 | 14 направлений и 11 перевозчиков по годовому релизу; есть расписание и тарифный PDF | O062; S20, S34, S48 | O&D; спрос на собственный хаб; стоимость инженерной базы |
| Оренбург | — | Более 951 тыс. за 2025 | 12 направлений по годовому релизу; действующая линия Red Wings из SVX | O063; S19, S35 | Маршрутный спрос и трансфер; отдельный план новой базы |
| Самара | 1 159 | 3,57 млн за 2025 | Уже опорный город Red Wings; опубликованы объёмы отдельных пар | O064–O069; S11, S36 | Эффект именно новой базы относительно имеющегося присутствия; O&D |
| Казань | 1 319 | 5 384 816 за 2025 | Уже опорный город Red Wings; раскрыт туристический прокси | O070–O071; S11, S38 | Туристы, прибывшие по воздуху; трансфер и конкуренты на конкретных парах |
| Минеральные Воды | — | 4,6 млн за 2025, вторичный источник | В летнем перечне Red Wings; базовое присутствие Азимута по его журналу | O075, O089; S10, S41, S61 | Первичный итог, фактический статус базирования Red Wings зимой, влияние реконструкции |
| Барнаул | — | 792,6 тыс. за 2025 | Итог МТУ; действующие строки Red Wings из SVX | O055; S19, S30 | Пара Барнаул–Екатеринбург в пассажирах; доступная поддержка; актуальная инфраструктура |
| Екатеринбург | 1 536 | Около 8,385 млн за 2025 | Существующий хаб Red Wings и присутствие Уральских авиалиний; сеть и трансферный сервис подтверждены | O074; S15–S20, S40, S62 | Прирост сверх существующей сети; свободный ресурс самолётов и слотов |
| Сургут | — | Годовой итог не извлечён | Действующие линии SVX–SGC и OMS–SGC, перевозчики Red Wings и ЮТэйр | O043; S19, S21 | Годовой аэропортовый итог, конечный спрос, ограничения базирования |
| Кемерово | — | 458,2 тыс. за 2025 | МТУ и действующие строки Red Wings из SVX | O056; S19, S30 | Объём пары; новые стыковки; экономика минимальной частоты |
| Абакан | — | Годовой итог не извлечён | Строки Red Wings из SVX; строка плановой поддержки в перечне | S19, S45 | Первичный годовой поток, конечные пары, точная редакция поддержки |

### F.1. Что можно и нельзя вывести из этого лонглиста

Для Омска получен наиболее подробный в этом наборе пакет по альтернативной базе: история аэропорта, фактические направления, расписание, характеристики ВПП и тарифные документы. **Полнота найденных материалов не является баллом инвестиционной привлекательности.** По другим городам меньшая полнота может отражать раскрытие информации и ограничения доступа.

Для Самары, Казани и Екатеринбурга необходимо сначала определить контрфактический вариант: что добавляет новая база к уже имеющемуся присутствию. Для Минеральных Вод надо разрешить сезонное изменение перечня. Для Новосибирска, Красноярска и Иркутска есть проверяемое присутствие крупных региональных игроков, но это само по себе не исключает выгодных отдельных линий Red Wings.

Чтобы составить рейтинг, по каждому кандидату нужны одинаковые поля: местный конечный спрос, транзитные пары, сетевое положение, конкурентное предложение, инфраструктурная готовность, затраты и доступность поддержки. Веса и отсечение городов относятся к будущей модели. Неизвестный показатель должен снижать уверенность, а не автоматически получать нулевой балл.

### F.2. Драйверы спроса и инфраструктура: граница доказательств

Туристический показатель Казани [O071] может использоваться как объясняющий признак, но не переводится в авиапассажиров без распределения по видам транспорта и происхождению. Сопоставимые данные о доходах, деловых поездках, миграционных связях и туристических ночёвках по всему лонглисту не извлечены. Предположения об «экономическом потенциале» городов не представлены как наблюдения.

Для Омска опубликованы ВПП и перечень принимаемых типов [O081–O082]. Для остальных городов нельзя считать выполненной инженерную проверку только потому, что они принимают регулярные рейсы. Нужны сертификаты, актуальные AIP/NOTAM, характеристика покрытия, стоянки, категория аварийного обеспечения, противообледенительная обработка, режим работы, места экипажей и станция ТО. Объявленное строительство терминала не заменяет подтверждение его ввода и доступности именно для проекта.

Найденные планы реконструкции Минеральных Вод [S41] требуют первичной проектной и календарной проверки. Сумма реконструкции аэропорта не равна сумме вложений Red Wings в базу.

## G. Матрица маршрутов, реальное предложение и спрос

### G.1. Все десять приоритетных пар из Екатеринбурга уже присутствуют в опубликованном расписании

Источник расписания — S19; компоновка 100 кресел — S12. Для сопоставления выбрана **одна календарная неделя 30.11–06.12.2026**. Частоты получены развёртыванием дней недели внутри указанных интервалов; результат ручного чтения независимо проверен программным календарным подсчётом по HTML. Это расчёт опубликованного предложения, статус estimated_with_method, **не подтверждение выполнения будущих рейсов**.

Во всех строках перевозчик — Red Wings, опубликованный тип — RRJ-95B. Кресла рассчитаны только в направлении **из SVX** как частота × 100. Это расчёт ёмкости по заявленной компоновке; фактическая замена борта, отмена и обратные плечи в него не включены. Наблюдаемая загрузка и пассажиры по этим парам не найдены.

| Маршрут | Фактические пассажиры пары | Рейсов из SVX в выбранную неделю | Расчётное предложение, кресел из SVX | Номер рейса | Тариф | Источник и локатор | Ограничение |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| SVX–OMS, Омск | Не получены | 2 | 200 | WZ-5071 | От 5 830 руб. в витрине S22 | S19, OMS; S12; S22 | Витринная цена не средний тариф и не привязана к выбранной неделе |
| SVX–UFA, Уфа | Не получены | 4 | 400 | WZ-1025 | От 4 000 руб. в S22 | S19, UFA; S12; S22 | Нельзя переносить частоту на весь год |
| SVX–GSV, Саратов | Не получены | 2 | 200 | WZ-5047 | От 4 800 руб. в S22 | S19, GSV; S20; S12; S22 | Частота отличается от плановой строки субсидии |
| SVX–SGC, Сургут | Не получены | 2 | 200 | WZ-1017 | От 5 930 руб. в S22 | S19, SGC; S12; S22 | Витрина и фактическая продажа различаются |
| SVX–GOJ, Нижний Новгород | Не получены | 4 | 400 | WZ-5029 | Не получен | S19, GOJ; S12 | Дополнительные четверги в ноябре лежат вне выбранной недели |
| SVX–REN, Оренбург | Не получены | 4 | 400 | WZ-5049 | Не получен | S19, REN; S12 | В ноябре есть отдельная строка WZ-901; её не учитывать в этой неделе |
| SVX–BAX, Барнаул | Не получены | 4 | 400 | WZ-4503 и WZ-5075 | Не получен | S19, BAX; S12 | Включён разовый WZ-4503 в понедельник 30.11; обычных WZ-5075 — три |
| SVX–KZN, Казань | Не получены | 7 | 700 | WZ-1067 | Не получен | S19, KZN; S12 | Время и интервалы различаются по дням |
| SVX–KEJ, Кемерово | Не получены | 1 | 100 | WZ-5041 | Не получен | S19, KEJ; S12 | Во вторник 01.12 действует строка 01–07.12; нельзя добавить уже завершённый ноябрьский понедельник |
| SVX–ABA, Абакан | Не получены | 1 | 100 | WZ-5015 | Не получен | S19, ABA; S12 | В выбранную неделю действует четверг 03.12; понедельник 30.11 не покрыт интервалом |

Даты и дни в этой таблице не являются предлагаемой сетью проекта. Они показывают действующую исходную программу, с которой нужно сравнивать прирост.

### G.2. Точные строки для проверки времени и сезонности

Время указано **местное для каждого города**, как в расписании. «+1» означает следующие календарные сутки в пункте назначения. Полные наборы интервалов сохраняются в источнике; ниже — строки, позволяющие воспроизвести календарь выбранной недели. Часовой пояс аэропорта должен стать отдельным полем будущей таблицы; ICAO для большинства этих пунктов в проверенном расписании не раскрыт и не дописан догадкой.

| Назначение | Рейс | Вылет / прилёт | Дни | Период действия строки | Локатор |
| --- | --- | --- | --- | --- | --- |
| Омск OMS | WZ-5071 | 21:20 / 00:00 +1 | вт, пт | 27.10–18.12.2026 | S19, OMS |
| Уфа UFA | WZ-1025 | 22:30 / 23:45 | вт, чт, пт, вс | 01–20.12.2026 | S19, UFA |
| Саратов GSV | WZ-5047 | 18:25 / 19:30; 07:45 / 08:55 | ср; пт | 28.10–16.12; 30.10–25.12.2026 | S19, GSV |
| Сургут SGC | WZ-1017 | 12:40 / 14:25; 13:50 / 15:30 | ср; пт | 28.10.2026–24.03.2027; 30.10.2026–26.03.2027 | S19, SGC |
| Нижний Новгород GOJ | WZ-5029 | 08:35 / 08:40; 07:35 / 07:40; 08:40 / 08:40; 07:00 / 07:00 | пн; ср; пт; вс | до 21.12; 23.12; 25.12; 20.12.2026 соответственно | S19, GOJ |
| Оренбург REN | WZ-5049 | 16:00 / 17:35; 07:25 / 09:00; 19:35 / 21:10; 16:30 / 18:05 | пн; ср; пт; вс | 26.10–22.03; 28.10–24.03; 27.11–26.03; 06–20.12 | S19, REN; первые три переходят в 2027 |
| Барнаул BAX | WZ-4503; WZ-5075 | 22:50 / 03:20 +1; 23:35 / 04:00 +1 | пн; вт, чт, вс | только 30.11; 01–27.12.2026 | S19, BAX |
| Казань KZN | WZ-1067 | 11:00 / 10:45; 08:30 / 08:10; 22:25 / 22:05 | пн; чт, сб; вт, ср, пт, вс | 16.11–07.12; 29.10–26.12; 24.11–27.12.2026 | S19, KZN |
| Кемерово KEJ | WZ-5041 | 00:55 / 05:30 | пн, вт | 01–07.12.2026 | S19, KEJ |
| Абакан ABA | WZ-5015 | 02:00 / 06:55 | пн, чт | 03.12.2026–22.03.2027 | S19, ABA |

Контроль обратного плеча: в S20 присутствует GSV–SVX, WZ-5048, с указанием RRJ-95LR. Это расхождение детализации модификации с RRJ-95B в S19; нельзя автоматически создавать два разных физических самолёта или считать смену типа доказанной без бортового расписания. В S21 обратный OMS–SVX указан в омские среду/субботу: вылет после полуночи согласуется с вылетом из Екатеринбурга во вторник/пятницу.

### G.3. Альтернативный узел Омск: измеренный маршрутный поток и конкурентное предложение

Пассажиры — **2025 год из S23**, частоты — **опубликованное расписание на указанную неделю 2026 года из S21**. Разные годы не соединяются в расчёт фактической загрузки. Годовые значения маршрутов полностью приведены в O037–O046; ниже выделены пары, для которых найдено полезное расписание.

| Маршрут из Омска | Пассажиры направления в 2025 | Предложение на 30.11–06.12.2026 | Перевозчик / рейсы | Источник | Чего это не доказывает |
| --- | ---: | --- | --- | --- | --- |
| Новосибирск | 106 309 | 17 вылетов из OMS: 3 + 7 + 7 по трём номерам | S7; 5344, 5342, 5346; E170 | S23; S21, с. 1 | Конечный спрос без пересадок в Толмачево |
| Сургут | 29 964 | Ежедневно, 7 из OMS | ЮТэйр, 140; ATR | S23; S21, с. 1 | Что Red Wings получит весь поток или имеет такие же расходы |
| Казань | 27 510 | Два прямых вылета, ср/вс | Икар, 760; E190 | S23; S21, с. 2 | Что рейсы ЮВТ через Тобольск тоже являются беспосадочными |
| Красноярск | 23 192 | Два вылета, пн/сб | Россия, 6846; SSJ100 | S23; S21, с. 2 | Долю трансфера через Красноярск и маржу конкурента |
| Новый Уренгой | 27 762 | Три вылета из OMS: вт/чт/сб | Ямал; строки 318/918, SSJ100 | S23; S21, с. 2 | Спрос только конечной пары; часть программы многоучастковая |
| Иркутск | Не получены | Два вылета, вт/пт | S7, 6452; E170 | S21, с. 1 | Фактическую загрузку |
| Минеральные Воды | Не получены | Два вылета, вт/чт | Азимут, 6186; SSJ100 | S21, с. 2 | Рентабельность и доступную долю спроса |
| Екатеринбург | Не получены | Два вылета из OMS, ср/сб | Red Wings, 5072; SSJ100 | S21, с. 2 | Новый прирост, поскольку перевозчик уже летает |

Для этой таблицы кресла не рассчитаны: точные коммерческие компоновки всех опубликованных типов у соответствующих операторов не установлены. Средние проданные тарифы не получены. Числа частот являются вычислением календаря, а не годовым обязательством перевозчика.

### G.4. Что найдено по O&D и как оценивать отсутствующее

**Проверено:** национальная статистика и каталог открытых данных Росавиации; официальные и индексированные итоги аэропортов; релизы авиакомпаний; действующие расписания; перечни субсидируемых линий. Найдены фрагменты обслуженного маршрутного потока, но **не найдена открытая полная российская матрица конечных поездок** с пересадками, перевозчиками и тарифом. Коммерческие MIDT/GDS-выгрузки, OAG/Cirium и внутренние системы бронирования не были доступны и не обозначены как проверенные.

Допустимый порядок будущей оценки:

1. Для существующей линии собрать выполненные рейсы, фактические кресла и реальные перевезённые пассажиры за один период. Разделить прямые конечные и стыковочные поездки, если источник позволяет.
2. Для непокрытой прямой пары получить билеты/купонные цепочки через Москву и региональные узлы, сохраняя конечные пункты и направление. Если этого нет, явно строить модель, а не «восстанавливать» точное число из населения.
3. По сопоставимым линиям оценить зависимость спроса от обобщённой стоимости поездки: тариф, полное время, частота, пересадка, доступ к аэропорту. Проверить модель на маршрутах, не использованных для калибровки.
4. Раздельно оценить переключение с конкурентов, наземного транспорта, собственных рейсов и новые поездки. Сумма не должна превышать оценённый рынок без объяснения стимуляции.
5. Для хаба проверить пары входящих и исходящих рейсов по датам, минимальной стыковке, багажу, защите пересадки и наличию сквозного тарифа. Поток не равен произведению аэропортовых итогов.
6. Оставить базовый и осторожный сценарии с источником каждого предположения. При отсутствии калибровки не представлять диапазон загрузки как доверительный интервал измеренного спроса.

Общий поток «Омск–Москва» не показывает, сколько людей летят через Москву далее в конкретный регион. Умножение этого потока на произвольную долю пересадок недопустимо как наблюдение. Аналогично число кресел в расписании — верхняя граница предложения, а не доказанный спрос.

### G.5. Тарифы: какая цена найдена

В S22 показаны цены «от» без подтверждённой связки «момент поиска — дата вылета — состав тарифа — остаток мест». Они сохранены как витринные предложения. Средний доход авиакомпании от сегмента не измерен.

Для будущей выборки тарифов нужны: timestamp поиска, дата и время вылета, число пассажиров, класс и багаж, продавец, валюта, полный маршрут, прямой/стыковочный статус, обязательные сборы и правила возврата. Цена всей поездки с пересадкой не делится поровну на сегменты без правила распределения. Субсидия учитывается отдельной строкой дохода после проверки права на неё.

## H. Флот, аэропорты, экономика и субсидии

### H.1. Заявленный парк и доступность — разные сущности

S12 описывает текущую публичную витрину флота [O027–O030]. Дата её обновления не указана. Справка кейса содержит другие количества; ни одну версию нельзя автоматически принять за число исправных и свободных самолётов. Операционная база должна быть построена по конкретным бортам.

Нужная карточка борта: регистрация, модификация, коммерческие кресла, МВМ, двигатель, собственник/лизингодатель, статус лётной годности, план ТО, ограничения ресурса, базирование, назначенная программа, доступность по дням, экипажи и резерв. Значений этих полей для всего парка Red Wings в проверенных источниках нет.

Для существующего SSJ и нового SJ-100 нужны отдельные версии характеристик. Публичная дальность с продуктовой страницы — не график «полезная нагрузка — дальность», не допустимая зимняя дальность с запасным аэродромом и не разрешённая программа конкретного борта. S66 содержит одновременно брендинг SJ-100 и указание действующих операторов; без модификации его параметры нельзя механически объединить с S12.

### H.2. Поставки и сертификация

Факт сертификации двигателя сохранён в O093. Последовательность «сертификат двигателя → завершение сертификации самолёта → договор → передача → освоение → коммерческий ввод» не сокращается до одной даты.

S68 документирует прежнее ожидание поставок в 2026 году. S67 передаёт более позднее публичное заявление о второй половине 2027 года; оригинал интервью в исследовании не получен, поэтому статус вторичный. Твёрдый договор Red Wings с индивидуальным графиком, количеством и условиями передачи не найден. Упоминаемые в прессе совокупные партии для нескольких компаний не являются числом бортов Red Wings.

Для модели 2027–2028 это означает: отдельный сценарий без новых поставок до подтверждённой передачи; отдельный сценарий объявленного срока; ввод самолётов постепенно после освоения. Конкретные количества и месяцы нельзя заполнить без исходного договора или явно утверждённого допущения команды.

Рост назначенного ресурса прежних SSJ [O094] не увеличивает автоматически число доступных бортов: он не отменяет плановые ремонты, ресурс двигателей, запасные части и потребность в резерве.

### H.3. Конкретные проверенные аэропортовые ставки

Проверенные числовые ставки находятся в O076–O080. Все относятся к российским потребителям в Саратове и опубликованы **без НДС**. Основа массовых сборов — максимальная взлётная масса, а не фактическая масса рейса. Основа пассажирского сбора требует проверки исключений и правил начисления: нельзя начислять его всем прилетевшим и вылетевшим автоматически.

Сверхнормативная стоянка имеет часовую базу и зависит от сбора за взлёт–посадку. Для оценки новой базы следует отдельно узнать норму бесплатного времени, договор на длительную стоянку, стоимость места под резерв и условия размещения инженерного персонала.

В O076–O080 **нет** стоимости топлива, экипажа, обслуживания двигателя, лизинга, аэропортового комплексного разворота и полной себестоимости рейса. Сумма нескольких опубликованных сборов не является полной ценой оборота самолёта.

По Омску найдены базовый прейскурант и две поздние поправки [S49–S51]. Наличие прямых PDF подтверждено, однако таблицы ставок не прошли чтение и сверку; числовые цены по ним не внесены. Это конкретный приоритет извлечения, а не отсутствующий источник.

### H.4. Что нужно для полной экономики рейса и базы

| Компонент | Проверенный источник / состояние | Единица будущей модели | Допустимый метод до получения договора |
| --- | --- | --- | --- |
| Аэропортовые массовые и пассажирские сборы | Частично проверены S48; пакет Омска найден S49–S51 | Руб./т МВМ, руб./пассажира, руб./час, руб./операцию | Строки прейскуранта с категорией рейса, датой, налогами и скидкой |
| Наземное обслуживание | Каталоги найдены; полный перечень услуг не собран | Руб./разворот и отдельные операции | Применять только реально включённые услуги; избежать двойного начисления |
| Топливо и заправка | Цена топлива и фактический расход SSJ по участкам не получены | Кг или т × руб./т; заправка отдельно | Запросить цену с доставкой/хранением/заправкой и расход по профилю рейса |
| Аэронавигация | S55 содержит старый приказ; S56 указывает замену, ставки не сверены | По категории пользователя, МВМ и расстоянию | Получить актуальные приложения и расчёт применимого маршрута |
| ТОиР и двигатели | Ресурсный релиз S65; затратные договоры не получены | Руб./час, руб./цикл, календарные затраты | Разделить планер, двигатель, компоненты, резерв и капитальные события |
| Лизинг и страхование | Договоры Red Wings не получены | Руб./борт-месяц и прочие платежи | Отдельный сценарный параметр с владельцем допущения |
| Экипажи | План и ставки не получены | Борт-месяц, рабочие часы, командировки | Рассчитать график и нормы с данными оператора; не переносить иностранную зарплату |
| Перегоны и резерв | Зависит от маршрутизации и расписания | Часы/циклы без коммерческого пассажира | Сначала расписание оборотов, затем стоимость пустых участков |
| Дистрибуция и продажи | Ставки не получены | Процент дохода, руб./билет, руб./транзакцию | Разнести прямые продажи, агентов, эквайринг, возвраты |
| Задержки и отмены | История нерегулярности и расходы не получены | Руб./случай, час задержки, отменённый рейс | Моделировать по фактической частоте событий; не задавать произвольную «надбавку риска» |
| База и инженерная инфраструктура | Нет предложения аэропорта для Red Wings | Разовые вложения, месячные расходы, оборотный капитал | Смета: персонал, помещения, оборудование, обучение, стоянки, резерв запасных частей |
| Оборотный капитал | Данные договоров и денежных циклов не получены | Рубли и дни расчётов | Раздельно предоплаты, лизинг, топливо, сезонность продаж и задержка субсидий |

S53 и S54 дают примеры раскрытия экономики и капитальных вложений **аэропорта**. Они полезны для состава статей и проверки масштаба инфраструктуры, но их суммы не переносимы в бюджет авиакомпании. Средние иностранные эксплуатационные расходы на другой тип ВС в модель не включены.

### H.5. Регулирование и действительная применимость поддержки

Официальная карточка S44 прямо связывает предоставление субсидии с постановлением № 1780 от 25.10.2023 и решением о порядке предоставления. Старый текст S46 сохранён для истории. S47 сигнализирует утрату силы постановления № 1242, но отменяющий акт и точная дата перехода в этом проходе не извлечены. Поэтому ссылка «по 1242» без проверки решения и его редакции недостаточна для расчёта 2027 года.

В S45 обнаружены названия приказов: 899-П от 21.11.2025, 261-П от 15.05.2026, 845-П от 06.11.2025 и исторические изменения. Прямые адреса всех их оригинальных приложений не получены. Ошибка поиска по одному номеру акта может привести к документу другого ведомства или другого года.

Ниже сохранены **плановые строки официальной таблицы**, найденные в индексе; это не исполнение и не перечисленные деньги.

| Строка / маршрут | Период | Тип / кресла | Плановая частота | Парные рейсы | Софинансирование по формулировке таблицы | Источник и использование |
| --- | --- | --- | ---: | ---: | --- | --- |
| № 48, Екатеринбург–Омск, Red Wings | 01.01–30.04 и 01.10–31.12.2026 | SSJ-100 / 100 | 2 в неделю | 56 | Свердловская и Омская области по 30,5% | S45; только плановая строка |
| Дополнительная строка той же пары | 01–31.05 и 01–30.09.2026 | SSJ-100 / 100 | 2 | 18 | Области по 47,5% | S45; иной подынтервал и условия |
| № 51, Екатеринбург–Саратов, Red Wings | 01.01–30.04 и 01.10–31.12.2026 | SSJ-100 / 100 | 3 | 57 | Свердловская и Саратовская области по 30,5% | S45; не равна текущей частоте из G |
| Дополнительная строка Екатеринбург–Саратов | 01.05–30.09.2026 | SSJ-100 / 100 | 4 | 65 | Области по 47,5% | S45; есть и иная строка того же периода |
| Иная строка Екатеринбург–Саратов | 01.05–30.09.2026 | SSJ-100 / 100 | 4 | 23 | Свердловская область 95% | S45; не складывать до проверки редакции и состава |

Проценты в последнем столбце нельзя применять к выручке рейса или его полной себестоимости, пока не установлена база расчёта. Число парных рейсов по нескольким строкам не складывается автоматически: сначала надо понять, это части годового объёма, изменения условий или накопленная публикация редакций.

Чтобы признать субсидию доходом проекта, нужны: применимый порядок и версия, результат отбора, получатель и маршрут, точные периоды, ставка и лимит, софинансирование, ограничения на тарифы и категории пассажиров, условия отчётности, подтверждение выполнения, соглашение и порядок выплат. Наличие маршрута в перечне не равно праву на всю предполагаемую сумму. Подтверждённые выплаты Red Wings по перечисленным парам не найдены.

S05 называет также решения № 22-68866-00363-Р и № 22-68861-00481-Р для иных программ. Их условия и прямые документы в этом исследовании не извлечены. Результаты трёх программ нельзя отождествлять с региональным механизмом. Подтверждённый перечень победителей и ставок для проекта Red Wings на 2027 год не получен.

### H.6. Ограничения аэропортов и регулярность

Действующее расписание доказывает опубликованное предложение, а не отсутствие временных ограничений. Полного ряда закрытий, ограничений воздушного пространства, запасных посадок и отмен по кандидатам не восстановлено. Для Нижнего Новгорода есть официальный индикатор запасной нагрузки [O073]; он не измеряет стоимость задержек Red Wings.

При дальнейшей проверке нужно связывать ограничения с аэропортом, точным интервалом UTC и рейсом. Режим ограничения в один день не превращается в постоянный запрет, а отсутствие новостей о закрытии не доказывает непрерывную доступность.


## I. Подтверждённые результаты конкурентов

Сравнение ограничено измеряемыми фактами. Рост хабового трафика не доказывает окупаемость базы, а размер группы не является количеством пассажиров отдельной авиакомпании.

| Перевозчик / проект | Проверяемый результат | Источник / наблюдения | Что можно использовать | Что остаётся неизвестным |
| --- | --- | --- | --- | --- |
| S7, Новосибирск и Иркутск | Годовой поток S7 и объёмы через два узла раскрыты официальным каналом | S57; O083–O084 | Сравнить порядок масштаба и наличие нескольких узлов | Доля собственно трансфера, конечные пары и прибыльность каждого узла |
| S7, Иркутск | Аэропорт самостоятельно раскрывает пассажиров S7 за 9 месяцев 2025 | S32; O060 | Независимый от общего релиза S7 срез присутствия в конкретном аэропорту | Нельзя смешивать девять месяцев с годовыми 1,9 млн |
| Группа Аэрофлот, Красноярск | Годовой хабовый поток и состав базируемого парка в юбилейном сообщении | S58; O085–O086 | Состав проекта: не только рейсы, но и разные типы базируемых ВС | Оригинал релиза, единый охват с данными аэропорта, капитальные и операционные расходы |
| Авиакомпании в Красноярске | Аэропорт раскрывает отдельные показатели России, Аэрофлота и других перевозчиков | S31 | Сверка с юбилейным сообщением; рыночное присутствие | Порядок учёта трансфера и точное объединение перевозчиков |
| Red Wings, Екатеринбург | История запуска, результат первого года, предложенные стыковки и сквозной багаж | S15–S18; O032–O033 | Описать уже существующую инфраструктурную и продуктовую основу | Финансовый результат хаба, доля трансфера, чистый прирост пассажиров |
| Уральские авиалинии | Официальное сообщение подтверждает годовой масштаб и число рейсов в округлённой формулировке | S62; O090 | Установить существенного конкурента исходной базы | Точная доля Кольцово и маршрутная маржа из первичной отчётности |
| Азимут | Итог пассажиров и перечень базовых аэропортов в собственном журнале | S61; O089 | Релевантный оператор SSJ и сеть нескольких точек | Доходность баз, фактический резерв и условия субсидий по каждому маршруту |
| ЮТэйр | Официальные сообщения РСБУ и МСФО дают различающийся охват | S59–S60; O087–O088 | Сохранить раздельно самолётный, вертолётный и юридический периметры | Причина расхождения, затраты сопоставимого маршрута на SSJ |
| Аврора | Годовой поток, количество рейсов и занятость в подписанной перепечатке пресс-релиза | S69; O096 | Сопоставить региональную модель с оговоркой происхождения | Оригинал сообщения, отличие отдельного перевозчика от объединения партнёров |

Для будущего DR-02 эти наблюдения — точки проверки, а не готовое объяснение успеха. Нужны динамика по одинаковым периодам, доходы, расходы, доля пересадки, изменение предложения и закрытые направления. Успех одной базы не переносится на другую через одинаковый размер аэропорта.

### I.1. Екатеринбург Red Wings: что действительно установлено

S15 документирует начало региональной программы и объявление проекта хаба в 2020 году. S16 содержит результат первого года и отдельное высказывание о необходимости бюджетной поддержки направлений. S17 фиксирует расширение предложения в 2024 году. S18 прямо описывает удобные стыковки и регистрацию багажа до конечного пункта.

Этой цепочки достаточно, чтобы не трактовать Екатеринбург как новую, ещё не испытанную точку. Её недостаточно для утверждения о прибыльности или о способности без дополнительных вложений обслужить любую новую сеть. В открытом пакете не получены помаршрутные результаты и доля трансфера действующего хаба.

## J. Реестр конфликтов, дублей и сомнительных источников

| ID | Конфликт / риск | Что найдено | Как хранить и что перепроверить | Влияние на модель |
| --- | --- | --- | --- | --- |
| J01 | Опорные аэропорты в кейсе неполны | Справка S01 выделяет Москву и Екатеринбург; S10 и S11 дают более широкий сезонный перечень | Версии по сезонам; термин издателя отдельным полем | Иначе существующая точка ошибочно становится «новым хабом» |
| J02 | Лето и зима Red Wings различаются | Минеральные Воды присутствуют в S10, отсутствуют в перечне S11 | Не выводить прекращение базы из отсутствия названия; проверить операционное базирование | Меняется исходный ресурс и выбор контрфактической программы |
| J03 | Устаревшее руководство | S01 указывает Ивлиева; S13 сообщает назначение Чуева и предшествующий статус и.о. | Для актуальной справки использовать датированный официальный релиз | Исправляет контекст; не определяет экономику сети |
| J04 | Количество самолётов | S01 и текущая витрина S12 расходятся | Сохранить обе версии; запросить бортовой список и дату актуальности | Нельзя объявить арифметическую сумму парка свободным ресурсом |
| J05 | SSJ и SJ-100 смешиваются в брендинге | S12, S64–S66 описывают разные признаки и этапы | Модификация, двигатель и сертификат — самостоятельные поля | Влияет на кресла, дальность, ремонт и сроки ввода |
| J06 | Сертификат двигателя принимают за сертификат самолёта | S64 подтверждает ПД-8; S67 описывает последующую сертификацию самолёта как план | Раздельные события | Иначе доступность новых бортов появляется раньше действительности |
| J07 | Меняющиеся сроки поставки | Официальное старое ожидание S68 и поздний вторичный план S67 | Дата заявления, автор, стадия, плановая дата и статус | Существенный риск окупаемости и запуска |
| J08 | Ранние и поздние итоги 2024 | Ранний официальный пересказ: 111,6 млн; S71: 111,7 млн | Поздний итог основной; ранний сохранить как версию | Небольшой эффект на долю, существенный для воспроизводимости |
| J09 | Показатель рынка 2025 в справке округлён | S01: 108,9 млн; S03: 108,85 млн | Не создавать новое независимое наблюдение | Разная точность знаменателя |
| J10 | «На российских самолётах» заменяет внутренний поток | S08 делит парк и чартеры, а не публикует чистый внутренний числитель | Отдельные измерения типа ВС и географии | Иначе доля внутреннего рынка неверна |
| J11 | Числа инфографики кейса противоречат тексту | В S01 инфографика содержит рост +7% за 2025 и +3% за 2026 и сравнительные значения без методики | Не использовать как наблюдения или готовый результат модели | Риск построить всю стратегию на иллюстративной синтетике |
| J12 | Старый нормативный акт объявляют действующим | S46 — старая редакция; S47 — отметка утраты силы; S44 — иной порядок | Получить отменяющий акт, текущую версию решения и порядок 2027 | До этого субсидия проекта не подтверждена |
| J13 | Одинаковые пары несколько раз в перечне | S45 содержит несколько периодов и условий софинансирования | Сохранять номер строки/подстроки, редакцию и интервалы; не удалять по одной паре | Иначе сумма рейсов и поддержки задваивается |
| J14 | Субсидируемая частота отличается от расписания | G показывает фактический календарь объявления; H.5 — плановую таблицу | Разные метрики и дата версии, не выбирать удобную | Нельзя считать доход от субсидии по всему проданному расписанию |
| J15 | Барнаул: 790 тыс. против 792,6 тыс. | Ранняя пресса округляет; S30 даёт официальный территориальный итог | Основной — S30; точность исходных публикаций сохранить | Не усреднять и не считать двумя независимыми потоками |
| J16 | Красноярск: сумма двух компонентов не равна итогу | O057–O058: остаток 55 355 пассажиров | Не называть остаток транзитом без подтверждения определения | Влияет на структуру потока, не на опубликованный итог |
| J17 | Красноярский хаб: разные охваты источников | Юбилейное S58 даёт округлённый хабовый итог; S31 — потоки отдельных авиакомпаний | Сверить включение Победы, аэропортовый учёт и округление | Не считать прибыльность или долю из несовместимых рядов |
| J18 | S7: потоки трёх хабов не складываются в уникальных людей | S57 раскрывает узлы внутри одной сети | Проверить повторный учёт поездок между узлами | Нельзя выводить трансфер как остаток |
| J19 | ЮТэйр: РСБУ и МСФО расходятся | O087–O088 | Юридический периметр, партнёры, округление и методику проверить по полным отчётам | Не смешивать общий рынок, самолётный и вертолётный сегменты |
| J20 | Самарский релиз назван «новогодние праздники» | Основной текст S36 — годовые итоги 2025 | В поле периода использовать содержимое, не заголовок | Иначе ошибка периода на порядок |
| J21 | В омском PDF есть подозрительная дата | S21, физическая с. 3: строка рейса в Шарм-эль-Шейх содержит 09.12.25 внутри сезона 2026/27 | Сохранить raw_date; не исправлять без сверки расписания перевозчика | Ошибка года при развёртывании календаря |
| J22 | Тип самолёта одного плеча различается в детализации | S19: RRJ-95B, S20 для обратного плеча: RRJ-95LR | Нормализовать семейство, исходную модификацию сохранить | Нельзя молча приписать конкретный борт/дальность |
| J23 | Карта направлений не равна расписанию | S21 landing содержит длинный общий список городов, включая отсутствующие в выбранной неделе | Подтверждать рейс по датированной строке PDF | Иначе появятся несуществующие на период частоты |
| J24 | Агрегаторы и похожие домены | В поиске появились redwingsair.com и историческая omskavia.ru | Не использованы как официальный сайт Red Wings / Омского аэропорта | Защита от подмены издателя |
| J25 | Чужой документ с тем же номером | Поиск «261-П» вернул также приказ другого дня/года; «899» — иные акты | Ключ: издатель + вид + дата + номер, а не один номер | Иначе ложное нормативное основание |
| J26 | Тарифы для иностранного эксплуатанта | Найден такой PDF Курумоч; он не включён как применимая ставка Red Wings | Категория потребителя и валюта обязательны | Иначе ошибка суммы и налогообложения |
| J27 | Поисковая дата не равна дате документа | Старые PDF могут иметь недавнюю индексацию | Дата с титульного листа/текста; crawl_date отдельно | Исключает перенос данных 2020/2021 в 2026 |
| J28 | Первичные финансы не получены | S63 — вторичная карточка; точные рубли не подтверждены отчётом ФНС | Оригинал формы и пояснения обязательны | Нельзя из общей выручки вывести тариф новой региональной линии |
| J29 | Один релиз перепечатан многократно | Омские числа встречаются в СМИ; оригинал найден в S23 | Один документ/наблюдение, перепечатки — связи копирования | Число публикаций не усиливает независимость доказательства |
| J30 | Скачанный файл может быть заменён по тому же URL | Большинство сайтов используют изменяемые пути | Сохранять байты, дату и хеш после выгрузки; в этом отчёте хеш установлен только для S48 | Без версии результат нельзя точно воспроизвести |

Проверочная ранняя публикация для J08: landing_url = https://www.favt.gov.ru/novosti-rossii/?id=14334 ; direct_url = https://www.favt.gov.ru/novosti-rossii/?id=14334 ; тип embedded_html; дата 22.01.2025; локатор — первые два абзаца о годовом потоке. Это альтернативная версия национального наблюдения, а не дополнительный годовой объём.

Проверочная ранняя публикация для J15: landing_url = https://www.kommersant.ru/doc/8338904 ; direct_url = https://www.kommersant.ru/doc/8338904 ; тип embedded_html; дата 11.01.2026; локатор — первый абзац. В основной реестр количественных наблюдений взят официальный итог S30.

## K. Приоритизированный список дальнейшего сбора данных

Приоритет отражает способность изменить выбор между гипотезами. Срок в кейсе — 10 ноября 2026 года, 23:59 [S01]. Таблица задаёт порядок работы до сдачи; она не утверждает, что все закрытые данные будут получены к этому сроку.

| Приоритет | Нужный показатель | Конкретно проверенные источники | Что найдено и почему мало | Следующий доступный путь / метод | Влияние неопределённости |
| --- | --- | --- | --- | --- | --- |
| P0-1 | Конечный O&D и пересадки для 8–12 будущих пар | S02–S04, S19–S25, S30–S40 | Общие и отдельные маршрутные итоги; нет полной цепочки конечной поездки | Запросить у организаторов/оператора обезличенные конечные пары с купонами; при отсутствии — калиброванная модель на аналогах | Может полностью изменить выигрыш хаба |
| P0-2 | Базовое предложение и факт выполнения на этих парах | S19–S21; исторические S17, S25 | Текущие интервалы и частоты, но не годовой ряд выполненных рейсов | Развернуть календарь, получить статистику выполнения, отмен и бортовых замен | Иначе весь существующий поток записывается в прирост |
| P0-3 | Средний доход за сегмент и распределение сквозного тарифа | S08, S22, S63 | Реклама «от» и общая выручка | Билетные продажи или маршрутная управленческая отчётность; отдельный учёт сборов, допуслуг, субсидий | Может поменять знак вклада маршрута |
| P0-4 | Стоимость блока рейса SSJ и двигателя | S48–S56, S64–S66 | Часть аэропортовых ставок и технический ресурс; нет расходного профиля | Данные оператора по блок-часам, циклам, топливу, ТО, лизингу, экипажам | Прямо определяет безубыточную загрузку |
| P0-5 | Реально свободный парк и даты ввода новых ВС | S12, S64–S68 | Публичные количества, сертификат двигателя, меняющиеся планы | Бортовой план, подписанные договоры, ТО и экипажи по месяцам | Может сделать оба варианта неосуществимыми |
| P0-6 | Официальные условия и право на субсидию 2027 | S44–S47, S05 | Перечень 2026 и версия решения; нет будущего соглашения проекта | Получить текущую редакцию, отбор, ставки, лимиты и региональные обязательства | Существенно меняет выручку и денежный разрыв |
| P1-1 | Смета новой базы по финалистам | S48–S54 | Публичные сборы и аэропортовые формы | Адресное коммерческое предложение аэропорта: стоянка, ТО, помещения, персонал, запуск | Определяет капитальные вложения и окупаемость |
| P1-2 | Единая годовая и месячная статистика аэропортов | S23–S41 | Разная точность и периоды; неполный 2026 | Получить выгрузки формы 15-ГА/первичные аэропортовые отчёты с определениями | Влияет на рейтинг и сезонность |
| P1-3 | Население города/агломерации, доходы, туризм | S38, S42–S43 | Исторические крупные города; отдельный туристический прокси | Скачать актуальный муниципальный XLSX; задать границы охвата и единую методику агломерации | Влияет на прокси спроса; не заменяет O&D |
| P1-4 | Сертификаты, стоянки и ограничения аэропортов | S52; каталоги S48–S53 | Омск проверен частично; по остальным нет сопоставимой матрицы | Актуальные AIP/NOTAM, сертификаты и подтверждение слотов/ТО | Может исключить технически неподходящий вариант |
| P1-5 | Первичная финансовая отчётность Red Wings | S63 | Только вторичная карточка | ГИР БО по ИНН 7732107883; форма результатов, движение денег, пояснения | Проверка финансовых ограничений, не замена маршрутной экономики |
| P2-1 | Причины результата конкурентов | S31–S33, S57–S62, S69 | Пассажиры и предложение; мало затрат и причинных сравнений | Продолжить в DR-02: единые периоды, трансфер, расходы и закрытые линии | Помогает интерпретировать переносимость стратегии |
| P2-2 | Достоверные архивные копии | Все значимые источники | Проверенных независимых архивных URL нет | Найти реальные архивные снимки; сохранить исходные байты с хешами | Защищает воспроизводимость, не изменяет сам спрос |

### K.1. Минимальный пакет, с которым допустимо строить сценарии

По каждому выбранному маршруту должна быть одна карточка: исходное предложение; наблюдение либо воспроизводимый метод спроса; тариф и его тип; календарная программа; кресла; стоимость; применимая поддержка; источник и версия каждого входа. Отсутствующие величины становятся явно именованными допущениями с базовым и осторожным значением. Сценарные числа не переносятся обратно в фактический слой.

Для флота нужен реализуемый календарь оборотов с резервом, а не только деление годовых часов на абстрактный норматив. Для хаба — расписание стыковок и оценка конечных пар. Для прямой сети — включённые перегоны, возврат в место обслуживания и замещение существующей программы. Для обеих гипотез — единое определение добавленного пассажира и одинаковый прогноз знаменателя рынка.

## L. Передача инженерам: схема данных и воспроизводимость

Ниже предложены будущие таблицы. Это **описание схемы**, не созданные CSV/Parquet или программные файлы. Имена полей — технические идентификаторы; смысл и правила приведены по-русски.

### L.1. Справочники и ключи

| Таблица | Гранулярность / первичный ключ | Обязательные поля | Связи и ограничения |
| --- | --- | --- | --- |
| source_document | Один оригинальный документ или публикация, document_id | publisher_id, title, landing_url, direct_url, format, publication_date, date_precision, document_number, legal_effective_from/to, source_role | document_number уникален только вместе с издателем, датой и видом; зеркала связаны с оригиналом |
| source_version | Один полученный набор байтов/состояние страницы, source_version_id | document_id, fetched_at_utc, sha256, content_type, bytes, access_status, extraction_status, archive_url, archive_captured_at | document_id → source_document; неполученные хеши NULL, не фиктивная строка |
| observation | Одна метрика одного объекта и периода, observation_id | source_version_id, object_type/id, metric_id, value_raw, value_numeric, unit_id, period_start/end, period_kind, geography_id, locator, method, verification_status, permitted_use, limitations | NULL отличается от нуля; значение «более» хранит relation/operator; сырой текст обязателен |
| metric_definition | Одно определение, metric_id | name_ru, unit, numerator, denominator, population, counting_rule, directionality, accounting_basis, definition_source | «Пассажир аэропорта» и «пассажир перевозчика» — разные метрики |
| airport | Один аэропорт, airport_id | name_ru, city_id, IATA, ICAO, valid_from/to, timezone, operator_id | Коды могут меняться; город и аэропорт не один объект |
| city_geography | Территория в определённых границах, geography_id | city_name, boundary_type, municipal_code, boundary_version, population_date, area_definition | Город, округ, агломерация и зона охвата раздельны |
| airline | Один юридический перевозчик, airline_id | name, legal_id, IATA/ICAO, group_id, ownership_valid_from/to | Группа не подменяет авиакомпанию; не суммировать холдинг и дочернюю компанию |
| aircraft_variant | Одна модификация, variant_id | manufacturer, model, engine, MTOW_t, seats_config_id, performance_source, certificate_scope | SSJ с SaM146 и SJ-100 с ПД-8 раздельно |
| aircraft_tail_availability | Один борт-день или борт-месяц | tail_id, date/period, variant_id, seats, airworthy_status, maintenance, base_airport_id, allocated_program, reserve_status, crew_constraint | План поставки и фактическая доступность имеют разные поля и статусы |

### L.2. Спрос, предложение, экономика

| Таблица | Гранулярность / ключ | Основные поля | Ключевые проверки |
| --- | --- | --- | --- |
| airport_traffic | Аэропорт × период × измерение | airport_id, domestic/international, regularity, arrivals/departures, transit_rule, passengers, movements, source_version_id | Не смешивать вылеты, взлётно-посадочные операции и обороты |
| airline_traffic | Перевозчик/группа × период × сегмент | airline_id/group_id, scope, passengers, RPK, ASK, seat_factor, regularity, source_version_id | Одинаковая география и отчётный периметр перед сравнением долей |
| route_segment_traffic | Направленная пара аэропортов × перевозчик × период | origin_airport_id, destination_airport_id, passengers, directions_included, transfer_included, regularity, source_version_id | Если направление суммирования неизвестно, не делить на два |
| od_itinerary_traffic | Конечные пункты × путь × период | true_origin/destination, connecting_airports, operating_carriers, itinerary_passengers, journey_type, fare_scope | Конечная поездка отдельно от полётного сегмента; без персональных данных |
| schedule_rule | Одна исходная строка расписания, schedule_rule_id | source_version_id, origin/destination, carrier, flight_number_raw, equipment_raw, weekdays, start/end, local_times, arrival_day_offset, exceptions | Пересечения интервалов и разовые рейсы; сырой год не исправлять молча |
| scheduled_departure | Конкретный запланированный вылет | operating_carrier, flight_no, origin, departure_datetime_utc, destination, equipment, seats, schedule_rule_id | Устранить коды совместной эксплуатации; один физический вылет не несколько рейсов |
| operated_departure | Конкретный выполненный/отменённый рейс | scheduled_departure_id, actual_times, status, tail_id, flown_seats, carried_passengers | Отмена не превращается в рейс с нулевой загрузкой без отдельного статуса |
| fare_quote | Одно предложение билета на момент поиска | searched_at, travel_dates, itinerary, passenger_count, seller, fare_family, baggage, price, currency, taxes, refundability | «От» отделено от конкретного предложения и реального среднего дохода |
| segment_revenue | Маршрут × период × вид дохода | passenger_revenue, ancillaries, carrier_surcharges, pass_through_taxes, subsidy, allocation_method | Не складывать цену всей поездки и цену включённых сегментов |
| airport_tariff | Одна ставка × срок × категория | airport_id, service, value, unit, payer_category, domestic/international, VAT_rule, valid_from/to, basis, exclusions | МВМ против фактической массы, час против суток, пассажир против рейса |
| flight_cost_parameter | Параметр типа/контракта × период | fuel_price, fuel_unit, block_fuel, cycle_cost, flight_hour_cost, lease_cost, crew_cost, currency, cost_scope | Не двойной учёт затрат, включённых в комплексную ставку |
| base_cost | Одна статья базы × период × вариант | airport_id, scenario_id, item, capex/opex/working_capital, quantity, unit_cost, payment_schedule | Аэропортовые инвестиции отделить от обязательств Red Wings |
| subsidy_route_condition | Получатель × пара × подынтервал × редакция | decision_version, selection_id, carrier, route, equipment, seats, frequency, paired_flights, rate, rate_basis, cofinancing, ceiling | План, право, начисление и выплата — разные состояния |
| scenario_assumption | Один сценарный вход | assumption_id, owner, name_ru, base/cautious, value, unit, justification, sensitivity, approved_at | Нельзя использовать status verified_primary для допущения |
| model_result | Один результат сценария × период | result_id, scenario_id, metric_id, value, model_version, input_set_id | Не хранить результат как исходное измерение |
| lineage_edge | Одна зависимость | parent_id, child_id, transform_id, code_version, parameters, aggregation_rule | Для каждого результата восстанавливаются все наблюдения и допущения |

### L.3. Нормализация и запреты автоматического преобразования

- **Периоды.** Хранить календарный год, накопленный период, сезон, произвольный интервал и дату среза как разные period_kind. Девять месяцев не дополняются до года умножением без отдельной оценочной модели.
- **Единицы.** Исходную запись сохранять; тыс. и млн переводить в базовую единицу только с явным коэффициентом. Денежные ряды имеют валюту, налоги и дату цены.
- **География.** «Москва» в аэропортовом релизе может объединять несколько аэропортов. Не подставлять один аэропорт без подтверждения. Международный O&D не определяется по гражданству пассажира.
- **Направления.** Для опубликованных «Омск–город» неизвестное включение двух направлений сохраняется как unknown. Обратный полёт — отдельный физический рейс.
- **Календарь.** Локальное время переводить в UTC с зоной каждого аэропорта и arrival_day_offset. Число рейсов в неделю считать по конкретным датам, включая исключения.
- **Совместная эксплуатация.** Хранить продающего и выполняющего перевозчика. Несколько кодов одного физического вылета не создают несколько наборов кресел.
- **Пассажиры и кресла.** seats × departures — предложение. passengers / seats допустимо только при одинаковых периодах, направлении и фактически выполненной программе.
- **Стыковки.** Для хаба считать реализуемые пары сегментов по датам и условиям пересадки. Ограничивать общий поток вместимостью каждого плеча и не учитывать одну конечную поездку несколько раз внутри O&D.
- **Субсидии.** Обязательны документ, редакция, получатель и период. Поле allocated_budget не заменяет paid_subsidy.
- **Неизвестные поля.** NULL с reason_code. Значения not_found и unavailable — состояния происхождения/доступа, а не числовые нули.
- **Дубли.** Выделить document_family и copied_from. Перепечатки и языковые версии сайта не независимы.
- **Конфликты.** Хранить observation_revision и conflict_id. Ни среднее нескольких версий, ни выбор наибольшего значения не являются правилом разрешения.

### L.4. Проверки при последующей загрузке

1. Проверить внешние ключи, единицы, границы периодов и уникальность физического вылета.
2. Сверить суммы компонентов с итогом только если определения допускают сложение. Неизвестный остаток не подписывать «транзит».
3. Сверить версии источника с датой факта: поздняя индексация не обновляет историческую таблицу.
4. Проверить календарные частоты на выбранных неделях и переходе года; отдельные даты из S21 вынести на ручную сверку.
5. Запретить model_result и scenario_assumption в фактическом слое без соответствующего статуса.
6. Проверить прирост компании относительно её исходной программы: существующий собственный пассажир не становится новым автоматически.
7. Для каждого вывода о доле рынка проверить числитель, знаменатель, географию, период и отчётный периметр.
8. Проверить экономику на двойной учёт аэропортовых услуг, налогов и выплат.
9. Перед расчётом 2027 года обновить правовые редакции и фактический статус поставок.

## M. Полный список источников и маршрут проверки

Все зарегистрированные объекты перечислены ниже повторно с явными полями URL. Детальная доступность, локатор и назначение находятся в B. Количество записей не является количеством независимых доказательств: внутри есть каталоги, исторические версии и перепечатки.

### S01. Кейс 5. Red Wings — Новый хаб или прямые рейсы?

- Издатель: Материалы кейс-чемпионата в рабочем репозитории.
- Период: 2027–2028. Дата: не установлена.
- landing_url: https://github.com/We-seek-D-p/case-championship-26/blob/rewrite/задание/5%20кейс.md
- direct_url: https://api.github.com/repos/We-seek-D-p/case-championship-26/contents/задание/5%20кейс.md?ref=rewrite
- direct_type: api. archive_url: not_found.
- Локатор: §§ 6–9; инфографика.
- Доступность: прочитан через авторизованный доступ; ветка изменяемая. Статус: verified_primary.

### S02. Статистические данные: аналитическая таблица формы № 12-ГА

- Издатель: Росавиация.
- Период: 2023–2024. Дата: срез 27.01.2025.
- landing_url: https://www.favt.gov.ru/dejatelnost-vozdushnye-perevozki-stat-dannie/?from=old-site
- direct_url: https://www.favt.gov.ru/dejatelnost-vozdushnye-perevozki-stat-dannie/?from=old-site
- direct_type: embedded_html. archive_url: not_found.
- Локатор: «ВСЕ ПРЕДПРИЯТИЯ»; строки пассажиров, пассажирооборота и занятости.
- Доступность: найдено в индексе; прямое чтение — тайм-аут. Статус: unverified.

### S03. Российские авиакомпании перевезли в 2025 году почти 109 млн пассажиров

- Издатель: Росавиация.
- Период: 2025. Дата: 30.01.2026.
- landing_url: https://favt.gov.ru/novosti-novosti/?id=17763
- direct_url: https://favt.gov.ru/novosti-novosti/?id=17763
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы 1–3 основного сообщения.
- Доступность: текст найден в индексе; прямое чтение — тайм-аут. Статус: verified_primary.

### S04. Реестр открытых данных

- Издатель: Росавиация.
- Период: исторические ряды; свежесть не установлена. Дата: не установлена.
- landing_url: https://www.favt.gov.ru/opendata/
- direct_url: not_found
- direct_type: csv_catalog. archive_url: not_found.
- Локатор: наборы № 5, 7, 10.
- Доступность: каталог виден в индексе; файлы не получены. Статус: unverified.

### S05. Доклад о результатах деятельности за 2025 год, целях на 2026 год и плановом периоде до 2028 года

- Издатель: Минтранс России.
- Период: 2025; планы до 2028. Дата: 2026; точная дата не установлена.
- landing_url: https://mintrans.gov.ru/file/557797
- direct_url: https://mintrans.gov.ru/file/557797
- direct_type: pdf. archive_url: not_found.
- Локатор: физическая страница 5, раздел о воздушном транспорте.
- Доступность: PDF прочитан; 42 страницы; карточка публикации отдельно не найдена. Статус: verified_primary.

### S06. Расширение географии полетов — приоритет российских авиаперевозок

- Издатель: Минтранс России.
- Период: 2025. Дата: точная дата не установлена.
- landing_url: https://mintrans.gov.ru/press-center/news/12560
- direct_url: https://mintrans.gov.ru/press-center/news/12560
- direct_type: embedded_html. archive_url: not_found.
- Локатор: последний абзац о 54,4%.
- Доступность: текст в индексе. Статус: verified_primary.

### S07. Дмитрий Ядров доложил главе Правительства о работе авиационной отрасли

- Издатель: Росавиация.
- Период: май–август 2026. Дата: 29.09.2026.
- landing_url: https://www.favt.gov.ru/novosti-novosti/?id=19636
- direct_url: https://www.favt.gov.ru/novosti-novosti/?id=19636
- direct_type: embedded_html. archive_url: not_found.
- Локатор: «Итоги работы авиакомпаний»; «Итоги работы аэропортов».
- Доступность: текст в индексе. Статус: verified_primary.

### S08. Red Wings перевезла за год на российских самолетах 2 млн пассажиров и 2 совы

- Издатель: Red Wings.
- Период: 2025. Дата: 28.01.2026.
- landing_url: https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/
- direct_url: https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы о 24 тыс. рейсов, 2,7 млн пассажиров, 25 новых линиях.
- Доступность: текст в индексе; страница на /en/ содержит русский текст. Статус: verified_primary.

### S09. Российская авиакомпания Red Wings отмечает свой юбилей — 25 лет деятельности

- Издатель: Red Wings.
- Период: 2023; парк на дату релиза. Дата: точная дата не установлена.
- landing_url: https://flyredwings.com/en/press/news/rossijskaya-aviakompaniya-red-wings-otmechaet-svoj-yubilej-25-let-deyatelnosti/
- direct_url: https://flyredwings.com/en/press/news/rossijskaya-aviakompaniya-red-wings-otmechaet-svoj-yubilej-25-let-deyatelnosti/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзац о 2,66 млн пассажиров и 19 SSJ.
- Доступность: текст в индексе. Статус: verified_primary.

### S10. Red Wings перешла на летнее расписание полетов

- Издатель: Red Wings.
- Период: лето 2026. Дата: 31.03.2026.
- landing_url: https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/
- direct_url: https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые абзацы: 118 направлений и восемь городов.
- Доступность: текст в индексе. Статус: verified_primary.

### S11. Red Wings перешла на осенне-зимнее расписание полетов

- Издатель: Red Wings.
- Период: зима 2026/27. Дата: 27.10.2026.
- landing_url: https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/
- direct_url: https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: основной текст, строки извлечения 111–118.
- Доступность: страница прочитана. Статус: verified_primary.

### S12. Парк самолётов

- Издатель: Red Wings.
- Период: страница на дату проверки. Дата: не указана.
- landing_url: https://flyredwings.com/about/park/
- direct_url: https://flyredwings.com/about/park/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: блоки SSJ100, Ту-214, Boeing 777-200ER, Ту-204-100B; строки 115–218.
- Доступность: страница прочитана; нет даты актуализации. Статус: verified_primary.

### S13. Роман Чуев стал генеральным директором Red Wings

- Издатель: Red Wings.
- Период: назначение 2026. Дата: 30.10.2026.
- landing_url: https://flyredwings.com/en/press/news/roman-chuev-stal-generalnym-direktorom-red-wings/
- direct_url: https://flyredwings.com/en/press/news/roman-chuev-stal-generalnym-direktorom-red-wings/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые три абзаца.
- Доступность: текст в индексе. Статус: verified_primary.

### S14. Red Wings открыла программу полетов в Израиль на летний сезон 2027 года

- Издатель: Red Wings.
- Период: 28.03–24.10.2027. Дата: 03.11.2026.
- landing_url: https://flyredwings.com/press/news/red-wings-otkryla-programmu-poletov-v-izrail-na-letny-sezon-2027-goda/
- direct_url: https://flyredwings.com/press/news/red-wings-otkryla-programmu-poletov-v-izrail-na-letny-sezon-2027-goda/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые два абзаца.
- Доступность: текст в индексе. Статус: verified_primary.

### S15. Red Wings создаст транзитный хаб в Екатеринбурге

- Издатель: Red Wings.
- Период: 2020. Дата: 13.10.2020.
- landing_url: https://flyredwings.com/press/news/red-wings-sozdast-tranzitnyj-xab-v-ekaterinburge/
- direct_url: https://flyredwings.com/press/news/red-wings-sozdast-tranzitnyj-xab-v-ekaterinburge/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: дата конференции, начальные маршруты.
- Доступность: текст в индексе. Статус: verified_primary.

### S16. Red Wings: год базирования в Кольцово

- Издатель: Red Wings.
- Период: первый год проекта; январь–сентябрь 2021. Дата: 07.10.2021.
- landing_url: https://flyredwings.com/press/news/red-wings-god-bazirovaniya-v-kolczovo/
- direct_url: https://flyredwings.com/press/news/red-wings-god-bazirovaniya-v-kolczovo/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы о финансовой поддержке и 470 тыс. пассажиров.
- Доступность: текст в индексе. Статус: verified_primary.

### S17. Red Wings развивает новые маршруты из Екатеринбурга

- Издатель: Red Wings.
- Период: весна–лето 2024. Дата: 23.04.2024.
- landing_url: https://flyredwings.com/en/press/news/red-wings-razvivaet-novye-marshruty-iz-ekaterinburga/
- direct_url: https://flyredwings.com/en/press/news/red-wings-razvivaet-novye-marshruty-iz-ekaterinburga/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзац частот по 13 городам.
- Доступность: текст в индексе. Статус: verified_primary.

### S18. Red Wings будет летать в Ставрополь из Екатеринбурга

- Издатель: Red Wings.
- Период: 2025. Дата: 29.04.2025.
- landing_url: https://flyredwings.com/press/news/red-wings-budet-letat-v-stavropol-iz-ekaterinburga/
- direct_url: https://flyredwings.com/press/news/red-wings-budet-letat-v-stavropol-iz-ekaterinburga/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзац о стыковках и регистрации багажа до конечного пункта.
- Доступность: текст в индексе. Статус: verified_primary.

### S19. Сезонное расписание вылетов

- Издатель: Аэропорт Кольцово.
- Период: осень–зима 2026/27. Дата: изменяемая страница.
- landing_url: https://ar-svx.ru/schedule/
- direct_url: https://ar-svx.ru/schedule/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: строки рейсов WZ по кодам назначения; время местное.
- Доступность: HTML прочитан; таблица извлечена также напрямую. Статус: verified_primary.

### S20. Расписание рейсов из Саратова

- Издатель: Аэропорт Гагарин.
- Период: осень–зима 2026/27. Дата: изменяемая страница.
- landing_url: https://ar-gsv.ru/schedule/
- direct_url: https://ar-gsv.ru/schedule/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: WZ-5048; S7-5158; S7-7058; строки 95–156.
- Доступность: HTML прочитан. Статус: verified_primary.

### S21. Сезонное расписание «Зима 2026»

- Издатель: Омский аэропорт.
- Период: зима 2026/27. Дата: редакция 05.11.2026.
- landing_url: https://www.aeroomsk.ru/karta-poleta/
- direct_url: https://www.aeroomsk.ru/karta-poleta/pdf/w26/w26-20261105.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: 3 страницы; строки парных рейсов и интервалы дат.
- Доступность: страница и PDF прочитаны. Статус: verified_primary.

### S22. Направления из Екатеринбурга

- Издатель: Red Wings.
- Период: витрина на дату проверки. Дата: дата предложения не раскрыта.
- landing_url: https://flyredwings.com/directions/ekaterinburg/
- direct_url: https://flyredwings.com/directions/ekaterinburg/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: карточки Уфы, Саратова, Омска, Сургута.
- Доступность: текст в индексе. Статус: verified_primary.

### S23. Итоги производственной деятельности за 2025 год

- Издатель: Омский аэропорт.
- Период: 2025. Дата: 15.01.2026.
- landing_url: https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/253/
- direct_url: https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/253/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: строки 123–140; топ-10 направлений.
- Доступность: официальная страница прочитана. Статус: verified_primary.

### S24. Пассажиропоток Омского аэропорта в 2024 году составил 1 726 029 человек

- Издатель: Омский аэропорт.
- Период: 2023–2024. Дата: 09.01.2025.
- landing_url: https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/210/
- direct_url: https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/210/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые три абзаца.
- Доступность: текст в индексе. Статус: verified_primary.

### S25. Омский аэропорт обслужил в 2023 году 1 680 206 человек

- Издатель: Омский аэропорт.
- Период: 2023. Дата: 09.01.2024.
- landing_url: https://aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/142/
- direct_url: https://aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/142/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: перечень субсидируемых линий 2023.
- Доступность: текст в индексе. Статус: verified_primary.

### S26. Международный аэропорт «Уфа» подвел итоги 2025 года

- Издатель: Аэропорт Уфа.
- Период: 2025. Дата: 27.01.2026.
- landing_url: https://www.airportufa.ru/news/2025/mezhdunarodnyy-aeroport-ufa-podvel-itogi-2025-goda/
- direct_url: https://www.airportufa.ru/news/2025/mezhdunarodnyy-aeroport-ufa-podvel-itogi-2025-goda/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые абзацы о пассажирах и прибыли.
- Доступность: текст в индексе. Статус: verified_primary.

### S27. Итоги пассажиропотока за 2025 год

- Издатель: Аэропорт Пермь, официальный канал.
- Период: 2025. Дата: точная дата сообщения не извлечена.
- landing_url: https://t.me/s/permairport?before=347
- direct_url: https://t.me/s/permairport?before=347
- direct_type: embedded_html. archive_url: not_found.
- Локатор: сообщение с 2 004 861; описание канала указывает aviaperm.ru.
- Доступность: текст официального канала в индексе; ссылка на отдельный пост не извлечена. Статус: verified_primary.

### S28. Пассажиропоток аэропорта Рощино за 2025 год превысил 2,76 млн человек

- Издатель: AEX / AviaStat со ссылкой на аэропорт Рощино.
- Период: 2025. Дата: 14.01.2026.
- landing_url: https://www.aex.ru/news/2026/1/14/291500/
- direct_url: https://www.aex.ru/news/2026/1/14/291500/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: основной текст.
- Доступность: вторичная публикация прочитана в индексе; оригинал не найден. Статус: verified_secondary.

### S29. Итоги пассажиропотока за 2025 год

- Издатель: Аэропорт Челябинск, официальный канал.
- Период: 2025. Дата: точная дата сообщения не извлечена.
- landing_url: https://t.me/s/cekport_tg/410
- direct_url: https://t.me/s/cekport_tg/410
- direct_type: embedded_html. archive_url: not_found.
- Локатор: сообщение с 2 166 689 пассажирами.
- Доступность: текст канала в индексе. Статус: verified_primary.

### S30. Итоги года аэропортов Западной Сибири

- Издатель: Западно-Сибирское МТУ Росавиации.
- Период: 2025. Дата: 22.01.2026.
- landing_url: https://zs-m.favt.ru/novosti-novosti/?id=12414
- direct_url: https://zs-m.favt.ru/novosti-novosti/?id=12414
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы Толмачево, Богашево, Барнаул, Кемерово.
- Доступность: текст в индексе; прямое чтение — тайм-аут. Статус: verified_primary.

### S31. Производственные итоги за 2025 год

- Издатель: Аэропорт Красноярск, KJA TEAM.
- Период: 2025. Дата: 14.01.2026.
- landing_url: https://team.kja.aero/media/aeroport-krasnoyarsk-po-itogam-2025-goda-1-1
- direct_url: https://team.kja.aero/media/aeroport-krasnoyarsk-po-itogam-2025-goda-1-1
- direct_type: embedded_html. archive_url: not_found.
- Локатор: «Пассажирский трафик»; «Популярные направления и авиакомпании».
- Доступность: текст в индексе. Статус: verified_primary.

### S32. Подводим итоги за 9 месяцев 2025 года

- Издатель: Международный аэропорт Иркутск.
- Период: январь–сентябрь 2025. Дата: 19.10.2025.
- landing_url: https://www.iktport.ru/ru/about/novosti/726-подводим-итоги-за-9-месяцев-2025-года
- direct_url: https://www.iktport.ru/ru/about/novosti/726-подводим-итоги-за-9-месяцев-2025-года
- direct_type: embedded_html. archive_url: not_found.
- Локатор: пассажиры всего и рейтинг авиакомпаний.
- Доступность: текст в индексе. Статус: verified_primary.

### S33. Почти миллион пассажиров и более 7 млн кг багажа: итоги лета

- Издатель: Международный аэропорт Иркутск.
- Период: июнь–август 2026. Дата: 17.09.2026.
- landing_url: https://iktport.ru/ru/about/novosti/799-почти-миллион-пассажиров-и-более-7-млн-кг-багажа-аэропорт-иркутска-подвёл-итоги-работы-за-лето
- direct_url: https://iktport.ru/ru/about/novosti/799-почти-миллион-пассажиров-и-более-7-млн-кг-багажа-аэропорт-иркутска-подвёл-итоги-работы-за-лето
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы пассажиров по сегментам и авиакомпаниям.
- Доступность: текст в индексе. Статус: verified_primary.

### S34. В 2025 году аэропорт «Гагарин» обслужил 1 млн 64 тыс. пассажиров

- Издатель: Аэропорт Гагарин.
- Период: 2025. Дата: 20.01.2026.
- landing_url: https://ar-gsv.ru/about/news/v-2025-godu-aeroport-gagarin-obsluzhil-1-mln-64-tys-passazhi/
- direct_url: https://ar-gsv.ru/about/news/v-2025-godu-aeroport-gagarin-obsluzhil-1-mln-64-tys-passazhi/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые два абзаца; список 14 направлений и 11 перевозчиков.
- Доступность: текст в индексе. Статус: verified_primary.

### S35. Аэропорт Оренбург обслужил за 2025 год более 950 тысяч пассажиров

- Издатель: Аэропорт Оренбург.
- Период: 2025. Дата: 15.01.2026.
- landing_url: https://ar-ren.ru/about/news/aeroport-orenburg-obsluzhil-za-2025-god-bolee-950/
- direct_url: https://ar-ren.ru/about/news/aeroport-orenburg-obsluzhil-za-2025-god-bolee-950/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые три абзаца.
- Доступность: текст в индексе. Статус: verified_primary.

### S36. Итоги работы в новогодние праздники — текст содержит итоги 2025 года

- Издатель: Аэропорт Курумоч.
- Период: 2025. Дата: 14.01.2026.
- landing_url: https://ar-kuf.ru/about/news/itogi-raboty-v-novogodnie-prazdnik/
- direct_url: https://ar-kuf.ru/about/news/itogi-raboty-v-novogodnie-prazdnik/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы годового потока и направлений.
- Доступность: текст в индексе; заголовок не соответствует содержанию. Статус: verified_primary.

### S37. Пассажиропоток аэропорта Курумоч превысил 3,5 миллиона человек

- Издатель: Аэропорт Курумоч.
- Период: 2024. Дата: 17.01.2025.
- landing_url: https://ar-kuf.ru/about/news/passazhiropotok-aeroporta-kurumoch-prevysil-3-5-milliona-che/
- direct_url: https://ar-kuf.ru/about/news/passazhiropotok-aeroporta-kurumoch-prevysil-3-5-milliona-che/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы о годовом потоке, Москве, Петербурге и Сочи.
- Доступность: текст в индексе. Статус: verified_primary.

### S38. Муниципальный документ об итогах работы Казани в 2025 году; полное название не извлечено

- Издатель: Официальный портал правовой информации Татарстана.
- Период: 2025. Дата: февраль 2026 по каталогу; точная дата не установлена.
- landing_url: https://pravo.tatarstan.ru/file/npa/2026-02/1794855/npa_1794856.pdf
- direct_url: https://pravo.tatarstan.ru/file/npa/2026-02/1794855/npa_1794856.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: страница с печатным номером 5: туризм и аэропорт.
- Доступность: текст PDF в индексе; прямое чтение — тайм-аут. Статус: verified_primary.

### S39. За 2025 год выросло количество нижегородцев, летавших за рубеж

- Издатель: Аэропорт Нижнего Новгорода.
- Период: 2025. Дата: 14.01.2026.
- landing_url: https://ar-goj.ru/about/news/za-2025-god-vyroslo-kolichestvo-nizhegorodtsev-letavshikh-za/
- direct_url: https://ar-goj.ru/about/news/za-2025-god-vyroslo-kolichestvo-nizhegorodtsev-letavshikh-za/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые абзацы, 26 направлений и запасные посадки.
- Доступность: текст в индексе. Статус: verified_primary.

### S40. Развитие инфраструктуры, новые сервисы и рост пассажиропотока: итоги 2025 года

- Издатель: Аэропорт Кольцово.
- Период: 2025. Дата: 19.01.2026.
- landing_url: https://ar-svx.ru/about/news/razvitie-infrastruktury-novye-servisy-i-rost-passazhiropotok/
- direct_url: https://ar-svx.ru/about/news/razvitie-infrastruktury-novye-servisy-i-rost-passazhiropotok/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые три абзаца.
- Доступность: текст в индексе. Статус: verified_primary.

### S41. Аэропорт Минвод в 2025 году снизил пассажиропоток на 4,6%

- Издатель: Финмаркет / Интерфакс, пресс-служба аэропорта.
- Период: 2025; инфраструктурные планы 2026–2028. Дата: 19.01.2026.
- landing_url: https://www.finmarket.ru/news/6545429
- direct_url: https://www.finmarket.ru/news/6545429
- direct_type: embedded_html. archive_url: not_found.
- Локатор: основной текст и последний абзац.
- Доступность: вторичная публикация в индексе; оригинал аэропорта не найден. Статус: verified_secondary.

### S42. Численность населения РФ по муниципальным образованиям

- Издатель: Росстат.
- Период: на 01.01.2025; каталог также содержит 2024. Дата: 25.04.2025 для файла 2025 по каталогу.
- landing_url: https://rosstat.gov.ru/folder/12781?print=1&source=subscribe
- direct_url: not_found
- direct_type: xlsx_catalog. archive_url: not_found.
- Локатор: «Оперативная информация», файл 1,07 МБ.
- Доступность: каталог в индексе; прямой XLSX не получен; HTTP 503. Статус: unverified.

### S43. Россия 2025: крупнейшие города

- Издатель: Росстат.
- Период: население на 01.01.2024. Дата: 2025; точная дата не установлена.
- landing_url: https://rosstat.gov.ru/storage/mediabank/Rossia_2025.pdf
- direct_url: https://rosstat.gov.ru/storage/mediabank/Rossia_2025.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: таблица «Крупнейшие города России на 1 января 2024 г., тыс. человек».
- Доступность: таблица PDF в индексе; прямое чтение — тайм-аут; отдельная карточка не найдена. Статус: verified_primary.

### S44. Господдержка региональных перевозок; решение № 22-64160-00191-Р, версия 7

- Издатель: Росавиация.
- Период: порядок предоставления субсидии. Дата: 26.11.2024 — дата базового решения; дата версии не установлена.
- landing_url: https://favt.gov.ru/dejatelnost-gosudarstvennaia-podderzhka-subsidii/?id=15106
- direct_url: https://favt.ru/public/materials/0/3/9/e/7/039e77a7205ca81e3070590870e45a3e.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: титульный лист; раздел 1; приложения нужно дочитать.
- Доступность: карточка и начало PDF в индексе; полное чтение — тайм-аут. Статус: verified_primary.

### S45. Региональное субсидирование перевозок: перечни 2024–2026

- Издатель: Росавиация.
- Период: 2024–2026. Дата: актуализация в 2026; точная дата HTML не установлена.
- landing_url: https://favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony/?from=old-site
- direct_url: https://favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony/?from=old-site
- direct_type: embedded_html. archive_url: not_found.
- Локатор: таблица 2026; архив приказов 899-П, 261-П, 845-П, 1187-П.
- Доступность: таблица прочитана фрагментами в индексе, включая строки № 48 и 51; прямое чтение — тайм-аут; old/special — зеркала. Статус: verified_primary.

### S46. Правила по постановлению Правительства РФ от 25.12.2013 № 1242, историческая редакция

- Издатель: Росавиация, архив нормативных материалов.
- Период: редакция включает изменения до 14.11.2018. Дата: дата загрузки не установлена.
- landing_url: https://old.favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony
- direct_url: https://old.favt.gov.ru/public/materials/0/d/2/d/a/0d2da0ba156a854e116346650116d1d5.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: титульная страница, список изменяющих документов.
- Доступность: начало PDF в индексе. Статус: verified_primary.

### S47. Постановление № 1242, редакция 14.10.2023: отметка об утрате силы

- Издатель: КонсультантПлюс.
- Период: правовой статус на дату проверки. Дата: дата утраты силы не извлечена.
- landing_url: https://www.consultant.ru/document/cons_doc_LAW_156427/
- direct_url: https://www.consultant.ru/document/cons_doc_LAW_156427/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: статус над заголовком.
- Доступность: текст карточки в индексе; отменяющий акт не получен. Статус: verified_secondary.

### S48. Прейскурант для российских потребителей по состоянию на 21.12.2025 с изменениями от 01.08.2026

- Издатель: АО «СарАэро-Инвест».
- Период: редакция 01.08.2026. Дата: дата публикации не указана.
- landing_url: https://ar-gsv.ru/about/info/
- direct_url: https://ar-gsv.ru/upload/iblock/e03/x30km5z81eqnv9f1mhqs3im92866fzqy/Preyskurant-AO-SarAero_Invest-dlya-rossiyskikh-ekspluatantov-s-21.12.2025-_s-izmeneniyami-s-01.08.2026_.pdf
- direct_type: pdf_scan. archive_url: not_found.
- Локатор: страницы 1–2, разделы I и II.1.
- Доступность: PDF скачан; 11 страниц; страницы 1–2 проверены визуально. Статус: verified_primary.

### S49. Прейскурант для российских потребителей с 21.08.2026

- Издатель: Омский аэропорт.
- Период: с 21.08.2026. Дата: дата загрузки не установлена.
- landing_url: https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/
- direct_url: https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/tarifs_rus_20260821.pdf
- direct_type: pdf_scan. archive_url: not_found.
- Локатор: 11 страниц; таблицы ставок.
- Доступность: PDF доступен; текстовый слой не извлечён. Статус: verified_primary.

### S50. Изменения к прейскуранту с 10.10.2026

- Издатель: Омский аэропорт.
- Период: с 10.10.2026. Дата: не установлена.
- landing_url: https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/
- direct_url: https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/pr568-2026.pdf
- direct_type: pdf_scan. archive_url: not_found.
- Локатор: 1 страница.
- Доступность: PDF доступен; ставки не прочитаны. Статус: verified_primary.

### S51. Изменения к прейскуранту с 15.10.2026

- Издатель: Омский аэропорт.
- Период: с 15.10.2026. Дата: не установлена.
- landing_url: https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/
- direct_url: https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/pr610-2026.pdf
- direct_type: pdf_scan. archive_url: not_found.
- Локатор: 1 страница.
- Доступность: PDF доступен; ставки не прочитаны. Статус: verified_primary.

### S52. Коды и характеристики

- Издатель: Омский аэропорт.
- Период: страница на дату проверки. Дата: не указана.
- landing_url: https://www.aeroomsk.ru/aviakompaniyam/kody-i-kharakteristiki/
- direct_url: https://www.aeroomsk.ru/aviakompaniyam/kody-i-kharakteristiki/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: таблица кодов, ВПП и принимаемых ВС; строки 124–144.
- Доступность: HTML прочитан. Статус: verified_primary.

### S53. Основные показатели ФХД СЕМ за 2025–2027 годы

- Издатель: Аэропорт Курумоч.
- Период: 2025 — факт; 2026–2027 — прогноз. Дата: не установлена.
- landing_url: https://ar-kuf.ru/about/info/
- direct_url: https://ar-kuf.ru/upload/iblock/964/ugdj79k4p95x7qjgpy17rokry33zngn4/Osnovnye-pokazateli-FKHD-SEM-v-sfere-okazaniya-reguliruemykh-uslug-za-2025_2027-gg.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: таблица доходов и расходов; столбцы факт/прогноз.
- Доступность: карточка и таблица в индексе; HTML каталога прочитан. Статус: verified_primary.

### S54. Отчёт об инвестиционной программе за 2024 год, формы 3а–г

- Издатель: Аэропорт Нижнего Новгорода.
- Период: 2024. Дата: не установлена.
- landing_url: https://goj.aero/upload/iblock/54c/i3h4wxp5659sjwweyoixytoq5ntss6t8/Investitsionnaya-programma-otchyet-po-formam-3a_b_v_g-za-2024-g.pdf
- direct_url: https://goj.aero/upload/iblock/54c/i3h4wxp5659sjwweyoixytoq5ntss6t8/Investitsionnaya-programma-otchyet-po-formam-3a_b_v_g-za-2024-g.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: строки оборудования; отдельная карточка не найдена.
- Доступность: таблица PDF в индексе. Статус: verified_primary.

### S55. Ставки сборов за аэронавигационное обслуживание: приказ ФАС № 595/24

- Издатель: Росавиация.
- Период: редакция 2024. Дата: 30.08.2024 — дата акта.
- landing_url: https://favt.gov.ru/dejatelnost-ajeronavigacionnoe-obsluzhivanie-stavki-sborov/
- direct_url: https://favt.gov.ru/dejatelnost-ajeronavigacionnoe-obsluzhivanie-stavki-sborov/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: приложения по разным категориям пользователей.
- Доступность: текст в индексе; возможно устаревший. Статус: verified_primary.

### S56. Приказ ФАС от 16.12.2025 № 1101/25 о ставках АНО

- Издатель: ГАРАНТ.
- Период: 2026. Дата: 16.12.2025; регистрация 26.01.2026.
- landing_url: https://base.garant.ru/413529528/
- direct_url: https://base.garant.ru/413529528/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: пункты 1–2; приложения 1–11.
- Доступность: текст в индексе; официальный опубликованный экземпляр не найден. Статус: verified_secondary.

### S57. S7 Airlines подвела итоги 2025 года

- Издатель: S7 Group, официальный канал S7 Newsroom.
- Период: 2025. Дата: точная дата сообщения не извлечена.
- landing_url: https://t.me/s/s7newsroom/544
- direct_url: https://t.me/s/s7newsroom/544
- direct_type: embedded_html. archive_url: not_found.
- Локатор: сообщение об итогах 2025; 12,8 млн и потоки через три хаба.
- Доступность: текст официального канала в индексе. Статус: verified_primary.

### S58. Аэрофлот отмечает 5-летие сибирского хаба

- Издатель: Пресс-релиз Аэрофлота, перепечатка АвиаПорт.
- Период: 2021–2026; 2025 отдельно. Дата: июнь 2026; точный день не подтверждён.
- landing_url: https://www.aviaport.ru/news/aeroflot-otmechaet-5-letie-sibirskogo-khaba/
- direct_url: https://www.aviaport.ru/news/aeroflot-otmechaet-5-letie-sibirskogo-khaba/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы о 2,2 млн, 32 направлениях и 10 самолётах.
- Доступность: найден текст перепечатки; оригинал aeroflot.ru не получен. Статус: verified_secondary.

### S59. Группа «ЮТэйр» выпустила отчётность по МСФО за 2025 год

- Издатель: ЮТэйр.
- Период: 2025. Дата: точная дата не извлечена.
- landing_url: https://www.utair.ru/about/news/gruppa-yuteyr-vypustila-otchyetnost-po-msfo-za-2025-god/
- direct_url: https://www.utair.ru/about/news/gruppa-yuteyr-vypustila-otchyetnost-po-msfo-za-2025-god/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: разделы самолётных и вертолётных перевозок.
- Доступность: официальное сообщение в индексе; полный PDF МСФО не получен. Статус: verified_primary.

### S60. «ЮТэйр» опубликовал отчётность по РСБУ за 2025 год

- Издатель: ЮТэйр.
- Период: 2025. Дата: точная дата не извлечена.
- landing_url: https://www.utair.ru/about/news/yuteyr-opublikoval-otchetnost-po-rsbu-za-2025-god/
- direct_url: https://www.utair.ru/about/news/yuteyr-opublikoval-otchetnost-po-rsbu-za-2025-god/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: пассажиропоток ПАО и внутренние перевозки.
- Доступность: текст официального сообщения в индексе. Статус: verified_primary.

### S61. Бортовой журнал «Ваш Азимут», № 97

- Издатель: Авиакомпания Азимут.
- Период: итоги 2025. Дата: выпуск к Новому 2026 году; точная дата не установлена.
- landing_url: https://azimuth.ru/ru/about/journal
- direct_url: https://azimuth.ru/uploads/ckeditor/attachments/949/vash_azimut_97.pdf
- direct_type: pdf. archive_url: not_found.
- Локатор: обращение руководства «Уважаемые пассажиры!».
- Доступность: текст PDF и каталог в индексе. Статус: verified_primary.

### S62. Двойной триумф: премия «Крылья России»

- Издатель: Уральские авиалинии.
- Период: 2025. Дата: 02.06.2026.
- landing_url: https://www.uralairlines.ru/uz/news/element/dvoynoy-triumf-uralskie-avialinii-stali-laureatami-premii-krylya-rossii-v-nominatsiyakh-aviakompaniya/
- direct_url: https://www.uralairlines.ru/uz/news/element/dvoynoy-triumf-uralskie-avialinii-stali-laureatami-premii-krylya-rossii-v-nominatsiyakh-aviakompaniya/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: комментарий о более 8 млн пассажиров и почти 53 тыс. рейсов.
- Доступность: текст официального сообщения в индексе; /uz/ содержит русский текст. Статус: verified_primary.

### S63. АО «Ред Вингс», ИНН 7732107883: бухгалтерские показатели

- Издатель: РБК Компании.
- Период: 2025. Дата: дата обновления не установлена.
- landing_url: https://companies.rbc.ru/id/1027700281091-ao-red-vings/
- direct_url: https://companies.rbc.ru/id/1027700281091-ao-red-vings/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: блок выручки, прибыли и себестоимости за 2025.
- Доступность: вторичная карточка в индексе; отчёт ФНС не получен. Статус: verified_secondary.

### S64. Дмитрий Ядров вручил сертификаты типа на Ил-114-300 и ПД-8

- Издатель: Росавиация.
- Период: 05.06.2026. Дата: 05.06.2026.
- landing_url: https://favt.gov.ru/novosti-novosti/?id=18741
- direct_url: https://favt.gov.ru/novosti-novosti/?id=18741
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые абзацы и «Пять фактов о двигателе ПД-8».
- Доступность: текст официального сообщения в индексе. Статус: verified_primary.

### S65. SSJ-100 получили одобрение главного изменения типовой конструкции

- Издатель: Ростех / ОАК.
- Период: 12.10.2026. Дата: 12.10.2026.
- landing_url: https://www.rostec.ru/media/news/samolety-ssj-100-poluchili-odobrenie-glavnogo-izmeneniya-tipovoy-konstruktsii/
- direct_url: https://www.rostec.ru/media/news/samolety-ssj-100-poluchili-odobrenie-glavnogo-izmeneniya-tipovoy-konstruktsii/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые три абзаца; версии с SaM146.
- Доступность: текст в индексе. Статус: verified_primary.

### S66. SJ-100: продуктовая страница

- Издатель: ПАО «Яковлев».
- Период: не установлен; страница изменяемая. Дата: не указана.
- landing_url: https://yakovlev.ru/products/sj-100/
- direct_url: https://yakovlev.ru/products/sj-100/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: блоки вместимости, дальности, числа операторов.
- Доступность: текст в индексе; смешение брендинга с действующим SSJ. Статус: verified_primary.

### S67. Первые SJ-100 и МС-21 передадут авиакомпаниям во второй половине 2027 года

- Издатель: Авиация России, со ссылкой на интервью «Вести».
- Период: объявленный план 2027. Дата: сообщение о выступлении 15.09.2026.
- landing_url: https://aviation21.ru/pervye-sj-100-i-ms-21-peredadut-aviakompaniyam-vo-vtoroj-polovine-2027-goda/
- direct_url: https://aviation21.ru/pervye-sj-100-i-ms-21-peredadut-aviakompaniyam-vo-vtoroj-polovine-2027-goda/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: абзацы сроков, сертификации и контрактов.
- Доступность: вторичная публикация в индексе; оригинал интервью не получен. Статус: verified_secondary.

### S68. Общественный совет оценил перспективные планы отечественного авиастроения

- Издатель: Росавиация.
- Период: план на 2026 из 2025 года. Дата: 23.10.2025.
- landing_url: https://favt.gov.ru/novosti-novosti?id=17091
- direct_url: https://favt.gov.ru/novosti-novosti?id=17091
- direct_type: embedded_html. archive_url: not_found.
- Локатор: пункт о поставках SJ-100 в 2026.
- Доступность: текст официального сообщения в индексе. Статус: verified_primary.

### S69. «Аврора» — дипломант национальной авиационной премии «Крылья России»

- Издатель: Пресс-релиз Авроры, AVIA RU.
- Период: 2025. Дата: 02.06.2026.
- landing_url: https://www.aviaru.net/pr/76792/
- direct_url: https://www.aviaru.net/pr/76792/
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые два абзаца: около 1,6 млн, 18 тыс. рейсов, 83%.
- Доступность: перепечатка с указанием издателя; оригинал не найден. Статус: verified_secondary.

### S70. Итоги гражданской авиации за 2023 год

- Издатель: Росавиация.
- Период: 2023. Дата: март 2024; точная дата сообщения не извлечена.
- landing_url: https://special.favt.gov.ru/novosti-novosti/?id=11187
- direct_url: https://special.favt.gov.ru/novosti-novosti/?id=11187
- direct_type: embedded_html. archive_url: not_found.
- Локатор: «Результаты перевозок»: 105,4 млн, международные 22,4 млн, внутренние 83 млн.
- Доступность: текст официальной страницы в индексе; полный файл статистики не выгружен. Статус: verified_primary.

### S71. Пассажиропоток российских авиакомпаний в 2024 году вырос почти на 6%

- Издатель: Росавиация.
- Период: 2024. Дата: 03.02.2025.
- landing_url: https://www.favt.gov.ru/novosti-rossii/?id=14454
- direct_url: https://www.favt.gov.ru/novosti-rossii/?id=14454
- direct_type: embedded_html. archive_url: not_found.
- Локатор: первые абзацы: 111,7 млн; 84,7 млн и 27 млн.
- Доступность: текст официальной страницы в индексе; полный файл статистики не выгружен. Статус: verified_primary.

### Итоговая проверка качества и границы готовности

- Исходное задание прочитано; его иллюстративные числа не приняты за исходную статистику.
- В каталоге у каждого объекта есть два отдельных поля URL либо явный not_found для неполученного прямого файла.
- Каждая строка наблюдения имеет период, единицу, издателя через source_id, локатор, способ извлечения, статус и допустимое использование.
- Вычисления частот и ёмкости выделены отдельно от фактических перевозок; витринные цены отделены от дохода.
- Не установлены и не выдуманы отсутствующие O&D, загрузки, свободные борта, расходы SSJ и будущие выплаты.
- Планы поставок, сертификация двигателя и эксплуатация самолётов не объединены в одно событие.
- Все собственные пояснения, заголовки и выводы написаны по-русски; технические имена полей и статусов сохранены для последующей обработки.
- Единственный пользовательский результат — настоящий отчёт. Рабочие извлечения и визуальная проверка документов не являются отдельными поставляемыми файлами.

**Готово к передаче:** каталог, извлечённые наблюдения, лонглист, датированные примеры расписаний, проверенные ставки, конфликты и схема данных. **Не готово к выдаче за доказанную стратегию:** полная маршрутная экономика, оценка конечного спроса и подтверждённая доступность нового флота.

