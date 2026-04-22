import os 
import streamlit as st
from dotenv import load_dotenv
from rag_agents import executa_grafo


st.set_page_config(page_title = "Agente de Segurança", page_icon = ":100:", layout = "wide")

if not load_dotenv():
    st.error("Não foi possível carregar o arquivo .env. Certifique-se de que ele existe na raiz do projeto.")
    st.stop()

if "GROQ_API_KEY" not in os.environ or not os.environ["GROQ_API_KEY"]:
    st.error("GROQ_API_KEY não encontrada no .env. Por favor, adicione sua chave de API do Groq.")
    st.stop()

st.title("🛡️ Projeto 2 ThreatRAG Sentinel")
st.markdown("Sistema Multi-Agentes de IA Para Detecção e Análise de Ameaças em Logs")
st.write('Faça o upload de um arquivo de log de servidor web (.txt) e os Agentes de IA irão limpá-lo e analisá-lo em busca de ameaças.')

col1, col2=st.columns([1, 2])

with col1:
    st.subheader("Carregar Arquivo de Log")
    uploaded_file = st.file_uploader("Escolha o arquivo de log (.txt)", type="txt")
    analyze_button = st.button("Analisar Logs", type="primary", use_container_width=True)
    st.info("""Como funciona?
    1.  **Agente 1 (Pré-processador):** Filtra os logs, removendo ruídos e isolando linhas suspeitas.
    2.  **Agente 2 (Analista):** Recebe os logs filtrados e gera um relatório completo de ameaças.
    3. IA pode cometer erros. Use esta app com cautela
""")

with col2:
    st.subheader("Relatório de Análise")
    if analyze_button and uploaded_file is not None:
        log_data = uploaded_file.read().decode("utf-8")
        with st.expander("Ver logs brutos carregados"):
            st.code(log_data, language="log")
        with st.spinner("Os Agentes de IA estão analisando os logs... 🕵️‍♂️"):
            try:
                final_state = executa_grafo(log_data)
                st.markdown(final_state['analysis_report'])
                with st.expander("Ver logs filtrados (input do Analista)"):
                    st.code(final_state['cleaned_log'], language="log")
            except Exception as e:
                st.error(f"Ocorreu um erro durante a análise: {e}")
                st.exception(e)
    elif analyze_button:
        st.warning("Por favor, faça o upload de um arquivo de log primeiro.")
    else:
        st.info("Aguardando o upload do arquivo de log e o comando de análise.")

