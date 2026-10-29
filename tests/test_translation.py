import unittest
from unittest.mock import patch
from urllib.error import URLError

from pixel_diario.translation import traduzir


class TranslationTests(unittest.TestCase):
    def test_translates_titles_and_summaries(self):
        item = {"id": "story-1", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=["Jogo lançado hoje", "Um jogo novo."],
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

    def test_translates_fields_independently_when_service_changes_line_breaks(self):
        item = {"id": "story-3", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=["Jogo lançado hoje.", "Um jogo novo."],
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Jogo lançado hoje.")
        self.assertEqual(result[0]["resumo"], "Um jogo novo.")

    def test_title_only_fallback_uses_translated_title(self):
        item = {
            "id": "story-4",
            "titulo": "A game launches today",
            "resumo": "O feed não forneceu detalhes além do título. "
            "A informação disponível é: A game launches today",
        }

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=[
                "Um jogo chega hoje",
                "O feed não forneceu detalhes além do título. "
                "A informação disponível é: A game launches today",
            ],
        ):
            result = traduzir([item])

        self.assertIn("Um jogo chega hoje", result[0]["resumo"])
        self.assertNotIn("A game launches today", result[0]["resumo"])


if __name__ == "__main__":
    unittest.main()
