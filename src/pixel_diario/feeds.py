"""Download e leitura de feeds RSS e Atom."""

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def baixar(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (PixelDiario RSS reader)"}
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()


def _local_name(tag):
    return tag.split("}")[-1].lower()


def _filho(element, *names):
    for child in element:
        if _local_name(child.tag) in names:
            return child
    return None


def limpar(text, limite=300):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limite:
        text = text[:limite].rsplit(" ", 1)[0] + "…"
    return text


def data(text):
    if not text:
        return None
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
        except (TypeError, ValueError, OverflowError):
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def ler_feed(conteudo, fonte, peso):
    raiz = ET.fromstring(conteudo)
    saida = []
    for element in raiz.iter():
        if _local_name(element.tag) not in ("item", "entry"):
            continue
        titulo = _filho(element, "title")
        link_element = _filho(element, "link")
        link = None
        if link_element is not None:
            link = link_element.get("href") or (link_element.text or "").strip()
        if titulo is None or not link or not link.startswith("http"):
            continue
        published = _filho(element, "pubdate", "published", "updated", "date")
        summary = _filho(element, "description", "summary", "encoded", "content")
        published_at = data(published.text if published is not None else None)
        if published_at is None:
            continue
        saida.append({
            "titulo": limpar("".join(titulo.itertext()), 200),
            "link": link,
            "data": published_at,
            "resumo": limpar(
                "".join(summary.itertext()) if summary is not None else "", 1800
            ),
            "fonte": fonte,
            "peso": peso,
        })
    return saida
