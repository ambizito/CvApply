# Arquitetura da Solução

A arquitetura do CvApply prioriza execução 100% local. Um serviço Python coordena a interface desktop (Tkinter/ttk), a automação de navegação com Playwright/WebKit e as integrações com modelos de linguagem. Todas as informações persistem em arquivos JSON no diretório do usuário, e variáveis sensíveis permanecem em `.env`.

## Diagrama de Componentes

- **Interface Local (Tkinter/ttk)**: fluxo guiado para capturar dados do candidato, configurar provedores de LLM e acompanhar execuções de scraping.
- **Orquestrador Python**: expõe serviços internos (FastAPI interna opcional) para a UI, realiza validações, gera prompts e controla estados salvos em JSON.
- **Módulo LLM**: adapta prompts para provedores remotos ou locais (Ollama/LM Studio). Respeita configuração local-first e permite fallback manual.
- **Automação Playwright (WebKit visível)**: abre o navegador WebKit para scraping e preenchimento. Eventos de CAPTCHA disparam notificação na UI para o usuário concluir manualmente.
- **Persistência JSON**: arquivos `profiles.json`, `jobs.json`, `runs.json` e `settings.json` versionam dados de usuário, vagas e execuções.

## Tecnologias Utilizadas

- **Linguagem**: Python 3.11+.
- **Interface**: Tkinter com widgets ttk e estilos customizados.
- **Automação**: Playwright com engine WebKit, executando em modo headed para que o usuário acompanhe cada passo.
- **Integração LLM**: bibliotecas `openai`, `anthropic`, `ollama` (condicionais) e/ou `langchain` para composição de pipelines.
- **Geração de Documentos**: `weasyprint` para PDF, `python-docx-template` para DOCX e renderização HTML/Markdown com `markdown-it-py`.
- **Configuração**: `.env` carregado via `python-dotenv` para chaves privadas e seleção de provedores.

## Hospedagem

- Distribuição local via pacote Python (pip/poetry) ou binário criado com PyInstaller.
- Execução acontece na estação do usuário, sem dependência de serviços externos obrigatórios.
- Atualizações são entregues como novos instaladores ou scripts de upgrade.

## Camadas e Adapters

1. **UI Layer**: janelas Tkinter/ttk para perfil, análise de vagas, geração e exportação. Comunica-se com o orquestrador via chamadas diretas ou API local.
2. **Core Services**:
   - `profiles`: ingestão, deduplicação e normalização dos dados de currículo.
   - `jobs`: busca, scraping e monitoramento de vagas, reutilizando Playwright para navegação assistida.
   - `generation`: composição de prompts, chamada a LLMs e pós-processamento dos documentos.
3. **Automation Adapter**: camada que encapsula Playwright, detecta mudanças de DOM, sinais de CAPTCHA e disponibiliza hooks para a UI.
4. **Persistence Adapter**: abstrai leitura/escrita em JSON, garantindo bloqueio de arquivo e backups incrementais.
5. **Integration Adapter**: gerencia conectores de LLM e fallback local.

## Diagrama (ASCII)

```
[Usuário]
    |
[Tkinter/ttk UI]
    |
[Orquestrador Python]----[Persistência JSON]
    |               \
    |                \--[Módulo LLM]
    |
[Playwright WebKit (headed)] --> [Navegador visível]
           |
   [Detecção de CAPTCHA] -> [Prompt ao usuário]
```

## Modelo de Dados (sugerido)

- `data/profiles.json`: dados pessoais, habilidades, experiências, idiomas.
- `data/jobs.json`: vagas coletadas (origem, status, notas do usuário).
- `data/runs.json`: histórico de execuções de automação, incluindo marcação de CAPTCHAs e tempo gasto.
- `config/settings.json`: preferências de layout, provedores de LLM habilitados, caminhos de templates.
- `templates/`: layouts base para PDF/DOCX/HTML.
- `logs/`: auditoria local das execuções Playwright, incluindo capturas de tela e passos executados.
