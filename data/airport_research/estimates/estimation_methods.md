# Расчётные методы

Все индивидуальные входы находятся в estimates.csv, колонка input_observations — JSON. Ссылки на A_R/B_R/C_R разрешаются через documentation/INPUT_OBSERVATIONS.csv. Ссылки на profile_id — seasonal_profiles.csv. Численные входы дополнительно встроены в JSON; переходить на сайт для повторения арифметики не нужно.

| Метод | Формула / смысл | Ограничение |
|---|---|---|
| annual_component_residual | total − known_component − explicit_additive_transit | Сохраняет исходное округление |
| reported_growth_from_prior_year | round(2162423×1.005) | CEK 2024, оценка по округлённому росту |
| normalize_reported_partial_split | share=international/(domestic+international), scale to total | KZN: исходная сумма не совпадает с итогом |
| normalize_lower_bound_split | Нормализация нижних границ SVX | Оценка внутри доступных ограничений |
| own_other_year_share | Доля другого года того же аэропорта | Не фиксирует изменение структуры |
| regional_peer_share | Доля явно названного аналога | Низкая уверенность |
| available_months_annualized_share | Доля по опубликованным месяцам MMK | Малые международные числа нестабильны |
| movement_share_seat_adjustment | Доля операций × условные кресла; общая загрузка | ZIA, не фактическая доля пассажиров |
| seasonal_residual_constrained_fit | Остаток года × веса + целочисленная подгонка | Опубликованные ячейки фиксированы |
| constrained_component_allocation | Годовые суммы, фиксированные месяцы, минимум остатков | Не воспроизводит неизвестное историческое расписание |
| passengers_per_movement_peer | Ptarget/Ppeer × movements_peer | Обобщает различия флота/загрузки |
| balanced_arrival_proxy / split | 2×departures; movements≈departures+arrivals | Баланс — допущение |
| peer_median_cargo_intensity | P × median(cargo_mail_peer/Ppeer) | Охваты грузовых потоков могут различаться |
| own_other_year_cargo_intensity | Собственная интенсивность другого года | Не учитывает отдельные грузовые контракты |
| airline_mail_share_proxy_scenario | mail=total×2823/(13905+2823) | Сценарий по одному перевозчику за 11 месяцев |
| same_carrier_route_median | Медиана известных частот Red Wings | Не опубликованная частота конкретной линии |
| fleet_configuration_midpoint | (98+100)/2=99 | Не подтверждение схемы каждого борта |
| two_way_schedule_capacity_scenario | C=2×f×w×q, w=(end−start+1)/7 | Условное окно; без отмен и фактического LF |
| comparable_market_share | Pcarrier/Pmarket×100 | База должна быть одинаковой |

Диапазоны помесячного итога ±25%, частей ±30%; конкретные интервалы операций/груза и сценарные параметры приведены по каждой оценке. Это не вероятностная модель. У связанных долей, месяцев и компонентов интервалы зависимы; независимый выбор всех минимумов/максимумов нарушит годовые ограничения.
