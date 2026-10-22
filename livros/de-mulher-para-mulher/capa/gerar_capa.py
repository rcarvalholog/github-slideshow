"""Gera a capa e a contracapa de "De mulher para mulher" (A5, preto puro, sem moldura).

Uso: python3 livros/de-mulher-para-mulher/capa/gerar_capa.py
Saídas: capa.pdf e contracapa.pdf nesta pasta. A gravura é gravura-opcao-4.png.
Requer a fonte EB Garamond baixada por tools/gerar_pdf_a5.py.
"""
import os

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph

PASTA = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(os.path.expanduser("~"), ".cache", "graca-que-espera", "fontes")
for nome, arquivo in [("G", "400-normal"), ("GI", "400-italic"), ("GB", "600-normal")]:
    pdfmetrics.registerFont(TTFont(nome, os.path.join(FONTES, f"EBGaramond-{arquivo}.ttf")))
LARGURA, ALTURA = A5


def espacado(c, texto, fonte, tamanho, y, espaco):
    largura = sum(pdfmetrics.stringWidth(ch, fonte, tamanho) for ch in texto) + espaco * (len(texto) - 1)
    x = (LARGURA - largura) / 2
    c.setFont(fonte, tamanho)
    for ch in texto:
        c.drawString(x, y, ch)
        x += pdfmetrics.stringWidth(ch, fonte, tamanho) + espaco


def ornamento(c, y):
    c.setLineWidth(0.5)
    c.line(LARGURA / 2 - 22 * mm, y, LARGURA / 2 - 4 * mm, y)
    c.line(LARGURA / 2 + 4 * mm, y, LARGURA / 2 + 22 * mm, y)
    c.circle(LARGURA / 2, y, 1.1 * mm, fill=1)


def nova_pagina(caminho, titulo):
    c = canvas.Canvas(caminho, pagesize=A5)
    c.setTitle(titulo)
    c.setFillGray(0)
    c.setStrokeGray(0)
    return c


def capa():
    c = nova_pagina(os.path.join(PASTA, "capa.pdf"), "De mulher para mulher — capa")
    espacado(c, "DE MULHER", "GB", 26, ALTURA - 36 * mm, 1.5)
    c.setFont("GI", 14)
    c.drawCentredString(LARGURA / 2, ALTURA - 43.5 * mm, "para")
    espacado(c, "MULHER", "GB", 26, ALTURA - 54 * mm, 1.5)
    ornamento(c, ALTURA - 61 * mm)
    c.setFont("GI", 10.5)
    c.drawCentredString(LARGURA / 2, ALTURA - 68 * mm, "Eva conta a você a sua história,")
    c.drawCentredString(LARGURA / 2, ALTURA - 73 * mm, "do primeiro dia à criação dos filhos")
    largura_img = 128 * mm
    altura_img = largura_img * 720 / 1280
    topo, base = ALTURA - 80 * mm, 34 * mm
    y = base + ((topo - base) - altura_img) / 2
    c.drawImage(os.path.join(PASTA, "gravura-opcao-4.png"), (LARGURA - largura_img) / 2, y, largura_img, altura_img)
    ornamento(c, 29 * mm)
    espacado(c, "COLEÇÃO GRAÇA QUE ESPERA", "G", 8, 22.5 * mm, 2.2)
    c.setFont("G", 12.5)
    c.drawCentredString(LARGURA / 2, 15.5 * mm, "Ricardo Carvalho Barbosa")
    c.showPage()
    c.save()


def contracapa():
    c = nova_pagina(os.path.join(PASTA, "contracapa.pdf"), "De mulher para mulher — contracapa")
    corpo = ParagraphStyle("c", fontName="G", fontSize=11.5, leading=16.5, alignment=TA_JUSTIFY, spaceAfter=8)
    citacao = ParagraphStyle("q", fontName="GI", fontSize=13, leading=17, alignment=TA_CENTER, spaceAfter=14)
    texto = [
        Paragraph("“Querida, sente-se aqui comigo.<br/>Não precisa ter pressa.”", citacao),
        Paragraph(
            "Quase tudo o que se diz sobre Eva cabe numa frase: foi ela quem comeu o fruto. "
            "Mas a história dela é muito maior do que aquela tarde.", corpo),
        Paragraph(
            "Neste livro, a primeira mulher conversa com você, de mulher para mulher. Conta o dia em "
            "que nasceu, o encontro com Adão, as tardes com Deus, a conversa que não deveria ter tido, "
            "as roupas que o Senhor costurou com as próprias mãos, os filhos que criou, o túmulo que "
            "cavou e os netos que começaram a orar.", corpo),
        Paragraph(
            "Em cada capítulo, Eva abre a Bíblia Sagrada, mostra onde Jesus aparece na sua história e "
            "deixa um conselho para a sua vida. Porque a história de uma mulher não termina no seu "
            "pior dia. Deus escreve depois.", corpo),
    ]
    Frame(19 * mm, 80 * mm, LARGURA - 38 * mm, 98 * mm, showBoundary=0,
          leftPadding=0, rightPadding=0, topPadding=0).addFromList(texto, c)
    ornamento(c, 72 * mm)
    espacado(c, "COLEÇÃO GRAÇA QUE ESPERA", "G", 8, 63 * mm, 2.2)
    c.setFont("GI", 10.5)
    for k, titulo in enumerate(["Os dias de Adão", "Os pensamentos de Eva", "De mulher para mulher"]):
        c.drawCentredString(LARGURA / 2, (55 - 6 * k) * mm, titulo)
    ornamento(c, 31 * mm)
    c.setFont("G", 12.5)
    c.drawCentredString(LARGURA / 2, 21 * mm, "Ricardo Carvalho Barbosa")
    c.showPage()
    c.save()


if __name__ == "__main__":
    capa()
    contracapa()
    print("capa.pdf e contracapa.pdf gerados em", PASTA)
