# Programação de Funcionalidades

Esta seção descreve as funcionalidades planejadas para o CvApply considerando a nova arquitetura local com backend Python, automação Playwright/WebKit e interface Tkinter/ttk. O objetivo é manter o usuário no controle, acompanhando automações em tempo real e armazenando dados apenas no dispositivo.

## Visão Geral do Fluxo

1. **Inicialização e Pré-verificações**
   - Execução de testes automatizados de ambiente (conectividade geral, acesso ao LinkedIn, presença e validade de credenciais) via módulo `system_checks`.
   - Leitura de arquivos JSON (`profiles.json`, `jobs.json`, `runs.json`, `settings.json`).
   - Carregamento do `.env` para chaves de LLM e parâmetros de scraping.
   - Sincronização da UI com o estado persistido (últimos perfis e vagas acessadas).

2. **Onboarding e Gestão de Perfil**
   - Coleta inicial de email e senha do LinkedIn quando o usuário abre o app pela primeira vez, com persistência local cifrada pelo `SessionManager`.
   - Onboarding assistido para criação do perfil Playwright/WebKit e tentativa de login automática nas execuções subsequentes.
   - Formulários Tkinter/ttk para dados pessoais, experiências, habilidades e idiomas.
   - Validação imediata (campos obrigatórios, limites de caracteres) e salvamento incremental no JSON.
   - Geração de versões de currículo baseadas em templates (PDF/DOCX/HTML/Markdown) com revisão visual.

3. **Busca e Scraping de Vagas**
   - Configuração de filtros (palavras-chave, local, tipo de contrato) e execução do Playwright em WebKit headed.
   - Exibição do navegador durante a automação, permitindo ao usuário acompanhar cliques, scrolls e coletas.
   - Detecção de CAPTCHA via eventos de DOM; a UI pausa o fluxo e solicita que o usuário resolva manualmente (RF-008).
   - Registro estruturado das vagas encontradas em `jobs.json`, com captura de contexto (link, empresa, notas do usuário).

4. **Geração e Adaptação Assistida por LLM**
   - Seleção de provedores disponíveis (local via Ollama, nuvem mediante configuração). Nenhum tráfego é enviado sem consentimento.
   - Construção de prompts dinâmicos com base nos dados do perfil e descrição da vaga.
   - Pós-processamento dos resultados (normalização de bullets, verificação de requisitos) antes de disponibilizar para edição.

5. **Preenchimento Assistido de Formulários**
   - Utilização do Playwright para navegar até o formulário de candidatura.
   - Campos são preenchidos de forma automatizada; o usuário pode intervir a qualquer momento.
   - Quando campos livres demandam resposta personalizada, a UI oferece sugestões geradas pelo LLM para revisão humana.

6. **Exportação e Auditoria**
   - Salvamento de versões finais em múltiplos formatos com histórico vinculado à vaga.
   - Geração de logs e capturas de tela das automações para auditoria local.
   - Possibilidade de reabrir execuções anteriores a partir de `runs.json`.

## Requisitos Cobertos

- RF-001, RF-002, RF-003, RF-006, RF-007, RF-008.

## Orientações de Execução

1. Crie e ative um ambiente virtual Python.
2. Instale dependências (FastAPI opcional, Playwright com `playwright install --with-deps webkit`).
3. Configure o arquivo `.env` com as chaves de LLM desejadas.
4. Inicie o aplicativo via `python -m cvapply.app` (executa a UI Tkinter) e acompanhe o navegador WebKit aberto automaticamente.

## Troubleshooting Inicial

- **Playwright não encontra o WebKit**: execute `playwright install webkit` novamente e verifique permissões do SO.
- **Variáveis de ambiente ausentes**: confirme o `.env` e reinicie a aplicação para recarregar as configurações.
- **Arquivos JSON corrompidos**: utilize o backup incremental gerado em `data/backups/` para restaurar o estado.
- **Falha nas verificações prévias**: corrija a conexão com a internet, confira o status do LinkedIn e edite/salva novamente as credenciais pelo menu de configurações antes de reiniciar o fluxo.
