"""Junta capa, miolo e contracapa num arquivo único.

Uso: python3 tools/juntar_capa.py [--livreto] <capa.pdf> <miolo.pdf> <contracapa.pdf> <saida.pdf>

Sem --livreto (leitura na tela): capa, miolo e contracapa, em sequência.
Com --livreto (para montar_livreto_a4.py): capa, verso da capa em branco,
miolo, páginas em branco até completar um múltiplo de 4 e a contracapa como
última página, para capa e contracapa ficarem na folha de fora do livreto.
"""
import sys

from pypdf import PdfReader, PdfWriter


def juntar(capa, miolo, contracapa, saida, livreto=False):
    escritor = PdfWriter()
    pagina_capa = PdfReader(capa).pages[0]
    largura, altura = float(pagina_capa.mediabox.width), float(pagina_capa.mediabox.height)
    escritor.add_page(pagina_capa)
    if livreto:
        escritor.add_blank_page(largura, altura)
    for pagina in PdfReader(miolo).pages:
        escritor.add_page(pagina)
    if livreto:
        while (len(escritor.pages) + 1) % 4:
            escritor.add_blank_page(largura, altura)
    escritor.add_page(PdfReader(contracapa).pages[0])
    titulo = (PdfReader(miolo).metadata or {}).get("/Title", "")
    escritor.add_metadata({"/Title": titulo})
    with open(saida, "wb") as f:
        escritor.write(f)
    return len(escritor.pages)


if __name__ == "__main__":
    livreto = "--livreto" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--livreto"]
    if len(args) != 4:
        print(__doc__)
        sys.exit(2)
    print(f"{args[3]}: {juntar(*args, livreto=livreto)} páginas")
