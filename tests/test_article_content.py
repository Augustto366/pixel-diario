import unittest
from unittest.mock import patch

from pixel_diario.article_content import _ArticleParser, enriquecer_resumos


class ArticleContentTests(unittest.TestCase):
    def test_extracts_article_paragraphs_and_skips_navigation(self):
        parser = _ArticleParser()
        parser.feed(
            "<nav><p>Navigation with enough words to be discarded completely.</p></nav>"
            "<main><article><p>The studio confirmed a new game release date "
            "during its broadcast. Players can expect the title on consoles "
            "and computers this winter.</p><p>Developers also showed a new "
            "gameplay trailer and announced the opening of preorders next week."
            "</p></article></main>"
            "<footer><p>Footer text with enough words to be excluded here.</p></footer>"
        )

        text = parser.article_text()

        self.assertIn("confirmed a new game release date", text)
        self.assertIn("opening of preorders next week", text)
        self.assertNotIn("Navigation", text)
        self.assertNotIn("Footer text", text)

    def test_enrichment_uses_full_article_when_available(self):
        item = {
            "id": "story-1",
            "titulo": "Studio announces a game",
            "resumo": "The studio announced a game.",
            "link": "https://example.com/story",
            "fonte": "Example",
        }
        full_text = (
            "The developer confirmed a release date during its showcase, "
            "sharing the announcement with players around the world. "
            "The game launches in March for PC and consoles, with versions "
            "planned for current generation platforms. "
            "Preorders will open next week for several editions and include "
            "additional digital items for early customers."
        )

        with patch(
            "pixel_diario.article_content.extrair_artigo",
            return_value=full_text,
        ):
            result = enriquecer_resumos([item])

        self.assertIn("launches in March", result[0]["resumo"])
        self.assertGreater(len(result[0]["resumo"].split()), 10)


if __name__ == "__main__":
    unittest.main()
