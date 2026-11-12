import csv
from pathlib import Path
import unittest

from simulate_strategy import simulate


class SimulationTests(unittest.TestCase):
    def test_defaults_match_published_summary(self):
        path = Path(__file__).resolve().parents[1] / 'results/strategy/hypothesis_comparison.csv'
        with path.open(encoding='utf-8', newline='') as file:
            for row in csv.DictReader(file):
                plans = simulate({'year': int(row['year']), 'scenario': row['scenario']})['plans']
                summary = next(p['summary'] for p in plans if p['hypothesis'] == row['hypothesis'])
                for key in ('net_passenger_segments', 'contribution_rub', 'share_delta_pp',
                            'transfer_net_journeys', 'total_aircraft'):
                    self.assertAlmostEqual(summary[key], float(row[key]), places=6)

    def test_two_aircraft_allow_pilot_but_not_full_program(self):
        pilot = simulate({'year': 2027, 'fleet': 2})
        self.assertEqual(pilot['leaders_by_contribution'], ['H2'])
        full = simulate({'fleet': 2})
        self.assertEqual(full['leaders_by_contribution'], [])
        self.assertTrue(all(p['summary'] is None for p in full['plans']))

    def test_fare_zero_changes_revenue_but_not_passengers(self):
        normal = simulate({})['plans'][0]['summary']
        free = simulate({'fare_factor': 0})['plans'][0]['summary']
        self.assertEqual(free['incremental_revenue_rub'], 0)
        self.assertEqual(free['net_passenger_segments'], normal['net_passenger_segments'])

    def test_per_route_target_and_shorter_season(self):
        result = simulate({'weeks': 26, 'routes': {'H2-01': {'annual_local_target': 10000}}})
        omsk = next(row for row in result['route_results'] if row['route_id'] == 'H2-01')
        self.assertEqual(omsk['seats'], 10400)
        self.assertEqual(omsk['local_segments'], 5000)

    def test_published_demand_thresholds_equalize_both_plans(self):
        path = Path(__file__).resolve().parents[1] / 'results/strategy/decision_thresholds.csv'
        with path.open(encoding='utf-8', newline='') as file:
            thresholds = [float(r['value']) for r in csv.DictReader(file)
                          if r['parameter'] == 'common_local_target_equal_cash_base']
        self.assertEqual(len(thresholds), 2)
        for threshold in thresholds:
            plans = simulate({'policy': {'common_capture': threshold / 211000}})['plans']
            left, right = [p['summary']['contribution_rub'] for p in plans]
            self.assertAlmostEqual(left, right, places=5)

    def test_zero_hour_cost_and_unknown_fields(self):
        result = simulate({'policy': {'variable_rub_block_h': 0}})
        h1 = result['plans'][0]['summary']
        self.assertEqual(h1['variable_cost_rub'], h1['departures'] * 20000)
        with self.assertRaises(ValueError):
            simulate({'policy': {'seats': -10}})
        with self.assertRaises(ValueError):
            simulate({'routes': {'wrong': {}}})


if __name__ == '__main__':
    unittest.main()
