import csv
import unittest

from rank_cities import ROOT
from simulate_strategy import simulate_cities


class CityRankingTests(unittest.TestCase):
    def test_defaults_match_published_report(self):
        with (ROOT / 'results/cities/city_ranking.csv').open(encoding='utf-8', newline='') as file:
            published = list(csv.DictReader(file))
        actual = simulate_cities({})['ranking']
        self.assertEqual([r['city'] for r in actual], [r['city'] for r in published])
        for row, old in zip(actual, published, strict=True):
            self.assertAlmostEqual(row['score'], float(old['score']), places=8)
            self.assertEqual(row['rank'], int(old['rank']))
            self.assertEqual(row['new_hub_eligible'], old['new_hub_eligible'] == 'True')

    def test_weight_and_size_cap_can_change_leader(self):
        self.assertEqual(simulate_cities({'size_weight': .60})['top_three'][0], 'Уфа')
        self.assertEqual(simulate_cities({'size_weight': .90})['top_three'][0], 'Казань')
        result = simulate_cities({'passenger_cap': 5_000_000})
        self.assertEqual(result['top_three'][0], 'Уфа')
        kazan = next(r for r in result['ranking'] if r['city'] == 'Казань')
        self.assertEqual(kazan['size_score'], 100)
        self.assertNotIn('Казань', result['top_three_new_base'])

    def test_growth_scale_anchors_and_interpolation(self):
        changes = {'Уфа': {'growth': 2}, 'Казань': {'growth': -30},
                   'Омск': {'growth': 20}, 'Саратов': {'growth': -2},
                   'Оренбург': {'growth': 6}}
        result = simulate_cities({'growth_min': -2, 'growth_max': 6, 'city_overrides': changes})
        rows = {r['city']: r for r in result['ranking']}
        self.assertEqual([rows[city]['growth_score'] for city in changes], [50, 0, 100, 0, 100])
        self.assertTrue(all(0 <= r['score'] <= 100 for r in rows.values()))

    def test_unknown_growth_is_not_zero(self):
        result = simulate_cities({'city_overrides': {'Уфа': {'growth': None}}})
        ufa = next(r for r in result['ranking'] if r['city'] == 'Уфа')
        self.assertIsNone(ufa['growth_score'])
        self.assertAlmostEqual(ufa['score'], ufa['size_score'])
        self.assertAlmostEqual(ufa['score_high'] - ufa['score_low'], 25)
        result = simulate_cities({'size_weight': 0, 'city_overrides': {'Уфа': {'growth': None}}})
        ufa = next(r for r in result['ranking'] if r['city'] == 'Уфа')
        self.assertIsNone(ufa['score'])
        self.assertIsNone(ufa['rank'])
        self.assertEqual((ufa['score_low'], ufa['score_high']), (0, 100))

    def test_passenger_override_has_scenario_provenance(self):
        result = simulate_cities({'city_overrides': {'Уфа': {'passengers': 3_000_000}}})
        ufa = next(r for r in result['ranking'] if r['city'] == 'Уфа')
        self.assertEqual(ufa['size_score'], 50)
        criterion = next(r for r in result['criteria'] if r['city'] == 'Уфа' and r['criterion'] == 'size')
        self.assertEqual(criterion['status'], 'scenario')
        self.assertIn('исходное наблюдение', criterion['sources'])

    def test_reject_invalid_parameters(self):
        for options in ({'size_weight': 1.01}, {'passenger_cap': 0}, {'growth_min': 10},
                        {'city_overrides': {'Новый город': {}}}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                simulate_cities(options)


if __name__ == '__main__':
    unittest.main()
