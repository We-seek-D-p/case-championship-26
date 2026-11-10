# Red Wings — новый хаб или прямые рейсы

**H2: десять прямых пар из Екатеринбурга, по два дополнительных оборота в неделю.
Два рабочих SJ-100 и один резервный.** После поставки самолётов — пилот трёх пар,
затем расширение по продажам и покрытию расходов.

| Полная программа 2028 | Базовый | Осторожный |
|---|---:|---:|
| Дополнительные сегменты | 143,6 тыс. | 97,8 тыс. |
| Дополнительная выручка | 1,85 млрд ₽ | 1,14 млрд ₽ |
| Прирост доли к рынку 2025 | +0,132 п.п. | +0,090 п.п. |
| Результат после расходов программы | 877 млн ₽ | 169 млн ₽ |

[Материалы защиты](submission/README.md) ·
[Расчёт и условия выбора](analysis/08-strategy-decision.md) ·
[Рейтинг городов](analysis/06-city-ranking.md) ·
[Данные](data/processed/README.md) ·
[Источники](data/SOURCE_MANIFEST.md).

H1 даёт больше сегментов. H2 выбрана по осторожной экономике и возможности начать
с пилота. Денежное преимущество в базе исчезает при снижении только тарифа H2
примерно на 2%. Это сценарная оценка, не чистая прибыль и не подтверждённый O&D.

## Расчёт

Python 3.14 и uv. Для готового окружения:

```sh
uv run --frozen --no-sync python scripts/rank_cities.py
uv run --frozen --no-sync python scripts/compare_growth_strategies.py
uv run --frozen --no-sync python scripts/check_strategy.py
uv run --frozen --no-sync python scripts/build_defense.py
```

| Скрипт | Назначение |
|---|---|
| `rank_cities.py` | Рейтинг городов, таблицы и графики |
| `compare_growth_strategies.py` | Расчёт H1/H2, сценариев, ротаций и карты |
| `build_defense.py` | Паспорт и презентация PDF, маршрутная таблица |
| `check_strategy.py` | Проверка арифметики, кресел и ротаций при изменении модели |

Графики сохраняются в `analysis/figures/`:

- `rank_cities.py`: `airport_passengers.png`, `city_scores.png`, `criteria_comparison.png`.
- `compare_growth_strategies.py`: `strategy_comparison.png`, `strategy_route_map.png`,
  `selected_route_map.png`, `route_evidence_coverage.png`; также карта `submission/route-map.pdf`.
- `build_defense.py` создаёт PDF и вставляет готовую карту в презентацию.

`processed/` — готовая проверенная база. Параметры сценариев задаются в коде;
расчёт не обращается к сайтам. Отдельная проверка не нужна для сборки PDF.
Паспорт и презентация создаются только в PDF через ReportLab. Скрипт использует
ReportLab текущего окружения или установленного runtime Codex; путь можно задать
через `RUNTIME_PYTHON`. Другие зависимости проекта не добавлены.
