# Источники

Исходники не изменяются. scripts/prepare-data.ts использует csv-parse и Zod, читает относительно своего файла. JSON всегда генерируется перед dev/build/generate, исключён из Git. metadata: schemaVersion, gitSha, dataRevision, SHA256 прочитанных CSV, конфликты координат.

Основные пути: data/airport_research/processed/{airports,route_airports,airport_routes,airport_annual,airport_monthly}.csv. airports.csv приоритетен над внешними конечными точками. Пустые значения — null, не 0. Исторические строки хранятся раздельно; слой карты показывает первую строку для неориентированной пары в выбранном году, не суммирует зеркала или окна. Не является расписанием 2026.

Реестр data/airport_research/sources/sources.csv и документация DATA_LINEAGE.csv, ROUTE_KEYS.csv, ROUTE_QUALIFIERS.csv сохраняют происхождение мер. observed означает опубликованное по реестру, без независимой новой проверки. DATA_GAPS.md и DATA_CONFLICTS.md описывают пробелы и конфликты. Годовые/месячные значения не используются как O&D конкретного маршрута.

Экономика и базы: analysis/calculate.py, HUB_STRATEGY.md, HUB_CANDIDATES.md. Флот по presentation/slides.md — срез презентации, доступность не подтверждена. data/redwings_research/RED_WINGS_FLEET.md пуст и не подтверждает характеристики.

Каталог: https://flyredwings.com/about/park/ — проверен 13.11.2026: SSJ100 100/4200 км, Ту-204-100В 210/3800, Ту-214 194/5200, B777-200ER 412/9100. Вместимость SSJ100 99 из Python исправлена на 100, исходные исторические наблюдения не переписываются. SJ-100/ПД-8 не приравнивается к SaM146. Проверки ВПП не являются эксплуатационным допуском.

Груз: data/cargo_research/estimates/assumptions.csv, scenarios.csv и documentation/METHODOLOGY.md. Все коммерческие ставки scenario; аэропортовые тонны и Sky Gates не используются как доступный груз.

Карта: MapLibre GL JS (BSD-3-Clause); внешний стиль https://tiles.openfreemap.org/styles/positron, OpenFreeMap / OpenMapTiles / OpenStreetMap, атрибуция встроена. При недоступности сети нейтральный локальный фон с аэропортами и ортодромиями, явно обозначенный как схема; внешняя геометрия в fallback не используется, лицензия сторонних контуров не требуется. При отсутствии WebGL остаются таблица и расчёт.

Официальная документация стека: https://nuxt.com/docs/4.x/getting-started/installation, https://ui.nuxt.com/docs/getting-started/installation/nuxt, https://openfreemap.org/quick_start/.
