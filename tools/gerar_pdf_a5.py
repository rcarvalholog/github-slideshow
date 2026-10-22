"""Gera o PDF em A5 de um livro da Coleção Graça que Espera.

Uso: python3 tools/gerar_pdf_a5.py livros/<slug>/manuscrito.md livros/<slug>/<Titulo>-A5.pdf

Passos: pandoc (Markdown -> HTML), Chromium via Playwright (HTML -> PDF A5)
e pypdf + reportlab (numeração das páginas, menos a página de rosto).
A fonte EB Garamond é baixada do Google Fonts na primeira execução.
"""
import io
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONTES_DIR = os.path.join(os.path.expanduser("~"), ".cache", "graca-que-espera", "fontes")
FONTES_CSS_URL = (
    "https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500"
)

CSS = """
@page { size: A5; margin: 18mm 15mm 20mm 17mm; }
html { font-family: 'EB Garamond', serif; font-size: 11pt; color: #1b1b1b; }
body { margin: 0; line-height: 1.45; text-align: justify; hyphens: auto; }
p { margin: 0; text-indent: 1.2em; orphans: 3; widows: 3; }
h1 + p, h2 + p, .cap-num + h1 + p, blockquote + p, hr + p, p.subtitulo + p,
.secao-inicio > p:first-child { text-indent: 0; }
h1 { font-weight: 500; font-size: 20pt; line-height: 1.15; text-align: center;
     margin: 0 0 9mm; break-before: page; break-after: avoid; }
.cap-num { break-before: page; margin-top: 22mm; text-align: center; font-size: 10pt;
           letter-spacing: 0.18em; text-transform: uppercase; color: #6b5a3a; margin-bottom: 3mm; }
.cap-num + h1 { break-before: avoid; }
h1.sem-numero { margin-top: 22mm; }
h2 { font-weight: 500; font-size: 14pt; text-align: center; margin: 9mm 0 5mm; break-after: avoid; }
p.subtitulo { text-indent: 0; text-align: left; font-weight: 600; font-size: 11.5pt;
              margin: 5mm 0 2mm; break-after: avoid; }
blockquote { margin: 4mm 6mm 6mm; font-style: italic; text-align: left; color: #333; }
blockquote p { text-indent: 0; }
blockquote em { font-style: normal; }
hr { border: 0; margin: 5mm 0; text-align: center; break-after: avoid; }
hr::after { content: "\\2042"; font-size: 13pt; color: #6b5a3a; }
ul { padding-left: 0; list-style: none; font-size: 9.5pt; text-align: left; }
ul li { margin: 0 0 1.4mm; padding-left: 1.2em; text-indent: -1.2em; }
.rosto { break-after: page; height: 170mm; display: flex; flex-direction: column;
         justify-content: center; text-align: center; }
.rosto h1 { break-before: auto; font-size: 23pt; font-weight: 600; letter-spacing: 0.04em; margin: 0 0 6mm;
            text-wrap: balance; }
.rosto p { text-indent: 0; text-align: center; }
.rosto .subtitulo-livro { font-style: italic; font-size: 12pt; margin-bottom: 30mm; text-wrap: balance; }
.rosto .colecao { letter-spacing: 0.2em; text-transform: uppercase; font-size: 9pt; color: #6b5a3a; }
.rosto .versao { font-size: 8.5pt; color: #666; margin-top: 4mm; }
#oracao { break-before: page; margin-top: 25mm; }
.oracao p { text-align: center; text-indent: 0; font-style: italic; font-size: 11.5pt; margin-bottom: 3mm; }
"""

PRINT_JS = """
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: process.argv[3], preferCSSPageSize: true, printBackground: true });
  await browser.close();
})();
"""


def baixar_fontes():
    """Baixa a EB Garamond (TTF) e devolve o CSS @font-face apontando para os arquivos locais."""
    os.makedirs(FONTES_DIR, exist_ok=True)
    pedido = urllib.request.Request(FONTES_CSS_URL, headers={"User-Agent": "Mozilla/4.0"})
    css = urllib.request.urlopen(pedido).read().decode()
    blocos = []
    for bloco in re.findall(r"@font-face\s*{[^}]*}", css):
        estilo = re.search(r"font-style:\s*(\w+)", bloco).group(1)
        peso = re.search(r"font-weight:\s*(\d+)", bloco).group(1)
        url = re.search(r"url\(([^)]*)\)", bloco).group(1)
        destino = os.path.join(FONTES_DIR, f"EBGaramond-{peso}-{estilo}.ttf")
        if not os.path.exists(destino):
            urllib.request.urlretrieve(url, destino)
        blocos.append(bloco.replace(url, "file://" + destino))
    return "\n".join(blocos)


def montar_html(caminho_md, fontes_css):
    corpo = subprocess.run(
        ["pandoc", caminho_md, "-f", "markdown", "-t", "html5"],
        check=True, capture_output=True, text=True,
    ).stdout

    # Página de rosto: tudo antes do Prefácio, sem o marcador de nome do autor.
    inicio = corpo.index('<h1 id="prefácio">')
    rosto, resto = corpo[:inicio], corpo[inicio:]
    rosto = re.sub(r"<p>\[Nome do autor\]</p>\s*", "", rosto)
    rosto = re.sub(r"<p><em>(Citações bíblicas:.*?)</em></p>", r'<p class="versao">\1</p>', rosto)
    rosto = re.sub(r"<p>(Coleção Graça que Espera)</p>", r'<p class="colecao">\1</p>', rosto)
    rosto = re.sub(r"<p><em>(.*?)</em></p>", r'<p class="subtitulo-livro">\1</p>', rosto, count=1, flags=re.S)
    rosto = f'<section class="rosto">{rosto}</section>'

    # "Capítulo Um — Nome" vira número em versalete e nome como título.
    resto = re.sub(
        r'<h1 id="[^"]*">(Capítulo [^<—]+?) — ([^<]+)</h1>',
        r'<div class="cap-num">\1</div><h1>\2</h1>',
        resto,
    )
    resto = re.sub(r"<h1 (id=\"[^\"]*\")>", r'<h1 \1 class="sem-numero">', resto)
    # Parágrafos que são só um subtítulo em negrito (A Palavra, O olhar para Cristo...).
    resto = re.sub(r"<p><strong>([^<]+)</strong></p>", r'<p class="subtitulo">\1</p>', resto)
    # A oração final ganha um bloco próprio, centralizado, até o próximo título de nível 1.
    resto = re.sub(
        r'<h2 id="oração">(.*?)</h2>(.*?)(?=<h1|$)',
        r'<h2 id="oracao">\1</h2><div class="oracao">\2</div>',
        resto,
        count=1,
        flags=re.S,
    )

    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<style>{fontes_css}{CSS}</style></head><body>{rosto}{resto}</body></html>"""


def numerar_paginas(pdf_entrada, pdf_saida, titulo):
    pdfmetrics.registerFont(TTFont("EBGaramond", os.path.join(FONTES_DIR, "EBGaramond-400-normal.ttf")))
    leitor = PdfReader(pdf_entrada)
    escritor = PdfWriter()
    largura, _ = A5
    for i, pagina in enumerate(leitor.pages):
        if i > 0:  # a página de rosto fica sem número
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A5)
            c.setFont("EBGaramond", 9)
            c.setFillGray(0.35)
            c.drawCentredString(largura / 2, 11 * 2.8346, str(i + 1))
            c.save()
            buffer.seek(0)
            pagina.merge_page(PdfReader(buffer).pages[0])
        escritor.add_page(pagina)
    escritor.add_metadata({"/Title": titulo, "/Subject": "Coleção Graça que Espera"})
    with open(pdf_saida, "wb") as f:
        escritor.write(f)
    return len(leitor.pages)


def titulo_legivel(titulo):
    """'OS DIAS DE ADÃO' -> 'Os Dias de Adão' (preposições e artigos em minúsculas)."""
    pequenas = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "para", "por", "com"}
    palavras = titulo.lower().split()
    return " ".join(
        p if i > 0 and p in pequenas else p[:1].upper() + p[1:] for i, p in enumerate(palavras)
    )


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    caminho_md, pdf_saida = argv[1], argv[2]
    titulo = re.search(r"^# (.+)$", open(caminho_md, encoding="utf-8").read(), re.MULTILINE).group(1)
    html = montar_html(caminho_md, baixar_fontes())
    with tempfile.TemporaryDirectory() as tmp:
        caminho_html = os.path.join(tmp, "livro.html")
        pdf_bruto = os.path.join(tmp, "livro.pdf")
        script = os.path.join(tmp, "imprimir.js")
        open(caminho_html, "w", encoding="utf-8").write(html)
        open(script, "w").write(PRINT_JS)
        env = dict(os.environ, NODE_PATH=subprocess.run(
            ["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        subprocess.run(["node", script, caminho_html, pdf_bruto], check=True, env=env)
        paginas = numerar_paginas(pdf_bruto, pdf_saida, titulo_legivel(titulo))
    print(f"{pdf_saida}: {paginas} páginas A5")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
