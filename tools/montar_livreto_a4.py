"""Monta um livreto para impressão: páginas A5 imposicionadas duas a duas em folhas A4.

Uso: python3 tools/montar_livreto_a4.py [--em-ordem] <livro-A5.pdf> <saida-A4.pdf>

--em-ordem: duas páginas por face na ordem normal de leitura (1-2, 3-4, ...),
para imprimir frente e verso sem dobrar (folhas soltas ou espiral).

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


def ordem_sequencial(total):
    """Pares (esquerda, direita) na ordem de leitura; None = página em branco."""
    n = total + total % 2
    return [tuple(p if p < total else None for p in (i, i + 1)) for i in range(0, n, 2)], n


def montar(entrada, saida, em_ordem=False):
    leitor = PdfReader(entrada)
    paginas = leitor.pages
    largura, altura = A4_PAISAGEM
    escritor = PdfWriter()
    pares, n = (ordem_sequencial if em_ordem else ordem_livreto)(len(paginas))
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
    sufixo = " (A4, 2 páginas por face)" if em_ordem else " (livreto A4)"
    escritor.add_metadata({"/Title": (leitor.metadata or {}).get("/Title", "") + sufixo})
    with open(saida, "wb") as f:
        escritor.write(f)
    return len(paginas), n, len(pares)


if __name__ == "__main__":
    em_ordem = "--em-ordem" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--em-ordem"]
    if len(args) != 2:
        print(__doc__)
        sys.exit(2)
    paginas, n, faces = montar(args[0], args[1], em_ordem)
    print(f"{args[1]}: {paginas} páginas A5 -> {n} com brancos -> {faces} faces A4 ({(faces + 1) // 2} folhas)")
