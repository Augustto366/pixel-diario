"""Extração de parágrafos de páginas de notícias para resumos mais completos."""

import html
import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

from .summarization import gerar_resumo

_USER_AGENT = "Mozilla/5.0 (compatible; PixelDiario/1.0)"
_MAX_PAGE_BYTES = 1_000_000
_MIN_ARTICLE_WORDS = 40
_SKIP_TAGS = {
    "aside", "footer", "form", "header", "nav", "script", "style", "svg",
}
_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class _ArticleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.content_depth = 0
        self.paragraph = None
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        if self.skip_depth:
            if tag not in _VOID_TAGS:
                self.skip_depth += 1
            return
        if tag in _SKIP_TAGS:
            self.skip_depth = 1
            return
        if tag in ("article", "main"):
            self.content_depth += 1
        if tag == "p":
            self.paragraph = (self.content_depth > 0, [])

    def handle_startendtag(self, tag, attrs):
        if self.skip_depth:
            return
        if tag == "p":
            self._finish_paragraph()

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag == "p":
            self._finish_paragraph()
        if tag in ("article", "main") and self.content_depth:
            self.content_depth -= 1

    def handle_data(self, data):
        if self.paragraph is not None and not self.skip_depth:
            self.paragraph[1].append(data)

    def _finish_paragraph(self):
        if self.paragraph is None:
            return
        in_content, parts = self.paragraph
        text = re.sub(r"\s+", " ", html.unescape(" ".join(parts))).strip()
        if len(text.split()) >= 8:
            self.paragraphs.append((in_content, text))
        self.paragraph = None

    def article_text(self):
        self._finish_paragraph()
        content = [text for in_content, text in self.paragraphs if in_content]
        paragraphs = content or [
            text for _, text in self.paragraphs
        ]
        return " ".join(paragraphs[:12])[:12000]


def extrair_artigo(url):
    if not url.startswith("https://"):
        raise ValueError(f"URL de notícia inválida: {url}")
    request = urllib.request.Request(
        url,
        headers={"User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        content_type = response.headers.get_content_type()
        if content_type != "text/html":
            raise ValueError(f"Tipo de conteúdo não suportado: {content_type}")
        content = response.read(_MAX_PAGE_BYTES)
        charset = response.headers.get_content_charset() or "utf-8"
    parser = _ArticleParser()
    parser.feed(content.decode(charset, errors="replace"))
    text = parser.article_text()
    if not text:
        raise ValueError("A página não contém parágrafos de artigo legíveis.")
    return text


def enriquecer_resumos(itens):
    """Usa páginas completas quando acessíveis e preserva o fallback do feed."""
    falhas = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(extrair_artigo, item["link"]): item
            for item in itens
        }
        for future in as_completed(futures):
            item = futures[future]
            try:
                article_text = future.result()
            except (
                urllib.error.URLError,
                TimeoutError,
                UnicodeError,
                ValueError,
            ) as error:
                falhas.append((item.get("fonte", "fonte desconhecida"), error))
                continue
            if len(article_text.split()) >= _MIN_ARTICLE_WORDS:
                item["resumo"] = gerar_resumo(item["titulo"], article_text)

    if falhas:
        fontes = ", ".join(sorted({fonte for fonte, _ in falhas}))
        print(
            f"{len(falhas)} artigo(s) não puderam ser consultados "
            f"({fontes}); seus resumos usam o conteúdo do feed."
        )
    return itens
