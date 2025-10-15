# CvApply — Documentação do Projeto *(PT/EN)*

> **Status**: Rascunho / Skeleton — v0.1
> **Licença sugerida**: Apache-2.0
> **Alvo de UI**: CLI **ou** Desktop (Electron) **ou** Web local (decidir pelo caminho mais simples durante o MVP)


## Visão Geral / Overview

**PT**: O **CvApply** é uma aplicação open source para desenvolvedores que automatiza a criação e adaptação de currículos para vagas — inicialmente focada no LinkedIn. O app coleta dados do usuário (formulários, LinkedIn, GitHub, CV existente), busca vagas, e usa LLMs para gerar versões do currículo alinhadas à descrição da vaga, em PT-BR e EN. Todo o processamento e armazenamento são **locais**, exceto chamadas opcionais à API de LLM (ou uso de LLM local).

**EN**: **CvApply** is an open-source app for developers that automates resume generation/tailoring for jobs — starting with LinkedIn. It ingests user data (forms, LinkedIn, GitHub, existing CV), searches jobs, and uses LLMs to produce role-aligned resumes in PT-BR and EN. All processing/storage is **local**, except optional calls to a cloud LLM API (or a local LLM).

> **Nota/Note**: Automação e scraping podem violar Termos de Serviço de terceiros. O uso é de responsabilidade do usuário. / Automation & scraping may violate third-party ToS. Use at your own risk.

---

## Documentação / Table of Contents

* [Visão Geral / Overview](#visão-geral--overview)
* [Recursos Principais / Key Features](#recursos-principais--key-features)
* [Arquitetura / Architecture](#arquitetura--architecture)
* [Modos de Interface / Interface Modes](#modos-de-interface--interface-modes)
* [Fluxo de Ponta a Ponta / End-to-End Flow](#fluxo-de-ponta-a-ponta--end-to-end-flow)
* [Requisitos Funcionais](#requisitos-funcionais)
* [Requisitos Não Funcionais](#requisitos-não-funcionais)
* [Instalação / Installation](#instalação--installation)
* [Configuração (.env)](#configuração-env)
* [Segurança e Privacidade / Security & Privacy](#segurança-e-privacidade--security--privacy)
* [Modelo de Dados / Data Model](#modelo-de-dados--data-model)
* [Templates (CV/Letters/Prompts)](#templates-cvlettersprompts)
* [Qualidade/ATS & Métricas](#qualidadeats--métricas)
* [Testes / Testing](#testes--testing)
* [Roadmap](#roadmap)
* [Contribuindo / Contributing](#contribuindo--contributing)
* [Licença / License](#licença--license)
* [FAQ](#faq)
* [Troubleshooting](#troubleshooting)



---

## Recursos Principais / Key Features

* Ingestão de dados: formulários, LinkedIn (scraping autenticado), GitHub, PDF/DOCX.
* Unificação de experiências (deduplicação e merge via LLM). Campos **fixos** (não alterar) e **forçar inclusão**.
* Busca de vagas no LinkedIn (keywords, local/remoto, nível, filtros básicos).
* Geração de currículo **ATS-friendly** (PT-BR/EN), carta de apresentação e respostas para screening.
* Edição com diffs, versionamento por vaga, exportação em **PDF/DOCX/HTML/Markdown**.
* “Um clique” para abrir/preencher a candidatura (quando possível), com confirmações humanas.
* Suporte multi-LLM (OpenAI/Azure/Anthropic/Local via Ollama), fallback configurável.
* Armazenamento **sem banco**, em **JSON/YAML** locais.

---

## Arquitetura / Architecture

**Camadas e Adapters**

* **Core Orchestrator**: fluxo geral (coleta → busca → geração → revisão → aplicação).
* **Scraper Adapter (LinkedIn)**: automação de navegador (ex.: Playwright/Puppeteer) + sessão/login.
* **LLM Provider Adapter**: OpenAI/Azure/Anthropic/Local (Ollama) com fallback e caching.
* **Templates/Exporters**: HTML → PDF/DOCX/MD; prompts versionados por perfil/idioma.
* **UI Adapters**: CLI / Electron / Web local.
* **Storage Local**: `data/` (perfis, vagas, versões, configs) em JSON/YAML.

**Diagrama (rústico/placeholder)**

```
User ↔ UI (CLI/Electron/Web)
        ↕
     Core Orchestrator
   ↙         |         ↘
Scraper    LLM API     Exporters
 (LinkedIn) (or Local) (PDF/DOCX/MD)
        ↘     |      ↙
            Storage (JSON/YAML)
```

---

## Modos de Interface / Interface Modes

* **CLI**: comandos para importar dados, buscar vagas, gerar CV, exportar.
* **Desktop (Electron)**: UI com formulários, visualização de vagas e editor de CV com diffs.
* **Web Local**: servidor local (localhost), sem serviços externos.

> **MVP**: escolher 1 modo inicial (o mais simples para entregar rápido) e manter interfaces como adapters.

---

## Fluxo de Ponta a Ponta / End-to-End Flow

1. **Perfil**: usuário preenche formulários OU importa LinkedIn/GitHub/CV (PDF/DOCX).
2. **Normalização**: merge/dedupe via LLM; marcar **campos fixos** e **forçar inclusão**.
3. **Vagas (LinkedIn)**: busca/scraping; lista e detalhes; salvar seleção.
4. **Geração**: CV alinhado à vaga + (opcional) carta/answers; PT-BR/EN conforme a vaga.
5. **Revisão**: diffs, ajustes “adicionar algo”, “re-gerar mantendo X”.
6. **Aplicar**: abrir/preencher; revisar perguntas; confirmar upload/envio.
7. **Exportar**: PDF/DOCX/HTML/MD; versionar por vaga.

---

## Requisitos Funcionais

* **Coleta & Preparo**: formulários; import LinkedIn/GitHub/PDF/DOCX; unificação via LLM; campos fixos/forçar inclusão.
* **Busca de Vagas**: LinkedIn (keywords, local/remoto, nível, filtros básicos); dedupe; atualização.
* **Geração**: templates ATS (PT/EN); currículo/carta/answers; respeitar fixos; histórico de versões.
* **Edição/Export**: visualização com diff; re-gerar com restrições; export PDF/DOCX/HTML/MD; bilíngue.
* **Perguntas da Vaga**: extrair/exibir; sugestões da LLM com revisão obrigatória.
* **Aplicação 1-Click**: abrir/preencher via automação; pausas para ações humanas.
* **Configurações**: modo de interface; provedor LLM; idioma; `.env`.
* **Persistência**: arquivos locais JSON/YAML; logs locais.
* **Métricas ATS**: cobertura de keywords; score de alinhamento; alertas de inconsistências.

---

## Requisitos Não Funcionais

* **Privacidade**: tudo local; exceção: chamadas à LLM cloud (ou LLM local). Sem telemetria.
* **Segurança**: segredos via `.env`; não logar dados sensíveis; limpeza de temporários.
* **Portabilidade**: Windows/macOS/Linux. Desempenho-alvo: ~50 vagas em 3–5 min (variável).
* **Robustez**: retry/backoff; detecção de rate-limit/CAPTCHA; reexecução de etapas.
* **Usabilidade**: i18n PT/EN; atalhos/UX simples.
* **Extensibilidade**: adapters (UI/LLM/Scraper/Export); prompts e templates versionados.
* **Conformidade/ToS**: documento de modos de uso; responsabilidade do usuário.
* **Documentação**: README PT/EN; guias de instalação/uso/limitações/troubleshooting.
* **Licença**: Apache-2.0 (sugerido).

---

## Instalação / Installation

**Pré-requisitos** (ex.: Node.js LTS, Python opcional, wkhtmltopdf/Playwright): *TODO*

**Passos genéricos**

```bash
# Clonar
git clone https://github.com/<org>/cvapply.git
cd cvapply

# Copiar exemplo de env
cp .env.example .env
# Editar .env com suas chaves e preferências

# Instalar dependências (ex.: pnpm ou npm)
pnpm i   # ou: npm i

# Rodar modo escolhido (exemplos)
# CLI
pnpm run cli
# Desktop (Electron)
pnpm run desktop
# Web local
pnpm run web
```

---

## Configuração (.env)

Exemplo inicial (ajuste conforme seu provedor/modelo):

```ini
# LLM
LLM_PROVIDER=openai        # openai|azure|anthropic|ollama
OPENAI_API_KEY=sk-xxxx
LLM_MODEL=gpt-4o-mini      # ou modelo local via Ollama
LLM_BASE_URL=              # se usar endpoint custom/local

# Idioma padrão
DEFAULT_LOCALE=pt-BR       # pt-BR|en-US

# LinkedIn (autenticação/sessão)
LINKEDIN_COOKIES_PATH=./data/session/linkedin.json  # sessão do navegador
# Evitar armazenar usuário/senha; preferir salvar sessão via login manual automatizado

# Paths
DATA_DIR=./data
EXPORT_DIR=./export
TEMPLATES_DIR=./templates
PROMPTS_DIR=./prompts
```

> **Boas práticas**: preferir login manual uma vez (headful) e **salvar sessão**. Evitar salvar senhas em disco.

---

## Segurança e Privacidade / Security & Privacy

* **Local-first**: dados do perfil, vagas e currículos ficam no seu disco.
* **LLM Cloud**: se habilitado, o conteúdo relevante para geração será enviado ao provedor. Revise políticas do provedor.
* **Sem telemetria**: o projeto não envia dados para terceiros.
* **Aviso**: automação/scraping podem violar ToS. Você é responsável pelo uso.

---

## Modelo de Dados / Data Model

**Arquivos sugeridos**

```
/data
  profile.json           # dados do usuário normalizados
  sources/
    linkedin_raw.json    # scrap cru do LinkedIn
    github_raw.json      # dados do GitHub
    cv_import.raw.json   # extração de PDF/DOCX
  jobs/
    2025-10-15-linkedin.json  # resultados de busca
  generations/
    <jobId>/cv_v1.md
    <jobId>/cv_v2.md
    <jobId>/coverletter_v1.md
  settings.json
  logs/
```

**Exemplos de schema (simplificado)**

```json
// profile.json (simplificado)
{
  "basics": {"name": "...", "email": "...", "location": "...", "links": ["..."]},
  "skills": ["TypeScript", "React", "Node.js"],
  "experience": [
    {
      "company": "...",
      "role": "...",
      "start": "2023-01",
      "end": "2025-08",
      "highlights": ["...", "..."],
      "fixed": false
    }
  ],
  "education": [...],
  "certifications": [...],
  "fixed_fields": ["skills", "location"]
}
```

---

## Templates (CV/Letters/Prompts)

* **CV**: HTML/Markdown ATS-friendly (1 coluna, fontes padrão). Pastas por idioma (`pt-BR`, `en-US`).
* **Cover Letter**: opcional por vaga.
* **Prompts**: versionados por perfil/idioma/tipo de vaga.

```
/templates
  /cv
    /pt-BR/base.html
    /en-US/base.html
  /cover
    /pt-BR/base.md
    /en-US/base.md
/prompts
  /backend/pt-BR.md
  /backend/en-US.md
  /frontend/pt-BR.md
  /frontend/en-US.md
```

---

## Qualidade/ATS & Métricas

* **Cobertura de keywords**: % de requisitos da vaga mapeados no CV.
* **Score de alinhamento**: fórmula simples (ex.: pesos para requisitos obrigatórios × presença).
* **Alertas**: datas incoerentes, gaps longos, excesso de buzzwords.
* **Validação**: opcional, passar CV por um parser ATS local para sanity check.

---

## Testes / Testing

* **Fixtures**: vagas reais sanitizadas, perfis sintéticos.
* **Mocks**: LLM e scraping.
* **E2E**: fluxo completo com sessão salva (ambiente de desenvolvimento).
* **Regressão de prompts**: snapshot das saídas por vaga-perfil.

---

## Roadmap

* **MVP**: UI única (a decidir), scraping LinkedIn, geração CV PT/EN, export PDF/DOCX/MD, 1-click apply assistido.
* **v0.2**: editor com diffs; answers para screening; caching de LLM; métricas ATS básicas.
* **v0.3**: suporte Ollama (LLM local) plug-and-play; melhor normalização GitHub; melhorias de UX.
* **v0.4**: plug-ins de conectores; testes E2E cross-plataforma; pacote binário (Windows/macOS/Linux).

---

## Contribuindo / Contributing

* **Issues** e **PRs** bem-vindos! Siga o template, inclua steps de reprodução e testes.
* **Padrões**: lint, commit messages, convenções de pasta.

---

## Licença / License

Sugerida: **Apache License 2.0**.
`LICENSE`: *TODO inserir texto oficial.*

---

## FAQ

* **Preciso de banco de dados?** Não. O projeto usa arquivos locais.
* **Posso usar LLM local?** Sim (ex.: Ollama) configurando `LLM_PROVIDER`/`LLM_BASE_URL`.
* **O app aplica automaticamente?** Ele abre e pré-preenche quando possível; passos críticos pedem confirmação humana.
* **Isso viola ToS?** Pode violar. Você assume a responsabilidade pelo uso.

---

## Troubleshooting

* **CAPTCHA/Rate limit**: use sessão salva; reduza frequência; realize login manual headful; tente novamente mais tarde.
* **PDF vazio**: verifique wkhtmltopdf/Playwright PDF e caminhos de template.
* **LLM falha**: checar chave, modelo e limite de tokens; alternar provedor/fallback.
* **Encoding PT/EN**: valide locale e fontes no exportador.

---

## Estrutura de Pastas (sugerida)

```
cvapply/
  apps/
    cli/
    desktop/
    web/
  packages/
    core/
    scraper-linkedin/
    llm/
    exporters/
    templates/
  data/
  prompts/
  docs/
  .env.example
  LICENSE
  README.md
```

> **Próximos passos**: decidir o **modo de UI** para o MVP, criar `.env.example`, definir dependências (Playwright/Export), e iniciar o `core` com contratos dos adapters (TypeScript recomendado).



# Armazenamento do Código-Fonte

* <a href="src/README.md">Código Fonte</a>

# Armazenamento da Apresentação

* <a href="presentation/README.md">Apresentação da solução</a>
