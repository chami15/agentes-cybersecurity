# Projeto 4 — ProgCompliGuard

Sistema **multi-agente** de auditoria de código: recebe um arquivo de código + a política de desenvolvimento da empresa, aponta as violações e devolve uma versão refatorada do código aplicando as correções.

## O que faz

O usuário sobe dois arquivos no Streamlit:
1. A **política da empresa** (`.txt`) — ex: regras de segurança, nomenclatura, tratamento de exceções.
2. O **código** a auditar (`.py`, `.java`, `.c`, `.cpp`).

A política vai para um RAG (Chroma + HuggingFace embeddings). Depois, um pipeline LangGraph com dois agentes executa em sequência:

1. **Agente Auditor** — Lê o código linha por linha, cruza com o contexto da política via RAG e gera um relatório listando violações ("Violação da Regra X") e conformidades ("Em conformidade com a Regra X"). Não corrige nada.
2. **Agente Corretor** — Recebe o relatório do Auditor + o código original + o contexto e devolve o código refatorado com explicação curta de cada mudança.

A UI mostra os dois relatórios lado a lado em colunas.

## Quando usar

Use este projeto como referência quando precisar de:
- Um exemplo de **multi-agente com separação de responsabilidades** (auditar ≠ corrigir), onde cada agente tem um system prompt focado e a saída de um vira input do outro.
- Demonstrar a técnica de **Chain-of-Thought via instruções numeradas** no system prompt para guiar o raciocínio do LLM.
- Aplicar **RAG sobre uma política/documento de governança** que o usuário fornece em runtime, sem precisar treinar nada.
- Permitir que o usuário insira a **API Key na própria UI** (para deploys onde cada usuário usa sua chave).

## Stack

- **LangGraph** com `StateGraph` linear (`auditor → corretor → END`).
- **LangChain + Groq** (`llama-3.3-70b-versatile`).
- **ChromaDB** em memória + HuggingFace Embeddings (`all-MiniLM-L6-v2`).
- **Streamlit** com upload duplo (política + código).

## Estrutura

- [app_agente.py](app_agente.py) — Tudo em um arquivo: setup do RAG, definição do estado, dois nós do grafo, build do workflow e UI Streamlit.
- [tmp_policy.txt](tmp_policy.txt) — Política de exemplo (DSATechCorp — Python). Usado como referência e regravado a cada execução com o conteúdo enviado pelo usuário.

## Como rodar

1. Instale dependências (compartilhadas com os demais projetos LangChain).
2. Execute: `streamlit run app_agente.py`.
3. Cole sua API Key do Groq na sidebar.
4. Suba um arquivo de política e um arquivo de código.
5. Clique em "Executar".
