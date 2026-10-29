"""Curiosidades históricas da indústria com fontes verificáveis."""

from zoneinfo import ZoneInfo

_FONTE_NINTENDO = (
    "Nintendo — história corporativa",
    "https://www.nintendo.co.jp/corporate/en/history/index.html",
)

_CURIOSIDADES = [
    (
        "A Nintendo começou com cartas",
        "Em 1889, Fusajiro Yamauchi começou a fabricar e vender cartas "
        "japonesas Hanafuda em Kyoto. A empresa só passaria a produzir "
        "videogames muitas décadas depois.",
        _FONTE_NINTENDO,
    ),
    (
        "Cartas ocidentais no Japão",
        "Em 1902, a Nintendo começou a fabricar e vender as primeiras cartas "
        "de baralho ocidentais produzidas no Japão, ampliando seu negócio "
        "original muito antes dos videogames.",
        _FONTE_NINTENDO,
    ),
    (
        "Cartas de plástico pioneiras",
        "Em 1953, a Nintendo se tornou a primeira empresa a produzir em massa "
        "cartas de plástico no Japão — um marco da fase da companhia dedicada "
        "a jogos de cartas.",
        _FONTE_NINTENDO,
    ),
    (
        "Disney chegou às cartas",
        "Em 1959, a Nintendo começou a vender cartas de baralho com personagens "
        "da Disney. A iniciativa ajudou a levar a empresa além das cartas "
        "tradicionais japonesas.",
        _FONTE_NINTENDO,
    ),
    (
        "O nome atual veio em 1963",
        "A companhia mudou seu nome para Nintendo Co., Ltd. em 1963. Naquele "
        "momento, ela ainda estava longe de lançar seus consoles mais famosos.",
        _FONTE_NINTENDO,
    ),
    (
        "Antes dos consoles, uma atração de tiro",
        "Em 1973, a Nintendo desenvolveu o Laser Clay Shooting System, um "
        "sistema de entretenimento para espaços de lazer — uma de suas "
        "experiências com diversão eletrônica antes dos consoles domésticos.",
        _FONTE_NINTENDO,
    ),
    (
        "Os primeiros videogames domésticos da Nintendo",
        "Em 1977, a Nintendo lançou no Japão seus primeiros videogames para "
        "casa: TV Game 15 e TV Game 6. Eles vieram antes do Famicom, conhecido "
        "como NES fora do Japão.",
        _FONTE_NINTENDO,
    ),
    (
        "A Nintendo entrou nos arcades",
        "Em 1978, a Nintendo desenvolveu e começou a vender máquinas de "
        "videogame para fliperamas, antes de Donkey Kong se tornar um de seus "
        "grandes sucessos arcade.",
        _FONTE_NINTENDO,
    ),
    (
        "Game & Watch e a Nintendo of America",
        "Em 1980, a Nintendo lançou a linha portátil Game & Watch e estabeleceu "
        "uma subsidiária integral em Nova York. O ano marcou dois passos "
        "importantes em portátil e expansão internacional.",
        _FONTE_NINTENDO,
    ),
    (
        "Donkey Kong nasceu no arcade",
        "A Nintendo desenvolveu e começou a vender Donkey Kong como jogo de "
        "arcade em 1981. O título surgiu antes da estreia do Famicom e do NES.",
        _FONTE_NINTENDO,
    ),
    (
        "Famicom e NES são o mesmo console",
        "Em 1983, a Nintendo lançou no Japão o Family Computer System, ou "
        "Famicom. O console ficou conhecido como Nintendo Entertainment System "
        "nos mercados fora do Japão.",
        _FONTE_NINTENDO,
    ),
    (
        "Super Mario Bros. chegou em 1985",
        "A Nintendo começou a vender Super Mario Bros. para o NES em 1985, "
        "dois anos depois do lançamento japonês do Famicom.",
        _FONTE_NINTENDO,
    ),
    (
        "Game Boy foi lançado em 1989",
        "A Nintendo lançou o Game Boy em 1989. No ano seguinte, apresentou "
        "também o Super Famicom, chamado Super Nintendo Entertainment System "
        "em outros mercados.",
        _FONTE_NINTENDO,
    ),
    (
        "Nintendo 64 chegou em 1996",
        "O Nintendo 64 foi lançado em 1996, mais de uma década depois do "
        "Famicom e sete anos após o Game Boy.",
        _FONTE_NINTENDO,
    ),
    (
        "Nintendo DS veio antes do Wii",
        "O portátil Nintendo DS foi lançado em 2004. O Wii chegou em 2006, "
        "mostrando como a Nintendo mantinha linhas doméstica e portátil em "
        "paralelo.",
        _FONTE_NINTENDO,
    ),
    (
        "O Switch combina console doméstico e portátil",
        "Quando lançou o Nintendo Switch em 2017, a Nintendo o descreveu como "
        "um console doméstico que também pode ser usado como portátil — uma "
        "combinação das duas formas de jogar.",
        _FONTE_NINTENDO,
    ),
    (
        "O PlayStation original estreou no Japão",
        "O primeiro PlayStation foi lançado no Japão em 3 de dezembro de 1994. "
        "A chegada à América do Norte e à Europa aconteceu em setembro de 1995.",
        (
            "PlayStation — 30 anos de história",
            "https://www.playstation.com/en-us/playstation-history/",
        ),
    ),
    (
        "O PlayStation usava CDs",
        "O PlayStation original usava CD-ROM. Segundo a própria Sony, isso "
        "permitia jogos maiores do que as alternativas em cartucho e ajudava "
        "a fabricar os discos de forma mais rápida e econômica.",
        (
            "PlayStation — 30 anos de história",
            "https://www.playstation.com/en-us/playstation-history/",
        ),
    ),
    (
        "O primeiro PlayStation passou de 100 milhões",
        "A Sony informa que o PlayStation original vendeu mais de 102 milhões "
        "de consoles no mundo entre 1994 e 2006.",
        (
            "PlayStation — 30 anos de história",
            "https://www.playstation.com/en-us/playstation-history/",
        ),
    ),
    (
        "Steam existe desde 2003",
        "A Valve criou o Steam em 2003 como canal de distribuição digital, "
        "antes da popularização das lojas de aplicativos. A plataforma depois "
        "se expandiu para milhares de criadores e editoras.",
        (
            "Valve — sobre a empresa",
            "https://www.valvesoftware.com/en/about",
        ),
    ),
]


def curiosidade_do_dia(agora):
    """Seleciona uma curiosidade diferente a cada dia no fuso de Brasília."""
    data_local = agora.astimezone(ZoneInfo("America/Sao_Paulo")).date()
    titulo, texto, (fonte, link) = _CURIOSIDADES[
        data_local.toordinal() % len(_CURIOSIDADES)
    ]
    return {
        "data": data_local.isoformat(),
        "titulo": titulo,
        "texto": texto,
        "fonte": fonte,
        "link": link,
    }


def _validate_curiosities():
    if not _CURIOSIDADES or any(
        not title or not text or not source or not link.startswith("https://")
        for title, text, (source, link) in _CURIOSIDADES
    ):
        raise ValueError("Todas as curiosidades precisam de texto e fonte HTTPS.")


_validate_curiosities()
