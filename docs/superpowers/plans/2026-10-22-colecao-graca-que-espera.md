# Coleção "Graça que Espera" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar a skill da coleção "Graça que Espera" e escrever com ela o primeiro livro, "Como eram os dias de Noé", entregue em .docx.

**Architecture:** Uma skill nova (`SKILL.md`) que herda a estrutura da skill `manuscrito-biblico` e acrescenta as regras da coleção. Um script Python verifica, de forma automática, se um manuscrito cumpre essas regras. O livro é escrito em Markdown e convertido para .docx com pandoc.

**Tech Stack:** Markdown, Python 3 (`python-docx` 1.2.0), pandoc.

**Spec:** `docs/superpowers/specs/2026-10-22-colecao-graca-que-espera-design.md`

## Global Constraints

- Português brasileiro, tom pastoral; Bíblia Sagrada evangélica como base de tudo.
- Movimento de todo livro: história contada → fragilidade humana → graça de Jesus que restaura com muita paciência.
- A conclusão termina com uma oração curta: o leitor se apresenta a Jesus, agradece pela leitura e pela visão nova, pede encorajamento para "a próxima leitura".
- A oração não cita títulos de outros livros; cada livro é completo em si.
- Nada moralista ou acusador; o final é alegre, não pesado.
- Estrutura herdada da `manuscrito-biblico`: página de rosto, prefácio, introdução, 8–12 capítulos, Carta ao Leitor, conclusão.
- Página de rosto traz "Coleção Graça que Espera".

## Review Focus

1. Oração final citando o título de outro livro — o verificador falha se a oração contiver um título entre aspas ou "Coleção".
2. Conclusão que termina com imagem/explicação depois da oração — o verificador exige que a oração seja a última seção do arquivo.
3. Tom acusador/moralista em algum capítulo — leitura humana do revisor, ponto a ponto, na Task 2.
4. Referências bíblicas sem livro/capítulo/versículo — o verificador conta referências no formato `Livro cap:vers` e exige ≥ 3 por capítulo.
5. Livro curto demais (capítulos rasos) — o verificador exige ≥ 18.000 palavras no total.

---

### Task 1: Skill da coleção + verificador

**Files:**
- Create: `skills/colecao-graca-que-espera/SKILL.md`
- Create: `tools/verificar_manuscrito.py`
- Create: `tools/test_verificar_manuscrito.py`
- Install (cópia, fora do git): `/root/.claude/skills/colecao-graca-que-espera/SKILL.md`

**Interfaces:**
- Produces: `verificar(caminho_md: str) -> list[str]` — lista de problemas (vazia = aprovado). CLI: `python3 tools/verificar_manuscrito.py <arquivo.md>`; sai com código 0 se aprovado, 1 caso contrário, imprimindo cada problema.
- Produces: convenção de títulos no Markdown: `# Prefácio`, `# Introdução`, `# Capítulo N — <título>`, `# Carta ao Leitor`, `# Conclusão`, `## Oração` (último cabeçalho do arquivo, dentro da Conclusão).

- [ ] **Step 1: Escrever os testes do verificador** em `tools/test_verificar_manuscrito.py` (unittest, manuscritos sintéticos em strings):
  - `test_aprova_manuscrito_completo`: 8 capítulos, ≥ 3 referências cada, ≥ 18.000 palavras, `## Oração` final mencionando "Jesus" e "próxima leitura" → `verificar` retorna `[]`.
  - `test_falha_sem_oracao`: sem `## Oração` → problema contendo "Oração".
  - `test_falha_texto_apos_oracao`: cabeçalho depois de `## Oração` → problema contendo "última".
  - `test_falha_oracao_cita_titulo`: oração contém `"Como eram os dias de Noé"` ou "Coleção" → problema contendo "título".
  - `test_falha_poucos_capitulos`: 7 capítulos → problema contendo "capítulos".
  - `test_falha_poucas_referencias`: um capítulo com 2 referências → problema contendo "referências".
  - `test_falha_curto`: < 18.000 palavras → problema contendo "palavras".
  - `test_falha_sem_carta`: sem `# Carta ao Leitor` → problema contendo "Carta".
  - `test_falha_rosto_sem_colecao`: texto antes de `# Prefácio` sem "Coleção Graça que Espera" → problema contendo "rosto".
- [ ] **Step 2: Rodar e ver falhar:** `python3 -m unittest tools/test_verificar_manuscrito.py -v` → FAIL (módulo inexistente).
- [ ] **Step 3: Implementar `verificar`** em `tools/verificar_manuscrito.py`. Referência bíblica = regex `\b[1-3]?\s?[A-ZÁÉÍÓÚ][a-zçãõáéíóúâêô]+\s\d{1,3}:\d{1,3}`. Oração deve conter "Jesus" e "próxima leitura" (sem diferenciar maiúsculas).
- [ ] **Step 4: Rodar e ver passar:** mesmo comando → todos OK.
- [ ] **Step 5: Escrever `skills/colecao-graca-que-espera/SKILL.md`.** Frontmatter `name: colecao-graca-que-espera`; description: escreve um livro da Coleção Graça que Espera a partir de um título. Conteúdo: tudo da `manuscrito-biblico` (fundamentos, processo, estrutura, regras de capítulo), mais as Global Constraints acima, a convenção de títulos acima, e a seção "Oração final" substituindo o encerramento "com imagem". Instrui rodar `tools/verificar_manuscrito.py` antes de entregar e converter com `pandoc manuscrito.md -o <titulo>.docx`.
- [ ] **Step 6: Instalar a cópia** em `/root/.claude/skills/colecao-graca-que-espera/SKILL.md` e confirmar com `diff` (sem saída).
- [ ] **Step 7: Commit:** `git add skills tools && git commit -m "Adiciona skill da Coleção Graça que Espera e verificador de manuscritos"`

### Task 2: Livro 1 — "Como eram os dias de Noé"

**Files:**
- Create: `livros/como-eram-os-dias-de-noe/manuscrito.md`
- Create: `livros/como-eram-os-dias-de-noe/Como-eram-os-dias-de-Noe.docx`

**Interfaces:**
- Consumes: a skill da Task 1 (regras e convenção de títulos) e `verificar_manuscrito.py`.

- [ ] **Step 1: Arco do livro.** Escrever no topo do trabalho (não no arquivo) o arco de 8–12 capítulos: fragilidade = viver num mundo que perdeu o rumo e sentir-se sozinho; graça = a paciência de Deus enquanto a arca era construída (1 Pedro 3:20; 2 Pedro 3:9), cumprida em Cristo (Mateus 24:37-39; Hebreus 11:7).
- [ ] **Step 2: Escrever o manuscrito completo** seguindo a skill, capítulo a capítulo.
- [ ] **Step 3: Verificar:** `python3 tools/verificar_manuscrito.py livros/como-eram-os-dias-de-noe/manuscrito.md` → sai 0, sem problemas. Corrigir e repetir até passar.
- [ ] **Step 4: Revisão de tom** (Review Focus 3): reler cada capítulo procurando acusação ou moralismo; reescrever trechos encontrados.
- [ ] **Step 5: Converter:** `pandoc livros/como-eram-os-dias-de-noe/manuscrito.md -o livros/como-eram-os-dias-de-noe/Como-eram-os-dias-de-Noe.docx` e abrir com `python-docx` para confirmar que o último parágrafo pertence à oração.
- [ ] **Step 6: Commit e push:** `git add livros && git commit -m "Livro 1 da Coleção Graça que Espera: Como eram os dias de Noé" && git push -u origin claude/install-script-execution-2yn8gq`
