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
    """Anexa traduções opcionais sem substituir os textos originais."""
    falhas = 0
    for item in itens:
        for campo, destino in (
            ("titulo", "titulo_pt"),
            ("resumo", "resumo_pt"),
        ):
            original = item.get(campo, "")
            if (
                campo == "resumo"
                and original.startswith(
                    "O feed não forneceu detalhes além do título."
                )
                and item.get("titulo_pt")
            ):
                item[destino] = gerar_resumo(item["titulo_pt"], "")
                continue
            try:
                item[destino] = _traduzir_texto(original)
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
                    f"{item.get('id', 'notícia')} ({destino}): {error}"
                )
    if falhas:
        print(
            f"{falhas} tradução(ões) não foram obtidas; "
            "a edição será publicada mesmo assim."
        )
    return itens


def traduzir_curiosidade(curiosidade):
    """Anexa a tradução de um fato sem substituir o idioma da fonte."""
    original = curiosidade["titulo"]
    try:
        titulo_pt = _traduzir_texto(curiosidade["titulo"])
        texto_pt = _traduzir_texto(curiosidade["texto"])
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
    curiosidade["titulo_pt"] = titulo_pt
    curiosidade["texto_pt"] = texto_pt
    return curiosidade
