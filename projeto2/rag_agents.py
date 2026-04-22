import os
import certifi
import shutil
from typing import TypedDict
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
os.environ['SSL_CERT_FILE'] = certifi.where()


def get_llm():
    if 'GROQ_API_KEY' not in os.environ:
        raise EnvironmentError('GROQ_API_KEY não encontrada no arquivo .env')
    return ChatGroq(model='llama-3.3-70b-versatile', temperature=0)

class AgenteState(TypedDict, total=False):
    raw_logs: str
    cleaned_log: str
    retrived_context: str
    analysis_report: str

def carrega_dados():
    presist_dir = os.environ.get('RAG_PERSIST_DIR', './rag_store')

    kb_dir = os.environ.get('RAG_KB_DIR', './knowledge_base')

    embbedings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

    if os.path.exists(presist_dir) and os.listdir(presist_dir):
        try:
            vectorDB = Chroma(persist_directory=presist_dir, embedding_function=embbedings)
            # Teste rápido para garantir que o banco está acessível
            vectorDB.as_retriever(search_kwargs={"k": 1}).invoke("test")
            return vectorDB.as_retriever(search_kwargs = {"k": 5})
        except Exception:
            # Se o banco estiver corrompido, removemos para recriar do zero
            try:
                shutil.rmtree(presist_dir)
            except Exception:
                pass
    
    text, metadados = [] , []

    if os.path.isdir(kb_dir):
        for root, _, files in os.walk(kb_dir):
            for fname in files:
                if fname.lower().endswith(('.txt', '.md')):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():
                                text.append(content)
                                metadados.append({'source': fpath})
                    except Exception:
                        pass

    if not text:
        text = ['Cole aqui procedimentos internos de resposta a incidentes mapeamento mitre attack e etc']

        metadados = [{'source': 'placeholder'}]

    vectorDB = Chroma.from_texts(
        texts=text,
        embedding=embbedings,
        metadatas=metadados,
        persist_directory=presist_dir
    )
    return vectorDB.as_retriever(search_kwargs = {"k": 5})

def retrive(retriver, query:str):
    if hasattr(retriver, 'invoke'):
        return retriver.invoke(query)
    if hasattr(retriver, 'get_relevant_documents'):
        return retriver.get_relevant_documents(query)
    return []

def rag_tool(query: str) -> str:
    retriver = carrega_dados()
    docs = retrive(retriver, query)
    if not docs:
        return "nenhum contexto relevante foi encontrado"
    joined = '\n\n'.join([f"[Fonte: {getattr(d, 'metadata', {}).get('source', 'desconhecida')}]\n{getattr(d, 'page_content', str(d))}" for d in docs])
    return joined if joined.strip() else "nenhum contexto relevante foi encontrado"

def agente_processa_dados(state : AgenteState) -> dict:
    print('Iniciando processamento do Agente')

    system_prompt='''Você é um agente de pré-processamento de dados de segurança. Sua tarefa é 
    receber um bloco de logs de servidor web. 
    
    Seu trabalho é:
    1.  Filtrar e remover linhas de "ruído" (ex: logs de status 200 para 
        arquivos .jpg, .png, .css, .js).
    2.  Manter todas as linhas que parecem suspeitas ou anômalas. 
        Exemplos de logs suspeitos:
        - Status HTTP 404, 403, 401, 500.
        - Tentativas de injeção (SQLi) (ex: ' OR '1'='1', 'UNION SELECT').
        - Tentativas de Directory Traversal (ex: '../', '/etc/passwd').
        - Scanners de vulnerabilidade (ex: User-Agents como "Nmap", "sqlmap").
        - Probing de diretórios (ex: /admin.php, /wp-login.php).

    Retorne *apenas* a lista de logs suspeitos que o analista deve investigar.
    Se nenhum log suspeito for encontrado, retorne "Nenhuma atividade suspeita detectada.
'''
    prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Por favor, filtre os seguintes logs:\n\n{logs}")
        ])

    chain = prompt | get_llm()
    response = chain.invoke({"logs": state["raw_logs"]})

    cleaned_log = response.content
    print(f"--- Logs Limpos ---\n{cleaned_log}")
    return {"cleaned_log": cleaned_log}

def agente_analisa_dados(state : AgenteState) -> dict:
    print('Iniciando Analise do Agente')

    rag_query = (
        "Forneça contexto tático, técnicas MITRE ATT&CK relevantes e guias de remediação "
        "para analisar as seguintes evidências de ataque em logs web:\n\n"
        f'{state["cleaned_log"][:4000]}'
    )

    context = rag_tool(rag_query)

    system_prompt = """
    Você é o "ThreatRAG Sentinel", um Analista de Cibersegurança de IA sênior.
    Sua tarefa é analisar os logs de servidor web *pré-filtrados* e suspeitos 
    e gerar um relatório completo em Markdown, incorporando contexto recuperado via RAG.
    O relatório deve incluir:
    1. Resumo Executivo (1–2 frases)
    2. Ameaças Identificadas (tipos e descrições)
    3. IOCs (IPs, User-Agents, URLs/endpoints)
    4. TTPs mapeadas ao MITRE ATT&CK (IDs e justificativas)
    5. Recomendações (curto e longo prazo, priorizadas)
    6. Referências/Fontes (inclua as fontes da KB quando existirem)
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human",
         "Evidências (logs suspeitos):\n\n{logs}\n\n"
         "Contexto RAG recuperado (fontes internas):\n\n{context}\n\n"
         "Gere o relatório completo seguindo a estrutura acima.")
    ])

    chain = prompt | get_llm()
    response = chain.invoke({"logs": state["cleaned_log"], "context": context})
    
    report = response.content
    print(f"--- Contexto RAG (trecho) ---\n{context[:1000]}")
    print(f"--- Relatório Final ---\n{report}")
    return {"retrieved_context": context, "analysis_report": report}

def cria_grafo():
    workflow = StateGraph(AgenteState)
    workflow.add_node('preprocessor', agente_processa_dados)
    workflow.add_node('analyzer', agente_analisa_dados)
    workflow.set_entry_point('preprocessor')
    workflow.add_edge('preprocessor', 'analyzer')
    workflow.add_edge('analyzer', END)
    app = workflow.compile()
    return app

def executa_grafo(log_data: str) -> dict:
    app = cria_grafo()
    inputs = {"raw_logs": log_data}
    final_state = app.invoke(inputs)
    return final_state
