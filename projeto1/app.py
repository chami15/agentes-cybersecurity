#imports
import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rag import get_retriver
from agent import criar_agente, AgentState

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

#setando a pagina
st.set_page_config(page_title="Cyber Guardin", page_icon=":100:", layout="wide")
st.title("CyberGuardian AI")
st.subheader("Agente de conformidade e politicas de segurança")
with st.sidebar:
    st.header("Agente")
    st.header("projeto 1")
    st.divider()

    st.header("instruções de uso")
    st.write(
        """
        1.**Carregue o PDF** Faça upload do PDF de politica de segurança e conformidades no formato PDF.

        2.**Aguarde** O sistema ira processar e indexar o documento inserido.

        3.**Pergunte** Agora sua vez de fazer qualquer pergunta sobre o documento indexado.
        """
    )

    st.info(
        """"
        **Exemplos de uso**:
        -Qual a politica de senhas ? 
        -Como os dados dos clientes devem ser tratados ?
        -Quais os procedimentos para relatar um incidente de segurança ? 
        """
    )
    st.divider()

    st.markdown("A IA pode cometer erros, sempre confira a resposta")

@st.cache_resource
def carrega_agent(upload_file):
    print("Processando novo arquivo PDF")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(upload_file.getvalue())
            tmp_file_path = tmp_file.name

        retriver = get_retriver(tmp_file_path)

        if retriver:
            agent_executor = criar_agente(retriver)
            print("Agente criado com sucesso")
            return agent_executor
        else:
            st.error("Falha ao criar retriver, verifique o pdf")
            return None
        
    except Exception as e:
        st.error(f"erro ao processar arquivo por: {e}")
        return None
    
    finally:
        if "tmp_file_path" in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg["content"])

pdf_doc = st.file_uploader("Carregue sua politica de segurança:", type=['pdf'])

if pdf_doc:
    agent_executor = carrega_agent(pdf_doc)

    if agent_executor:
        if prompt := st.chat_input("Pergunte algo sobre a politica:"):
            st.session_state.messages.append({'role': 'user', 'content':prompt})
            st.chat_message('user').write(prompt)

            system_prompt = (
                "Você é o 'CyberGuardian AI', um assistente de cibersegurança focado em conformidade."
                "Sua única tarefa é responder perguntas sobre o documento de política de segurança fornecido."
                "\n\nREGRAS ESTRITAS DE OPERAÇÃO:"
                "1. Sempre que o usuário fizer uma pergunta, você DEVE usar a ferramenta 'check_security_policy' para buscar a informação."
                "2. Após a ferramenta retornar a informação (como uma 'ToolMessage'), você NUNCA MAIS deve chamar a ferramenta novamente."
                "3. Você DEVE usar o contexto da 'ToolMessage' para formular a resposta final para o usuário."
                "4. Se a ferramenta não encontrar nada, informe ao usuário que a política não cobre esse tópico."
                "5. Responda de forma direta e concisa, baseando-se *apenas* no texto da política."
            )

            langgraph_state_input = [SystemMessage(content=system_prompt)]
            for msg in st.session_state.messages:
                if msg['role'] =='user':
                    langgraph_state_input.append(HumanMessage(content=msg['content']))
                else: 
                    langgraph_state_input.append(AIMessage(content=msg['content']))

            with st.chat_message('assistant'):
                with st.spinner("Analisando politica de segurança"):
                    try:
                        result_state = agent_executor.invoke({"messages" : langgraph_state_input})
                        response = result_state['messages'][-1].content
                        st.session_state.messages.append({'role' : "assistant", 'content':response})
                        st.write(response)
                    except Exception as e:
                        st.error(f"Não foi possivel acessar a memoria do agente: {e}")
                    
else:
    print('por favor carrege um documento pdf pra criar o agente')
