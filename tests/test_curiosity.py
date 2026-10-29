import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from pixel_diario.curiosity import curiosidade_do_dia


class CuriosityTests(unittest.TestCase):
    def test_fetches_web_articles_and_never_repeats_saved_page_ids(self):
        first_extract = (
            "The video game industry has developed through many decades of "
            "technological change. Its early commercial history includes "
            "arcades, home consoles, personal computers, and portable systems."
        )
        second_extract = (
            "A game company develops interactive entertainment and publishes "
            "hardware, software, publishing, and distribution. These changes "
            "shaped how games are made and played around the world."
        )

        def fake_request(parameters):
            if parameters.get("list") == "categorymembers":
                if parameters.get("cmcontinue") == "next-page":
                    return {
                        "query": {
                            "categorymembers": [
                                {"pageid": 13, "title": "Game company"}
                            ]
                        }
                    }
                return {
                    "query": {
                        "categorymembers": [
                            {"pageid": 10, "title": "Nintendo"},
                            {"pageid": 11, "title": "Video game industry"},
                            {"pageid": 12, "title": "History of video games"},
                        ]
                    },
                    "continue": {"cmcontinue": "next-page"},
                }
            if parameters.get("pageids") == 12:
                return {
                    "query": {
                        "pages": [{
                            "pageid": 12,
                            "title": "History of video games",
                            "extract": first_extract,
                            "fullurl": "https://en.wikipedia.org/wiki/History_of_video_games",
                        }]
                    }
                }
            if parameters.get("pageids") == 13:
                return {
                    "query": {
                        "pages": [{
                            "pageid": 13,
                            "title": "Game company",
                            "extract": second_extract,
                            "fullurl": "https://en.wikipedia.org/wiki/Game_company",
                        }]
                    }
                }
            raise AssertionError(f"Unexpected API request: {parameters}")

        first_day = datetime(2026, 10, 29, 20, tzinfo=ZoneInfo("America/Sao_Paulo"))
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch("pixel_diario.curiosity._request", side_effect=fake_request),
                patch(
                    "pixel_diario.curiosity.traduzir_curiosidade",
                    side_effect=lambda curiosity: curiosity,
                ),
            ):
                first = curiosidade_do_dia(first_day, directory)
                second = curiosidade_do_dia(
                    first_day + timedelta(days=1), directory
                )

            state = Path(directory, "curiosidades_vistas.json")
            saved = state.read_text(encoding="utf-8")

        self.assertEqual(first["titulo"], "History of video games")
        self.assertEqual(second["titulo"], "Game company")
        self.assertEqual(first["data"], "2026-10-29")
        self.assertEqual(second["data"], "2026-10-30")
        self.assertIn("https://en.wikipedia.org/wiki/History_of_video_games", first["link"])
        self.assertIn("Wikipédia — History of video games", first["fonte"])
        self.assertIn('"seen": [', saved)
        self.assertIn("12", saved)
        self.assertIn("13", saved)

    def test_fails_instead_of_repeating_when_sources_are_exhausted(self):
        def empty_category(parameters):
            if parameters.get("list") == "categorymembers":
                return {"query": {"categorymembers": []}}
            raise AssertionError("No article should be requested")

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "pixel_diario.curiosity._request", side_effect=empty_category
            ):
                with self.assertRaisesRegex(RuntimeError, "artigos inéditos"):
                    curiosidade_do_dia(
                        datetime.now(ZoneInfo("America/Sao_Paulo")), directory
                    )


if __name__ == "__main__":
    unittest.main()
