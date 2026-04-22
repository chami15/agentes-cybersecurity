# Projeto 1 — CyberGuardian AI

Agente de conformidade que responde perguntas sobre uma política de segurança em PDF carregada pelo usuário, usando RAG (Retrieval-Augmented Generation) sobre o documento.

## O que faz

O usuário sobe um PDF de política de segurança no Streamlit. O sistema indexa o documento em um vector store FAISS e expõe um chat onde o usuário pergunta sobre o conteúdo da política. O agente decide quando consultar o documento via tool `check_security_policy` e responde apenas com base no que está no PDF.

## Quando usar

Use este projeto como referência quando precisar de:
- Um agente conversacional (ReAct/tool-calling) com **uma única ferramenta de RAG** sobre um documento que o usuário fornece em runtime.
- Um exemplo mínimo de **LangGraph** (`StateGraph` + `ToolNode`) com decisão condicional entre chamar a tool e finalizar.
- Padrão de UI Streamlit com upload de PDF, indexação cacheada (`@st.cache_resource`) e histórico de conversa em `session_state`.

## Stack

- **LangGraph** para orquestrar o agente (nó `agent` + `ToolNode` + roteamento condicional).
- **LangChain + Groq** (`llama-3.3-70b-versatile`) como LLM com tool binding.
- **FAISS** como vector store em memória.
- **HuggingFace Embeddings** (`all-MiniLM-L6-v2`) para gerar embeddings localmente.
- **PyPDFLoader** + `RecursiveCharacterTextSplitter` para chunking.
- **Streamlit** para a interface.

## Estrutura

- [agent.py](agent.py) — Define o `CyberSecurityAgent`, o `AgentState` (TypedDict), o grafo LangGraph e a tool `check_security_policy`.
- [rag.py](rag.py) — Pipeline de indexação: carrega o PDF, divide em chunks, gera embeddings e devolve um retriever FAISS.
- [app.py](app.py) — Interface Streamlit, system prompt do agente e loop de chat.
- [requirements.txt](requirements.txt) — Dependências.

## Como rodar

1. Crie um `.env` na raiz do repositório com `GROQ_API_KEY=...`.
2. Instale dependências: `pip install -r requirements.txt`.
3. Execute: `streamlit run app.py`.
4. Suba um PDF de política e faça perguntas no chat.
