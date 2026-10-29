"""Configurações editoriais e caminhos do projeto."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = PROJECT_ROOT / "templates" / "index.html"

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
MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]
STOP = set(
    "the and for with from that this into over after about their will have has are "
    "was were its his her you your new out how why what who all not but can more "
    "than just says say now one two first game games gaming video get gets".split()
)
QUENTES = [
    "gta", "nintendo", "switch", "xbox", "playstation", "ps5", "ps6", "steam",
    "valve", "microsoft", "sony", "layoff", "layoffs", "union", "acquisition",
    "price", "prices", "ram", "nvidia", "amd", "earnings", "revenue", "record",
    "shutdown", "cyberattack", "delay", "delayed", "launch",
]
CATS = [
    ("Hardware", [
        "gpu", "ram", "nvidia", "amd", "console", "handheld", "steam machine",
        "steam deck", "switch 2", "ps6", "ssd", "memory", "chip", "hardware",
        "rtx", "processor",
    ]),
    ("Mercado", [
        "layoff", "layoffs", "earnings", "revenue", "sales", "acquisition",
        "acquires", "union", "unionize", "stock", "shutdown", "shut down",
        "funding", "investor", "financial", "record", "price increase",
    ]),
    ("Técnico", [
        "unreal", "unity", "engine", "dlss", "fsr", "cyberattack", "security",
        "breach", "ai ", "generative", "developer tool", "open source",
        "patch notes", "benchmark",
    ]),
    ("Plataformas", [
        "steam", "epic games store", "game pass", "playstation plus", "app store",
        "eshop", "store",
    ]),
]
