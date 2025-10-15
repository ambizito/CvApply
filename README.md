# CvApply - Documentacao do Projeto

> Status: Rascunho / Skeleton - v0.1
> Licenca sugerida: Apache-2.0
> Alvo de UI: CLI, Desktop (Electron) ou Web local (a decidir no MVP)

Resumo: projeto front-end para criacao e personalizacao de curriculos (CV) com HTML/CSS/JS. Este repositorio segue um template de documentacao com secoes organizadas na pasta `docs`.

---

## Visao Geral

O CvApply e um site estatico que ajuda o usuario a montar um curriculo de forma simples e rapida, alem de oferecer dicas e modelos prontos. O codigo-fonte do site esta em `src` e a documentacao detalhada esta organizada por secoes em `docs`.

---

## Recursos Principais

- Ingestao de dados: formularios, LinkedIn (scraping autenticado), GitHub, PDF/DOCX.
- Unificacao de experiencias: deduplicacao e mesclagem assistida (LLM), com campos fixos e "forcar inclusao".
- Busca de vagas (LinkedIn): pesquisa por palavras-chave, local/remoto, nivel e filtros basicos.
- Geracao de curriculo ATS-friendly (PT-BR/EN), carta de apresentacao e respostas para screening.
- Edicao com diffs e versionamento por vaga; exportacao em PDF/DOCX/HTML/Markdown.
- "Um clique" para abrir/preencher candidatura (quando possivel), com confirmacoes humanas.
- Suporte multi-LLM (OpenAI/Azure/Anthropic/Local via Ollama) com fallback configuravel.
- Armazenamento local (sem banco) em JSON/YAML.

---

## Documentacao

- Documentacao de Contexto: `docs/01-Documentacao de Contexto.md`
- Especificacao do Projeto: `docs/02-Especificação do Projeto.md`
- Projeto de Interface: `docs/04-Projeto de Interface.md`
- Arquitetura da Solucao: `docs/05-Arquitetura da Solução.md`
- Programacao de Funcionalidades: `docs/07-Programação de Funcionalidades.md`

Tambem ha orientacoes especificas em `src/README.md` (uso do site) e `presentation/README.md` (apresentacao).

---

## Como Executar

- Opcao rapida: abra `src/index.html` diretamente no navegador.
- Servidor local (recomendado): sirva a pasta `src` com qualquer servidor HTTP estatico.

Exemplos:

```
# Python 3
python -m http.server -d src 5500

# Node (npx serve)
npx serve src -l 5500
```

Depois acesse `http://localhost:5500`.

---

## Estrutura do Repositorio

- `docs/` - documentacao do projeto por secoes
- `src/` - codigo-fonte do site (HTML/CSS/JS e assets)
- `presentation/` - materiais de apresentacao
- `README.md` - indice principal com links para as secoes em `docs`

---

## Contribuicao e Licenca

- Contribuicoes sao bem-vindas via pull requests.
- Licenca sugerida: Apache-2.0 (ajuste se necessario).

