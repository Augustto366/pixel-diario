import unittest
from unittest.mock import patch
from urllib.error import URLError

from pixel_diario.translation import traduzir, traduzir_curiosidade


class TranslationTests(unittest.TestCase):
    def test_stores_translations_without_replacing_original_text(self):
        item = {"id": "story-1", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=["Jogo lançado hoje", "Um jogo novo."],
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Game launches today")
        self.assertEqual(result[0]["resumo"], "A new game.")
        self.assertEqual(result[0]["titulo_pt"], "Jogo lançado hoje")
        self.assertEqual(result[0]["resumo_pt"], "Um jogo novo.")

    def test_keeps_original_text_when_translation_service_fails(self):
        item = {"id": "story-2", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=URLError("offline"),
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Game launches today")
        self.assertEqual(result[0]["resumo"], "A new game.")
        self.assertNotIn("titulo_pt", result[0])
        self.assertNotIn("resumo_pt", result[0])

    def test_translates_each_field_independently(self):
        item = {"id": "story-3", "titulo": "Game launches today", "resumo": "A new game."}

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=["Jogo lançado hoje.", "Um jogo novo."],
        ):
            result = traduzir([item])

        self.assertEqual(result[0]["titulo"], "Game launches today")
        self.assertEqual(result[0]["resumo"], "A new game.")
        self.assertEqual(result[0]["titulo_pt"], "Jogo lançado hoje.")
        self.assertEqual(result[0]["resumo_pt"], "Um jogo novo.")

    def test_title_only_fallback_is_translated_using_original_title(self):
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

        self.assertEqual(result[0]["titulo"], "A game launches today")
        self.assertIn("Um jogo chega hoje", result[0]["resumo_pt"])
        self.assertNotIn("A game launches today", result[0]["resumo_pt"])

    def test_curiosity_translation_keeps_source_language(self):
        curiosity = {
            "titulo": "History of video games",
            "texto": "The industry started decades ago.",
            "fonte": "Wikipedia",
        }

        with patch(
            "pixel_diario.translation._traduzir_texto",
            side_effect=["História dos videogames", "A indústria começou há décadas."],
        ):
            result = traduzir_curiosidade(curiosity)

        self.assertEqual(result["titulo"], "History of video games")
        self.assertEqual(result["texto"], "The industry started decades ago.")
        self.assertEqual(result["titulo_pt"], "História dos videogames")
        self.assertEqual(result["texto_pt"], "A indústria começou há décadas.")


if __name__ == "__main__":
    unittest.main()
