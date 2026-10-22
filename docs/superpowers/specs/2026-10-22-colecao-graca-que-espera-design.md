# Coleção "Graça que Espera" — Design

## Intenção

Uma coleção de livros cristãos evangélicos. Cada livro leva o leitor de uma
fragilidade humana até a graça restauradora de Jesus, e o leitor termina feliz,
com uma visão nova e com vontade de ler o próximo livro da coleção.

## Objetivos

- Todo livro tem a Bíblia Sagrada (evangélica) como base de tudo.
- Todo livro segue o mesmo movimento: uma história contada → uma fragilidade
  humana → a graça de Jesus que restaura com muita paciência.
- Toda conclusão termina com uma **oração curta** em que o leitor se apresenta
  a Jesus, agradece pela experiência da leitura e pela visão nova que não
  conhecia, e pede encorajamento para a próxima leitura.
- Cada livro é completo em si; os livros podem ser lidos em qualquer ordem.
  A oração não cita títulos — só abre o coração para "a próxima leitura".
- (Atualização a pedido do autor, livro 3) Os livros citam os títulos já
  publicados da coleção no prefácio, no texto e numa página "Da mesma coleção".

## Fora do escopo

- Publicar os livros na web (pode vir depois, com a skill `publicar-livros-web`).

## O que faria o projeto fracassar

- Um livro moralista, que acusa em vez de restaurar.
- Um livro que termina pesado em vez de alegre.

## Caminhos considerados

1. **Skill própria da coleção, por cima da skill `manuscrito-biblico`. — Escolhido.**
   Todo livro novo sai no padrão da coleção a partir de um título.
2. Alterar a skill `manuscrito-biblico` existente — mudaria também livros fora
   da coleção e perderia o final atual "com imagem".
3. Escrever sem skill — cada livro novo exigiria repetir as regras.

## O que será feito

1. Criar a skill `colecao-graca-que-espera`: usa a estrutura da
   `manuscrito-biblico` e acrescenta as regras da coleção; o final "com imagem"
   da conclusão é substituído pela oração.
2. Escrever o primeiro livro: **"Os dias de Adão"**. ("Como eram os dias de Noé" fica como segundo livro, num trabalho posterior.)

## Escolhas do Claude (para o autor conferir)

- Fragilidade do primeiro livro: a vergonha que nos faz esconder de Deus e dos
  outros (Gênesis 3:8-10); a graça paciente de Deus que procura ("Onde estás?")
  e veste (Gênesis 3:21), cumprida em Cristo, o segundo Adão (Romanos 5:17-19;
  1 Coríntios 15:45).
- Formato de entrega: Word (.docx), pronto para revisão e para a skill de
  publicação na web.
- A skill é salva no repositório e no container; o autor a adiciona à conta
  claude.ai para ela persistir.
