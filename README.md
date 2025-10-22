# CvApply - Documentacao do Projeto

> Status: Rascunho / Skeleton - v0.1
> Licenca sugerida: Apache-2.0
> Alvo de UI: CLI, Desktop (Electron) ou Web local (a decidir no MVP)

Resumo: projeto front-end para criacao e personalizacao de curriculos (CV) com HTML/CSS/JS. Este repositorio segue um template de documentacao com secoes organizadas na pasta `docs`. O protótipo atual inclui uma aplicação Tkinter responsável por realizar verificações prévias de ambiente, coletar as credenciais do LinkedIn e iniciar o fluxo automático de login quando os pré-requisitos são atendidos.

---

## Visao Geral

O CvApply é uma aplicação que utiliza modelos de linguagem (LLM) para gerar e adaptar currículos conforme vagas específicas, facilitando a personalização e otimização do CV para processos seletivos. Além disso, oferece dicas, modelos prontos e recursos avançados para o usuário. O código-fonte está em `src` e a documentação detalhada está organizada por seções em `docs`.

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

- Especificacao do Projeto: `docs/02-Especificação do Projeto.md`
- Projeto de Interface: `docs/04-Projeto de Interface.md`
- Arquitetura da Solucao: `docs/05-Arquitetura da Solução.md`
- Programacao de Funcionalidades: `docs/07-Programação de Funcionalidades.md`

Tambem ha orientacoes especificas em `src/README.md` (uso do site) e `presentation/README.md` (apresentacao).

---

## Como Executar

1. Crie (opcional, mas recomendado) um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
   > A versão do Playwright fixada (1.55.0) já inclui binários recentes do `greenlet`, evitando a necessidade de compilações
   > manuais em ambientes Windows/VMs mesmo com Python 3.14.
2. Instale o runtime do Playwright para o WebKit (necessário apenas na primeira execução):
   ```bash
   playwright install webkit
   ```
3. Inicie a interface nativa:
   ```bash
   python -m src.main
   ```

   Ao iniciar, a aplicação executa automaticamente uma sequência de verificações:

   1. Conectividade com a internet (`https://www.google.com`).
   2. Acesso à página inicial do LinkedIn (com até 5 tentativas e intervalo de 5s).
   3. Presença de credenciais armazenadas localmente.
   4. Validação básica do formato das credenciais (email e senha).

   Em caso de falha em qualquer etapa, a UI apresenta o status individual dos testes e permite tentar novamente após os ajustes necessários. Quando todas as verificações forem aprovadas, o fluxo segue para a coleta de credenciais (primeira execução), onboarding guiado no WebKit e, nas execuções seguintes, tentativa automática de login e abertura da página Home.

### Execução de testes automatizados

Para validar as rotinas de verificação do sistema e garantir a regressão dos fluxos existentes, execute:

```bash
pytest
```

Os testes utilizam `pytest` e cobrem os cenários principais de conectividade e persistência de credenciais, além de manter cenários futuros marcados como `xfail` até que as funcionalidades sejam implementadas.

## Estrutura do Repositorio


---

## Contribuicao e Licenca

- Contribuicoes sao bem-vindas via pull requests.
- Licenca sugerida: Apache-2.0 
