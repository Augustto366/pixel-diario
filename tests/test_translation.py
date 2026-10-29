import unittest
from unittest.mock import patch
from urllib.error import URLError

from pixel_diario.translation import traduzir


class TranslationTests(unittest.TestCase):
    def test_translates_titles_and_summaries(self):
        item = {"id": "story-1", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            return_value="Jogo lançado hoje\nUm jogo novo.",
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Jogo lançado hoje")
        self.assertEqual(result[0]["resumo"], "Um jogo novo.")

    def test_keeps_original_text_when_translation_service_fails(self):
        item = {"id": "story-2", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=URLError("offline"),
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Game launches today")
        self.assertEqual(result[0]["resumo"], "A new game.")

    def test_keeps_original_when_translator_removes_field_separator(self):
        item = {"id": "story-3", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            return_value="Jogo lançado hoje. Um jogo novo.",
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Game launches today")
        self.assertEqual(result[0]["resumo"], "A new game.")


if __name__ == "__main__":
    unittest.main()
