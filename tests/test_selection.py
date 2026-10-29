import unittest
from datetime import datetime, timedelta, timezone

from pixel_diario.selection import escolher


class SelectionTests(unittest.TestCase):
    def test_groups_duplicate_coverage_and_prefers_heavier_source(self):
        now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
        stories = [
            {
                "titulo": "Steam Deck games receive major update today",
                "resumo": "Update details",
                "link": "https://example.com/first",
                "data": now - timedelta(hours=1),
                "fonte": "Source A",
                "peso": 1.0,
            },
            {
                "titulo": "Steam Deck games receive major update tomorrow",
                "resumo": "More update details",
                "link": "https://example.com/second",
                "data": now - timedelta(hours=2),
                "fonte": "Source B",
                "peso": 1.2,
            },
        ]

        selected = escolher(stories, now)

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["fonte"], "Source B")
        self.assertEqual(selected[0]["outras"], ["Source A"])
        self.assertEqual(selected[0]["cat"], "Hardware")
        self.assertEqual(selected[0]["link"], "https://example.com/second")


if __name__ == "__main__":
    unittest.main()
