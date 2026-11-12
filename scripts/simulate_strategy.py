"""Interactive scenario runner using the same calculations as the published tables."""
import argparse
import json
import math
from pathlib import Path

from compare_growth_strategies import CASES, POLICY, calculate, inputs, rotations


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


def prompt():
    options = {}
    for key, label, convert in (
        ('year', 'Год [2028]', int),
        ('scenario', 'Сценарий base или cautious [base]', str),
        ('fleet', 'Доступно самолётов вместе с резервом [без ограничения]', int),
        ('weeks', 'Рабочих недель [по сценарию]', int),
        ('fare_factor', 'Множитель цен билетов, например 0.8 [1]', float),
        ('demand_factor', 'Множитель спроса, например 0.5 [1]', float),
    ):
        raw = input(f'{label}: ').strip()
        if raw:
            options[key] = convert(raw)
    return options


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--interactive', action='store_true', help='опрос в консоли')
    mode.add_argument('--scenario-file', type=Path, help='JSON с параметрами эксперимента')
    parser.add_argument('--output', type=Path, help='сохранить входы и результаты в JSON')
    args = parser.parse_args()
    try:
        options = (prompt() if args.interactive else
                   json.loads(args.scenario_file.read_text(encoding='utf-8')) if args.scenario_file else {})
        result = simulate(options)
        if args.output:
            with args.output.open('x', encoding='utf-8') as file:
                json.dump(result, file, ensure_ascii=False, indent=2, allow_nan=False)
                file.write('\n')
    except (OSError, ValueError, TypeError, AttributeError, EOFError) as error:
        parser.error(str(error))

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
