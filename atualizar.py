#!/usr/bin/env python3
"""Pixel Diário: busca feeds RSS, escolhe as 20 notícias mais relevantes e gera index.html."""
import os, re, sys, json, html, hashlib, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

# (nome, url do feed, peso). Os endereços de feed mudam: se algum falhar, o log mostra qual.
FEEDS = [
    ("Kotaku", "https://kotaku.com/rss", 1.0),
    ("Game Developer", "https://www.gamedeveloper.com/rss.xml", 1.2),
    ("PocketGamer.biz", "https://www.pocketgamer.biz/rss/", 1.0),
    ("GamesIndustry.biz", "https://www.gamesindustry.biz/feed", 1.2),
    ("Game Informer", "https://gameinformer.com/rss.xml", 1.0),
    ("Eurogamer", "https://www.eurogamer.net/feed", 1.0),
    ("PC Gamer", "https://www.pcgamer.com/rss/", 1.0),
    ("IGN", "https://feeds.ign.com/ign/all", 1.0),
    ("Polygon", "https://www.polygon.com/rss/index.xml", 1.0),
    ("VGC", "https://www.videogameschronicle.com/feed/", 1.0),
    ("Rock Paper Shotgun", "https://www.rockpapershotgun.com/feed", 0.9),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/gaming", 1.1),
    ("Tom's Hardware", "https://www.tomshardware.com/feeds/all", 1.0),
    ("Adrenaline", "https://adrenaline.com.br/feed/", 0.9),
]

TOTAL = 20
MAX_POR_FONTE = 4
HORAS = 40
MODELO_IA = "claude-haiku-5-5"
MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
STOP = set("the and for with from that this into over after about their will have has are was were its his her you your new out how why what who all not but can more than just says say now one two first game games gaming video get gets".split())
QUENTES = ["gta","nintendo","switch","xbox","playstation","ps5","ps6","steam","valve","microsoft","sony","layoff","layoffs","union","acquisition","price","prices","ram","nvidia","amd","earnings","revenue","record","shutdown","cyberattack","delay","delayed","launch"]
CATS = [
    ("Hardware", ["gpu","ram","nvidia","amd","console","handheld","steam machine","steam deck","switch 2","ps6","ssd","memory","chip","hardware","rtx","processor"]),
    ("Mercado", ["layoff","layoffs","earnings","revenue","sales","acquisition","acquires","union","unionize","stock","shutdown","shut down","funding","investor","financial","record","price increase"]),
    ("Técnico", ["unreal","unity","engine","dlss","fsr","cyberattack","security","breach","ai ","generative","developer tool","open source","patch notes","benchmark"]),
    ("Plataformas", ["steam","epic games store","game pass","playstation plus","app store","eshop","store"]),
]

def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (PixelDiario RSS reader)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()

def ln(tag):
    return tag.split("}")[-1].lower()

def filho(el, *nomes):
    for c in el:
        if ln(c.tag) in nomes:
            return c
    return None

def limpar(txt, n=300):
    txt = html.unescape(re.sub(r"<[^>]+>", " ", txt or ""))
    txt = re.sub(r"\s+", " ", txt).strip()
    if len(txt) > n:
        txt = txt[:n].rsplit(" ", 1)[0] + "…"
    return txt

def data(txt):
    if not txt:
        return None
    try:
        d = parsedate_to_datetime(txt)
    except Exception:
        try:
            d = datetime.fromisoformat(txt.strip().replace("Z", "+00:00"))
        except Exception:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)

def ler_feed(conteudo, fonte, peso):
    raiz = ET.fromstring(conteudo)
    saida = []
    for el in raiz.iter():
        if ln(el.tag) not in ("item", "entry"):
            continue
        t = filho(el, "title")
        l = filho(el, "link")
        link = None
        if l is not None:
            link = l.get("href") or (l.text or "").strip()
        if t is None or not link or not link.startswith("http"):
            continue
        d = filho(el, "pubdate", "published", "updated", "date")
        s = filho(el, "description", "summary", "encoded", "content")
        dt = data(d.text if d is not None else None)
        if dt is None:
            continue
        saida.append({"titulo": limpar("".join(t.itertext()), 200), "link": link, "data": dt,
                      "resumo": limpar("".join(s.itertext()) if s is not None else ""),
                      "fonte": fonte, "peso": peso})
    return saida

def tokens(titulo):
    return {w for w in re.findall(r"[a-z0-9']+", titulo.lower()) if (len(w) > 2 and w not in STOP)}

def agrupar(itens):
    grupos = []
    for it in sorted(itens, key=lambda x: x["data"], reverse=True):
        tk = tokens(it["titulo"])
        it["_tk"] = tk
        for g in grupos:
            comum = len(tk & g["tk"])
            if comum >= 3 or (comum >= 2 and comum / max(1, min(len(tk), len(g["tk"]))) >= 0.6):
                g["itens"].append(it)
                break
        else:
            grupos.append({"tk": tk, "itens": [it]})
    return grupos

def pontuar(g, agora):
    fontes = {i["fonte"] for i in g["itens"]}
    rep = max(g["itens"], key=lambda i: (i["peso"], i["data"]))
    horas = (agora - rep["data"]).total_seconds() / 3600
    frescor = max(0.0, 1 - horas / 48) * 2
    quentes = min(1.5, 0.5 * sum(1 for w in QUENTES if w in rep["_tk"]))
    return len(fontes) * 3 + rep["peso"] + frescor + quentes, rep, sorted(fontes)

def categoria(txt):
    t = " " + txt.lower() + " "
    for nome, palavras in CATS:
        if any(p in t for p in palavras):
            return nome
    return "Jogos"

def escolher(todos, agora):
    corte = agora - timedelta(hours=HORAS)
    recentes = [i for i in todos if i["data"] >= corte]
    if len(recentes) < TOTAL * 2:
        recentes = [i for i in todos if i["data"] >= agora - timedelta(hours=96)]
    pont = []
    for g in agrupar(recentes):
        p, rep, fontes = pontuar(g, agora)
        pont.append((p, rep, fontes))
    pont.sort(key=lambda x: x[0], reverse=True)
    por_fonte, esc = {}, []
    for p, rep, fontes in pont:
        if por_fonte.get(rep["fonte"], 0) >= MAX_POR_FONTE:
            continue
        por_fonte[rep["fonte"]] = por_fonte.get(rep["fonte"], 0) + 1
        esc.append({"id": hashlib.sha1(rep["link"].encode()).hexdigest()[:10],
                    "cat": categoria(rep["titulo"] + " " + rep["resumo"]),
                    "fonte": rep["fonte"], "outras": [f for f in fontes if f != rep["fonte"]],
                    "titulo": rep["titulo"], "resumo": rep["resumo"], "importa": "", "link": rep["link"]})
        if len(esc) == TOTAL:
            break
    return esc

def traduzir(itens):
    chave = os.environ.get("ANTHROPIC_API_KEY")
    if not chave:
        print("Sem ANTHROPIC_API_KEY: mantendo títulos e trechos originais.")
        return itens
    base = [{"i": n, "titulo": it["titulo"], "resumo": it["resumo"]} for n, it in enumerate(itens)]
    prompt = ("Você edita um portal de notícias de games. Para cada item, devolva em português do Brasil: "
              "'titulo' (traduzido, natural), 'resumo' (1 a 2 frases, escritas com suas palavras, sem copiar o original) "
              "e 'importa' (1 frase sobre por que a notícia importa para o mercado ou para quem joga). "
              "Responda SOMENTE com um array JSON de objetos {i, titulo, resumo, importa}, sem texto extra.\n\n"
              + json.dumps(base, ensure_ascii=False))
    corpo = json.dumps({"model": MODELO_IA, "max_tokens": 6000,
                        "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=corpo, headers={
        "x-api-key": chave, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            resp = json.loads(r.read())
        txt = "".join(b.get("text", "") for b in resp["content"])
        txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
        for o in json.loads(txt):
            it = itens[o["i"]]
            it["titulo"] = o.get("titulo") or it["titulo"]
            it["resumo"] = o.get("resumo") or it["resumo"]
            it["importa"] = o.get("importa", "")
    except Exception as e:
        print("Tradução falhou, seguindo com o original:", e)
    return itens

def renderizar(itens, agora, pasta="."):
    meta = {"data": f"{agora.day} de {MESES[agora.month-1]} de {agora.year}", "itens": itens}
    dados = json.dumps(meta, ensure_ascii=False).replace("</", "<\\/")
    with open(os.path.join(pasta, "template.html"), encoding="utf-8") as f:
        modelo = f.read()
    with open(os.path.join(pasta, "index.html"), "w", encoding="utf-8") as f:
        f.write(modelo.replace("__DADOS__", dados))

def main():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    todos = []
    for nome, url, peso in FEEDS:
        try:
            lidos = ler_feed(baixar(url), nome, peso)
            print(f"ok   {nome}: {len(lidos)} itens")
            todos += lidos
        except Exception as e:
            print(f"FALHA {nome} ({url}): {e}")
    itens = escolher(todos, datetime.now(timezone.utc))
    if len(itens) < 5:
        print("Poucos itens coletados; mantendo a edição anterior.")
        sys.exit(1)
    renderizar(traduzir(itens), agora)
    print(f"Edição gerada com {len(itens)} notícias.")

if __name__ == "__main__":
    main()
