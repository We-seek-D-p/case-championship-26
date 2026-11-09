# План загрузки первоисточников Red Wings

**Статус на 10.11.2026:** это список заданий на скачивание, **не база уже скачанных файлов**. Составлен по [DR-01](../research/reports/NEW-DR-01-REPORT-RU.md). 71 позиция: S01 — локальный кейс; S02–S71 — 70 внешних источников. Ни одна внешняя позиция пока не имеет статуса `downloaded`.

## Правила

| Поле | Значение |
|---|---|
| **ID** | Стабильный код источника из DR-01; его нужно переносить в будущие таблицы |
| **Страница** | Официальная страница публикации или найденная карточка, где можно проверить происхождение |
| **Прямо** | Адрес исходного PDF или HTML; когда не найден, явно написано **не найден** |
| **Имя файла** | **Точное имя сохранения**, в папке, указанной перед таблицей; такое же значение записано в `save_as` и `raw_path` |
| **Приоритет** | **P0** — первым делом, **P1** — дополнение, **P2** — исторический/контекстный материал |

В [`source_manifest.csv`](source_manifest.csv) для всех строк отдельно сохранены полный путь `raw_path`, полный заголовок, период, `landing_url`, `direct_url`, исходное имя файла из URL (`publisher_filename`), способ получения, доступность и статус. Название нашего сохранённого файла может отличаться от оригинального имени сервера: оригинальное имя сохраняется **в реестре**, а префикс ID убирает коллизии.

S04 и S42 — страницы **каталогов**, а не найденные CSV/XLSX. Их HTML можно сохранить, но настоящую выгрузку придётся найти отдельно и зарегистрировать **новой строкой** (например, S04-01 / S42-01). Для S19/S20 расписания могут подгружаться JavaScript — пустая HTML-оболочка не подходит как исходные данные.

## Первая очередь

| Задача | Источники | Что получим |
|---|---|---|
| Рынок и Red Wings | S02, S03, S04, S05, S08, S11, S12 | Базовые показатели, парк, сеть; найти полноценные статистические выгрузки |
| Расписания | S19, S20, S21 | Действующие в конкретные даты направления и частоты, **не** фактический спрос |
| Аэропорты | S23, S26–S31, S34–S36, S38–S40 | Сопоставимые годовые показатели и опубликованные маршрутные итоги |
| Субсидии и стоимость | S44, S45, S48–S51 | Текущие правила и опубликованные аэропортовые сборы |
| Население | S42, S43 | Муниципальные/городские данные нужного периода |

---

## Рынок и статистика перевозок

**Папка для сохранения:** `data/raw/market/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S02** | Росавиация — Статистические данные: аналитическая таблица формы № 12-ГА | 2023–2024 | [Открыть](https://www.favt.gov.ru/dejatelnost-vozdushnye-perevozki-stat-dannie/?from=old-site) | [HTML](https://www.favt.gov.ru/dejatelnost-vozdushnye-perevozki-stat-dannie/?from=old-site) | `S02__rosaviation_form_12ga.html` | P0 |
| **S03** | Росавиация — Российские авиакомпании перевезли в 2025 году почти 109 млн пассажиров | 2025 | [Открыть](https://favt.gov.ru/novosti-novosti/?id=17763) | [HTML](https://favt.gov.ru/novosti-novosti/?id=17763) | `S03__rosaviation_passengers_2025.html` | P0 |
| **S04** | Росавиация — Реестр открытых данных | исторические ряды; свежесть не установлена | [Открыть](https://www.favt.gov.ru/opendata/) | **не найден** | `S04__rosaviation_opendata_catalog.html` | P0 |
| **S05** | Минтранс России — Доклад о результатах деятельности за 2025 год, целях на 2026 год и плановом периоде до 2028 года | 2025; планы до 2028 | [Открыть](https://mintrans.gov.ru/file/557797) | [PDF](https://mintrans.gov.ru/file/557797) | `S05__mintrans_report_2025.pdf` | P0 |
| **S06** | Минтранс России — Расширение географии полетов — приоритет российских авиаперевозок | 2025 | [Открыть](https://mintrans.gov.ru/press-center/news/12560) | [HTML](https://mintrans.gov.ru/press-center/news/12560) | `S06__rasshirenie_geografii_poletov_prioritet_rossiyskikh_aviape.html` | P1 |
| **S07** | Росавиация — Дмитрий Ядров доложил главе Правительства о работе авиационной отрасли | май–август 2026 | [Открыть](https://www.favt.gov.ru/novosti-novosti/?id=19636) | [HTML](https://www.favt.gov.ru/novosti-novosti/?id=19636) | `S07__dmitriy_yadrov_dolozhil_glave_pravitelstva_o_rabote_aviats.html` | P1 |
| **S70** | Росавиация — Итоги гражданской авиации за 2023 год | 2023 | [Открыть](https://special.favt.gov.ru/novosti-novosti/?id=11187) | [HTML](https://special.favt.gov.ru/novosti-novosti/?id=11187) | `S70__itogi_grazhdanskoy_aviatsii_za_2023_god.html` | P0 |
| **S71** | Росавиация — Пассажиропоток российских авиакомпаний в 2024 году вырос почти на 6% | 2024 | [Открыть](https://www.favt.gov.ru/novosti-rossii/?id=14454) | [HTML](https://www.favt.gov.ru/novosti-rossii/?id=14454) | `S71__passazhiropotok_rossiyskikh_aviakompaniy_v_2024_godu_vyros.html` | P0 |

## Авиакомпании и конкуренты

**Папка для сохранения:** `data/raw/airlines/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S08** | Red Wings — Red Wings перевезла за год на российских самолетах 2 млн пассажиров и 2 совы | 2025 | [Открыть](https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/) | [HTML](https://flyredwings.com/en/press/news/red-wings-perevezla-za-god-na-rossijskix-samoletax-2-mln-passazhirov-i-2-sovy/) | `S08__redwings_results_2025.html` | P0 |
| **S09** | Red Wings — Российская авиакомпания Red Wings отмечает свой юбилей — 25 лет деятельности | 2023; парк на дату релиза | [Открыть](https://flyredwings.com/en/press/news/rossijskaya-aviakompaniya-red-wings-otmechaet-svoj-yubilej-25-let-deyatelnosti/) | [HTML](https://flyredwings.com/en/press/news/rossijskaya-aviakompaniya-red-wings-otmechaet-svoj-yubilej-25-let-deyatelnosti/) | `S09__rossiyskaya_aviakompaniya_red_wings_otmechaet_svoy_yubiley.html` | P2 |
| **S10** | Red Wings — Red Wings перешла на летнее расписание полетов | лето 2026 | [Открыть](https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/) | [HTML](https://flyredwings.com/en/press/news/red-wings-pereshla-na-letnee-raspisanie-poletov/) | `S10__red_wings_pereshla_na_letnee_raspisanie_poletov.html` | P1 |
| **S11** | Red Wings — Red Wings перешла на осенне-зимнее расписание полетов | зима 2026/27 | [Открыть](https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/) | [HTML](https://flyredwings.com/press/news/red-wings-pereshla-na-osenne-zimnee-raspisanie-poletov/) | `S11__red_wings_pereshla_na_osenne_zimnee_raspisanie_poletov.html` | P0 |
| **S13** | Red Wings — Роман Чуев стал генеральным директором Red Wings | назначение 2026 | [Открыть](https://flyredwings.com/en/press/news/roman-chuev-stal-generalnym-direktorom-red-wings/) | [HTML](https://flyredwings.com/en/press/news/roman-chuev-stal-generalnym-direktorom-red-wings/) | `S13__roman_chuev_stal_generalnym_direktorom_red_wings.html` | P2 |
| **S14** | Red Wings — Red Wings открыла программу полетов в Израиль на летний сезон 2027 года | 28.03–24.10.2027 | [Открыть](https://flyredwings.com/press/news/red-wings-otkryla-programmu-poletov-v-izrail-na-letny-sezon-2027-goda/) | [HTML](https://flyredwings.com/press/news/red-wings-otkryla-programmu-poletov-v-izrail-na-letny-sezon-2027-goda/) | `S14__red_wings_otkryla_programmu_poletov_v_izrail_na_letniy_sez.html` | P1 |
| **S15** | Red Wings — Red Wings создаст транзитный хаб в Екатеринбурге | 2020 | [Открыть](https://flyredwings.com/press/news/red-wings-sozdast-tranzitnyj-xab-v-ekaterinburge/) | [HTML](https://flyredwings.com/press/news/red-wings-sozdast-tranzitnyj-xab-v-ekaterinburge/) | `S15__red_wings_sozdast_tranzitnyy_khab_v_ekaterinburge.html` | P2 |
| **S16** | Red Wings — Red Wings: год базирования в Кольцово | первый год проекта; январь–сентябрь 2021 | [Открыть](https://flyredwings.com/press/news/red-wings-god-bazirovaniya-v-kolczovo/) | [HTML](https://flyredwings.com/press/news/red-wings-god-bazirovaniya-v-kolczovo/) | `S16__red_wings_god_bazirovaniya_v_koltsovo.html` | P2 |
| **S17** | Red Wings — Red Wings развивает новые маршруты из Екатеринбурга | весна–лето 2024 | [Открыть](https://flyredwings.com/en/press/news/red-wings-razvivaet-novye-marshruty-iz-ekaterinburga/) | [HTML](https://flyredwings.com/en/press/news/red-wings-razvivaet-novye-marshruty-iz-ekaterinburga/) | `S17__red_wings_razvivaet_novye_marshruty_iz_ekaterinburga.html` | P2 |
| **S18** | Red Wings — Red Wings будет летать в Ставрополь из Екатеринбурга | 2025 | [Открыть](https://flyredwings.com/press/news/red-wings-budet-letat-v-stavropol-iz-ekaterinburga/) | [HTML](https://flyredwings.com/press/news/red-wings-budet-letat-v-stavropol-iz-ekaterinburga/) | `S18__red_wings_budet_letat_v_stavropol_iz_ekaterinburga.html` | P2 |
| **S22** | Red Wings — Направления из Екатеринбурга | витрина на дату проверки | [Открыть](https://flyredwings.com/directions/ekaterinburg/) | [HTML](https://flyredwings.com/directions/ekaterinburg/) | `S22__napravleniya_iz_ekaterinburga.html` | P2 |
| **S57** | S7 Group, официальный канал S7 Newsroom — S7 Airlines подвела итоги 2025 года | 2025 | [Открыть](https://t.me/s/s7newsroom/544) | [HTML](https://t.me/s/s7newsroom/544) | `S57__s7_airlines_podvela_itogi_2025_goda.html` | P1 |
| **S58** | Пресс-релиз Аэрофлота, перепечатка АвиаПорт — Аэрофлот отмечает 5-летие сибирского хаба | 2021–2026; 2025 отдельно | [Открыть](https://www.aviaport.ru/news/aeroflot-otmechaet-5-letie-sibirskogo-khaba/) | [HTML](https://www.aviaport.ru/news/aeroflot-otmechaet-5-letie-sibirskogo-khaba/) | `S58__aeroflot_otmechaet_5_letie_sibirskogo_khaba.html` | P1 |
| **S59** | ЮТэйр — Группа «ЮТэйр» выпустила отчётность по МСФО за 2025 год | 2025 | [Открыть](https://www.utair.ru/about/news/gruppa-yuteyr-vypustila-otchyetnost-po-msfo-za-2025-god/) | [HTML](https://www.utair.ru/about/news/gruppa-yuteyr-vypustila-otchyetnost-po-msfo-za-2025-god/) | `S59__gruppa_yuteyr_vypustila_otchyotnost_po_msfo_za_2025_god.html` | P1 |
| **S60** | ЮТэйр — «ЮТэйр» опубликовал отчётность по РСБУ за 2025 год | 2025 | [Открыть](https://www.utair.ru/about/news/yuteyr-opublikoval-otchetnost-po-rsbu-za-2025-god/) | [HTML](https://www.utair.ru/about/news/yuteyr-opublikoval-otchetnost-po-rsbu-za-2025-god/) | `S60__yuteyr_opublikoval_otchyotnost_po_rsbu_za_2025_god.html` | P2 |
| **S61** | Авиакомпания Азимут — Бортовой журнал «Ваш Азимут», № 97 | итоги 2025 | [Открыть](https://azimuth.ru/ru/about/journal) | [PDF](https://azimuth.ru/uploads/ckeditor/attachments/949/vash_azimut_97.pdf) | `S61__bortovoy_zhurnal_vash_azimut_97.pdf` | P1 |
| **S62** | Уральские авиалинии — Двойной триумф: премия «Крылья России» | 2025 | [Открыть](https://www.uralairlines.ru/uz/news/element/dvoynoy-triumf-uralskie-avialinii-stali-laureatami-premii-krylya-rossii-v-nominatsiyakh-aviakompaniya/) | [HTML](https://www.uralairlines.ru/uz/news/element/dvoynoy-triumf-uralskie-avialinii-stali-laureatami-premii-krylya-rossii-v-nominatsiyakh-aviakompaniya/) | `S62__dvoynoy_triumf_premiya_krylya_rossii.html` | P2 |
| **S63** | РБК Компании — АО «Ред Вингс», ИНН 7732107883: бухгалтерские показатели | 2025 | [Открыть](https://companies.rbc.ru/id/1027700281091-ao-red-vings/) | [HTML](https://companies.rbc.ru/id/1027700281091-ao-red-vings/) | `S63__ao_red_vings_inn_7732107883_bukhgalterskie_pokazateli.html` | P1 |
| **S69** | Пресс-релиз Авроры, AVIA RU — «Аврора» — дипломант национальной авиационной премии «Крылья России» | 2025 | [Открыть](https://www.aviaru.net/pr/76792/) | [HTML](https://www.aviaru.net/pr/76792/) | `S69__avrora_diplomant_natsionalnoy_aviatsionnoy_premii_krylya_r.html` | P2 |

## Парк самолётов и поставки

**Папка для сохранения:** `data/raw/fleet/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S12** | Red Wings — Парк самолётов | страница на дату проверки | [Открыть](https://flyredwings.com/about/park/) | [HTML](https://flyredwings.com/about/park/) | `S12__park_samolyotov.html` | P0 |
| **S64** | Росавиация — Дмитрий Ядров вручил сертификаты типа на Ил-114-300 и ПД-8 | 05.06.2026 | [Открыть](https://favt.gov.ru/novosti-novosti/?id=18741) | [HTML](https://favt.gov.ru/novosti-novosti/?id=18741) | `S64__dmitriy_yadrov_vruchil_sertifikaty_tipa_na_il_114_300_i_pd.html` | P1 |
| **S65** | Ростех / ОАК — SSJ-100 получили одобрение главного изменения типовой конструкции | 12.10.2026 | [Открыть](https://www.rostec.ru/media/news/samolety-ssj-100-poluchili-odobrenie-glavnogo-izmeneniya-tipovoy-konstruktsii/) | [HTML](https://www.rostec.ru/media/news/samolety-ssj-100-poluchili-odobrenie-glavnogo-izmeneniya-tipovoy-konstruktsii/) | `S65__ssj_100_poluchili_odobrenie_glavnogo_izmeneniya_tipovoy_ko.html` | P2 |
| **S66** | ПАО «Яковлев» — SJ-100: продуктовая страница | не установлен; страница изменяемая | [Открыть](https://yakovlev.ru/products/sj-100/) | [HTML](https://yakovlev.ru/products/sj-100/) | `S66__sj_100_produktovaya_stranitsa.html` | P1 |
| **S67** | Авиация России, со ссылкой на интервью «Вести» — Первые SJ-100 и МС-21 передадут авиакомпаниям во второй половине 2027 года | объявленный план 2027 | [Открыть](https://aviation21.ru/pervye-sj-100-i-ms-21-peredadut-aviakompaniyam-vo-vtoroj-polovine-2027-goda/) | [HTML](https://aviation21.ru/pervye-sj-100-i-ms-21-peredadut-aviakompaniyam-vo-vtoroj-polovine-2027-goda/) | `S67__pervye_sj_100_i_ms_21_peredadut_aviakompaniyam_vo_vtoroy_p.html` | P2 |
| **S68** | Росавиация — Общественный совет оценил перспективные планы отечественного авиастроения | план на 2026 из 2025 года | [Открыть](https://favt.gov.ru/novosti-novosti?id=17091) | [HTML](https://favt.gov.ru/novosti-novosti?id=17091) | `S68__obschestvennyy_sovet_otsenil_perspektivnye_plany_otechestv.html` | P2 |

## Расписания

**Папка для сохранения:** `data/raw/schedules/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S19** | Аэропорт Кольцово — Сезонное расписание вылетов | осень–зима 2026/27 | [Открыть](https://ar-svx.ru/schedule/) | [HTML](https://ar-svx.ru/schedule/) | `S19__koltsovo_schedule_winter_2026.html` | P0 |
| **S20** | Аэропорт Гагарин — Расписание рейсов из Саратова | осень–зима 2026/27 | [Открыть](https://ar-gsv.ru/schedule/) | [HTML](https://ar-gsv.ru/schedule/) | `S20__saratov_schedule_winter_2026.html` | P0 |
| **S21** | Омский аэропорт — Сезонное расписание «Зима 2026» | зима 2026/27 | [Открыть](https://www.aeroomsk.ru/karta-poleta/) | [PDF](https://www.aeroomsk.ru/karta-poleta/pdf/w26/w26-20261105.pdf) | `S21__omsk_schedule_20261105.pdf` | P0 |

## Аэропорты и пассажиропоток

**Папка для сохранения:** `data/raw/airports/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S23** | Омский аэропорт — Итоги производственной деятельности за 2025 год | 2025 | [Открыть](https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/253/) | [HTML](https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/253/) | `S23__itogi_proizvodstvennoy_deyatelnosti_za_2025_god.html` | P0 |
| **S24** | Омский аэропорт — Пассажиропоток Омского аэропорта в 2024 году составил 1 726 029 человек | 2023–2024 | [Открыть](https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/210/) | [HTML](https://www.aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/210/) | `S24__passazhiropotok_omskogo_aeroporta_v_2024_godu_sostavil_1_7.html` | P2 |
| **S25** | Омский аэропорт — Омский аэропорт обслужил в 2023 году 1 680 206 человек | 2023 | [Открыть](https://aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/142/) | [HTML](https://aeroomsk.ru/ob-aeroporte/press-tsentr/novosti/142/) | `S25__omskiy_aeroport_obsluzhil_v_2023_godu_1_680_206_chelovek.html` | P2 |
| **S26** | Аэропорт Уфа — Международный аэропорт «Уфа» подвел итоги 2025 года | 2025 | [Открыть](https://www.airportufa.ru/news/2025/mezhdunarodnyy-aeroport-ufa-podvel-itogi-2025-goda/) | [HTML](https://www.airportufa.ru/news/2025/mezhdunarodnyy-aeroport-ufa-podvel-itogi-2025-goda/) | `S26__mezhdunarodnyy_aeroport_ufa_podvel_itogi_2025_goda.html` | P0 |
| **S27** | Аэропорт Пермь, официальный канал — Итоги пассажиропотока за 2025 год | 2025 | [Открыть](https://t.me/s/permairport?before=347) | [HTML](https://t.me/s/permairport?before=347) | `S27__itogi_passazhiropotoka_za_2025_god.html` | P0 |
| **S28** | AEX / AviaStat со ссылкой на аэропорт Рощино — Пассажиропоток аэропорта Рощино за 2025 год превысил 2,76 млн человек | 2025 | [Открыть](https://www.aex.ru/news/2026/1/14/291500/) | [HTML](https://www.aex.ru/news/2026/1/14/291500/) | `S28__passazhiropotok_aeroporta_roschino_za_2025_god_prevysil_2.html` | P1 |
| **S29** | Аэропорт Челябинск, официальный канал — Итоги пассажиропотока за 2025 год | 2025 | [Открыть](https://t.me/s/cekport_tg/410) | [HTML](https://t.me/s/cekport_tg/410) | `S29__itogi_passazhiropotoka_za_2025_god.html` | P0 |
| **S30** | Западно-Сибирское МТУ Росавиации — Итоги года аэропортов Западной Сибири | 2025 | [Открыть](https://zs-m.favt.ru/novosti-novosti/?id=12414) | [HTML](https://zs-m.favt.ru/novosti-novosti/?id=12414) | `S30__itogi_goda_aeroportov_zapadnoy_sibiri.html` | P0 |
| **S31** | Аэропорт Красноярск, KJA TEAM — Производственные итоги за 2025 год | 2025 | [Открыть](https://team.kja.aero/media/aeroport-krasnoyarsk-po-itogam-2025-goda-1-1) | [HTML](https://team.kja.aero/media/aeroport-krasnoyarsk-po-itogam-2025-goda-1-1) | `S31__proizvodstvennye_itogi_za_2025_god.html` | P0 |
| **S32** | Международный аэропорт Иркутск — Подводим итоги за 9 месяцев 2025 года | январь–сентябрь 2025 | [Открыть](https://www.iktport.ru/ru/about/novosti/726-подводим-итоги-за-9-месяцев-2025-года) | [HTML](https://www.iktport.ru/ru/about/novosti/726-подводим-итоги-за-9-месяцев-2025-года) | `S32__podvodim_itogi_za_9_mesyatsev_2025_goda.html` | P2 |
| **S33** | Международный аэропорт Иркутск — Почти миллион пассажиров и более 7 млн кг багажа: итоги лета | июнь–август 2026 | [Открыть](https://iktport.ru/ru/about/novosti/799-почти-миллион-пассажиров-и-более-7-млн-кг-багажа-аэропорт-иркутска-подвёл-итоги-работы-за-лето) | [HTML](https://iktport.ru/ru/about/novosti/799-почти-миллион-пассажиров-и-более-7-млн-кг-багажа-аэропорт-иркутска-подвёл-итоги-работы-за-лето) | `S33__pochti_million_passazhirov_i_bolee_7_mln_kg_bagazha_itogi.html` | P2 |
| **S34** | Аэропорт Гагарин — В 2025 году аэропорт «Гагарин» обслужил 1 млн 64 тыс. пассажиров | 2025 | [Открыть](https://ar-gsv.ru/about/news/v-2025-godu-aeroport-gagarin-obsluzhil-1-mln-64-tys-passazhi/) | [HTML](https://ar-gsv.ru/about/news/v-2025-godu-aeroport-gagarin-obsluzhil-1-mln-64-tys-passazhi/) | `S34__v_2025_godu_aeroport_gagarin_obsluzhil_1_mln_64_tys_passaz.html` | P0 |
| **S35** | Аэропорт Оренбург — Аэропорт Оренбург обслужил за 2025 год более 950 тысяч пассажиров | 2025 | [Открыть](https://ar-ren.ru/about/news/aeroport-orenburg-obsluzhil-za-2025-god-bolee-950/) | [HTML](https://ar-ren.ru/about/news/aeroport-orenburg-obsluzhil-za-2025-god-bolee-950/) | `S35__aeroport_orenburg_obsluzhil_za_2025_god_bolee_950_tysyach.html` | P0 |
| **S36** | Аэропорт Курумоч — Итоги работы в новогодние праздники — текст содержит итоги 2025 года | 2025 | [Открыть](https://ar-kuf.ru/about/news/itogi-raboty-v-novogodnie-prazdnik/) | [HTML](https://ar-kuf.ru/about/news/itogi-raboty-v-novogodnie-prazdnik/) | `S36__itogi_raboty_v_novogodnie_prazdniki_tekst_soderzhit_itogi.html` | P0 |
| **S37** | Аэропорт Курумоч — Пассажиропоток аэропорта Курумоч превысил 3,5 миллиона человек | 2024 | [Открыть](https://ar-kuf.ru/about/news/passazhiropotok-aeroporta-kurumoch-prevysil-3-5-milliona-che/) | [HTML](https://ar-kuf.ru/about/news/passazhiropotok-aeroporta-kurumoch-prevysil-3-5-milliona-che/) | `S37__passazhiropotok_aeroporta_kurumoch_prevysil_3_5_milliona_c.html` | P2 |
| **S38** | Официальный портал правовой информации Татарстана — Муниципальный документ об итогах работы Казани в 2025 году; полное название не извлечено | 2025 | [Открыть](https://pravo.tatarstan.ru/file/npa/2026-02/1794855/npa_1794856.pdf) | [PDF](https://pravo.tatarstan.ru/file/npa/2026-02/1794855/npa_1794856.pdf) | `S38__munitsipalnyy_dokument_ob_itogakh_raboty_kazani_v_2025_god.pdf` | P0 |
| **S39** | Аэропорт Нижнего Новгорода — За 2025 год выросло количество нижегородцев, летавших за рубеж | 2025 | [Открыть](https://ar-goj.ru/about/news/za-2025-god-vyroslo-kolichestvo-nizhegorodtsev-letavshikh-za/) | [HTML](https://ar-goj.ru/about/news/za-2025-god-vyroslo-kolichestvo-nizhegorodtsev-letavshikh-za/) | `S39__za_2025_god_vyroslo_kolichestvo_nizhegorodtsev_letavshikh.html` | P0 |
| **S40** | Аэропорт Кольцово — Развитие инфраструктуры, новые сервисы и рост пассажиропотока: итоги 2025 года | 2025 | [Открыть](https://ar-svx.ru/about/news/razvitie-infrastruktury-novye-servisy-i-rost-passazhiropotok/) | [HTML](https://ar-svx.ru/about/news/razvitie-infrastruktury-novye-servisy-i-rost-passazhiropotok/) | `S40__razvitie_infrastruktury_novye_servisy_i_rost_passazhiropot.html` | P0 |
| **S41** | Финмаркет / Интерфакс, пресс-служба аэропорта — Аэропорт Минвод в 2025 году снизил пассажиропоток на 4,6% | 2025; инфраструктурные планы 2026–2028 | [Открыть](https://www.finmarket.ru/news/6545429) | [HTML](https://www.finmarket.ru/news/6545429) | `S41__aeroport_minvod_v_2025_godu_snizil_passazhiropotok_na_4_6.html` | P1 |
| **S52** | Омский аэропорт — Коды и характеристики | страница на дату проверки | [Открыть](https://www.aeroomsk.ru/aviakompaniyam/kody-i-kharakteristiki/) | [HTML](https://www.aeroomsk.ru/aviakompaniyam/kody-i-kharakteristiki/) | `S52__kody_i_kharakteristiki.html` | P0 |

## Росстат и демография

**Папка для сохранения:** `data/raw/demography/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S42** | Росстат — Численность населения РФ по муниципальным образованиям | на 01.01.2025; каталог также содержит 2024 | [Открыть](https://rosstat.gov.ru/folder/12781?print=1&source=subscribe) | **не найден** | `S42__rosstat_population_catalog_2025.html` | P0 |
| **S43** | Росстат — Россия 2025: крупнейшие города | население на 01.01.2024 | [Открыть](https://rosstat.gov.ru/storage/mediabank/Rossia_2025.pdf) | [PDF](https://rosstat.gov.ru/storage/mediabank/Rossia_2025.pdf) | `S43__rosstat_russia_2025.pdf` | P0 |

## Субсидии и право

**Папка для сохранения:** `data/raw/regulation/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S44** | Росавиация — Господдержка региональных перевозок; решение № 22-64160-00191-Р, версия 7 | порядок предоставления субсидии | [Открыть](https://favt.gov.ru/dejatelnost-gosudarstvennaia-podderzhka-subsidii/?id=15106) | [PDF](https://favt.ru/public/materials/0/3/9/e/7/039e77a7205ca81e3070590870e45a3e.pdf) | `S44__rosaviation_subsidy_rules_v7.pdf` | P0 |
| **S45** | Росавиация — Региональное субсидирование перевозок: перечни 2024–2026 | 2024–2026 | [Открыть](https://favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony/?from=old-site) | [HTML](https://favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony/?from=old-site) | `S45__subsidised_routes_2026.html` | P0 |
| **S46** | Росавиация, архив нормативных материалов — Правила по постановлению Правительства РФ от 25.12.2013 № 1242, историческая редакция | редакция включает изменения до 14.11.2018 | [Открыть](https://old.favt.gov.ru/dejatelnost-vozdushnye-perevozki-subsidirovanie-regiony) | [PDF](https://old.favt.gov.ru/public/materials/0/d/2/d/a/0d2da0ba156a854e116346650116d1d5.pdf) | `S46__pravila_po_postanovleniyu_pravitelstva_rf_ot_25_12_2013_12.pdf` | P2 |
| **S47** | КонсультантПлюс — Постановление № 1242, редакция 14.10.2023: отметка об утрате силы | правовой статус на дату проверки | [Открыть](https://www.consultant.ru/document/cons_doc_LAW_156427/) | [HTML](https://www.consultant.ru/document/cons_doc_LAW_156427/) | `S47__postanovlenie_1242_redaktsiya_14_10_2023_otmetka_ob_utrate.html` | P2 |
| **S55** | Росавиация — Ставки сборов за аэронавигационное обслуживание: приказ ФАС № 595/24 | редакция 2024 | [Открыть](https://favt.gov.ru/dejatelnost-ajeronavigacionnoe-obsluzhivanie-stavki-sborov/) | [HTML](https://favt.gov.ru/dejatelnost-ajeronavigacionnoe-obsluzhivanie-stavki-sborov/) | `S55__stavki_sborov_za_aeronavigatsionnoe_obsluzhivanie_prikaz_f.html` | P2 |
| **S56** | ГАРАНТ — Приказ ФАС от 16.12.2025 № 1101/25 о ставках АНО | 2026 | [Открыть](https://base.garant.ru/413529528/) | [HTML](https://base.garant.ru/413529528/) | `S56__prikaz_fas_ot_16_12_2025_1101_25_o_stavkakh_ano.html` | P2 |

## Сборы и расходы аэропортов

**Папка для сохранения:** `data/raw/costs/`

| ID | Что скачивать | Период | Страница | Прямо | Имя файла | Приоритет |
|---|---|---|---|---|---|---|
| **S48** | АО «СарАэро-Инвест» — Прейскурант для российских потребителей по состоянию на 21.12.2025 с изменениями от 01.08.2026 | редакция 01.08.2026 | [Открыть](https://ar-gsv.ru/about/info/) | [PDF](https://ar-gsv.ru/upload/iblock/e03/x30km5z81eqnv9f1mhqs3im92866fzqy/Preyskurant-AO-SarAero_Invest-dlya-rossiyskikh-ekspluatantov-s-21.12.2025-_s-izmeneniyami-s-01.08.2026_.pdf) | `S48__saratov_tariffs_20260801.pdf` | P0 |
| **S49** | Омский аэропорт — Прейскурант для российских потребителей с 21.08.2026 | с 21.08.2026 | [Открыть](https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/) | [PDF](https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/tarifs_rus_20260821.pdf) | `S49__omsk_tariffs_20260821.pdf` | P0 |
| **S50** | Омский аэропорт — Изменения к прейскуранту с 10.10.2026 | с 10.10.2026 | [Открыть](https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/) | [PDF](https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/pr568-2026.pdf) | `S50__omsk_tariffs_amendment_20261010.pdf` | P0 |
| **S51** | Омский аэропорт — Изменения к прейскуранту с 15.10.2026 | с 15.10.2026 | [Открыть](https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/) | [PDF](https://www.aeroomsk.ru/aviakompaniyam/stavki-i-tarify/2026/pr610-2026.pdf) | `S51__omsk_tariffs_amendment_20261015.pdf` | P0 |
| **S53** | Аэропорт Курумоч — Основные показатели ФХД СЕМ за 2025–2027 годы | 2025 — факт; 2026–2027 — прогноз | [Открыть](https://ar-kuf.ru/about/info/) | [PDF](https://ar-kuf.ru/upload/iblock/964/ugdj79k4p95x7qjgpy17rokry33zngn4/Osnovnye-pokazateli-FKHD-SEM-v-sfere-okazaniya-reguliruemykh-uslug-za-2025_2027-gg.pdf) | `S53__osnovnye_pokazateli_fkhd_sem_za_2025_2027_gody.pdf` | P1 |
| **S54** | Аэропорт Нижнего Новгорода — Отчёт об инвестиционной программе за 2024 год, формы 3а–г | 2024 | [Открыть](https://goj.aero/upload/iblock/54c/i3h4wxp5659sjwweyoixytoq5ntss6t8/Investitsionnaya-programma-otchyet-po-formam-3a_b_v_g-za-2024-g.pdf) | [PDF](https://goj.aero/upload/iblock/54c/i3h4wxp5659sjwweyoixytoq5ntss6t8/Investitsionnaya-programma-otchyet-po-formam-3a_b_v_g-za-2024-g.pdf) | `S54__otchyot_ob_investitsionnoy_programme_za_2024_god_formy_3a.pdf` | P2 |

## Когда документ получен

1. **Не переписывать числовые значения из отчёта в `raw`.** Скачивать исходный файл/HTML с публикации. Имя сохранения — из таблицы, а полный путь — из CSV.
2. Обновить в CSV `download_status` на `downloaded` только после **физического появления** документа. Если блокировка, CAPTCHA или страница без таблиц — оставить `not_downloaded`, указать проблему в заметке.
3. Если издатель обновил документ, **не перезаписывать молча**: новый URL/редакция → новая строка/версия. Никаких обязательных хешей.
4. Codex извлекает из каждого оригинала *полную относящуюся к делу таблицу* в `data/processed/`. В каждой записи нужны `source_id`, `raw_path`, период, единица, точная страница/строка. Публикация числа ≠ O&D спрос.
5. Структурированные выводы оформлять в `analysis/*.md`, со ссылками на исходные документы; не выдавать смоделированную загрузку за реальные пассажирские потоки.

## Критические отсутствующие данные

| Что нужно | Есть ли полноценный набор среди S01–S71? | Примечание |
|---|---|---|
| Полные конечные поездки O&D между кандидатными парами | **Нет** | Опубликованный поток на линии не раскрывает конечный пункт пассажира |
| Фактические пассажиры/занятость **по каждому рейсу** Red Wings | **Нет** | Расписание показывает предложение, а не выполненные перевозки |
| Реализованная средняя выручка по паре | **Нет** | Рекламная цена «от» не является средним тарифом |
| Доступный резерв исправных ВС и экипажей | **Нет** | Заявленный парк и планы поставок не равны свободному ресурсу |
| Полная себестоимость полёта и новой базы | **Нет** | Аэропортовые сборы — одна часть расходной модели |
| Подписанные будущие субсидии Red Wings | **Нет** | Наличие программы 2026 не равно договору на 2027–2028 |
