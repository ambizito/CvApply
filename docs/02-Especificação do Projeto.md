# Especificações do Projeto

O CvApply é uma aplicação que utiliza modelos de linguagem (LLM) para gerar e adaptar currículos conforme vagas específicas, permitindo ao usuário personalizar seu CV de forma inteligente e automatizada.


## Requisitos

As tabelas que se seguem apresentam os requisitos funcionais e não funcionais que detalham o escopo do projeto.

### Requisitos Funcionais

|ID    | Descrição do Requisito  | Prioridade |
|------|------------------------------------------------------------------------------------|----|
|RF-001| A aplicação deverá permitir o download do “CV em diferentes formatos, pdf, txt...” | ALTA |
|RF-002| A aplicação deve ser capaz de salvar meus dados.                                   | MÉDIA |
|RF-003| A aplicação deve possuir um tópico de dicas de como montar um CV.                  | BAIXA |
|RF-006| A aplicação deve possuir layouts predefinidos e a opção de personalização.         | ALTA |
|RF-007| A aplicação deve ter páginas de fácil navegação, para facilitar correções,         | MÉDIA |
|      | caso seja necessário                                                               |      |
|RF-008| A aplicação deve identificar quando um CAPTCHA aparecer e solicitar ao usuário     | ALTA |
|      | que o resolva antes de prosseguir.                                                 |      |
|RF-009| A aplicação deve permitir a redação de cartas de apresentação personalizadas para  | ALTA |
|      | cada candidatura.                                                                  |      |
|RF-010| A aplicação deve redigir emails de candidatura endereçados à empresa da vaga.      | MÉDIA |


### Requisitos não Funcionais

|ID     | Descrição do Requisito  |Prioridade |
|-------|-------------------------------------------------------------------|----|
|RNF-001| A aplicação deve responder aos comandos em menos de 1 segundo.  | ALTA |
|RNF-004| A aplicação deve se recuperar de falhas em 1 segundo e ser      | BAIXA |
|       | passível de atualizações e correções em 2 ou 3 semanas.         |       |
|RNF-005| A aplicação deverá ser capaz de concluir a tarefa em no máximo  | ALTA |
|       | 1 minuto.                                                       |      |
|RNF-007| A aplicação deve ter um layout simples, moderno e de fácil      | ALTA |
|RNF-008| A aplicação deverá ser ágil, versátil e sem travamentos.        | ALTA |


## Restrições

O projeto está restrito pelos itens apresentados na tabela a seguir.

|ID| Restrição                                             |
|--|-------------------------------------------------------|
|RE-01 |   |


## Recursos Principais

- Ingestão de dados: formulários, LinkedIn (scraping autenticado), GitHub, PDF/DOCX.
- Unificação de experiências: deduplicação e mesclagem assistida (LLM), com campos fixos e “forçar inclusão”.
- Busca de vagas (LinkedIn): pesquisa por palavras‑chave, local/remoto, nível e filtros básicos.
- Geração de currículo ATS‑friendly (PT‑BR/EN), carta de apresentação e respostas para screening.
- Edição com diffs e versionamento por vaga; exportação em PDF/DOCX/HTML/Markdown.
- “Um clique” para abrir/preencher candidatura (quando possível), com confirmações humanas.
- Suporte multi‑LLM (OpenAI/Azure/Anthropic/Local via Ollama) com fallback configurável.
- Armazenamento local em JSON.

## Modos de Interface


## Fluxo de Uso (alto nível)

0. Pré-verificações: validar conexão com a internet, acesso ao LinkedIn e credenciais locais antes de iniciar o onboarding.
1. Perfil: usuário preenche formulários ou importa dados (LinkedIn/GitHub/CV).
2. Normalização: merge/dedupe; marcar campos fixos e forçar inclusão quando necessário.
3. Vagas: busca/scraping no LinkedIn; salvar seleção.
4. Geração: produzir CV/carta/answers alinhados à vaga; revisão humana com diffs.
5. Exportação: salvar em PDF/DOCX/HTML/MD e organizar por vaga/versão.

## Segurança e Privacidade

- Local‑first: dados permanecem no disco do usuário.
- LLM Cloud (opcional): revisar políticas dos provedores antes de habilitar.
- Sem telemetria: não enviamos dados para terceiros.
- Aviso: automação/scraping podem violar ToS de terceiros; uso é de responsabilidade do usuário.
