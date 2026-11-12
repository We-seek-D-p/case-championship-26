"""Interactive scenario runner using the same calculations as the published tables."""
import argparse
import json
import math
from pathlib import Path

from compare_growth_strategies import CASES, POLICY, calculate, inputs, rotations
from rank_cities import CAP, CITIES, WEIGHT, calculate_ranking, core_city_data


def number(value, name, minimum, maximum=math.inf, *, integer=False):
    if (type(value) not in (int, float) or not math.isfinite(value)
            or not minimum <= value <= maximum or (integer and type(value) is not int)):
        raise ValueError(f'{name}: допустимо {"целое " if integer else ""}число от {minimum} до {maximum:g}')
    return value


def simulate(options):
    year = options.get('year', 2028)
    scenario = options.get('scenario', 'base')
    if year not in (2027, 2028) or scenario not in CASES:
        raise ValueError('Выберите год 2027 или 2028 и сценарий base или cautious.')
    policy = {**POLICY, **options.get('policy', {})}
    settings = {**CASES[scenario], **options.get('scenario_settings', {})}
    editable_policy = {
        'seats', 'spare_aircraft', 'fixed_aircraft_rub_year', 'variable_rub_block_h',
        'airport_rub_departure', 'H1_fixed_rub_year', 'H2_fixed_rub_year',
        'H1_startup_rub', 'H2_startup_rub', 'transfer_fare_factor', 'common_capture',
        'transfer_capture', 'H2_added_roundtrips_week',
    }
    editable_case = {'load', 'fare', 'demand', 'transfer_demand', 'existing_displacement',
                     'new_displacement', 'transfer_displacement', f'ramp_{year}'}
    if (options.keys() - {'year', 'scenario', 'fleet', 'weeks', 'fare_factor', 'demand_factor',
                          'policy', 'scenario_settings', 'routes', 'include_startup'}
            or options.get('policy', {}).keys() - editable_policy
            or options.get('scenario_settings', {}).keys() - editable_case):
        raise ValueError('Неизвестный или недоступный для изменения параметр.')
    for key in editable_policy:
        if key in {'seats', 'spare_aircraft', 'H2_added_roundtrips_week'}:
            minimum = 0 if key == 'spare_aircraft' else 1
            maximum = 7 if key == 'H2_added_roundtrips_week' else math.inf
            number(policy[key], key, minimum, maximum, integer=True)
        else:
            maximum = 1 if key in {'transfer_fare_factor', 'common_capture', 'transfer_capture'} else math.inf
            number(policy[key], key, 0, maximum)
    for key in editable_case:
        maximum = math.inf if key in {'fare', 'demand', 'transfer_demand'} else 1
        number(settings[key], key, 0, maximum)

    fleet = options.get('fleet')
    if fleet is not None:
        number(fleet, 'fleet', 0, integer=True)
    weeks = options.get('weeks')
    if weeks is not None:
        number(weeks, 'weeks', 1, 52, integer=True)
    include_startup = options.get('include_startup', year == 2027)
    if type(include_startup) is not bool:
        raise ValueError('include_startup: укажите true или false.')
    fare_factor = number(options.get('fare_factor', 1), 'fare_factor', 0)
    demand_factor = number(options.get('demand_factor', 1), 'demand_factor', 0)

    records, rw, market = inputs(save_references=False)
    overrides = options.get('routes', {})
    if overrides.keys() - {r['route_id'] for r in records}:
        raise ValueError('В routes указан неизвестный номер маршрута.')
    for row in records:
        row['annual_local_target'] = row['common_analog_passengers'] * policy['common_capture']
        if row['hypothesis'] == 'H2':
            row['added_roundtrips_week'] = policy['H2_added_roundtrips_week']
        for field, value in overrides.get(row['route_id'], {}).items():
            if field not in {'annual_local_target', 'fare_rub_oneway'}:
                raise ValueError(f"{row['route_id']}: недоступное поле {field}")
            row[field] = number(value, field, 0)
    # The 2027 pilot is scheduled by calculate() using its own route subset.
    schedule = rotations(records, policy=policy) if year == 2028 else []
    routes, summaries, transfers = calculate(
        records, schedule, rw, market, scenario, year, fare_factor, demand_factor,
        policy=policy, settings=settings, weeks_override=weeks, include_startup=include_startup,
    )
    plans = []
    for row in summaries:
        fits = fleet is None or row['total_aircraft'] <= fleet
        plans.append({
            'hypothesis': row['hypothesis'],
            'fits_fleet': fits,
            'required_by_schedule': row['total_aircraft'],
            'missing_aircraft': max(0, row['total_aircraft'] - fleet) if fleet is not None else 0,
            'summary': row if fits else None,
        })
    feasible = [plan['summary'] for plan in plans if plan['fits_fleet']]
    best = max((r['contribution_rub'] for r in feasible), default=None)
    winners = [r['hypothesis'] for r in feasible if r['contribution_rub'] == best]
    included = {plan['hypothesis'] for plan in plans if plan['fits_fleet']}
    effective_routes = [r for r in records if any(
        r['route_id'] == output['route_id'] for output in routes
    )]
    return {
        'settings': {'year': year, 'scenario': scenario, 'fleet_limit': fleet,
                     'fare_factor': fare_factor, 'demand_factor': demand_factor,
                     'policy': policy, 'scenario_settings': settings, 'weeks_override': weeks,
                     'include_startup': include_startup,
                     'red_wings_reference_segments': rw, 'market_reference_segments': market},
        'leaders_by_contribution': winners,
        'plans': plans,
        'route_inputs': effective_routes,
        'route_results': [r for r in routes if r['hypothesis'] in included],
        'transfer_results': transfers if 'H1' in included else [],
    }


def simulate_cities(options):
    settings = dict(size_weight=WEIGHT, passenger_cap=CAP, growth_min=-10, growth_max=10)
    if options.keys() - (settings.keys() | {'city_overrides'}):
        raise ValueError('Неизвестный параметр рейтинга городов.')
    settings.update(options)
    data = core_city_data()
    _, criteria, cities, _ = calculate_ranking(data, **settings)
    if options:
        _, _, baseline, _ = calculate_ranking(data)
        baseline_ranks = {row['city']: row['rank'] for row in baseline}
    else:
        baseline_ranks = {row['city']: row['rank'] for row in cities}
    ranking = []
    for row in cities:
        entry = {key: value for key, value in row.items() if key not in ('total', 'growth_refs', 'routes')}
        entry['baseline_rank'] = baseline_ranks[row['city']]
        entry['places_gained'] = None if row['rank'] is None else entry['baseline_rank'] - row['rank']
        ranking.append(entry)
    ranked = [row for row in ranking if row['rank'] is not None]
    return {
        'settings': {**settings, 'growth_weight': 1 - settings['size_weight']},
        'top_three': [r['city'] for r in ranked[:3]],
        'top_three_new_base': [r['city'] for r in ranked if r['new_hub_eligible']][:3],
        'ranking': ranking,
        'criteria': criteria,
    }


def prompt(*, cities=False):
    options = {}
    fields = (
        ('size_weight', 'Вес размера, от 0 до 1 [0.75]', float),
        ('passenger_cap', 'Поток, при котором размер даёт 100 баллов [6000000]', float),
        ('growth_min', 'Рост для 0 баллов, % [-10]', float),
        ('growth_max', 'Рост для 100 баллов, % [10]', float),
    ) if cities else (
        ('year', 'Год [2028]', int),
        ('scenario', 'Сценарий base или cautious [base]', str),
        ('fleet', 'Доступно самолётов вместе с резервом [без ограничения]', int),
        ('weeks', 'Рабочих недель [по сценарию]', int),
        ('fare_factor', 'Множитель цен билетов, например 0.8 [1]', float),
        ('demand_factor', 'Множитель спроса, например 0.5 [1]', float),
    )
    for key, label, convert in fields:
        raw = input(f'{label}: ').strip()
        if raw:
            options[key] = convert(raw.replace(',', '.') if convert is float else raw)
    if cities:
        overrides = prompt_city_overrides()
        if overrides:
            options['city_overrides'] = overrides
    return options


def prompt_city_overrides():
    overrides = {}
    names = list(CITIES)
    print('Города: ' + ', '.join(f'{i}. {name}' for i, name in enumerate(names, 1)))
    while True:
        choice = input('Номер города для изменения [Enter — рассчитать]: ').strip()
        if not choice:
            return overrides
        if not choice.isdecimal() or not 1 <= int(choice) <= len(names):
            print('Введите номер из списка.')
            continue
        city = names[int(choice) - 1]
        passengers = input(f'{city}: пассажиры за год [Enter — оставить]: ').strip()
        growth = input('Годовой рост в % [Enter — оставить, ? — данных нет]: ').strip()
        try:
            change = {}
            if passengers:
                change['passengers'] = int(passengers)
            if growth:
                change['growth'] = None if growth == '?' else float(growth.replace(',', '.'))
            if change:
                overrides.setdefault(city, {}).update(change)
        except ValueError:
            print('Введите целое число пассажиров и числовой рост либо ?.')


def print_city_ranking(result):
    for row in result['ranking']:
        city = row['city']
        score = 'без балла' if row['score'] is None else f"{row['score']:.2f}"
        growth = 'нет данных' if row['growth'] is None else f"{row['growth']:+.2f}%"
        print(f"{row['rank'] or '—'}. {city}: {score}; рост {growth}; "
              f"покрытие весов {row['coverage']:.0%}; диапазон балла "
              f"{row['score_low']:.2f}–{row['score_high']:.2f}; "
              f"место в стандарте {row['baseline_rank']}.")
    print('Общая тройка: ' + (', '.join(result['top_three']) or 'нет оценки'))
    print('Тройка для проверки новой базы: ' + (', '.join(result['top_three_new_base']) or 'нет оценки'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--interactive', action='store_true', help='опрос в консоли')
    mode.add_argument('--scenario-file', type=Path, help='JSON с параметрами эксперимента')
    parser.add_argument('--cities', action='store_true', help='рейтинг городов вместо расчёта рейсов')
    parser.add_argument('--output', type=Path, help='сохранить входы и результаты в JSON')
    args = parser.parse_args()
    try:
        options = (prompt(cities=args.cities) if args.interactive else
                   json.loads(args.scenario_file.read_text(encoding='utf-8')) if args.scenario_file else {})
        if not isinstance(options, dict):
            raise ValueError('Файл сценария должен содержать объект JSON.')
        result = simulate_cities(options) if args.cities else simulate(options)
        if args.output:
            with args.output.open('x', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=2, allow_nan=False)
                file.write('\n')
    except (OSError, ValueError, TypeError, AttributeError, EOFError) as error:
        parser.error(str(error))

    if args.cities:
        print_city_ranking(result)
        return

    for plan in result['plans']:
        h, needed = plan['hypothesis'], plan['required_by_schedule']
        row = plan['summary']
        if row is None:
            print(f"{h}: графику нужно {needed} бортов с резервом. Не хватает {plan['missing_aircraft']}.")
            continue
        print(f"{h}: {needed} бортов с резервом, {row['weeks']} недель, "
              f"{row['net_passenger_segments']:,.0f} доп. сегментов, "
              f"{row['transfer_net_journeys']:,.0f} доп. поездок с пересадкой, "
              f"+{row['share_delta_pp']:.3f} п.п., "
              f"выручка {row['incremental_revenue_rub']/1e6:,.1f} млн ₽, "
              f"результат {row['contribution_rub']/1e6:,.1f} млн ₽.")
    leaders = ', '.join(result['leaders_by_contribution'])
    print(f'Лидер по результату: {leaders}.' if leaders else 'Для заданного парка оба графика недоступны.')


if __name__ == '__main__':
    main()
