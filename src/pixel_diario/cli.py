"""Orquestração do processo de atualização diária."""

import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from .archive import atualizar_historico
from .config import FEEDS
from .feeds import baixar, ler_feed
from .render import renderizar
from .selection import escolher
from .translation import traduzir


def main():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    todos = []
    for nome, url, peso in FEEDS:
        try:
            lidos = ler_feed(baixar(url), nome, peso)
            print(f"ok   {nome}: {len(lidos)} itens")
            todos += lidos
        except Exception as error:
            print(f"FALHA {nome} ({url}): {error}")
    itens = escolher(todos, datetime.now(timezone.utc))
    if len(itens) < 5:
        print("Poucos itens coletados; mantendo a edição anterior.")
        sys.exit(1)
    itens = traduzir(itens)
    atualizar_historico(agora)
    renderizar(itens, agora)
    print(f"Edição gerada com {len(itens)} notícias.")
