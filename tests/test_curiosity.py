import unittest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pixel_diario.curiosity import curiosidade_do_dia


class CuriosityTests(unittest.TestCase):
    def test_curiosity_changes_on_brasilia_calendar_day(self):
        today = datetime(2026, 10, 29, 19, 59, tzinfo=ZoneInfo("America/Sao_Paulo"))
        tomorrow = datetime(2026, 10, 30, 20, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))

        today_curiosity = curiosidade_do_dia(today)
        tomorrow_curiosity = curiosidade_do_dia(tomorrow)

        self.assertEqual(today_curiosity["data"], "2026-10-29")
        self.assertEqual(tomorrow_curiosity["data"], "2026-10-30")
        self.assertNotEqual(today_curiosity["titulo"], tomorrow_curiosity["titulo"])
        self.assertTrue(today_curiosity["link"].startswith("https://"))
        self.assertTrue(tomorrow_curiosity["link"].startswith("https://"))

    def test_same_brasilia_day_gets_same_curiosity(self):
        morning_utc = datetime(2026, 10, 29, 12, 0, tzinfo=ZoneInfo("UTC"))
        evening_brasilia = datetime(
            2026, 10, 29, 20, 0, tzinfo=ZoneInfo("America/Sao_Paulo")
        )

        self.assertEqual(
            curiosidade_do_dia(morning_utc),
            curiosidade_do_dia(evening_brasilia),
        )

    def test_curiosity_does_not_repeat_during_the_20_day_rotation(self):
        first_day = datetime(2026, 10, 29, tzinfo=ZoneInfo("America/Sao_Paulo"))
        titles = {
            curiosidade_do_dia(first_day + timedelta(days=offset))["titulo"]
            for offset in range(20)
        }

        self.assertEqual(len(titles), 20)


if __name__ == "__main__":
    unittest.main()
