import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pixel_diario.archive import atualizar_historico
from pixel_diario.render import renderizar


class ArchiveAndRenderTests(unittest.TestCase):
    def test_archives_previous_edition_with_template_spacing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edition = {
                "data": "28 de outubro de 2026",
                "itens": [{"id": "story-1", "titulo": "Notícia"}],
            }
            (root / "historico.json").write_text("[]", encoding="utf-8")
            (root / "index.html").write_text(
                "var D = " + json.dumps(edition, ensure_ascii=False)
                + ", I = D.itens",
                encoding="utf-8",
            )

            history = atualizar_historico(
                datetime(2026, 10, 29, tzinfo=timezone.utc), root
            )

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], "story-1")
        self.assertTrue(history[0]["publicado_em"].startswith("2026-10-28"))

    def test_render_escapes_script_closing_sequence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            template = root / "template.html"
            template.write_text("<script>var D = __DADOS__;</script>", encoding="utf-8")
            renderizar(
                [{"id": "x", "titulo": "</script>"}],
                datetime(2026, 10, 29, tzinfo=timezone.utc),
                root,
                template,
                curiosidade={
                    "data": "2026-10-29",
                    "titulo": "Fato do dia",
                    "texto": "Texto curto.",
                    "fonte": "Fonte oficial",
                    "link": "https://example.com/fonte",
                },
            )

            generated = (root / "index.html").read_text(encoding="utf-8")

        self.assertIn("<\\/script>", generated)
        self.assertNotIn("</script>;", generated)
        self.assertIn('"curiosidade"', generated)
        self.assertIn("https://example.com/fonte", generated)

    def test_page_template_has_original_and_translation_toggle(self):
        from pixel_diario.config import TEMPLATE_PATH

        template = TEMPLATE_PATH.read_text(encoding="utf-8")

        self.assertIn("Traduzir para português", template)
        self.assertIn("Ver original", template)
        self.assertIn("n.titulo_pt", template)
        self.assertIn("n.resumo_pt", template)


if __name__ == "__main__":
    unittest.main()
