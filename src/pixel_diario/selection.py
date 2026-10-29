"""Agrupamento, classificação e priorização das notícias."""

import hashlib
import re
from datetime import timedelta

from .config import CATS, HORAS, MAX_POR_FONTE, QUENTES, STOP, TOTAL
from .summarization import gerar_resumo


def tokens(titulo):
    return {
        word for word in re.findall(r"[a-z0-9']+", titulo.lower())
        if len(word) > 2 and word not in STOP
    }


def agrupar(itens):
    grupos = []
    for item in sorted(itens, key=lambda news: news["data"], reverse=True):
        item_tokens = tokens(item["titulo"])
        item["_tk"] = item_tokens
        for group in grupos:
            comuns = len(item_tokens & group["tk"])
            if comuns >= 3 or (
                comuns >= 2
                and comuns / max(1, min(len(item_tokens), len(group["tk"]))) >= 0.6
            ):
                group["itens"].append(item)
                break
        else:
            grupos.append({"tk": item_tokens, "itens": [item]})
    return grupos


def pontuar(grupo, agora):
    fontes = {item["fonte"] for item in grupo["itens"]}
    representante = max(
        grupo["itens"], key=lambda item: (item["peso"], item["data"])
    )
    horas = (agora - representante["data"]).total_seconds() / 3600
    frescor = max(0.0, 1 - horas / 48) * 2
    quentes = min(
        1.5, 0.5 * sum(1 for word in QUENTES if word in representante["_tk"])
    )
    return (
        len(fontes) * 3 + representante["peso"] + frescor + quentes,
        representante,
        sorted(fontes),
    )


def categoria(texto):
    texto = " " + texto.lower() + " "
    for nome, palavras in CATS:
        if any(palavra in texto for palavra in palavras):
            return nome
    return "Jogos"


def escolher(todos, agora):
    corte = agora - timedelta(hours=HORAS)
    recentes = [item for item in todos if item["data"] >= corte]
    if len(recentes) < TOTAL * 2:
        recentes = [
            item for item in todos
            if item["data"] >= agora - timedelta(hours=96)
        ]
    pontuacoes = [
        pontuar(grupo, agora) for grupo in agrupar(recentes)
    ]
    pontuacoes.sort(key=lambda result: result[0], reverse=True)

    por_fonte, escolhidos = {}, []
    for _, representante, fontes in pontuacoes:
        if por_fonte.get(representante["fonte"], 0) >= MAX_POR_FONTE:
            continue
        por_fonte[representante["fonte"]] = (
            por_fonte.get(representante["fonte"], 0) + 1
        )
        escolhidos.append({
            "id": hashlib.sha1(representante["link"].encode()).hexdigest()[:10],
            "cat": categoria(representante["titulo"] + " " + representante["resumo"]),
            "fonte": representante["fonte"],
            "outras": [fonte for fonte in fontes if fonte != representante["fonte"]],
            "titulo": representante["titulo"],
            "resumo": gerar_resumo(
                representante["titulo"], representante["resumo"]
            ),
            "importa": "",
            "link": representante["link"],
        })
        if len(escolhidos) == TOTAL:
            break
    return escolhidos
