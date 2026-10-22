"""Monta um livreto para impressão: páginas A5 imposicionadas duas a duas em folhas A4.

Uso: python3 tools/montar_livreto_a4.py [--em-ordem] <livro-A5.pdf> <saida-A4.pdf>

--duas-copias: cada face leva a mesma página duas vezes (1|1 na frente, 2|2
no verso). Imprimindo frente e verso e cortando a folha ao meio, saem dois
exemplares A5 com cada página na frente e a seguinte no verso. Funciona com
qualquer modo de virar o papel.

--cortar-empilhar: um exemplar. Imprima frente e verso virando pela borda
curta, corte o maço ao meio e coloque a pilha da direita embaixo da da
esquerda: as páginas A5 ficam em ordem, cada uma com a seguinte no verso.

As páginas são completadas com páginas em branco até um múltiplo de 4 e
dispostas na ordem de livreto (grampo a cavalo): imprimindo frente e verso,
virando pela borda curta, e dobrando o maço ao meio, a leitura sai na ordem.
"""
import sys

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject

A4_PAISAGEM = (841.89, 595.28)


def ordem_livreto(total):
    """Pares (esquerda, direita) de índices 0-based por face; None = página em branco."""
    n = total + (-total) % 4
    pares = []
    for folha in range(n // 4):
        pares.append((n - 1 - 2 * folha, 2 * folha))          # frente
        pares.append((2 * folha + 1, n - 2 - 2 * folha))      # verso
    return [tuple(p if p < total else None for p in par) for par in pares], n


def ordem_duas_copias(total):
    """Cada face repete a mesma página nas duas metades; None = página em branco."""
    n = total + total % 2
    return [(i if i < total else None,) * 2 for i in range(n)], n


def ordem_cortar_empilhar(total):
    """Um exemplar para cortar ao meio e empilhar (direita embaixo da esquerda).

    A metade esquerda das folhas leva as páginas 1..2F e a direita 2F+1..4F.
    Ao virar a folha pela borda curta, o verso da metade esquerda é a metade
    direita da face de trás; por isso o verso de cada página vai do lado oposto.
    """
    n = total + (-total) % 4
    folhas = n // 4
    pares = []
    for j in range(folhas):
        esq, dir_ = 2 * j, 2 * folhas + 2 * j
        pares.append((esq, dir_))              # frente
        pares.append((dir_ + 1, esq + 1))      # verso
    return [tuple(p if p < total else None for p in par) for par in pares], n


MODOS = {"livreto": ordem_livreto, "duas-copias": ordem_duas_copias, "cortar-empilhar": ordem_cortar_empilhar}


def montar(entrada, saida, modo="livreto"):
    leitor = PdfReader(entrada)
    paginas = leitor.pages
    largura, altura = A4_PAISAGEM
    escritor = PdfWriter()
    pares, n = MODOS[modo](len(paginas))
    for esquerda, direita in pares:
        face = PageObject.create_blank_page(width=largura, height=altura)
        for indice, deslocamento in ((esquerda, 0), (direita, largura / 2)):
            if indice is None:
                continue
            pagina = paginas[indice]
            caixa = pagina.mediabox
            escala = min((largura / 2) / float(caixa.width), altura / float(caixa.height))
            dx = deslocamento + ((largura / 2) - float(caixa.width) * escala) / 2
            dy = (altura - float(caixa.height) * escala) / 2
            face.merge_transformed_page(pagina, Transformation().scale(escala).translate(dx, dy))
        face.mediabox = RectangleObject([0, 0, largura, altura])
        escritor.add_page(face)
    sufixo = {"livreto": " (livreto A4)", "duas-copias": " (A4, 2 cópias por folha)",
              "cortar-empilhar": " (A4, cortar e empilhar)"}[modo]
    escritor.add_metadata({"/Title": (leitor.metadata or {}).get("/Title", "") + sufixo})
    with open(saida, "wb") as f:
        escritor.write(f)
    return len(paginas), n, len(pares)


if __name__ == "__main__":
    modo = "livreto"
    for opcao in ("--duas-copias", "--cortar-empilhar"):
        if opcao in sys.argv:
            modo = opcao[2:]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    paginas, n, faces = montar(args[0], args[1], modo)
    print(f"{args[1]}: {paginas} páginas A5 -> {n} com brancos -> {faces} faces A4 ({(faces + 1) // 2} folhas)")
