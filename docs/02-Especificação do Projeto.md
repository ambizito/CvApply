# Especificacoes do Projeto

Os pontos mais relevantes foram observados no nosso dia a dia, como trabalhadores ou recrutadores, sempre nos deparamos com alguns desses problemas.

## Requisitos

As tabelas a seguir consolidam os requisitos funcionais e nao funcionais derivados dos Recursos Principais.

### Requisitos Funcionais

| ID     | Descricao do Requisito                                                                                              | Prioridade |
|--------|---------------------------------------------------------------------------------------------------------------------|------------|
| RF-001 | Importar dados via formularios e por arquivos (PDF/DOCX), com integracoes para LinkedIn e GitHub.                   | ALTA       |
| RF-002 | Unificar e deduplicar experiencias com mesclagem assistida (LLM), permitindo "campos fixos" e "forcar inclusao".   | ALTA       |
| RF-003 | Pesquisar vagas (LinkedIn) com filtros (palavra-chave, local/remoto, nivel) e salvar selecoes.                      | MEDIA      |
| RF-004 | Gerar curriculo ATS-friendly (PT-BR/EN), carta de apresentacao e respostas de screening alinhadas a vaga.           | ALTA       |
| RF-005 | Editar com diffs e manter versionamento por vaga, com historico de geracoes.                                        | MEDIA      |
| RF-006 | Exportar artefatos em PDF, DOCX, HTML e Markdown.                                                                    | ALTA       |
| RF-007 | Preencher candidatura com "um clique" quando possivel, solicitando confirmacoes humanas antes de enviar.           | MEDIA      |
| RF-008 | Selecionar provedor de LLM (OpenAI/Azure/Anthropic/Local via Ollama) com fallback configuravel.                     | MEDIA      |
| RF-009 | Armazenar dados localmente (sem banco) em JSON/YAML: perfis, vagas, geracoes e configuracoes.                       | ALTA       |
| RF-010 | Interface Web local responsiva e acessivel, com navegacao simples entre etapas.                                      | ALTA       |
| RF-011 | Permitir configuracao de idioma (PT-BR/EN) para CV e carta.                                                          | MEDIA      |

### Requisitos Nao Funcionais

| ID      | Descricao do Requisito                                                                                 | Prioridade |
|---------|---------------------------------------------------------------------------------------------------------|------------|
| RNF-001 | Desempenho: interacoes comuns < 500 ms; geracoes/exportacoes < 5 s em hardware comum.                  | ALTA       |
| RNF-002 | Responsividade: uso fluido em desktop e dispositivos moveis.                                           | ALTA       |
| RNF-003 | Privacidade: dados locais por padrao; sem telemetria; LLM em nuvem apenas com consentimento explicito. | ALTA       |
| RNF-004 | Confiabilidade: nao corromper dados; versoes imutaveis; recuperacao de sessao apos falhas.             | MEDIA      |
| RNF-005 | Compatibilidade: navegadores modernos (Chrome, Edge, Firefox, Safari) atualizados.                     | MEDIA      |
| RNF-006 | Acessibilidade/Usabilidade: navegacao por teclado, contraste adequado e marcas ARIA basicas.           | MEDIA      |
| RNF-007 | Extensibilidade: arquitetura por adapters (LLM/Scraper/Export) e configuracao declarativa.             | MEDIA      |
| RNF-008 | Manutenibilidade: codigo modular, documentado e com logs legiveis.                                     | MEDIA      |
| RNF-009 | Seguranca: validacao de entradas e de arquivos importados; evitar execucao de conteudo nao confiavel.  | ALTA       |
| RNF-010 | Offline-first: funcionalidades principais sem conexao; degradacao graciosa quando usar servicos externos.| MEDIA     |

## Restricoes

O projeto esta restrito pelos itens apresentados na tabela a seguir.

|ID| Restricao                                             |
|--|-------------------------------------------------------|
|RE-01 | Inicialmente a aplicacao nao tera banco de dados  |
|RE-02 | A aplicacao deve ser implementada em HTML, CSS e JavaScript.  |
|RE-03 | A aplicacao deve ser executavel em diversas plataformas como Windows, Unix, Android e iOS.   |
|RE-04 | A aplicacao devera se integrar com sistemas legados.   |

## Recursos Principais

Conteudo movido para `README.md` (pagina principal) para dar visao rapida do produto.

## Modos de Interface

- Web Local: interface principal deste repositorio (site estatico em `src`).
- CLI/Desktop (futuros): mantidos como opcoes de evolucao do MVP.

## Fluxo de Uso (alto nivel)

1. Perfil: usuario preenche formularios ou importa dados (LinkedIn/GitHub/CV).
2. Normalizacao: merge/dedupe; marcar campos fixos e forcar inclusao quando necessario.
3. Vagas: busca/scraping no LinkedIn; salvar selecao.
4. Geracao: produzir CV/carta/answers alinhados a vaga; revisao humana com diffs.
5. Exportacao: salvar em PDF/DOCX/HTML/MD e organizar por vaga/versao.

## Seguranca e Privacidade

- Local-first: dados permanecem no disco do usuario.
- LLM Cloud (opcional): revisar politicas dos provedores antes de habilitar.
- Sem telemetria: nao enviamos dados para terceiros.
- Aviso: automacao/scraping podem violar ToS de terceiros; uso e de responsabilidade do usuario.

