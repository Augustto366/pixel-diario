"""Curiosidades diárias obtidas da Wikipédia sem repetir artigos publicados."""

import json
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import PROJECT_ROOT
from .summarization import gerar_resumo
from .translation import traduzir_curiosidade

_API_URL = "https://en.wikipedia.org/w/api.php"
_CATEGORIES = (
    "Category:History of video games",
    "Category:Video game industry",
)
_USER_AGENT = (
    "PixelDiario/1.0 "
    "(https://github.com/augustto366/pixel-diario; daily curiosity feature)"
)
_STATE_FILENAME = "curiosidades_vistas.json"
_LEGACY_SEEN_TITLES = {
    "Donkey Kong",
    "Famicom",
    "Game Boy",
    "Game & Watch",
    "Hanafuda",
    "History of Nintendo",
    "Laser Clay Shooting System",
    "Nintendo",
    "Nintendo 64",
    "Nintendo DS",
    "Nintendo Playing Cards",
    "Nintendo Switch",
    "Nintendo Entertainment System",
    "PlayStation (console)",
    "Steam (service)",
    "Super Mario Bros.",
    "TV Game",
    "Video game industry",
    "Wii",
}


def _normalized_title(title):
    return " ".join(title.casefold().split())


def _request(parameters):
    query = urllib.parse.urlencode(parameters)
    request = urllib.request.Request(
        f"{_API_URL}?{query}",
        headers={"User-Agent": _USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read())
    if "error" in payload:
        raise ValueError(f"Erro da API da Wikipédia: {payload['error']}")
    return payload


def _load_state(path):
    if not path.exists():
        return {
            "category_index": 0,
            "continue": None,
            "pending": [],
            "seen": [],
            "seen_titles": sorted(_LEGACY_SEEN_TITLES),
        }
    with path.open(encoding="utf-8") as file:
        state = json.load(file)
    if (
        not isinstance(state, dict)
        or not isinstance(state.get("category_index"), int)
        or state["category_index"] < 0
        or not isinstance(state.get("pending"), list)
        or not isinstance(state.get("seen"), list)
        or not isinstance(state.get("seen_titles"), list)
        or (
            state.get("continue") is not None
            and not isinstance(state["continue"], str)
        )
        or any(not isinstance(page_id, int) for page_id in state["seen"])
        or any(not isinstance(title, str) for title in state["seen_titles"])
        or any(
            not isinstance(page, dict)
            or not isinstance(page.get("pageid"), int)
            or not isinstance(page.get("title"), str)
            for page in state["pending"]
        )
    ):
        raise ValueError(f"Arquivo de histórico de curiosidades inválido: {path}")
    return state


def _save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            delete=False,
        ) as file:
            json.dump(state, file, ensure_ascii=False, indent=2)
            file.write("\n")
            temporary_path = Path(file.name)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _next_page(state):
    seen_titles = {
        _normalized_title(title) for title in state["seen_titles"]
    }
    while state["category_index"] < len(_CATEGORIES):
        if state["pending"]:
            candidate = state["pending"].pop(0)
            if (
                candidate["pageid"] not in state["seen"]
                and _normalized_title(candidate["title"])
                not in seen_titles
            ):
                return candidate
            continue

        parameters = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": _CATEGORIES[state["category_index"]],
            "cmnamespace": 0,
            "cmlimit": 50,
            "format": "json",
            "formatversion": 2,
        }
        continuation = state.get("continue")
        if continuation:
            parameters["cmcontinue"] = continuation
            parameters["continue"] = "-||"

        response = _request(parameters)
        members = response.get("query", {}).get("categorymembers", [])
        state["pending"] = [
            {"pageid": page["pageid"], "title": page["title"]}
            for page in members
            if isinstance(page.get("pageid"), int)
            and isinstance(page.get("title"), str)
            and page["pageid"] not in state["seen"]
        ]
        state["continue"] = response.get("continue", {}).get("cmcontinue")
        if not state["pending"] and state["continue"] is None:
            state["category_index"] += 1
            state["continue"] = None

    raise RuntimeError(
        "Não há mais artigos inéditos nas categorias de curiosidades da Wikipédia."
    )


def _article(page_id):
    response = _request({
        "action": "query",
        "pageids": page_id,
        "prop": "extracts|info",
        "exintro": 1,
        "explaintext": 1,
        "inprop": "url",
        "format": "json",
        "formatversion": 2,
    })
    pages = response.get("query", {}).get("pages", [])
    if not pages or pages[0].get("pageid") != page_id:
        raise ValueError(f"A Wikipédia não retornou o artigo {page_id}.")
    page = pages[0]
    excerpt = page.get("extract", "").strip()
    link = page.get("fullurl", "").strip()
    if not excerpt or not link.startswith("https://"):
        raise ValueError(f"O artigo {page_id} não tem resumo ou link válido.")
    return page, excerpt, link


def curiosidade_do_dia(agora, pasta=PROJECT_ROOT):
    """Obtém o próximo artigo inédito e registra sua publicação."""
    data_local = agora.astimezone(ZoneInfo("America/Sao_Paulo")).date()
    caminho_estado = Path(pasta) / _STATE_FILENAME
    estado = _load_state(caminho_estado)

    while True:
        candidato = _next_page(estado)
        page_id = candidato["pageid"]
        try:
            artigo, trecho, link = _article(page_id)
        except ValueError as error:
            print(f"Artigo ignorado ({candidato['title']}): {error}")
            estado["seen"].append(page_id)
            continue

        titulo_original = artigo.get("title") or candidato["title"]
        texto = gerar_resumo(titulo_original, trecho)
        curiosidade = traduzir_curiosidade({
            "data": data_local.isoformat(),
            "titulo": titulo_original,
            "texto": texto,
            "fonte": f"Wikipédia — {titulo_original}",
            "link": link,
        })
        estado["seen"].append(page_id)
        estado["seen_titles"].append(titulo_original)
        _save_state(caminho_estado, estado)
        return curiosidade
