"""Persistência e migração do arquivo de notícias anteriores."""

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import MESES, PROJECT_ROOT


def data_publicacao(rotulo, fallback):
    match = re.fullmatch(
        r"(\d{1,2}) de ([a-zç]+) de (\d{4})", (rotulo or "").lower()
    )
    if not match or match.group(2) not in MESES:
        return fallback.isoformat(timespec="seconds")
    return datetime(
        int(match.group(3)),
        MESES.index(match.group(2)) + 1,
        int(match.group(1)),
        12,
        tzinfo=ZoneInfo("America/Sao_Paulo"),
    ).isoformat(timespec="seconds")


def atualizar_historico(agora, pasta=PROJECT_ROOT):
    pasta = Path(pasta)
    caminho = pasta / "historico.json"
    if caminho.exists():
        with caminho.open(encoding="utf-8") as arquivo:
            historico = json.load(arquivo)
        if not isinstance(historico, list) or any(
            not isinstance(noticia, dict)
            or not isinstance(noticia.get("id"), str)
            for noticia in historico
        ):
            raise ValueError(
                "historico.json precisa conter uma lista de notícias com id."
            )
    else:
        historico = []

    caminho_index = pasta / "index.html"
    if caminho_index.exists():
        pagina = caminho_index.read_text(encoding="utf-8")
        anterior = re.search(
            r"var\s+D\s*=\s*(\{.*?\})\s*,\s*I\s*=\s*D\.itens",
            pagina,
            re.S,
        )
        if anterior:
            edicao = json.loads(anterior.group(1))
            publicado_em = data_publicacao(edicao.get("data"), agora)
            for noticia in edicao.get("itens", []):
                if isinstance(noticia, dict) and isinstance(
                    noticia.get("id"), str
                ):
                    noticia.setdefault("publicado_em", publicado_em)
                    historico.append(noticia)

    unicas = {}
    for noticia in historico:
        unicas.setdefault(noticia["id"], noticia)
    historico = sorted(
        unicas.values(),
        key=lambda noticia: noticia.get("publicado_em", ""),
        reverse=True,
    )
    with caminho.open("w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")
    return historico
