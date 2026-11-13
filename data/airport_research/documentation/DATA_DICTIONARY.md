# Словарь данных

Пустая ячейка означает неизвестное. Ни `0`, ни строка unknown не заменяют отсутствующее число. В scenario возможен явно выбранный ноль; он не является наблюдением. Строковые идентификаторы и коды не следует преобразовывать в числа. Все поля `notes` — текст.

Основные ключи: см. README. Единица каждой количественной колонки указана ниже; исходные raw имеют собственные схемы и не считаются нормализованными.

## documentation/CARGO_SCOPE_OBSERVATIONS.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `value` | number? | Численное значение метрики в unit |
| `unit` | string? | Единица; person/movement/departure/arrival/aircraft/flight/tonne/seat/percent |
| `qualifier` | string? | Оригинальный признак округления или границы |
| `observation_id` | string? | A_R/B_R/C_R + физическая CSV-строка исходного файла (заголовок=1) |
| `source_ids` | string? | Список source_id через ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## documentation/COVERAGE.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `annual_rows` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `monthly_rows` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `historical_route_observations` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `red_wings_observations` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `route_census_complete` | string enum | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `infrastructure_historical_verified` | string enum | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## documentation/DATA_CONFLICTS.csv

| Колонка | Тип | Значение |
|---|---|---|
| `entity_id` | string? | IATA; для груза IATA|scope; для ВПП IATA|runway_id; для маршрута route_id; для рынка airline |
| `period` | string? | YYYY / YYYY-MM; static или ISO-дата для справочников |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `selected_value` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `alternative_value` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `reason` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |

## documentation/DATA_LINEAGE.csv

| Колонка | Тип | Значение |
|---|---|---|
| `entity_type` | string? | Тип сущности для соединения происхождения |
| `entity_id` | string? | IATA; для груза IATA|scope; для ВПП IATA|runway_id; для маршрута route_id; для рынка airline |
| `period` | string? | YYYY / YYYY-MM; static или ISO-дата для справочников |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `source_ids` | string? | Список source_id через ; |
| `estimate_id` | string? | Уникальный ID расчёта E000001… |
| `method` | string? | Стабильное имя метода расчёта/импорта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## documentation/INPUT_OBSERVATIONS.csv

| Колонка | Тип | Значение |
|---|---|---|
| `observation_id` | string? | A_R/B_R/C_R + физическая CSV-строка исходного файла (заголовок=1) |
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `period` | string? | YYYY / YYYY-MM; static или ISO-дата для справочников |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `value` | number? | Численное значение метрики в unit |
| `unit` | string? | Единица; person/movement/departure/arrival/aircraft/flight/tonne/seat/percent |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `qualifier` | string? | Оригинальный признак округления или границы |
| `record_role` | string? | main/alternative из исходного исследования |
| `source_ids` | string? | Список source_id через ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `raw_path` | string? | Путь исходного файла относительно корня набора |
| `raw_csv_row` | integer? | Физический номер строки CSV с заголовком |
| `formula` | string? | Формула или однозначное правило |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## documentation/PASSENGER_RECONCILIATION.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `check` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `annual_value` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `comparison_value` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `difference` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `classification` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## documentation/RAW_MANIFEST.csv

| Колонка | Тип | Значение |
|---|---|---|
| `path` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `bytes` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `sha256` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |

## documentation/ROUTE_KEYS.csv

| Колонка | Тип | Значение |
|---|---|---|
| `route_id` | string? | Стабильный хеш составного ключа версии расписания |
| `origin_iata` | string? | Аэропорт отправления сегмента, не код города |
| `destination_iata` | string? | Аэропорт назначения сегмента, не код города |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `season` | string? | S/W/published_window/annual_presence; не гарантия круглогодичности |
| `valid_from` | string? | Опубликованное/логически выведенное начало окна в пределах year; для среза может обозначать дату подтверждения |
| `valid_to` | string? | Конец опубликованного окна или этапа частоты; пусто — не установлен |
| `carrier` | string? | Перевозчик; marketing/operator pair явно разделён /; пусто — неизвестно или все перевозчики в агрегате |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |

## documentation/ROUTE_QUALIFIERS.csv

| Колонка | Тип | Значение |
|---|---|---|
| `route_id` | string? | Стабильный хеш составного ключа версии расписания |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `value` | number? | Численное значение метрики в unit |
| `qualifier` | string? | Оригинальный признак округления или границы |
| `low` | integer? | Нижняя граница чувствительности/сценария, не CI |
| `high` | integer? | Верхняя граница чувствительности/сценария, не CI |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## documentation/VALUE_ORIGIN_COUNTS.csv

| Колонка | Тип | Значение |
|---|---|---|
| `entity_type` | string? | Тип сущности для соединения происхождения |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `nonempty_numeric_values` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |

## estimates/assumptions.csv

| Колонка | Тип | Значение |
|---|---|---|
| `assumption_id` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `entity_scope` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `parameter` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `central_value` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `low` | number? | Нижняя граница чувствительности/сценария, не CI |
| `high` | number? | Верхняя граница чувствительности/сценария, не CI |
| `unit` | string? | Единица; person/movement/departure/arrival/aircraft/flight/tonne/seat/percent |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `basis` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `source_ids` | string? | Список source_id через ; |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## estimates/estimates.csv

| Колонка | Тип | Значение |
|---|---|---|
| `estimate_id` | string? | Уникальный ID расчёта E000001… |
| `entity_type` | string? | Тип сущности для соединения происхождения |
| `entity_id` | string? | IATA; для груза IATA|scope; для ВПП IATA|runway_id; для маршрута route_id; для рынка airline |
| `period` | string? | YYYY / YYYY-MM; static или ISO-дата для справочников |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `estimate_value` | number? | Центральное расчётное значение в unit |
| `unit` | string? | Единица; person/movement/departure/arrival/aircraft/flight/tonne/seat/percent |
| `low` | number? | Нижняя граница чувствительности/сценария, не CI |
| `high` | number? | Верхняя граница чувствительности/сценария, не CI |
| `method` | string? | Стабильное имя метода расчёта/импорта |
| `formula` | string? | Формула или однозначное правило |
| `input_observations` | string? | JSON с численными входами и ссылками на исходные наблюдения |
| `source_ids` | string? | Список source_id через ; |
| `confidence` | string? | Качественная уверенность: low/medium/high; не вероятность |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## estimates/seasonal_profiles.csv

| Колонка | Тип | Значение |
|---|---|---|
| `profile_id` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `peer_airport_iata` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `peer_observation_year` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `target_year` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `month` | integer? | Календарный месяц 1–12 |
| `weight` | number? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `peer_passengers` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `source_observation_id` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |

## processed/aircraft_compatibility.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `aircraft_type` | string? | Тип ВС, опубликованный либо оценённый в lineage |
| `as_of_date` | string? | Дата справочного снимка, не автоматическое подтверждение существования в 2024/25 |
| `longest_reference_runway_m` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `screening_threshold_m` | integer? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `length_screen` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `operational_compatibility` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `pcn_acn_check` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `declared_distances_check` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `maintenance_support` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `fuel_supply` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `source_ids` | string? | Список source_id через ; |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airline_market_annual.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airline` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `passengers` | integer? | Перевезённые пассажиры авиакомпании/сегмента, чел. |
| `market_share_pct` | number? | passengers/market_total×100, процентные пункты шкалы 0–100 |
| `scope` | string? | Охват показателя; входит в ключ, несовместимые scope не суммировать |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airport_annual.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `passengers_total` | integer? | Обслуженные пассажиры аэропорта, чел.; охват выбранного источника |
| `passengers_domestic` | integer? | Пассажиры ВВЛ, чел. |
| `passengers_international` | integer? | Пассажиры МВЛ, чел.; СНГ включён в международные |
| `transfer_passengers` | integer? | Пересадочные пассажиры, чел.; не добавлять к общему потоку |
| `transit_passengers` | integer? | Транзитные пассажиры, чел.; определение источника |

## processed/airport_cargo.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `cargo_tonnes` | number? | Груз, т; происхождение разложения проверять в lineage |
| `mail_tonnes` | number? | Почта, т; преимущественно scenario |
| `cargo_mail_total_tonnes` | number? | Совместная масса груза и почты, т; не тонно-километры |
| `scope` | string? | Охват показателя; входит в ключ, несовместимые scope не суммировать |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airport_infrastructure.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `as_of_date` | string? | Дата справочного снимка, не автоматическое подтверждение существования в 2024/25 |
| `runway_id` | string? | Обозначение пары направлений ВПП |
| `runway_length_m` | integer? | Справочная физическая длина, м; не TORA/LDA |
| `runway_width_m` | integer? | Ширина ВПП, м |
| `runway_surface` | string? | Тип покрытия в нормализованном виде |
| `pcn` | string? | Несущая способность покрытия; пусто, если неизвестна |
| `terminal_capacity_pax_year` | integer? | Проектная мощность терминала, пассажиров/год; не фактический трафик и не сумма по ВПП |
| `stand_count` | string? | Общее число мест стоянки; неизвестное не заменяется числом телетрапов |
| `operating_hours` | string? | Часы работы с подтверждённым охватом; пусто, если неизвестны |
| `restrictions` | string? | Известные ограничения или признак необходимости проверки AIP/NOTAM |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airport_inventory.csv

| Колонка | Тип | Значение |
|---|---|---|
| `input_batch` | string? | Имя исходного архивного блока |
| `input_record` | integer? | Позиция внутри блока 1–10 |
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `raw_name` | string? | Наименование ровно из соответствующего исходного блока |
| `canonical_airport_iata` | string? | Канонический IATA после дедупликации |
| `is_duplicate` | string enum | true/false — повтор исходной позиции |
| `duplicate_of` | string? | input_batch:input_record первой позиции |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airport_monthly.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `month` | integer? | Календарный месяц 1–12 |
| `passengers_total` | integer? | Обслуженные пассажиры аэропорта, чел.; охват выбранного источника |
| `passengers_domestic` | integer? | Пассажиры ВВЛ, чел. |
| `passengers_international` | integer? | Пассажиры МВЛ, чел.; СНГ включён в международные |

## processed/airport_operations.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `value` | integer? | Численное значение метрики в unit |
| `unit` | string? | Единица; person/movement/departure/arrival/aircraft/flight/tonne/seat/percent |
| `value_qualifier` | string? | Точность/граница: reported, rounded, exact, gt, estimated и т. п. |
| `definition` | string? | Смысл метрики, не заменяет unit |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airport_routes.csv

| Колонка | Тип | Значение |
|---|---|---|
| `origin_iata` | string? | Аэропорт отправления сегмента, не код города |
| `destination_iata` | string? | Аэропорт назначения сегмента, не код города |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `season` | string? | S/W/published_window/annual_presence; не гарантия круглогодичности |
| `valid_from` | string? | Опубликованное/логически выведенное начало окна в пределах year; для среза может обозначать дату подтверждения |
| `valid_to` | string? | Конец опубликованного окна или этапа частоты; пусто — не установлен |
| `carrier` | string? | Перевозчик; marketing/operator pair явно разделён /; пусто — неизвестно или все перевозчики в агрегате |
| `observation_type` | string? | published_schedule или published_route_presence; тип свидетельства существования, не происхождение всех чисел строки |
| `weekly_departures` | number? | Вылеты из origin за неделю; для симметричной пары совпадает с round trips. Максимумы/оценки различаются через lineage и notes |
| `aircraft_type` | string? | Тип ВС, опубликованный либо оценённый в lineage |
| `seats_per_departure` | integer? | Кресла одного вылета; не фактически занятые места |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/airports.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `airport_name` | string? | Наименование аэропорта |
| `city` | string? | Обслуживаемый город; аэропорты города не объединяются |
| `region` | string? | Субъект РФ |
| `country` | string? | ISO 3166-1 alpha-2 |
| `latitude` | number? | Широта WGS84, градусы |
| `longitude` | number? | Долгота WGS84, градусы |
| `timezone` | string? | IANA zone; применимый региональный пояс |

## processed/infrastructure_attributes.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `as_of_date` | string? | Дата справочного снимка, не автоматическое подтверждение существования в 2024/25 |
| `metric` | string? | Именованная метрика; не смешивать близкие определения |
| `value` | integer? | Численное значение метрики в unit |
| `unit` | string? | Единица; person/movement/departure/arrival/aircraft/flight/tonne/seat/percent |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/market_totals.csv

| Колонка | Тип | Значение |
|---|---|---|
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `passengers` | integer? | Перевезённые пассажиры авиакомпании/сегмента, чел. |
| `scope` | string? | Охват показателя; входит в ключ, несовместимые scope не суммировать |
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `source_locator` | string? | Конкретный абзац/таблица/страница или ID расчёта |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/route_airports.csv

| Колонка | Тип | Значение |
|---|---|---|
| `airport_iata` | string? | IATA исследуемого аэропорта; основной идентификатор |
| `airport_ident` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `airport_name` | string? | Наименование аэропорта |
| `city` | string? | Обслуживаемый город; аэропорты города не объединяются |
| `country` | string? | ISO 3166-1 alpha-2 |
| `latitude` | number? | Широта WGS84, градусы |
| `longitude` | number? | Долгота WGS84, градусы |

## processed/route_capacity.csv

| Колонка | Тип | Значение |
|---|---|---|
| `route_id` | string? | Стабильный хеш составного ключа версии расписания |
| `year` | integer? | Полный календарный год, если иной охват явно не задан |
| `assumed_valid_from` | string? | Начало сценарного окна ёмкости |
| `assumed_valid_to` | string? | Конец сценарного окна ёмкости |
| `weeks` | number? | Число календарных дней окна включительно /7 |
| `weekly_round_trips` | number? | Частота пары, принятая равной вылетам из одного конца |
| `seats_per_departure` | integer? | Кресла одного вылета; не фактически занятые места |
| `two_way_seats` | number? | Модельная ёмкость пары в обе стороны, 2×f×w×q |
| `value_origin` | string? | observed / derived / estimated / scenario |
| `estimate_id` | string? | Уникальный ID расчёта E000001… |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## sources/source_checks.csv

| Колонка | Тип | Значение |
|---|---|---|
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `evidence_status` | string? | Служебное поле; смысл задан названием и контекстом таблицы. JSON-поля читаются через json.loads, численные поля — в единицах строки. |
| `accessed_date` | string? | Дата проверки из текущего прохода или унаследованного реестра; статус отдельно |
| `local_path` | string? | Путь относительно data/airport_research |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## sources/sources.csv

| Колонка | Тип | Значение |
|---|---|---|
| `source_id` | string? | ID источника; в составных ссылках разделитель ; |
| `organization` | string? | Публикатор/владелец исходных данных |
| `title` | string? | Название источника |
| `url` | string? | Прямой исходный URL; пусто только у авторской модели |
| `published_date` | string? | ISO-дата публикации; пусто, если известен лишь год/месяц |
| `accessed_date` | string? | Дата проверки из текущего прохода или унаследованного реестра; статус отдельно |
| `source_type` | string? | Тип источника, не оценка точности каждого его числа |
| `local_path` | string? | Путь относительно data/airport_research |
| `notes` | string? | Краткое пояснение/ограничение; не машинный статус |

## processed/infrastructure_attributes.csv

Ключ: airport_iata+as_of_date+metric. value — опубликованный атрибут в unit; metric различает терминальную часовую мощность, контактные выходы и добавленные в 2024 места нового перрона. Это не общая годовая мощность/общее число стоянок. Остальные колонки совпадают по смыслу с общим словарём.

## documentation/ROUTE_QUALIFIERS.csv

Ключ: route_id+metric. qualifier различает верхнюю границу, центр опубликованного диапазона, оценённую медиану и опубликованную частоту. low/high заполняются только при опубликованном диапазоне/максимуме, пустой low не означает ноль.

## documentation/VALUE_ORIGIN_COUNTS.csv

entity_type, value_origin, nonempty_numeric_values — количество непустых основных числовых мер по происхождению. Не включены категориальные свойства, географический справочник, ёмкость дополнительных сценариев и совместимость.
