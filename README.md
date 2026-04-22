# Agentes de IA aplicados a Cibersegurança

Repositório com 7 projetos práticos de um curso da DSA para automações de agentes em cybersegurança, cada um demonstrando uma técnica diferente de construção de agentes de IA — de pipelines simples (pergunta/resposta com RAG) até arquiteturas multi-agente event-driven com guardrails e human-in-the-loop. O fio condutor entre todos é o **domínio de cibersegurança defensiva**: análise de logs, auditoria de código, triagem de vulnerabilidades e resposta a incidentes.

## Mapa dos projetos

| # | Projeto | O que demonstra | Stack principal |
|---|---------|------------------|------------------|
| [1](projeto1/) | **CyberGuardian AI** | Agente RAG single-tool sobre PDF de política | LangGraph + Groq + FAISS + Streamlit |
| [2](projeto2/) | **ThreatRAG Sentinel** | Multi-agente sequencial (filtro → análise) com RAG persistente | LangGraph + Groq + Chroma + Streamlit |
| [3](projeto3/) | **LogSense AI (MCP)** | Servidor MCP com 3 níveis de autonomia de cliente (determinístico → autônomo) | MCP (FastMCP) + OpenAI + Chroma |
| [4](projeto4/) | **ProgCompliGuard** | Multi-agente de auditoria (auditor → corretor) com Chain-of-Thought | LangGraph + Groq + Chroma + Streamlit |
| [5](projeto5/) | **IncidentOps** | Dois agentes em série + human-in-the-loop sobre Postgres real | LangChain + Groq + psycopg2 + Docker |
| [6](projeto6/) | **AgenteOps / DevSecOps** | Pipeline event-driven em tempo real (pub/sub) com Ollama local | ZeroMQ + Ollama + rich + asyncio |
| [7](projeto7/) | **Vulnerability Triage AI** | Pipeline de pentest defensivo com 5 nós, roteamento condicional e guardrails | LangGraph + Ollama + MySQL + Docker |

## Por que existem múltiplos projetos

Cada projeto é uma **iteração intencional** sobre uma dimensão diferente da construção de agentes:

- **Quantidade de agentes**: 1 (projeto 1) → 2 sequenciais (projetos 2, 4, 5) → 5 com roteamento (projeto 7).
- **Framework de orquestração**: LangGraph (1, 2, 4, 7) vs. chains manuais LangChain (3, 5) vs. event-driven sem framework de grafo (6).
- **LLM provider**: Groq cloud (1, 2, 4, 5), OpenAI (3), Ollama local (6, 7) — tradeoffs de custo, latência, privacidade.
- **Padrão de RAG**: in-memory FAISS (1) vs. Chroma persistente (2, 4) vs. embeddings da OpenAI no Chroma (3) vs. sem RAG (5, 6, 7).
- **Interface**: Streamlit (1, 2, 4) vs. CLI (3, 5) vs. dashboard rich em terminal (6) vs. saída em `.docx` (7).
- **Nível de autonomia**: pergunta-e-resposta (1, 2) → composição manual de tools (3v1, 3v2, 5) → agente decide e age (3v3, 6, 7).
- **Guardrails / human-in-the-loop**: confirmação manual antes de executar (5), bloqueio de comandos destrutivos (7).

Use este repositório como **catálogo de referência**: quando precisar montar um agente novo, vá direto para o projeto que mais se aproxima do padrão desejado e adapte.

## Pré-requisitos gerais

- **Python 3.10+**.
- **Docker Desktop** (projetos 5 e 7).
- **Ollama** com `llama3` e `mistral` (projetos 6 e 7).
- API keys (cada projeto usa uma combinação): `GROQ_API_KEY`, `OPENAI_API_KEY`. Configurar em `.env` na pasta do projeto.

Cada projeto tem seu próprio `README.md` com instruções específicas de execução.
