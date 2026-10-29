import unittest

from pixel_diario.summarization import gerar_resumo


class SummarizationTests(unittest.TestCase):
    def test_selects_relevant_sentences_and_keeps_source_order(self):
        title = "Studio announces a new game release date"
        excerpt = (
            "The developer confirmed the release date for its upcoming game "
            "during a showcase. The game launches on March 12 for PC and "
            "consoles, with preorders opening next week. The presentation also "
            "included a short gameplay trailer showing new locations."
        )

        summary = gerar_resumo(title, excerpt)

        self.assertIn("confirmed the release date", summary)
        self.assertIn("launches on March 12", summary)
        self.assertLess(
            summary.index("confirmed the release date"),
            summary.index("launches on March 12"),
        )
        self.assertLessEqual(len(summary.split()), 60)

    def test_missing_excerpt_is_reported_without_inventing_details(self):
        summary = gerar_resumo("Studio announces a new game", "")

        self.assertIn("não forneceu detalhes além do título", summary)
        self.assertIn("Studio announces a new game", summary)

    def test_uses_short_excerpt_without_padding_with_guesses(self):
        excerpt = "The studio delayed the game until next year."

        self.assertEqual(
            gerar_resumo("Studio delays its game", excerpt),
            excerpt,
        )

    def test_keeps_exclamation_mark_in_game_title_with_its_sentence(self):
        excerpt = (
            "Spacewar! was developed by students in 1962 as one of the first "
            "computer games. It inspired later developers."
        )

        summary = gerar_resumo("Early video game history", excerpt)

        self.assertIn("Spacewar! was developed", summary)


if __name__ == "__main__":
    unittest.main()
