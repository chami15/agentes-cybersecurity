import os
import streamlit as st
from typing import TypedDict, List
from openai import OpenAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


os.environ['TOKENIZERS_PARALLELISM'] = 'false'

st.set_page_config(page_title='Agente de IA', page_icon=':robot_face:', layout='wide')
st.title('Agente de IA')
st.title('ProgCompliGuard: Auditoria do codigo com Agentes de IA')
st.markdown('---')

with st.sidebar:
    st.header('Configurações')

    api_key = st.text_input('Cole sua API Key aqui', type='password')
    uploaded_policy = st.file_uploader('Upload Politica da empresa', type=['txt'])
    uploades_code = st.file_uploader('Upload do codigo', type=['py', 'java', 'c', 'cpp'])

    st.divider()

    st.info(''' 
        Projeto 4 do curso
        Use a IA com responsabilidade
    ''')

if not api_key:
    st.warning('Por favor insira sua chave de API')
    st.stop()

@st.cache_resource
def setup_rag(policy_text):
    with open('tmp_policy.txt', 'w', encoding='utf-8') as f:
        f.write(policy_text)

    loader = TextLoader('tmp_policy.txt', encoding='utf-8') #carrega documento
    documents = loader.load()#abre documento
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)#picota em partes
    docs = text_splitter.split_documents(documents)#volta doc picotado em partes

    embeddings = HuggingFaceEmbeddings(model_name = 'all-MiniLM-L6-v2')#cria embbedings
    db = Chroma.from_documents(docs, embeddings, collection_name='complice_rules')#coloca embeddings e doc em banco vetorial
    return db.as_retriever(search_kwargs={'k': 3})

class AgentState(TypedDict):
    code: str
    compliance_report: str
    correction_suggestion: str
    rag_context: str

llm = ChatGroq(api_key=api_key, model_name='llama-3.3-70b-versatile', temperature=0)

def agente_auditor(state:AgentState):

    code = state['code']
    context = state['rag_context']

    system_prompt = """Você é um Auditor Sênior de Segurança de Software (Agente 1).
    Sua tarefa é analisar códigos de programação nas mais diversas linguagens mas sempre em 
    relação às políticas da empresa fornecidas no contexto.
    
    CONTEXTO DE GOVERNANÇA (RAG):
    {context}
    
    CÓDIGO PARA ANÁLISE:
    {code}
    
    INSTRUÇÕES (CHAIN-OF-THOUGHT):
    1. Analise o código linha por linha.
    2. Para cada bloco de código, verifique se há uma regra correspondente no Contexto de Governança.
    3. Se encontrar uma violação, cite explicitamente: "Violação da Regra X (Página Y)".
    4. Se o código estiver correto, cite: "Em conformidade com a Regra X".
    5. Não sugira correções de código ainda, apenas liste os achados de conformidade e não conformidade.
    
    Saída esperada: Um relatório detalhado de auditoria."""

    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm
    response = chain.invoke({'context': context, 'code': code})
    return {'compliance_reporte' : response.content}

def agente_corretor(state:AgentState):
    code = state['code']
    report = state['compliance_report']
    context = state['rag_context']

    system_prompt = """Você é um Engenheiro de Software Especialista em Refatoração Segura (Agente 2).
    Sua tarefa é corrigir o código baseado no relatório do Auditor.
    
    CÓDIGO ORIGINAL:
    {code}
    
    RELATÓRIO DO AUDITOR:
    {report}
    
    CONTEXTO DE REGRAS:
    {context}
    
    INSTRUÇÕES (CHAIN-OF-THOUGHT):
    1. Leia o relatório do auditor para identificar os pontos críticos.
    2. Para cada violação apontada, reescreva o código de programação aplicando a correção necessária.
    3. Explique brevemente por que a mudança foi feita (ex: "Substituído System.out por Logger conforme Regra 3.2").
    4. Forneça o código completo refatorado no final.
    """

    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm
    response = chain.invoke({'report': report, 'code': code, 'context': context})
    return {'correction_suggestion': response.content}
    

workflow = StateGraph(AgentState)

workflow.add_node('auditor', agente_auditor)
workflow.add_node('corretor', agente_corretor)

workflow.set_entry_point('auditor')

workflow.add_edge('auditor', 'corretor')
workflow.add_edge('corretor', END)

app_graph = workflow.compile()

if uploaded_policy and uploades_code:
    policy_text = uploaded_policy.read().decode('utf-8')
    code_text = uploades_code.read().decode('utf-8')

    retriver = setup_rag(policy_text)

    if st.button('Executar'):
        with st.spinner('Executando...'):
            relevant_docs = retriver.invoke('segurança credenciais logs bugs exception sql injection boas praticas')
            context_str = '\n'.join([doc.page_content for doc in relevant_docs])

            inicial_state = {
                'code' : code_text,
                'rag_context' : context_str,
                'compliance_report' : '',
                'correction_suggestion' : ''
            } 

            result = app_graph.invoke(inicial_state)

            st.success('Executado com sucesso!')
            st.markdown('---')

            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Relatorio do Agente Auditor')
                st.text(result['compliance_report'])
                st.markdown(result['compliance_report'])

            with col2:
                st.subheader('Relatorio do Agente Corretor')
                st.markdown(result['correction_suggestion'])

            with st.expander('Ver codigo original'):
                st.code(code_text, language='python, java, c, cpp')

elif not uploaded_policy:
    st.warning('Por favor insira a politica da empresa')










