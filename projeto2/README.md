# Projeto 2 — ThreatRAG Sentinel

Sistema **multi-agente** que recebe um arquivo de logs de servidor web, filtra ruído e gera um relatório de ameaças em Markdown enriquecido com contexto de uma base de conhecimento via RAG.

## O que faz

O usuário sobe um `.txt` de logs no Streamlit. Um pipeline LangGraph com dois agentes processa os dados em sequência:

1. **Agente Pré-processador** — Recebe os logs brutos e remove linhas de ruído (status 200 para assets, etc.), mantendo apenas linhas suspeitas (404/403/500, SQLi, directory traversal, scanners, probing de admin).
2. **Agente Analista (ThreatRAG Sentinel)** — Recebe os logs filtrados, consulta uma base interna (Chroma) com procedimentos de resposta a incidentes / mapeamento MITRE ATT&CK, e gera um relatório estruturado: resumo executivo, ameaças, IOCs, TTPs (MITRE), recomendações e fontes.

## Quando usar

Use este projeto como referência quando precisar de:
- Um pipeline **multi-agente sequencial** em LangGraph (sem branching), onde a saída de um agente alimenta o próximo via estado compartilhado (`TypedDict`).
- Um exemplo de **RAG persistente** com Chroma (banco fica salvo em `rag_store/` entre execuções, com fallback se corromper).
- Separação clara entre uma etapa de **limpeza/filtragem** com LLM e uma etapa de **análise** com LLM + RAG.

## Stack

- **LangGraph** com `StateGraph` linear (`preprocessor → analyzer → END`).
- **LangChain + Groq** (`llama-3.3-70b-versatile`) para os dois agentes.
- **ChromaDB** persistente como vector store da base de conhecimento.
- **HuggingFace Embeddings** (`all-MiniLM-L6-v2`).
- **Streamlit** para upload e visualização.

## Estrutura

- [rag_agents.py](rag_agents.py) — Define o estado, os dois nós do grafo, a função `rag_tool` e o builder do grafo (`cria_grafo` / `executa_grafo`).
- [app.py](app.py) — UI Streamlit com upload de log, botão de análise e exibição do relatório final.
- [rag_store/](rag_store/) — Diretório persistente do Chroma.
- `.env` — Espera `GROQ_API_KEY`. Opcional: `RAG_PERSIST_DIR`, `RAG_KB_DIR` (pasta com `.txt`/`.md` da base de conhecimento).

## Como rodar

1. Configure `GROQ_API_KEY` no `.env`.
2. (Opcional) Adicione documentos `.txt`/`.md` em `knowledge_base/` para enriquecer o RAG.
3. Instale dependências: `pip install -r requirements.txt`.
4. Execute: `streamlit run app.py`.
5. Suba um log de servidor web e clique em "Analisar Logs".
