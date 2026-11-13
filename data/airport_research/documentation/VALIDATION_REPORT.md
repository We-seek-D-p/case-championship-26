# Результаты валидации

Проверок: 10284. Ошибок структуры/арифметики/ссылок: 0. CSV-файлов: 39.

Число проверок включает построчные проверки ключей, происхождения и сохранения опубликованных месячных ячеек. Это проверка целостности пакета, а не сертификация достоверности первоисточников.

## Ошибки

Не обнаружены.

## Сохранённые расхождения и ограничения

- AER 2025: total-domestic-international=-24547; see PASSENGER_RECONCILIATION
- CEK 2025: total-domestic-international=6268; see PASSENGER_RECONCILIATION
- GOJ 2025: total-domestic-international=-57000; see PASSENGER_RECONCILIATION
- GSV 2024: total-domestic-international=500; see PASSENGER_RECONCILIATION
- GSV 2025: total-domestic-international=400; see PASSENGER_RECONCILIATION
- KJA 2024 passengers_total: sum(months)-annual=-53; published values preserved
- KJA 2024: total-domestic-international=36310; see PASSENGER_RECONCILIATION
- KJA 2025: total-domestic-international=55355; see PASSENGER_RECONCILIATION
- KUF 2025: total-domestic-international=-2000; see PASSENGER_RECONCILIATION
- OVB 2024: total-domestic-international=1000; see PASSENGER_RECONCILIATION
- PEE 2025: total-domestic-international=12984; see PASSENGER_RECONCILIATION
- SVX 2025: total-domestic-international=-15000; see PASSENGER_RECONCILIATION
- UFA 2025: total-domestic-international=29715; see PASSENGER_RECONCILIATION
- VKO 2024 passengers_total: sum(months)-annual=790; published values preserved
- VKO 2024 passengers_domestic: sum(months)-annual=1665; published values preserved
- VKO 2024 passengers_international: sum(months)-annual=-875; published values preserved
- VKO 2025 passengers_total: sum(months)-annual=1373; published values preserved
- VKO 2025 passengers_domestic: sum(months)-annual=588; published values preserved
- VKO 2025 passengers_international: sum(months)-annual=-2215; published values preserved
- VOG 2024: total-domestic-international=493; see PASSENGER_RECONCILIATION
- Историческая маршрутная сеть неполна; объявления не подтверждают фактическое выполнение.
- Инфраструктура: справочный снимок 2026-11-13, не восстановленный AIP 2024/2025.
- SJ-100/Ту-214: эксплуатационная совместимость не определена; геометрический фильтр не является допуском.
- Унаследованные источники не прошли повторную независимую веб-проверку.
- Центральные оценки и scenario требуют фильтрации через DATA_LINEAGE перед фактическим анализом.

Проверены схемы, уникальность, периоды, неотрицательность, диапазоны оценок, IATA, ссылки на источники, наличие локальных свидетельств, формулы кресельной ёмкости, баланс операций, масштабы пассажиров на операцию, груз+почта и доли рынка. Отдельная почта преимущественно scenario; её сумма с грузом проверяется как арифметика сценария.

## Воспроизводимость

Повторный запуск scripts/reconstruct_monthly.py из данных пакета дал полное совпадение всех 576 строк и 1728 месячных числовых ячеек. Проверены в установленном окружении NumPy 2.3.5 / SciPy 1.17.0. Валидатор работает без этих зависимостей.
