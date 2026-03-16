import unittest
from datetime import datetime, timezone, timedelta
from tools.tabs import group_by_date

class TestGroupByDate(unittest.TestCase):
    def test_grouping_by_date(self):
        # Create tabs with specific timestamps
        base_time = datetime(2024, 2, 23, 10, 0, 0, tzinfo=timezone.utc)
        ts1 = int(base_time.timestamp() * 1000)  # same day
        ts2 = int((base_time + timedelta(days=1)).timestamp() * 1000)  # next day
        ts3 = int((base_time + timedelta(days=0, hours=5)).timestamp() * 1000)  # same day

        tabs = [
            {"id": 1, "title": "Tab1", "openedAt": ts1},
            {"id": 2, "title": "Tab2", "openedAt": ts2},
            {"id": 3, "title": "Tab3", "openedAt": ts3},
        ]

        grouped = group_by_date(tabs)
        self.assertEqual(set(grouped.keys()), {"2024-02-23", "2024-02-24"})
        self.assertEqual(len(grouped["2024-02-23"]), 2)
        self.assertEqual(len(grouped["2024-02-24"]), 1)
        # Ensure original tabs are preserved
        self.assertIn(tabs[0], grouped["2024-02-23"])
        self.assertIn(tabs[2], grouped["2024-02-23"])
        self.assertIn(tabs[1], grouped["2024-02-24"])

if __name__ == "__main__":
    unittest.main()
