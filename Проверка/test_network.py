import csv
import tempfile
import unittest
from pathlib import Path

import network


class NetworkTest(unittest.TestCase):
    def setUp(self):
        self.airports, self.routes, self.config = network.inputs()

    def test_distance_svx_oms(self):
        value = network.distance(self.airports["SVX"], self.airports["OMS"])
        self.assertGreaterEqual(value, 790)
        self.assertLessEqual(value, 820)

    def test_block_svx_oms(self):
        self.assertEqual(network.block(self.airports["SVX"], self.airports["OMS"]), 105)

    def test_routes_count(self):
        self.assertEqual(len(self.routes), 20)
        self.assertEqual(sum(1 for row in self.routes if row["variant"] == "D"), 10)
        self.assertEqual(sum(1 for row in self.routes if row["variant"] == "H"), 10)

    def test_rank_top3(self):
        rows = network.rank_cities(self.airports)
        self.assertEqual([row["город"] for row in rows[:3]], ["Омск", "Уфа", "Нижний Новгород"])

    def test_scenario_values(self):
        self.assertEqual(self.config["seats"], 100)
        self.assertEqual(self.config["cases"]["базовый"]["load_per_leg"], 75)
        self.assertEqual(self.config["cases"]["осторожный"]["load_per_leg"], 60)

    def test_build_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            network.build(Path(directory))
            path = Path(directory) / "Сравнение_гипотез.csv"
            with path.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 12)
            first = next(row for row in rows
                         if row["сеть"] == "первая очередь 8"
                         and row["сценарий"] == "базовый"
                         and row["год"] == "2028")
            self.assertEqual(first["чистый_прирост_посадок"], "99840")
            self.assertEqual(first["приведённый_вклад_2027_2028_руб"], "136835111")
            self.assertEqual(first["прирост_пп_рынок_108850000"], "0.09172")


if __name__ == "__main__":
    unittest.main()
