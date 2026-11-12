# Навигация по проекту Red Wings

Краткий указатель файлов и папок репозитория. Основной маршрут чтения: **задание → источники и данные → анализ → расчёты → материалы сдачи**.

## С чего начать

- [Модель по шагам](MODEL.md), [настройки](data/model_parameters.json), [калькулятор](scripts/simulate_strategy.py) и [текст двух слайдов](submission/model-slides.md).

| Файл | Суть |
|---|---|
| [README.md](README.md) | Краткое изложение решения, ключевые числа и команды для воспроизведения расчётов. |
| [FORMULAS.md](FORMULAS.md) | Краткий список формул, происхождение чисел и ссылки на расчётные файлы. |
| [analysis/10-updated-brief-alignment.md](analysis/10-updated-brief-alignment.md) | Проверка того, насколько проект покрывает уточнённую цель №2, цифровые сервисы и общую коммерческую стратегию. |
| [analysis/11-repo-audit-2026-11-10.md](analysis/11-repo-audit-2026-11-10.md) | Локальный аудит состояния проекта и зафиксированные ограничения проверок. Файл уже находился в рабочем дереве; его не следует считать новым результатом этой навигации. |
| [analysis/12-improvement-plan.md](analysis/12-improvement-plan.md) | Приоритетный перечень необходимых доработок и того, что не следует удалять. |
| [submission/README.md](submission/README.md) | Состав комплекта сдачи, содержание артефактов, их известные ограничения и инструкции по пересборке. |

## Требования и контекст кейса — `case/`

| Файл или папка | Суть |
|---|---|
| [case/CASE_BRIEF.md](case/CASE_BRIEF.md) | Подробное исходное задание: рейтинг городов, конкуренты, H1/H2, расчёты, карта, дорожная карта и формат защиты. Сохраняет силу, пока организаторы явно его не отменили. |
| [case/CLARIFICATION_2026-11-10.md](case/CLARIFICATION_2026-11-10.md) | Переданное команде уточнение: целевая концепция роста до позиции №2 и единая работа сети, цифровых сервисов и коммерции. Метрика и срок достижения в сообщении не заданы. |
| [case/README.md](case/README.md) | Указатель исходных материалов кейса. |
| `case/assets/` | Исходная инфографика кейса; содержит числа, методика которых в самом изображении не раскрыта. |
| `case/templates/` | Оригинальный шаблон паспорта проекта. |

## Аналитика — `analysis/`

| Файл или папка | Суть |
|---|---|
| [analysis/README.md](analysis/README.md) | Указатель аналитических документов. |
| [analysis/05-baseline.md](analysis/05-baseline.md) | Фактическая база и разграничение типов потоков и сценарных параметров. |
| [analysis/06-city-ranking.md](analysis/06-city-ranking.md) | Рейтинг десяти городов, критерии, веса и чувствительность результата. |
| [analysis/07-route-candidates.md](analysis/07-route-candidates.md) | Исследовательский пул из 18 маршрутных пар для H1 и H2; не является утверждённым расписанием. |
| [analysis/08-strategy-decision.md](analysis/08-strategy-decision.md) | Сравнение хаба H1 в Уфе и прямых рейсов H2 из Екатеринбурга, экономика, ограничения, ресурсы и план измерения. |
| [analysis/09-launch-roadmap.md](analysis/09-launch-roadmap.md) | Условия и риски запуска пилота и расширения H2 до 2028 года. |
| [analysis/10-updated-brief-alignment.md](analysis/10-updated-brief-alignment.md) | Статус покрытия расширенного задания и открытые задачи. |
| [analysis/11-repo-audit-2026-11-10.md](analysis/11-repo-audit-2026-11-10.md) | Сохранённый аудит проверки репозитория; локальная незакоммиченная работа, не перезаписана. |
| [analysis/12-improvement-plan.md](analysis/12-improvement-plan.md) | План приоритетных доработок по несоответствиям и пробелам задания. |
| `analysis/figures/` | PNG-графики и карты, используемые в аналитических материалах: потоки аэропортов, баллы городов, критерии, покрытие маршрутных свидетельств, сравнение стратегий и карты сети. |

## Источники и таблицы — `data/`

| Файл или папка | Суть |
|---|---|
| [data/README.md](data/README.md) | Вход в каталог подготовленных данных и реестр источников. |
| [data/SOURCE_MANIFEST.md](data/SOURCE_MANIFEST.md) | Читаемый каталог публикаций с `source_id`, периодами и ссылками. |
| [data/source_manifest.csv](data/source_manifest.csv) | Машиночитаемая версия метаданных источников для скриптов. Это не лишний дубль Markdown: форматы предназначены для разных задач. |
| [data/processed/README.md](data/processed/README.md) | Обзор подготовленных таблиц, происхождения и различий между видами потоков. |
| `data/processed/core/` | Четыре основные входные таблицы модели: `airports.csv` (показатели аэропортов), `route_passengers.csv` (потоки по линиям), `current_routes.csv` (маршруты и частоты), `market.csv` (рынок и перевозчики). |
| `data/processed/airports/` | `attributes.csv`, `metrics.csv`, `relations.csv`, `sources.csv`: характеристики, показатели и связи аэропортов с источниками. |
| `data/processed/airlines/` | `attributes.csv`, `fares.csv`, `metrics.csv`, `relations.csv`, `routes.csv`, `sources.csv`, `tariff_rules.csv`: флот, показатели, маршруты и тарифные сведения авиакомпаний. |
| [data/processed/airlines/README.md](data/processed/airlines/README.md#статистика-аэрофлота-s72) | Описание S72: группа и авиакомпания Аэрофлот, январь 2014 — февраль 2025; поля, единицы, пропуски, исправление заголовка периода и сохранённые расхождения. Данные не включены в модель H1/H2. |
| [data/processed/airlines/aeroflot_traffic_monthly.csv](data/processed/airlines/aeroflot_traffic_monthly.csv) | S72: абсолютные показатели отдельных месяцев, оба субъекта и три охвата перевозок. |
| [data/processed/airlines/aeroflot_traffic_ytd.csv](data/processed/airlines/aeroflot_traffic_ytd.csv) | S72: абсолютные показатели с начала года; не суммировать с месячными. |
| [data/processed/airlines/aeroflot_traffic_monthly_yoy.csv](data/processed/airlines/aeroflot_traffic_monthly_yoy.csv) | S72: опубликованные изменения отдельных месяцев к прошлому году; проценты, п.п. и кратности различаются. |
| [data/processed/airlines/aeroflot_traffic_ytd_yoy.csv](data/processed/airlines/aeroflot_traffic_ytd_yoy.csv) | S72: опубликованные изменения накопленных показателей к прошлому году; расхождения с месячным блоком сохранены. |
| `data/processed/flights/` | `russia_domestic_flights_2025.csv` и `scheduled_departures_winter_2026_27.csv`: опубликованные рейсы и варианты расписаний. Строка расписания не доказывает выполненный рейс. |
| `data/processed/market/` | `articles.csv`, `S02.csv`, `S03_image13.csv`, `S05_pages.csv`, `sources.csv`: извлечённые отраслевые сведения и записи источников. |
| `data/processed/schedules/` | `S19.csv` и `S20.csv`: сохранённые расписания из источников реестра. |
| `data/raw/` | Локальные исходники, если они есть у владельца рабочего дерева. Каталог исключён из Git по правилам проекта; не публиковать и не добавлять в удалённый репозиторий. |

## Расчётные результаты — `results/`

[Анализ Аэрофлота S72](analysis/13-aeroflot-benchmark.md) — масштаб, сезонность пассажиров и груза,
коммерческие проверки для H2 и ограничения применения. Воспроизведение:
[scripts/analyze_aeroflot_traffic.py](scripts/analyze_aeroflot_traffic.py), независимая проверка:
[scripts/check_aeroflot_analysis.py](scripts/check_aeroflot_analysis.py).
[results/aeroflot/README.md](results/aeroflot/README.md) описывает четыре расчётных CSV;
[график сезонности](analysis/figures/aeroflot_seasonality.png) строится из этих данных.

Таблицы в этом каталоге являются выходами расчётов; значения следует читать вместе с периодами, единицами и ограничениями в аналитике.

| Файл или папка | Суть |
|---|---|
| `results/cities/city_inputs.csv` | Входные показатели для рейтинга городов. |
| `results/cities/city_ranking.csv` | Итоговый рейтинг и варианты чувствительности. |
| `results/cities/criteria_scores.csv` | Критерии, веса и оценки городов. |
| `results/routes/route_candidates.csv` | Кандидатные маршрутные пары, показатели и свидетельства. |
| `results/strategy/assumptions.csv` | Общие допущения модели. |
| `results/strategy/controlled_comparison.csv` | Контрольный вариант методики сравнения. |
| `results/strategy/decision_thresholds.csv` | Пороговые условия и чувствительность выбора. |
| `results/strategy/fact_references.csv` | Связи ключевых фактов с источниками и локаторами. |
| `results/strategy/hypothesis_comparison.csv` | Сводное сравнение H1/H2 по годам и сценариям. |
| `results/strategy/pilot_2027_rotations.csv` | Недельные ротации пилотной программы. |
| `results/strategy/route_assumptions.csv` | Исходные предпосылки по маршрутам и частотам. |
| `results/strategy/route_scenarios.csv` | Сценарные показатели по отдельным маршрутам. |
| `results/strategy/sensitivity.csv` | Анализ чувствительности к ключевым параметрам. |
| `results/strategy/stress_tests.csv` | Стресс-сценарии, включая задержку начала программы. |
| `results/strategy/transfer_scenarios.csv` | Сценарии пересадочных связок гипотезы H1. |
| `results/strategy/weekly_rotations.csv` | Недельные ротации полной программы. |

## Исследования — `research/`

| Файл или папка | Суть |
|---|---|
| [research/README.md](research/README.md) | Указатель исследований и пояснение, что они не являются первичными источниками. |
| [research/reports/NEW-DR-01-REPORT-RU.md](research/reports/NEW-DR-01-REPORT-RU.md) | Исследовательский отчёт по первичным данным и свидетельствам. |
| [research/reports/NEW-DR-02-REPORT-RU.md](research/reports/NEW-DR-02-REPORT-RU.md) | Исследовательский отчёт по практике авиакомпаний и методологии. |

## Скрипты и среда

| Файл | Суть |
|---|---|
| [scripts/simulate_strategy.py](scripts/simulate_strategy.py) | Калькулятор рейсов и рейтинга городов. [Режим городов](MODEL.md#режим-рейтинга-городов). |
| [scripts/rank_cities.py](scripts/rank_cities.py) | Пересчитывает рейтинг городов и связанные графики/аналитику. |
| [scripts/compare_growth_strategies.py](scripts/compare_growth_strategies.py) | Рассчитывает варианты H1/H2, сценарии, ресурс и маршрутные результаты. |
| [scripts/check_strategy.py](scripts/check_strategy.py) | Независимые проверки арифметики и предметных ограничений модели. |
| [scripts/parse_aeroflot_traffic.py](scripts/parse_aeroflot_traffic.py) | Разбирает локальный XLS S72 в четыре CSV; `--check` сверяет готовую выгрузку без перезаписи. Команды — в README авиакомпаний; `xlrd==2.0.2` подключается временно через uv. |
| [scripts/build_defense.py](scripts/build_defense.py) | Собирает PDF и таблицы сдачи по сохранённым результатам. Пересборка может перезаписать артефакты. |
| [pyproject.toml](pyproject.toml), [uv.lock](uv.lock), [.python-version](.python-version) | Зависимости, lock-файл и версия Python проекта. |
| [AGENTS.md](AGENTS.md) | Правила работы с данными, расчётами, отчётами и изменениями проекта. |
| `.gitignore` | Исключает локальное окружение, кеши, IDE-файлы и `data/raw/` из Git. |

## Комплект сдачи — `submission/`

| Файл или папка | Суть |
|---|---|
| [submission/README.md](submission/README.md) | Состав сдачи, ограничения и состояние PDF. |
| [submission/project-passport.pdf](submission/project-passport.pdf) | Паспорт предложения; зафиксированное число страниц — 3 при требовании 1–2. |
| [submission/presentation.pdf](submission/presentation.pdf) | Презентация к защите; 8 слайдов при разрешённых 5–8. |
| [submission/route-map.pdf](submission/route-map.pdf) | Одностраничная карта выбранных маршрутных пар. |
| [submission/routes.md](submission/routes.md), [submission/routes.csv](submission/routes.csv) | Читаемое и машиночитаемое представление выбранных маршрутов. |
| [submission/speaker-notes.md](submission/speaker-notes.md) | Текст защиты по слайдам; фактическую длительность нужно проверить репетицией. |
| [submission/strategy-baseline.csv](submission/strategy-baseline.csv) | Сохранённая база пассажиропотока компаний для рабочего сравнения позиции №2. |
| `submission/templates/` | Предыдущие образцы оформления, не финальные материалы сдачи. |

## Локальные и игнорируемые каталоги

`.venv/`, `.idea/` и Python-кеши относятся к локальной среде, а не к содержанию проекта; они не входят в этот индекс как материалы решения. Не удаляйте и не публикуйте локальные файлы без отдельной необходимости. Новые документы в рамках этой задачи создаются только в рабочем дереве; отправка в удалённый репозиторий не выполняется.
