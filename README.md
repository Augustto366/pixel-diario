# Pixel Diário

Portal estático de notícias sobre games. Um processo diário coleta feeds RSS e
Atom, agrupa matérias relacionadas, seleciona as mais relevantes e gera a edição
publicada em `index.html`. O histórico de edições fica em `historico.json`.

## Requisitos

- Python 3.12 ou superior
- Conexão com a internet para coletar feeds e tentar traduzir os textos

## Desenvolvimento

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
```

Para gerar uma edição manualmente:

```powershell
python -m pixel_diario
```

O comando legado `python atualizar.py` também continua disponível. Os resumos
são extraídos localmente dos trechos RSS/Atom, sem depender de uma API paga.
Títulos e resumos são traduzidos para português pelo endpoint público do Google
Tradutor; a tradução é uma tentativa gratuita, sujeita a limites e mudanças no
serviço. Se ela falhar, o texto original é mantido e a edição continua.

Uma aba discreta de curiosidade busca artigos inéditos nas categorias da
Wikipédia sobre história e indústria de videogames, usando o resumo do artigo
como base e exibindo o link da fonte. Os identificadores já publicados ficam em
`curiosidades_vistas.json`, versionado junto com cada edição para evitar
repetições. A atualização ocorre com a edição das 20h (horário de Brasília),
sem API paga. O site mantém o crédito e a licença CC BY-SA da Wikipédia. Se a
fonte não estiver disponível ou não houver artigo inédito, a execução falha em
vez de republicar uma curiosidade antiga.

Como a geração usa o conteúdo que os feeds disponibilizam, um resumo pode ser
curto quando a fonte fornece poucos detalhes. Nesse caso, o site informa que
não havia conteúdo além do título, em vez de inventar informações.

## Organização

```text
src/pixel_diario/
  archive.py       persistência e leitura do histórico
  cli.py           fluxo de atualização
  config.py        feeds, regras editoriais e caminhos
  curiosity.py     curiosidades web sem repetição
  feeds.py         download e parsing de RSS/Atom
  render.py        geração de index.html a partir do template
  selection.py     agrupamento, classificação e pontuação
  summarization.py extração local das frases mais informativas
  translation.py   tradução gratuita em caráter opcional
templates/
  index.html       template do site
tests/             testes automatizados sem acesso à rede
```

O workflow do GitHub Actions instala o pacote, executa o comando `pixel-diario`
e publica somente os artefatos gerados (`index.html` e `historico.json`).
