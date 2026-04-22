from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from state import AgentState
from tools import port_scan_tool, mysql_login_check, safe_sql_query

llm_fast = ChatOllama(model='mistral', temperature=0)

llm_smart = ChatOllama(model='llama3', temperature=0.2)

def scanner_node(state: AgentState):
    print('Nó de escaneamento')

    ip = state['target_ip']
    port = state['target_port']
    status = port_scan_tool.invoke({'ip':ip, 'port':port})
    results = [f'Porta: {port}, Status: {status}']

    if status == 'OPEN':
        results.append('Serviço: MySQL (beseado pela porte)')

    return {'scan_results' : results}

def triage_node(state: AgentState):
    print('Nó de triagem e validação')
    results = state['scan_results']
    ip = state['target_ip']

    verified = []

    if any('MySQL' in r for r in results):
        check_msg = mysql_login_check.invoke({
            'ip' : ip,
            'user' : 'root',
            'password_list' :['root', ' 123456', 'password', 'admin']
        })

        if 'SUCESS' in check_msg:
            pwd = check_msg.split("'")[-2]
            
            verified.append({
                "type": "Weak Credentials",
                "severity": "CRITICAL",
                "details": check_msg,
                "credential": pwd
            })
            
            version_info = safe_sql_query.invoke({
                "ip": ip,
                "user": "root",
                "pwd": pwd,
                "query": "SELECT @@version;"
            })
            
            verified.append({
                "type": "Outdated Version",
                "severity": "MEDIUM",
                "details": f"DB Version: {version_info}"
            })

    return {'verified_vul' : verified}

def rerank_node(state: AgentState):
    print('Nó de re-ranqueamento...')

    vul = state['verified_vul']

    if not vul:
        return {'verified_vul' : []}
    
    prompt = PromptTemplate(
        template="""
        You are a CISO. Rank the following vulnerabilities by immediate business risk (0-100 score).
        Return JSON list.
        Vulnerabilities: {vulns}
        """,
        input_variables=["vulns"]
    )

    chain = prompt | llm_smart | JsonOutputParser()

    try: 
        ranked_vul = chain.invoke({'vul':str(vul)})

    except:
        ranked_vul = vul

    return {'verified_vul' : ranked_vul}

def remediation_node(state: AgentState):
    print('Nó de remediação...')

    vul = state['verified_vul']

    prompt = PromptTemplate(
        template="""
        You are a Senior DevOps Security Engineer.
        For each vulnerability found, provide the EXACT technical command to fix it.
        
        Context:
        - Database: MySQL 5.7
        - Environment: Docker
        - Target IP: {ip}
        
        Vulnerabilities:
        {vul}
        
        Output format:
        Provide a list of code blocks (SQL or BASH).
        Do not explain why, just show how.
        """,
        input_variables = ["vul", "ip"]
    )

    remediation_plan = (prompt | llm_smart).invoke({
        'vul': str(vul),
        'ip' : state['target_ip']
    })

    return {'remediation_steps' : remediation_plan.content}

def node_reporter(state: AgentState):
    print('Nó de reportar...')

    vul = state['verified_vul']
    fixes = state['remediation_steps']

    prompt = PromptTemplate(
        template="""
        Write a Professional Penetration Test Report.
        Language: Portuguese.
        
        Structure:
        1. Executive Summary
        2. Technical Findings (Use the provided findings)
        3. Recommended Remediation (Use the provided technical fixes)
        
        Findings Data:
        {vul}
        
        Technical Fixes Data:
        {fixes}
        """,
        input_variables = ["vul", "fixes"]
    )

    report = (prompt | llm_fast).invoke({
        'vul' : str(vul),
        'fixes' : str(fixes)
    })
    
    return {'final_report' : report.content}


