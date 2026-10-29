"""Tradução gratuita e opcional pelo endpoint público do Google Tradutor."""

import json
import urllib.error
import urllib.parse
import urllib.request

from .summarization import gerar_resumo


_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"


def _traduzir_texto(texto):
    params = urllib.parse.urlencode({
        "client": "gtx",
        "sl": "auto",
        "tl": "pt",
        "dt": "t",
        "q": texto,
    })
    request = urllib.request.Request(
        f"{_TRANSLATE_URL}?{params}",
        headers={"User-Agent": "Mozilla/5.0 (PixelDiario)"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read())
    segments = payload[0]
    translated = "".join(
        segment[0]
        for segment in segments
        if isinstance(segment, list)
        and segment
        and isinstance(segment[0], str)
    )
    if not translated.strip():
        raise ValueError("O serviço não retornou texto traduzido.")
    return translated.strip()


def traduzir(itens):
    """Traduz títulos e resumos; falhas preservam o texto original."""
    falhas = 0
    for item in itens:
        for campo in ("titulo", "resumo"):
            original = item.get(campo, "")
            try:
                item[campo] = _traduzir_texto(original)
            except (
                urllib.error.URLError,
                TimeoutError,
                json.JSONDecodeError,
                IndexError,
                TypeError,
                ValueError,
            ) as error:
                falhas += 1
                print(
                    f"Tradução indisponível para "
                    f"{item.get('id', 'notícia')} ({campo}): {error}"
                )
        if item.get("resumo", "").startswith(
            "O feed não forneceu detalhes além do título."
        ):
            item["resumo"] = gerar_resumo(item.get("titulo", ""), "")
    if falhas:
        print(
            f"{falhas} campo(s) permaneceram no idioma original; "
            "a edição será publicada mesmo assim."
        )
    return itens


def traduzir_curiosidade(curiosidade):
    """Traduz um fato externo sem impedir sua publicação se o serviço falhar."""
    original = curiosidade["titulo"]
    try:
        titulo = _traduzir_texto(curiosidade["titulo"])
        texto = _traduzir_texto(curiosidade["texto"])
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        IndexError,
        TypeError,
        ValueError,
    ) as error:
        print(
            f"Tradução da curiosidade indisponível ({original}): {error}"
        )
        return curiosidade
    curiosidade["titulo"] = titulo.strip()
    curiosidade["texto"] = texto.strip()
    return curiosidade
