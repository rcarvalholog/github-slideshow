"""Verifica se um manuscrito da Coleção Graça que Espera cumpre as regras da coleção.

Uso: python3 tools/verificar_manuscrito.py <manuscrito.md>
Sai com 0 se aprovado; senão imprime cada problema e sai com 1.
"""
import re
import sys

MIN_CAPITULOS = 8
MAX_CAPITULOS = 12
MIN_REFERENCIAS_POR_CAPITULO = 3
MIN_PALAVRAS = 18000
COLECAO = "Coleção Graça que Espera"
APENDICES = ("Referências bíblicas", "Referências bibliográficas")

REFERENCIA = re.compile(r"\b[1-3]?\s?[A-ZÁÉÍÓÚÂÊÔ][a-zçãõáéíóúâêô]+\s\d{1,3}:\d{1,3}")
CABECALHO = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
CABECALHO_NIVEL_1 = re.compile(r"^#\s+(.*)$", re.MULTILINE)


def _secoes(texto):
    """Lista de (nível, título, corpo) para cada cabeçalho, na ordem do arquivo."""
    marcas = list(CABECALHO.finditer(texto))
    secoes = []
    for i, m in enumerate(marcas):
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        secoes.append((len(m.group(1)), m.group(2).strip(), texto[m.end():fim]))
    return secoes


def _secoes_nivel_1(texto):
    """Lista de (título, corpo) de cada cabeçalho "# ", com o corpo indo até o próximo "# "."""
    marcas = list(CABECALHO_NIVEL_1.finditer(texto))
    return [
        (m.group(1).strip(), texto[m.end():marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)])
        for i, m in enumerate(marcas)
    ]


def verificar(caminho_md):
    with open(caminho_md, encoding="utf-8") as f:
        texto = f.read()
    problemas = []
    secoes = _secoes(texto)
    titulos = [t for _, t, _ in secoes]

    for m in CABECALHO.finditer(texto):
        if m.start() > 0 and not texto[:m.start()].endswith("\n\n"):
            problemas.append(
                f'O cabeçalho "{m.group(2).strip()}" precisa de uma linha em branco antes '
                "(senão o pandoc não o reconhece como título)."
            )

    inicio_prefacio = texto.find("# Prefácio")
    rosto = texto[:inicio_prefacio] if inicio_prefacio >= 0 else ""
    if COLECAO not in rosto:
        problemas.append(f'Página de rosto (antes de "# Prefácio") não traz "{COLECAO}".')

    for obrigatoria in ("Prefácio", "Introdução", "Carta ao Leitor", "Conclusão"):
        if obrigatoria not in titulos:
            problemas.append(f'Falta a seção "# {obrigatoria}".')

    capitulos = [(t, c) for t, c in _secoes_nivel_1(texto) if t.startswith("Capítulo ")]
    if not MIN_CAPITULOS <= len(capitulos) <= MAX_CAPITULOS:
        problemas.append(
            f"O livro tem {len(capitulos)} capítulos; o esperado é de {MIN_CAPITULOS} a {MAX_CAPITULOS}."
        )
    for titulo, corpo in capitulos:
        refs = len(REFERENCIA.findall(corpo))
        if refs < MIN_REFERENCIAS_POR_CAPITULO:
            problemas.append(
                f'"{titulo}" tem {refs} referências bíblicas; o mínimo é {MIN_REFERENCIAS_POR_CAPITULO}.'
            )

    palavras = len(re.findall(r"\w+", texto))
    if palavras < MIN_PALAVRAS:
        problemas.append(f"O livro tem {palavras} palavras; o mínimo é {MIN_PALAVRAS}.")

    if "Oração" not in titulos:
        problemas.append('Falta a "## Oração" no fim da Conclusão.')
    else:
        depois = titulos[len(titulos) - 1 - titulos[::-1].index("Oração") + 1:]
        if any(t not in APENDICES for t in depois):
            problemas.append(
                'A "## Oração" precisa ser a última seção do livro '
                "(depois dela só as listas de referências)."
            )
        oracao = [c for _, t, c in secoes if t == "Oração"][-1]
        if "jesus" not in oracao.lower():
            problemas.append("A oração precisa se dirigir a Jesus.")
        if "próxima leitura" not in oracao.lower():
            problemas.append('A oração precisa pedir encorajamento para "a próxima leitura".')
        cita_titulo = re.search(r'["“][^"”]+["”]', oracao) or re.search(r"\*[^*\n]+\*", oracao)
        if cita_titulo or "coleção" in oracao.lower() or "graça que espera" in oracao.lower():
            problemas.append("A oração não pode citar o título de outro livro nem a coleção.")

    return problemas


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    problemas = verificar(argv[1])
    for p in problemas:
        print(f"- {p}")
    if not problemas:
        print("Aprovado.")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
