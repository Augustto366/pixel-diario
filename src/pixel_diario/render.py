"""Renderização da edição estática do site."""

import json
from pathlib import Path

from .config import MESES, PROJECT_ROOT, TEMPLATE_PATH


def renderizar(itens, agora, pasta=PROJECT_ROOT, modelo=TEMPLATE_PATH):
    meta = {
        "data": f"{agora.day} de {MESES[agora.month - 1]} de {agora.year}",
        "itens": itens,
    }
    dados = json.dumps(meta, ensure_ascii=False).replace("</", "<\\/")
    template = Path(modelo).read_text(encoding="utf-8")
    if "__DADOS__" not in template:
        raise ValueError("O template não contém o marcador __DADOS__.")
    destino = Path(pasta) / "index.html"
    destino.write_text(template.replace("__DADOS__", dados), encoding="utf-8")
