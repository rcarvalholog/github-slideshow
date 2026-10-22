import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from verificar_manuscrito import verificar  # noqa: E402

PALAVRAS_POR_CAPITULO = 2400
ORACAO = (
    "## Oração\n\n"
    "Senhor Jesus, eu me apresento a Ti. Obrigado por esta leitura e pela visão "
    "nova que eu não conhecia. Encoraja meu coração para a próxima leitura. Amém.\n"
)


def capitulo(n, referencias=3):
    refs = " ".join(f"(Gênesis {n}:{i + 1})" for i in range(referencias))
    corpo = " ".join(["graça"] * PALAVRAS_POR_CAPITULO)
    return f"# Capítulo {n} — Título {n}\n\n{refs}\n\n{corpo}\n\n"


def manuscrito(
    capitulos=8,
    referencias=3,
    oracao=ORACAO,
    carta=True,
    rosto="# Os dias de Adão\n\nColeção Graça que Espera\n\n",
    palavras_por_capitulo=None,
    depois_da_oracao="",
):
    global PALAVRAS_POR_CAPITULO
    antigo = PALAVRAS_POR_CAPITULO
    if palavras_por_capitulo is not None:
        PALAVRAS_POR_CAPITULO = palavras_por_capitulo
    try:
        partes = [rosto, "# Prefácio\n\nTexto.\n\n", "# Introdução\n\nTexto.\n\n"]
        partes += [capitulo(n, referencias) for n in range(1, capitulos + 1)]
    finally:
        PALAVRAS_POR_CAPITULO = antigo
    if carta:
        partes.append("# Carta ao Leitor\n\nQuerido leitor.\n\n")
    partes.append("# Conclusão\n\nTexto.\n\n")
    if oracao:
        partes.append(oracao)
    partes.append(depois_da_oracao)
    return "".join(partes)


class VerificarManuscritoTest(unittest.TestCase):
    def rodar(self, texto):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(texto)
        try:
            return verificar(f.name)
        finally:
            os.unlink(f.name)

    def assertProblema(self, problemas, trecho):
        self.assertTrue(
            any(trecho in p for p in problemas),
            f"esperava problema contendo {trecho!r}, veio {problemas!r}",
        )

    def test_aprova_manuscrito_completo(self):
        self.assertEqual(self.rodar(manuscrito()), [])

    def test_falha_sem_oracao(self):
        self.assertProblema(self.rodar(manuscrito(oracao="")), "Oração")

    def test_falha_texto_apos_oracao(self):
        texto = manuscrito(depois_da_oracao="## Epílogo\n\nMais texto.\n")
        self.assertProblema(self.rodar(texto), "última")

    def test_aprova_listas_de_referencias_apos_oracao(self):
        texto = manuscrito(
            depois_da_oracao=(
                "# Referências bíblicas\n\nGênesis 3:9 — Deus procura Adão\n\n"
                "# Referências bibliográficas\n\nKELLER, Timothy. *O Deus Pródigo*.\n"
            )
        )
        self.assertEqual(self.rodar(texto), [])

    def test_falha_oracao_cita_titulo(self):
        oracao = ORACAO.replace("Amém.", 'Quero ler "Como eram os dias de Noé". Amém.')
        self.assertProblema(self.rodar(manuscrito(oracao=oracao)), "título")

    def test_falha_oracao_cita_colecao(self):
        oracao = ORACAO.replace("Amém.", "Obrigado pela Coleção. Amém.")
        self.assertProblema(self.rodar(manuscrito(oracao=oracao)), "título")

    def test_falha_oracao_sem_jesus(self):
        oracao = ORACAO.replace("Senhor Jesus", "Senhor")
        self.assertProblema(self.rodar(manuscrito(oracao=oracao)), "Jesus")

    def test_falha_poucos_capitulos(self):
        texto = manuscrito(capitulos=7, palavras_por_capitulo=3000)
        self.assertProblema(self.rodar(texto), "capítulos")

    def test_falha_poucas_referencias(self):
        self.assertProblema(self.rodar(manuscrito(referencias=2)), "referências")

    def test_falha_curto(self):
        texto = manuscrito(palavras_por_capitulo=100)
        self.assertProblema(self.rodar(texto), "palavras")

    def test_falha_sem_carta(self):
        self.assertProblema(self.rodar(manuscrito(carta=False)), "Carta")

    def test_falha_rosto_sem_colecao(self):
        texto = manuscrito(rosto="# Os dias de Adão\n\n")
        self.assertProblema(self.rodar(texto), "rosto")


if __name__ == "__main__":
    unittest.main()
