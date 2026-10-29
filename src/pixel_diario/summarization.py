"""Geração local de resumos a partir dos trechos fornecidos pelos feeds."""

import html
import re


_STOP_WORDS = set(
    "a an and are as at be been but by for from had has have in into is it its "
    "of on or that the their this to was were will with about after all also "
    "como da das de do dos e em entre foi isso mais mas na nas no nos o os ou "
    "para pela pelas pelo pelos por que se sem sua suas um uma uns umas".split()
)
_SENTENCE_BOUNDARY = re.compile(r'(?<=[.!?])\s+(?=[A-ZÀ-Þ0-9"“])')
_WORD = re.compile(r"\b[\w'-]+\b", re.UNICODE)


def _words(text):
    return _WORD.findall(text)


def _sentences(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return [
        sentence.strip()
        for sentence in _SENTENCE_BOUNDARY.split(text)
        if sentence.strip()
    ]


def gerar_resumo(titulo, trecho, min_palavras=35, max_palavras=60):
    """Escolhe as frases mais informativas sem acrescentar fatos ao texto."""
    sentences = _sentences(trecho)
    if not sentences:
        return (
            "O feed não forneceu detalhes além do título. "
            f"A informação disponível é: {titulo.strip()}"
        )

    title_words = {
        word.lower()
        for word in _words(titulo)
        if len(word) > 2 and word.lower() not in _STOP_WORDS
    }
    ranked = []
    for index, sentence in enumerate(sentences):
        words = _words(sentence)
        if len(words) < 5:
            continue
        content_words = {
            word.lower()
            for word in words
            if len(word) > 2 and word.lower() not in _STOP_WORDS
        }
        overlap = len(content_words & title_words) / max(1, len(title_words))
        position = 1 / (index + 1)
        detail = min(len(words), 30) / 30
        score = overlap * 2 + position + detail
        ranked.append((score, index, sentence, len(words)))

    if not ranked:
        return sentences[0]

    selected = []
    word_count = 0
    for _, index, sentence, sentence_words in sorted(
        ranked, key=lambda item: (-item[0], item[1])
    ):
        if selected and word_count + sentence_words > max_palavras:
            continue
        selected.append((index, sentence))
        word_count += sentence_words
        if word_count >= min_palavras or len(selected) == 3:
            break

    if word_count < min_palavras and len(selected) < 3:
        selected_indexes = {index for index, _ in selected}
        for index, sentence in enumerate(sentences):
            if index in selected_indexes:
                continue
            sentence_words = len(_words(sentence))
            if word_count + sentence_words > max_palavras:
                continue
            selected.append((index, sentence))
            word_count += sentence_words
            if word_count >= min_palavras or len(selected) == 3:
                break

    selected.sort(key=lambda item: item[0])
    return " ".join(sentence for _, sentence in selected)
