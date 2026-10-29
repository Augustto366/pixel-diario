"""Tradução gratuita e opcional pelo endpoint público do Google Tradutor."""

import json
import urllib.error
import urllib.parse
import urllib.request


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
        titulo = item.get("titulo", "")
        resumo = item.get("resumo", "")
        try:
            traduzido = _traduzir_texto(f"{titulo}\n{resumo}")
            titulo_traduzido, separator, resumo_traduzido = traduzido.partition("\n")
            if not separator or not titulo_traduzido.strip() or not resumo_traduzido.strip():
                raise ValueError(
                    "O serviço não preservou a separação entre título e resumo."
                )
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
                f"Tradução indisponível para {item.get('id', 'notícia')}: {error}"
            )
            continue
        item["titulo"] = titulo_traduzido.strip()
        item["resumo"] = resumo_traduzido.strip()
    if falhas:
        print(
            f"{falhas} notícia(s) permaneceram no idioma original; "
            "a edição será publicada mesmo assim."
        )
    return itens
