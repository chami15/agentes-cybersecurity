import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tools import tool_inspect_permission, tool_execute_contaiment
from dotenv import load_dotenv

load_dotenv()

llm_detective = ChatGroq(
    temperature = 0,
    model_name = 'llama-3.3-70b-versatile',
    api_key = os.getenv('GROQ_API_KEY')
)

llm_responder = ChatGroq(
    temperature = 0,
    model_name = 'llama-3.3-70b-versatile',
    api_key = os.getenv('GROQ_API_KEY')
)

def main():
    print('INICIANDO SISTEMA DE INCIDENTOPS')

    print('[*] Agente Detetive iniciando varredura de permissões')

    scan_result = tool_inspect_permission()
    print(f'Dados brutos do scan:\n{scan_result}')

    detective_prompt = ChatPromptTemplate.from_template(
    """
     Você é um Analista de Segurança Sênior (Blue Team).
        Analise o seguinte relatório de permissões de banco de dados:
    
        {scan_data}
    
        Se encontrar permissões concedidas a 'PUBLIC' em tabelas sensíveis, isso é um INCIDENTE CRÍTICO.
        Responda APENAS com um JSON no formato:
        {{
            "is_incident": true/false,
            "severity": "High/Medium/Low",
            "summary": "Resumo do que foi encontrado"
        }}
    """
    )

    chain_detective = detective_prompt | llm_detective
    analysis = chain_detective.invoke({'scan_data': scan_result})
    print(f'Analise do detetive: {analysis.content}')

    if 'true' not in analysis.content:
        print('[-] Nenhuma vulnerabilidade detectada. Encerrando.')
        return

    print('[!] INCIDENTE DETECTADO! Iniciando contenção...')

    prompt_responder = ChatPromptTemplate.from_template(
        """
         Você é um Engenheiro de Resposta a Incidentes (DBA Security).
        O Agente Detetive encontrou o seguinte problema: {scan_data}
        
        Sua tarefa: Gerar o comando SQL PostgreSQL exato para REVOGAR (REVOKE) 
        as permissões inseguras encontradas para o grupo 'PUBLIC'.
        
        Regras:
        1. Retorne APENAS o código SQL.
        2. Não inclua markdown, explicações ou ```.
        3. O comando deve ser algo como: REVOKE ALL ON TABLE nome_tabela FROM PUBLIC;
        """
    )
    chain_responder = prompt_responder | llm_responder
    containment_plan = chain_responder.invoke({"scan_data":analysis})
    sql_command = containment_plan.content.strip()
    
    print(f'[*] Agente respondente sugeriu ação: {sql_command}')

    confirm = input('Deseja executar o comando de contenção? (s/n): ')
    if confirm.lower() == 's':
        result = tool_execute_contaiment(sql_command)
        print(f'Resultado da execução: {result}')
        print('[*] Revalidando o ambiente')
        final_scan = tool_inspect_permission()
        print(f'Scan final: {final_scan}')
    else:
        print('[!] Operação cancelada pelo usuário.')

if __name__ == '__main__':
    main()


